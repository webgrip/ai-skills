#!/usr/bin/env python3
"""Per-skill release trains (Forgejo-hosted).

Each skill is its own independent release train:
  - its own tag         `<skill>-v<MAJOR.MINOR.PATCH>`
  - its own changelog   `skills/<skill>/CHANGELOG.md`
  - its own version     `skills/<skill>/.claude-plugin/plugin.json` (+ marketplace mirror)
  - its own artifact     the `<skill>.skill` zip, published to the generic
                         package registry at that skill's version
bumped ONLY by conventional commits that touch `skills/<skill>/` since that
skill's last tag. There is no repo-wide release tag — a change to one skill
releases that skill and nothing else.

    python3 scripts/release_skills.py plan     # print what would release; no writes, no side effects
    python3 scripts/release_skills.py apply     # write versions + changelogs + marketplace, commit, tag;
                                                 # push + Forgejo release + package publish when CI env present
    python3 scripts/release_skills.py plan --all   # ... and patch-release every skill, changed or not
                                                   # (in CI: `[release-all]` in the HEAD commit message)

Bump: breaking (`!`/BREAKING CHANGE) → major, `feat` → minor, else releasing
(`fix`/`perf`/`refactor`/`revert`) → patch. A skill with no releasing commit
since its last tag is skipped; a skill with no tag yet gets an initial
`<skill>-v<current plugin.json version>` baseline.

Idempotent by *reading before writing*: each skill is based off its own last
tag; `chore(release)`/`[skip ci]` commits are ignored; the package registry and
the release list are queried first, so a run that has nothing to do performs no
writes at all. Nothing swallows a 409 — every remote write is one the state
query said was needed, so a conflict is a real anomaly and fails the run.
Remote calls retry TRANSIENT failures (network-layer errors, 5xx) a few times,
re-reading the gated state between attempts — a timed-out write may have landed,
and blindly resending it would manufacture that very 409. 4xx never retries.
Stdlib only. Forgejo API + push auth come from the CI env (GITHUB_SERVER_URL,
GITHUB_REPOSITORY, GITEA_TOKEN; push creds from the token-authenticated
checkout).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import build_dist
import sync_marketplace

ROOT = Path(__file__).resolve().parent.parent
TYPE_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s*(?P<desc>.+)")
BREAKING_RE = re.compile(r"^BREAKING(?: CHANGES?)?:", re.M)
SEMVER_TAG_RE = re.compile(r"-v(\d+)\.(\d+)\.(\d+)$")
LEVELS = ("patch", "minor", "major")
RELEASING = {"feat", "fix", "perf", "refactor", "revert"}
SECTIONS = [
    ("feat", "### 🚀 Features"),
    ("fix", "### 🐛 Bug Fixes"),
    ("perf", "### ⚡ Performance"),
    ("refactor", "### ♻️ Refactoring"),
    ("revert", "### ⏪ Reverts"),
]


def git(*args, ok=(0,)):
    p = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if p.returncode not in ok:
        sys.exit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def skills():
    return sorted(d.name for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").exists())


def is_ancestor(tag):
    """Is `tag` on HEAD's history? Tags left behind by a history rewrite (this
    repo has several, from before the re-init) still resolve, but `<tag>..HEAD`
    against unrelated history yields *every* commit — which would compute a bump
    from a version the tree never had. Only tags we can actually diff against
    count as a baseline."""
    p = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", tag, "HEAD"],
                       capture_output=True, text=True)
    return p.returncode == 0


def last_tag(skill):
    best, best_key = None, (-1, -1, -1)
    for tag in git("tag", "--list", f"{skill}-v*").split():
        m = SEMVER_TAG_RE.search(tag)
        if m and is_ancestor(tag):
            key = tuple(int(x) for x in m.groups())
            if key > best_key:
                best, best_key = tag, key
    return best


def commits_touching(skill, base):
    rng = f"{base}..HEAD" if base else "HEAD"
    out = git("log", "--no-merges", "--format=%H", rng, "--", f"skills/{skill}/")
    result = []
    for sha in out.split():
        subject = git("log", "-1", "--format=%s", sha).strip()
        if subject.startswith("chore(release):") or "[skip ci]" in subject:
            continue
        body = git("log", "-1", "--format=%b", sha)
        result.append((sha[:8], subject, body))
    return result


def level_of(subject, body):
    m = TYPE_RE.match(subject)
    if (m and m.group("bang")) or BREAKING_RE.search(body):
        return "major"
    if m and m.group("type") == "feat":
        return "minor"
    return "patch"


def bumped(version, level):
    major, minor, patch = (int(x) for x in version.split("."))
    return {"major": f"{major + 1}.0.0", "minor": f"{major}.{minor + 1}.0"}.get(
        level, f"{major}.{minor}.{patch + 1}"
    )


def plugin_version(skill):
    return json.loads((ROOT / "skills" / skill / ".claude-plugin" / "plugin.json").read_text())["version"]


def bump_bundle(level):
    """Move the bundle plugin's version whenever any skill releases.

    The bundle carries a repo-wide version, not a per-skill one, and consumers
    only pull an update when the catalog version moves — so a release that left
    it untouched would never reach anyone installed on the bundle. It is
    versioned but deliberately never tagged: <skill>-v<X.Y.Z> stays the only
    release tag and the only unit of pinning.
    """
    pj = ROOT / ".claude-plugin" / "plugin.json"
    data = json.loads(pj.read_text())
    old = data["version"]
    data["version"] = bumped(old, level)
    pj.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"  bundle {data['name']}: {old} -> {data['version']} ({level})", file=sys.stderr)


def force_all_requested():
    """Should this run patch-release EVERY skill, changed or not?

    True when `--all` is passed, or when the commit at HEAD carries the
    `[release-all]` token anywhere in its message — the same self-limiting shape
    as `[skip ci]`. The token form is what CI uses: it lives in one commit, so
    the escape hatch expires the moment that commit is no longer HEAD. Wiring
    `--all` into release.yml instead would re-release the whole estate on every
    subsequent push to main, which is never what anyone means.

    Forgejo's merge and squash strategies both carry the PR title into the
    resulting commit message, so `[release-all]` in the PR title reaches HEAD;
    put it in the branch commit too and a rebase merge is covered as well."""
    if "--all" in sys.argv:
        return True
    return "[release-all]" in git("log", "-1", "--format=%B", "HEAD")


def plan(force_all=False):
    out = []
    for skill in skills():
        base = last_tag(skill)
        if base is None:
            out.append({"skill": skill, "base": None, "old": None, "new": plugin_version(skill),
                        "level": "initial", "initial": True, "forced": False, "commits": []})
            continue
        commits = commits_touching(skill, base)
        releasing = [c for c in commits if TYPE_RE.match(c[1]) and (
            level_of(c[1], c[2]) != "patch" or TYPE_RE.match(c[1]).group("type") in RELEASING)]
        if not releasing and not force_all:
            continue
        level = (max((level_of(s, b) for _, s, b in releasing), key=LEVELS.index)
                 if releasing else "patch")
        old = plugin_version(skill)
        out.append({"skill": skill, "base": base, "old": old, "new": bumped(old, level),
                    "level": level, "initial": False, "forced": not releasing,
                    "commits": releasing})
    return out


def changelog_section(new, commits, initial, forced=False):
    date = git("show", "-s", "--format=%cs", "HEAD").strip()
    lines = [f"## {new} ({date})", ""]
    if initial:
        return "\n".join(lines + ["Initial release.", ""])
    if forced and not commits:
        return "\n".join(lines + [
            "Maintenance release — estate-wide re-cut; no changes to this skill.", ""])
    grouped = {t: [] for t, _ in SECTIONS}
    for sha, subject, _ in commits:
        m = TYPE_RE.match(subject)
        t = m.group("type") if m else ""
        if t in grouped:
            scope, desc = m.group("scope"), m.group("desc")
            grouped[t].append(f"- **{scope}:** {desc} ({sha})" if scope else f"- {desc} ({sha})")
    for t, heading in SECTIONS:
        if grouped[t]:
            lines += [heading, ""] + grouped[t] + [""]
    return "\n".join(lines)


def write_changelog(skill, section):
    path = ROOT / "skills" / skill / "CHANGELOG.md"
    title = f"# {skill}\n"
    if path.exists():
        body = path.read_text()
        rest = body[len(title):].lstrip("\n") if body.startswith(title) else body
        path.write_text(f"{title}\n{section}\n\n{rest}".rstrip() + "\n")
    else:
        path.write_text(f"{title}\n{section}".rstrip() + "\n")


def _api():
    """(server, owner, repo, token) from the Forgejo Actions env, or None.

    Token comes from GITEA_TOKEN (set explicitly to the org bot token in
    release.yml) — NOT FORGEJO_TOKEN, which Forgejo auto-injects as the per-job
    token that the package registry rejects with 401 reqPackageAccess.
    """
    server = (os.environ.get("GITEA_URL") or os.environ.get("GITHUB_SERVER_URL") or "").rstrip("/")
    repo_path = os.environ.get("GITHUB_REPOSITORY") or ""
    token = os.environ.get("GITEA_TOKEN") or os.environ.get("WEBGRIP_CI_TOKEN")
    if not (server and "/" in repo_path and token):
        return None
    owner, repo = repo_path.split("/", 1)
    return server, owner, repo, token


def changelog_top(skill):
    """The newest '## …' section of skills/<skill>/CHANGELOG.md (release notes)."""
    path = ROOT / "skills" / skill / "CHANGELOG.md"
    if not path.exists():
        return f"{skill} release."
    out, seen = [], False
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            if seen:
                break
            seen = True
        if seen:
            out.append(line)
    return "\n".join(out).strip() or f"{skill} release."


TRANSIENT_TRIES = 3


def _remote_write(what, send, landed):
    """One remote write, retried on TRANSIENT failures only (network-layer
    errors, 5xx). Added after two consecutive runs (2026-08-27/28) died on a
    single un-retried POST through the tunnel.

    send() performs the raw HTTP call. landed() re-reads the server state the
    write was gated on and returns True once the write's effect is present —
    checked between attempts because a timed-out request may have landed
    anyway, and blindly resending it would manufacture the exact 409 this
    script treats as a concurrent writer. 4xx (409 included) is re-raised
    untouched for the caller to classify — never retried."""
    for attempt in range(1, TRANSIENT_TRIES + 1):
        try:
            send()
            return
        except urllib.error.HTTPError as e:
            if e.code < 500:
                raise
            err = f"{e.code} {e.read().decode()[:200]}"
        except (TimeoutError, urllib.error.URLError, OSError) as e:
            err = repr(e)
        if landed():
            print(f"  {what}: request errored ({err}) but the write landed — continuing",
                  file=sys.stderr)
            return
        if attempt == TRANSIENT_TRIES:
            sys.exit(f"{what} failed after {TRANSIENT_TRIES} attempts: {err}")
        wait = 3 * attempt
        print(f"  {what}: transient failure ({err}) — retrying in {wait}s "
              f"({attempt + 1}/{TRANSIENT_TRIES})", file=sys.stderr)
        time.sleep(wait)


def _get_json(url, token, timeout=30):
    """GET → parsed JSON, or None if the resource does not exist (404).

    The 'does it already exist?' primitive every remote write below is gated on:
    we never PUT/POST blind and recover from the conflict, because the registry's
    conflict recovery (delete + rewrite) is destructive. Reads are idempotent,
    so transient failures (network, 5xx) simply retry."""
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})
    for attempt in range(1, TRANSIENT_TRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code < 500:
                sys.exit(f"GET {url} failed: {e.code} {e.read().decode()[:200]}")
            err = f"{e.code} {e.read().decode()[:200]}"
        except (TimeoutError, urllib.error.URLError, OSError) as e:
            err = repr(e)
        if attempt == TRANSIENT_TRIES:
            sys.exit(f"GET {url} failed after {TRANSIENT_TRIES} attempts: {err}")
        time.sleep(3 * attempt)


def _put_skill(url, data, token, what, landed):
    """PUT the blob. Content-Type MUST be explicit: urllib otherwise defaults a
    body to application/x-www-form-urlencoded, and Forgejo's generic registry
    500s trying to parse the zip as a form.

    A 409 here is fatal by design. The caller only PUTs after the registry said
    the version was absent (or after deleting it), so a conflict means something
    else wrote it in between — and blindly clearing the way for our own upload
    is exactly how a healthy artifact gets destroyed. `landed` tells the retry
    path whether OUR bytes are already there (see _remote_write)."""
    def send():
        req = urllib.request.Request(url, data=data, method="PUT",
                                     headers={"Authorization": f"token {token}",
                                              "Content-Type": "application/octet-stream"})
        urllib.request.urlopen(req, timeout=60)
    try:
        _remote_write(what, send, landed)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:200]
        if e.code == 409:
            sys.exit(f"{what}: 409 although the version was absent a moment ago — concurrent "
                     f"write to {url}. Refusing to overwrite it; re-run once the other run "
                     f"has finished.")
        sys.exit(f"{what} failed: {e.code} {detail}")


def published_sha256(skill, version):
    """sha256 of the published <skill>.skill, or None if that version has no
    such file (absent version, or a phantom left by a partial earlier run)."""
    server, owner, _repo, token = _api()
    files = _get_json(f"{server}/api/v1/packages/{owner}/generic/{skill}/{version}/files", token)
    for f in files or []:
        if f.get("name") == f"{skill}.skill":
            return f.get("sha256")
    return None


def publish_artifact(skill, version):
    """Ensure the generic package registry holds this skill's zip at `version`.

    Returns "verified" (already correct — no write), "published" (uploaded), or
    "repaired" (the version existed but its blob was missing or differed).

    The zips are deterministic, so the published sha256 is directly comparable
    to a local rebuild: an unchanged skill verifies and we touch nothing. Only a
    genuine mismatch takes the destructive path (DELETE the version, re-PUT) —
    that path exists for phantoms left by a partial run (401 token / 500
    Content-Type), and must never run against a healthy artifact."""
    server, owner, _repo, token = _api()
    build_dist.DIST.mkdir(exist_ok=True)
    data = build_dist.build(ROOT / "skills" / skill, quiet=True).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    base = f"{server}/api/packages/{owner}/generic/{skill}/{version}"
    url = f"{base}/{skill}.skill"

    have = published_sha256(skill, version)
    ours_landed = lambda: published_sha256(skill, version) == digest
    if have == digest:
        return "verified"
    if have is None and _get_json(f"{server}/api/v1/packages/{owner}/generic/{skill}/{version}",
                                  token) is None:
        _put_skill(url, data, token, f"package publish {skill}@{version}", ours_landed)
        print(f"  published {skill}.skill @ {version}", file=sys.stderr)
        return "published"

    reason = "no .skill blob (phantom version)" if have is None else f"sha256 {have[:12]}… != {digest[:12]}…"
    print(f"  WARNING: {skill}@{version} is published but wrong — {reason}; "
          f"deleting the version and re-publishing", file=sys.stderr)
    delreq = urllib.request.Request(base, method="DELETE",
                                    headers={"Authorization": f"token {token}"})
    try:
        urllib.request.urlopen(delreq, timeout=30)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            sys.exit(f"delete {skill}@{version} failed: {e.code} {e.read().decode()[:200]} "
                     f"— refusing to leave a wrong artifact published")
    _put_skill(url, data, token, f"package re-publish {skill}@{version}", ours_landed)
    print(f"  re-published {skill}.skill @ {version}", file=sys.stderr)
    return "repaired"


def link_package(skill, version):
    """Link the generic package to the repo it was built in, if it isn't already.

    Forgejo packages are owner-scoped; a package with no repository link shows
    only under the owner's Packages, never on the repo's Packages tab. Packages
    pushed by an Actions job normally get linked automatically, so this is a
    backfill for the ones that didn't — and POSTing an already-linked package
    just returns 400, which is why we check first instead of logging that 400
    on every run. The endpoint links the package (all versions), not a version.

    Best-effort: linking is cosmetic and must never fail a release."""
    server, owner, repo, token = _api()
    meta = _get_json(f"{server}/api/v1/packages/{owner}/generic/{skill}/{version}", token)
    if (meta or {}).get("repository", {}).get("full_name") == f"{owner}/{repo}":
        return False
    url = f"{server}/api/v1/packages/{owner}/generic/{skill}/-/link/{repo}"
    req = urllib.request.Request(url, method="POST",
                                 headers={"Authorization": f"token {token}"})
    try:
        urllib.request.urlopen(req, timeout=30)
        print(f"  linked package {skill} -> {owner}/{repo}", file=sys.stderr)
        return True
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        detail = e.code if isinstance(e, urllib.error.HTTPError) else e.reason
        print(f"  (link {skill} -> {repo} returned {detail} — non-fatal)", file=sys.stderr)
        return False


def ensure_release(tag, notes):
    """Create the Forgejo release for an existing tag, if it has none (notes
    only; the .skill lives in the package registry). Returns True if created.

    Existence is checked by GET, not by POSTing and catching the 409 — so a
    conflict here means a concurrent run created it between the two calls, and
    that is worth failing on rather than papering over."""
    server, owner, repo, token = _api()
    exists_url = f"{server}/api/v1/repos/{owner}/{repo}/releases/tags/{tag}"
    if _get_json(exists_url, token) is not None:
        return False
    data = json.dumps({"tag_name": tag, "name": tag, "body": notes}).encode()

    def send():
        req = urllib.request.Request(
            f"{server}/api/v1/repos/{owner}/{repo}/releases", data=data, method="POST",
            headers={"Authorization": f"token {token}", "Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=30)
    try:
        _remote_write(f"Forgejo release {tag}", send,
                      landed=lambda: _get_json(exists_url, token) is not None)
        print(f"  created Forgejo release {tag}", file=sys.stderr)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 409:
            sys.exit(f"Forgejo release {tag}: 409 although it did not exist a moment ago — "
                     f"concurrent release run. Re-run once it has finished.")
        sys.exit(f"Forgejo release {tag} failed: {e.code} {e.read().decode()[:200]}")


def apply():
    # 1) Bump/commit/tag/push the skills that actually changed (may be none).
    force_all = force_all_requested()
    if force_all:
        print("[release-all]: patch-releasing EVERY skill, changed or not", file=sys.stderr)
    releases = plan(force_all)
    if releases:
        for r in releases:
            pj = ROOT / "skills" / r["skill"] / ".claude-plugin" / "plugin.json"
            data = json.loads(pj.read_text())
            data["version"] = r["new"]
            pj.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            write_changelog(r["skill"], changelog_section(
                r["new"], r["commits"], r["initial"], r["forced"]))
        # strongest level across this run — a major anywhere makes it a major
        bump_bundle(max((r["level"] for r in releases if r["level"] in LEVELS),
                        key=LEVELS.index, default="patch"))
        sync_marketplace.sync()
        tags = [f"{r['skill']}-v{r['new']}" for r in releases]
        git("add", "-A")
        git("commit", "-m", f"chore(release): {', '.join(tags)} [skip ci]")
        for tag in tags:
            git("tag", tag)
        print("prepared: " + ", ".join(tags))
        if _api():
            branch = os.environ.get("GITHUB_REF_NAME", "main")
            git("push", "origin", f"HEAD:{branch}")
            git("push", "origin", "--tags")
    else:
        print("no version bumps this run")

    # 2) Ensure EVERY skill's current version is published + has a release
    #    object. Idempotent (skips what already exists) and self-healing: it
    #    backfills a version whose earlier run tagged it but failed mid-publish,
    #    so a plain re-run recovers a partial release instead of skipping it.
    #    Every step reads before it writes, so a run with nothing to do makes no
    #    remote changes at all.
    if not _api():
        print("no CI API env — skipping package publish / releases")
        return
    tally = {"verified": 0, "published": 0, "repaired": 0}
    linked = created = 0
    for skill in skills():
        version = plugin_version(skill)
        tag = f"{skill}-v{version}"
        if tag not in git("tag", "--list", tag).split():
            continue  # not yet tagged (never released) — nothing to publish
        tally[publish_artifact(skill, version)] += 1
        linked += link_package(skill, version)
        created += ensure_release(tag, changelog_top(skill))
    print(f"packages: {tally['verified']} verified, {tally['published']} published, "
          f"{tally['repaired']} repaired; releases: {created} created; links: {linked} added")
    if tally["repaired"]:
        print(f"NOTE: {tally['repaired']} package(s) had to be repaired — see the WARNING lines "
              f"above; a published artifact had drifted from the tree at that version.")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "plan":
        releases = plan(force_all_requested())
        if not releases:
            print("no skills to release")
            return
        for r in releases:
            base = r["base"] or "(no prior tag)"
            arrow = f"{r['old']} → {r['new']}" if r["old"] else f"{r['new']} (initial)"
            why = "forced, no changes" if r["forced"] else f"{len(r['commits'])} releasing commit(s)"
            print(f"{r['skill']}: {arrow}  [{r['level']}]  since {base}  ({why})")
    elif mode == "apply":
        apply()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
