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

Bump: breaking (`!`/BREAKING CHANGE) → major, `feat` → minor, else releasing
(`fix`/`perf`/`refactor`/`revert`) → patch. A skill with no releasing commit
since its last tag is skipped; a skill with no tag yet gets an initial
`<skill>-v<current plugin.json version>` baseline.

Idempotent: each skill is based off its own last tag; `chore(release)`/`[skip ci]`
commits are ignored; a 409 from the package registry / existing release is
tolerated. Stdlib only. Forgejo API + push auth come from the CI env
(GITHUB_SERVER_URL, GITHUB_REPOSITORY, FORGEJO_TOKEN; push creds from the
token-authenticated checkout).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
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


def last_tag(skill):
    best, best_key = None, (-1, -1, -1)
    for tag in git("tag", "--list", f"{skill}-v*").split():
        m = SEMVER_TAG_RE.search(tag)
        if m:
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


def plan():
    out = []
    for skill in skills():
        base = last_tag(skill)
        if base is None:
            out.append({"skill": skill, "base": None, "old": None, "new": plugin_version(skill),
                        "level": "initial", "initial": True, "commits": []})
            continue
        commits = commits_touching(skill, base)
        releasing = [c for c in commits if TYPE_RE.match(c[1]) and (
            level_of(c[1], c[2]) != "patch" or TYPE_RE.match(c[1]).group("type") in RELEASING)]
        if not releasing:
            continue
        level = max((level_of(s, b) for _, s, b in releasing), key=LEVELS.index)
        old = plugin_version(skill)
        out.append({"skill": skill, "base": base, "old": old, "new": bumped(old, level),
                    "level": level, "initial": False, "commits": releasing})
    return out


def changelog_section(new, commits, initial):
    date = git("show", "-s", "--format=%cs", "HEAD").strip()
    lines = [f"## {new} ({date})", ""]
    if initial:
        return "\n".join(lines + ["Initial release.", ""])
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


def _put_skill(url, data, token):
    """PUT the blob. Returns True on 201/created, raises HTTPError otherwise.
    Content-Type MUST be explicit: urllib otherwise defaults a body to
    application/x-www-form-urlencoded, and Forgejo's generic registry 500s
    trying to parse the zip as a form."""
    req = urllib.request.Request(url, data=data, method="PUT",
                                 headers={"Authorization": f"token {token}",
                                          "Content-Type": "application/octet-stream"})
    urllib.request.urlopen(req, timeout=60)
    return True


def publish_artifact(skill, version):
    """Build the skill's .skill zip and PUT it to the generic package registry.

    Forgejo's generic registry is immutable: re-PUTting an existing version
    returns 409 even when that version holds no usable blob (an earlier partial
    run — 401 token / 500 Content-Type — can leave such a phantom). So on 409 we
    DELETE the version and re-PUT once. That makes a plain re-run self-heal a
    phantom instead of forever logging 'already published' over empty Packages."""
    api = _api()
    if not api:
        print(f"  (skip artifact for {skill} — no CI API env)", file=sys.stderr)
        return
    server, owner, _repo, token = api
    build_dist.DIST.mkdir(exist_ok=True)
    build_dist.build(ROOT / "skills" / skill)
    data = (build_dist.DIST / f"{skill}.skill").read_bytes()
    base = f"{server}/api/packages/{owner}/generic/{skill}/{version}"
    url = f"{base}/{skill}.skill"
    try:
        _put_skill(url, data, token)
        print(f"  published {skill}.skill @ {version}", file=sys.stderr)
        return
    except urllib.error.HTTPError as e:
        if e.code != 409:
            sys.exit(f"package publish {skill}@{version} failed: {e.code} {e.read().decode()[:200]}")
    # 409: a phantom/existing version — delete it and re-PUT once.
    print(f"  {skill}.skill @ {version} exists (409) — deleting phantom and re-publishing", file=sys.stderr)
    delreq = urllib.request.Request(base, method="DELETE",
                                    headers={"Authorization": f"token {token}"})
    try:
        urllib.request.urlopen(delreq, timeout=30)
    except urllib.error.HTTPError as e:
        if e.code not in (204, 404):
            print(f"  (delete {skill}@{version} returned {e.code} — attempting re-PUT anyway)", file=sys.stderr)
    try:
        _put_skill(url, data, token)
        print(f"  re-published {skill}.skill @ {version}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print(f"  {skill}.skill @ {version} still 409 after delete — treating as present", file=sys.stderr)
        else:
            sys.exit(f"package re-publish {skill}@{version} failed: {e.code} {e.read().decode()[:200]}")


def link_package(skill):
    """Link the generic package to the repo it was built in.

    Forgejo packages are owner-scoped and NOT auto-linked to a repository, so a
    freshly published .skill shows only under the owner's Packages, never on the
    repo's Packages tab. This POSTs the link so it surfaces on the repo. The
    endpoint links the package (all versions), not a single version.

    Best-effort: an already-linked package or any transient error is logged, not
    fatal — linking is cosmetic and must never fail a release."""
    api = _api()
    if not api:
        return
    server, owner, repo, token = api
    url = f"{server}/api/v1/packages/{owner}/generic/{skill}/-/link/{repo}"
    req = urllib.request.Request(url, method="POST",
                                 headers={"Authorization": f"token {token}"})
    try:
        urllib.request.urlopen(req, timeout=30)
        print(f"  linked package {skill} -> {owner}/{repo}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        # already linked / unsupported build: cosmetic — log and move on.
        print(f"  (link {skill} -> {repo} returned {e.code} — non-fatal)", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"  (link {skill} -> {repo} failed: {e.reason} — non-fatal)", file=sys.stderr)


def ensure_release(tag, notes):
    """Create the Forgejo release for an existing tag (notes-only; the .skill
    lives in the package registry). 409/already-exists is tolerated."""
    api = _api()
    if not api:
        print(f"  (skip Forgejo release {tag} — no CI API env)", file=sys.stderr)
        return
    server, owner, repo, token = api
    data = json.dumps({"tag_name": tag, "name": tag, "body": notes}).encode()
    req = urllib.request.Request(
        f"{server}/api/v1/repos/{owner}/{repo}/releases", data=data, method="POST",
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=30)
        print(f"  created Forgejo release {tag}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print(f"  Forgejo release {tag} already exists", file=sys.stderr)
        else:
            sys.exit(f"Forgejo release {tag} failed: {e.code} {e.read().decode()[:200]}")


def apply():
    # 1) Bump/commit/tag/push the skills that actually changed (may be none).
    releases = plan()
    if releases:
        for r in releases:
            pj = ROOT / "skills" / r["skill"] / ".claude-plugin" / "plugin.json"
            data = json.loads(pj.read_text())
            data["version"] = r["new"]
            pj.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            write_changelog(r["skill"], changelog_section(r["new"], r["commits"], r["initial"]))
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
    if not _api():
        print("no CI API env — skipping package publish / releases")
        return
    for skill in skills():
        version = plugin_version(skill)
        tag = f"{skill}-v{version}"
        if tag not in git("tag", "--list", tag).split():
            continue  # not yet tagged (never released) — nothing to publish
        publish_artifact(skill, version)
        link_package(skill)
        ensure_release(tag, changelog_top(skill))
    print("publish + releases ensured")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "plan":
        releases = plan()
        if not releases:
            print("no skills to release")
            return
        for r in releases:
            base = r["base"] or "(no prior tag)"
            arrow = f"{r['old']} → {r['new']}" if r["old"] else f"{r['new']} (initial)"
            print(f"{r['skill']}: {arrow}  [{r['level']}]  since {base}  "
                  f"({len(r['commits'])} releasing commit(s))")
    elif mode == "apply":
        apply()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
