#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2
GIT_BINARY_SNIFF_BYTES = 8000
DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
BLOB_BATCH_SIZE = 500
EXCERPT_WIDTH = 160
SKIPPED_LISTED = 5
CONFIG_KEY = "org-boundaries.exclude"
ALLOW_PREFIX = "allow:"
ORG_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
IDENT_LINE = re.compile(r"^(.*) <(.*)> \d+ [+-]\d{4}$")
HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
KNOWN_TOKEN = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|glpat-[A-Za-z0-9_-]{20,}"
    r"|xox[abposr]-[A-Za-z0-9-]{10,}"
    r"|sk-[A-Za-z0-9_-]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|AIza[0-9A-Za-z_-]{35}"
    r"|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
)
TOKEN_CANDIDATE = re.compile(r"[A-Za-z0-9+/=_-]{20,}")
RANDOM_TOKEN_MIN_BITS_PER_CHAR = 3.0
TOKEN_VISIBLE_PREFIX = 4
SURFACE_ORDER = ("content", "path", "identity", "message", "ref")


class UsageError(Exception):
    pass


@dataclass(frozen=True)
class Rule:
    label: str
    regex: re.Pattern


@dataclass(frozen=True)
class Rules:
    deny: tuple
    allow: tuple
    prefilter: re.Pattern | None


@dataclass(frozen=True)
class Finding:
    surface: str
    location: str
    label: str
    excerpt: str


@dataclass
class ScanStats:
    skipped_large: list


def run_git(repo: str, args: Sequence[str], stdin: bytes | None = None, ok_codes: Iterable[int] = (0,)) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", repo, *args],
            input=stdin,
            capture_output=True,
        )
    except FileNotFoundError as missing:
        raise UsageError("git is not installed or not on PATH") from missing
    if completed.returncode not in tuple(ok_codes):
        message = completed.stderr.decode(errors="replace").strip()
        raise UsageError(f"git {' '.join(args)} failed: {message}")
    return completed.stdout


def git_text(repo: str, args: Sequence[str], ok_codes: Iterable[int] = (0,)) -> str:
    return os.fsdecode(run_git(repo, args, ok_codes=ok_codes))


def split_nul(raw: bytes) -> list:
    return [os.fsdecode(part) for part in raw.split(b"\0") if part]


def repository_root(repo: str) -> Path:
    if not Path(repo).is_dir():
        raise UsageError(f"{repo} is not a directory")
    return Path(git_text(repo, ["rev-parse", "--show-toplevel"]).strip()).resolve()


def config_directory() -> Path:
    explicit = os.environ.get("ORG_BOUNDARIES_DIR")
    if explicit:
        return Path(explicit).expanduser()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "org-boundaries"


def configured_orgs(repo: str) -> list:
    return git_text(repo, ["config", "--get-all", CONFIG_KEY], ok_codes=(0, 1)).split()


def pattern_files(repo: str, orgs: list, explicit_files: list) -> list:
    names = orgs or ([] if explicit_files else configured_orgs(repo))
    if not names and not explicit_files:
        raise UsageError(
            f"no boundary configured: pass --org NAME or --patterns FILE, or set git config {CONFIG_KEY} NAME"
        )
    for name in names:
        if not ORG_NAME.fullmatch(name):
            raise UsageError(f"organisation name {name!r} may only hold letters, digits, dot, dash and underscore")
    return [Path(path).expanduser() for path in explicit_files] + [config_directory() / f"{name}.txt" for name in names]


def ensure_outside_repository(files: list, root: Path) -> None:
    for path in files:
        resolved = path.resolve()
        if resolved == root or root in resolved.parents:
            raise UsageError(
                f"patterns file {path} is inside the repository; keep it outside "
                f"(default {config_directory()}) so the guard does not name the organisation"
            )


def parse_rule(source: str, label: str) -> re.Pattern:
    try:
        return re.compile(source, re.IGNORECASE)
    except re.error as invalid:
        raise UsageError(f"rule {label}: invalid regular expression {invalid}") from invalid


def load_rules(files: list) -> Rules:
    deny = []
    allow = []
    for file_number, path in enumerate(files, start=1):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError as missing:
            raise UsageError(f"patterns file {path} not found") from missing
        except OSError as unreadable:
            raise UsageError(f"patterns file {path} unreadable: {unreadable}") from unreadable
        for line_number, line in enumerate(lines, start=1):
            source = line.strip()
            if not source or source.startswith("#"):
                continue
            label = f"{file_number}:{line_number}"
            if source.startswith(ALLOW_PREFIX):
                allow.append(parse_rule(source[len(ALLOW_PREFIX):].strip(), label))
            else:
                deny.append(Rule(label, parse_rule(source, label)))
    if not deny:
        raise UsageError("the patterns files hold no rules; an empty scan proves nothing")
    return Rules(tuple(deny), tuple(allow), combined_prefilter(deny))


def combined_prefilter(deny: list) -> re.Pattern | None:
    try:
        return re.compile("|".join(f"(?:{rule.regex.pattern})" for rule in deny), re.IGNORECASE)
    except re.error:
        return None


def mentions_any(rules: Rules, text: str) -> bool:
    if rules.prefilter is not None:
        return rules.prefilter.search(text) is not None
    return any(rule.regex.search(text) for rule in rules.deny)


def allowed_spans(rules: Rules, text: str) -> list:
    return [match.span() for allow in rules.allow for match in allow.finditer(text)]


def first_reportable_match(rule: Rule, text: str, allowed: list) -> re.Match | None:
    for match in rule.regex.finditer(text):
        if match.end() == match.start():
            continue
        if not any(start <= match.start() and match.end() <= end for start, end in allowed):
            return match
    return None


def bits_per_char(text: str) -> float:
    counts = Counter(text)
    return -sum(count / len(text) * math.log2(count / len(text)) for count in counts.values())


def looks_random(candidate: str) -> bool:
    has_classes = (
        any(c.isupper() for c in candidate)
        and any(c.islower() for c in candidate)
        and any(c.isdigit() for c in candidate)
    )
    return has_classes and bits_per_char(candidate) >= RANDOM_TOKEN_MIN_BITS_PER_CHAR


def masked(token: str) -> str:
    return f"{token[:TOKEN_VISIBLE_PREFIX]}…[{len(token)} chars masked]"


def mask_tokens(text: str) -> str:
    without_known = KNOWN_TOKEN.sub(lambda match: masked(match.group(0)), text)
    return TOKEN_CANDIDATE.sub(
        lambda match: masked(match.group(0)) if looks_random(match.group(0)) else match.group(0),
        without_known,
    )


def excerpt_around(rules: Rules, rule: Rule, line: str, match: re.Match) -> str:
    safe = mask_tokens(line.replace("\t", " "))
    rematch = first_reportable_match(rule, safe, allowed_spans(rules, safe))
    centre = rematch.start() if rematch else min(match.start(), len(safe))
    start = max(0, centre - EXCERPT_WIDTH // 3)
    window = safe[start:start + EXCERPT_WIDTH].strip()
    prefix = "…" if start > 0 else ""
    suffix = "…" if start + EXCERPT_WIDTH < len(safe) else ""
    return f"{prefix}{window}{suffix}"


def findings_in_line(rules: Rules, surface: str, location: str, line: str) -> Iterator[Finding]:
    if not mentions_any(rules, line):
        return
    allowed = allowed_spans(rules, line)
    for rule in rules.deny:
        match = first_reportable_match(rule, line, allowed)
        if match is not None:
            yield Finding(surface, location, f"rule {rule.label}", excerpt_around(rules, rule, line, match))


def is_binary(data: bytes) -> bool:
    return b"\0" in data[:GIT_BINARY_SNIFF_BYTES]


def findings_in_blob(rules: Rules, location: str, data: bytes) -> Iterator[Finding]:
    if is_binary(data):
        text = data.decode("latin-1")
        if not mentions_any(rules, text):
            return
        allowed = allowed_spans(rules, text)
        for rule in rules.deny:
            if first_reportable_match(rule, text, allowed) is not None:
                yield Finding("content", f"{location} (binary)", f"rule {rule.label}", "")
        return
    text = data.decode("utf-8", errors="replace")
    if not mentions_any(rules, text):
        return
    for line_number, line in enumerate(text.splitlines(), start=1):
        yield from findings_in_line(rules, "content", f"{location}:{line_number}", line)


def findings_in_paths(rules: Rules, paths: Iterable[str], prefix: str = "") -> Iterator[Finding]:
    for path in paths:
        yield from findings_in_line(rules, "path", f"{prefix}{path}", path)


def read_worktree_file(path: Path, display: str, max_bytes: int, stats: ScanStats) -> bytes | None:
    if path.is_symlink():
        return os.fsencode(os.readlink(path))
    if not path.is_file():
        return None
    if path.stat().st_size > max_bytes:
        stats.skipped_large.append(display)
        return None
    try:
        return path.read_bytes()
    except OSError:
        stats.skipped_large.append(f"{display} (unreadable)")
        return None


def scan_worktree_files(rules: Rules, root: Path, paths: list, max_bytes: int, stats: ScanStats) -> Iterator[Finding]:
    for display in paths:
        data = read_worktree_file(root / display, display, max_bytes, stats)
        if data is not None:
            yield from findings_in_blob(rules, display, data)


def blob_sizes(repo: str, shas: list) -> dict:
    raw = run_git(repo, ["cat-file", "--batch-check"], stdin="\n".join(shas).encode() + b"\n")
    sizes = {}
    for line in raw.decode().splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == "blob":
            sizes[parts[0]] = int(parts[2])
    return sizes


def read_blobs(repo: str, shas: list) -> Iterator[tuple]:
    for start in range(0, len(shas), BLOB_BATCH_SIZE):
        chunk = shas[start:start + BLOB_BATCH_SIZE]
        raw = run_git(repo, ["cat-file", "--batch"], stdin="\n".join(chunk).encode() + b"\n")
        offset = 0
        while offset < len(raw):
            header_end = raw.index(b"\n", offset)
            header = raw[offset:header_end].decode().split()
            offset = header_end + 1
            if len(header) != 3:
                continue
            size = int(header[2])
            yield header[0], header[1], raw[offset:offset + size]
            offset += size + 1


def scan_blobs(rules: Rules, repo: str, locations: dict, max_bytes: int, stats: ScanStats) -> Iterator[Finding]:
    if not locations:
        return
    sizes = blob_sizes(repo, list(locations))
    readable = []
    for sha, size in sizes.items():
        if size > max_bytes:
            stats.skipped_large.append(locations[sha])
        else:
            readable.append(sha)
    for sha, kind, data in read_blobs(repo, readable):
        if kind == "blob":
            yield from findings_in_blob(rules, locations[sha], data)


def tracked_paths(repo: str) -> list:
    return split_nul(run_git(repo, ["ls-files", "-z"]))


def untracked_paths(repo: str) -> list:
    return split_nul(run_git(repo, ["ls-files", "-z", "--others", "--exclude-standard"]))


def ref_names(repo: str) -> list:
    return git_text(repo, ["for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags"]).split("\n")


def index_blob_shas(repo: str) -> set:
    return {entry.split()[1] for entry in split_nul(run_git(repo, ["ls-files", "-z", "--stage"]))}


def ref_tip_blobs(repo: str) -> tuple:
    already_scanned = index_blob_shas(repo)
    locations = {}
    paths = {}
    for ref in filter(None, ref_names(repo)):
        if ref.endswith("/HEAD"):
            continue
        listing = run_git(repo, ["ls-tree", "-r", "-z", "--full-tree", ref], ok_codes=(0, 128))
        for entry in split_nul(listing):
            meta, _, path = entry.partition("\t")
            _, kind, sha = meta.split()
            paths.setdefault(f"{ref}:{path}", path)
            if kind == "blob" and sha not in already_scanned:
                locations.setdefault(sha, f"{ref}:{path}")
    return locations, paths


def scan_all_ref_paths(rules: Rules, ref_paths: dict, tracked: set) -> Iterator[Finding]:
    for location, path in ref_paths.items():
        if path not in tracked:
            yield from findings_in_line(rules, "path", location, path)


def history_revisions(since_commit: str | None, revision_range: str | None) -> list:
    if revision_range:
        return [revision_range]
    if since_commit:
        return ["--all", f"^{since_commit}"]
    return ["--all"]


def has_commits(repo: str) -> bool:
    return bool(git_text(repo, ["for-each-ref", "--count=1", "--format=%(refname)"]).strip())


def scan_identities(rules: Rules, repo: str, revisions: list) -> Iterator[Finding]:
    log = git_text(repo, ["log", "--format=%H%x1f%an%x1f%ae%x1f%cn%x1f%ce", *revisions, "--"])
    seen = {}
    for line in log.splitlines():
        sha, author_name, author_email, committer_name, committer_email = line.split("\x1f")
        for role, name, email in (("author", author_name, author_email), ("committer", committer_name, committer_email)):
            key = (role, name, email)
            latest, count = seen.get(key, (sha, 0))
            seen[key] = (latest, count + 1)
    for (role, name, email), (latest, count) in seen.items():
        plural = "commit" if count == 1 else "commits"
        location = f"{role} of {count} {plural}, latest {latest[:10]}"
        yield from findings_in_line(rules, "identity", location, f"{name} <{email}>")


def scan_messages(rules: Rules, repo: str, revisions: list) -> Iterator[Finding]:
    log = git_text(repo, ["log", "-z", "--format=%H%n%B", *revisions, "--"])
    for record in filter(None, log.split("\0")):
        sha, _, body = record.partition("\n")
        for line_number, line in enumerate(body.splitlines(), start=1):
            yield from findings_in_line(rules, "message", f"commit {sha[:10]} line {line_number}", line)


def scan_annotated_tags(rules: Rules, repo: str) -> Iterator[Finding]:
    listing = git_text(
        repo,
        ["for-each-ref", "--format=%(objecttype)%1f%(refname:short)%1f%(taggername)%1f%(taggeremail)%1f%(contents)%1e", "refs/tags"],
    )
    for record in filter(str.strip, listing.split("\x1e")):
        kind, tag, tagger_name, tagger_email, contents = record.lstrip("\n").split("\x1f", 4)
        if kind != "tag":
            continue
        yield from findings_in_line(rules, "identity", f"tagger of tag {tag}", f"{tagger_name} {tagger_email}")
        for line_number, line in enumerate(contents.splitlines(), start=1):
            yield from findings_in_line(rules, "message", f"tag {tag} line {line_number}", line)


def scan_ref_names(rules: Rules, repo: str) -> Iterator[Finding]:
    for ref in filter(None, ref_names(repo)):
        yield from findings_in_line(rules, "ref", ref, ref)


def staged_paths(repo: str, diff_filter: str) -> list:
    return split_nul(run_git(repo, ["diff", "--cached", "--name-only", "-z", "--no-renames", f"--diff-filter={diff_filter}"]))


def added_lines(diff: str) -> Iterator[tuple]:
    in_hunk = False
    line_number = 0
    for line in diff.splitlines():
        header = HUNK_HEADER.match(line)
        if header:
            in_hunk = True
            line_number = int(header.group(1))
            continue
        if not in_hunk or line.startswith("\\"):
            continue
        if line.startswith("+"):
            yield line_number, line[1:]
            line_number += 1
        elif line.startswith(" "):
            line_number += 1


def scan_staged_content(rules: Rules, repo: str, paths: list, max_bytes: int, stats: ScanStats) -> Iterator[Finding]:
    for path in paths:
        sha = git_text(repo, ["rev-parse", f":{path}"]).strip()
        size = blob_sizes(repo, [sha]).get(sha)
        if size is None:
            continue
        if size > max_bytes:
            stats.skipped_large.append(path)
            continue
        _, _, data = next(read_blobs(repo, [sha]))
        if is_binary(data):
            yield from findings_in_blob(rules, path, data)
            continue
        diff = git_text(repo, ["diff", "--cached", "-U0", "--no-color", "--no-ext-diff", "--no-renames", "--", path])
        for line_number, line in added_lines(diff):
            yield from findings_in_line(rules, "content", f"{path}:{line_number}", line)


def pending_identities(repo: str) -> Iterator[tuple]:
    for role, variable in (("author", "GIT_AUTHOR_IDENT"), ("committer", "GIT_COMMITTER_IDENT")):
        completed = subprocess.run(["git", "-C", repo, "var", variable], capture_output=True)
        match = IDENT_LINE.match(os.fsdecode(completed.stdout).strip()) if completed.returncode == 0 else None
        if match:
            yield role, f"{match.group(1)} <{match.group(2)}>"


def scan_pending_commit(rules: Rules, repo: str) -> Iterator[Finding]:
    for role, identity in pending_identities(repo):
        yield from findings_in_line(rules, "identity", f"next commit {role}", identity)
    branch = git_text(repo, ["symbolic-ref", "--short", "-q", "HEAD"], ok_codes=(0, 1)).strip()
    if branch:
        yield from findings_in_line(rules, "ref", f"refs/heads/{branch}", branch)


def comment_char(repo: str) -> str:
    configured = git_text(repo, ["config", "--get", "core.commentChar"], ok_codes=(0, 1)).strip()
    return configured if configured and configured != "auto" else "#"


def scan_message_file(rules: Rules, repo: str, message_file: str) -> Iterator[Finding]:
    marker = comment_char(repo)
    scissors = f"{marker} ------------------------ >8 ------------------------"
    try:
        lines = Path(message_file).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as unreadable:
        raise UsageError(f"message file {message_file} unreadable: {unreadable}") from unreadable
    for line_number, line in enumerate(lines, start=1):
        if line == scissors:
            return
        if not line.startswith(marker):
            yield from findings_in_line(rules, "message", f"commit message line {line_number}", line)


def full_sweep(rules: Rules, repo: str, root: Path, options: argparse.Namespace, stats: ScanStats) -> Iterator[Finding]:
    tracked = tracked_paths(repo)
    yield from scan_worktree_files(rules, root, tracked, options.max_bytes, stats)
    yield from findings_in_paths(rules, tracked)
    if options.untracked:
        untracked = untracked_paths(repo)
        yield from scan_worktree_files(rules, root, untracked, options.max_bytes, stats)
        yield from findings_in_paths(rules, untracked, prefix="untracked ")
    if not has_commits(repo):
        return
    if options.all_refs:
        locations, ref_paths = ref_tip_blobs(repo)
        yield from scan_blobs(rules, repo, locations, options.max_bytes, stats)
        yield from scan_all_ref_paths(rules, ref_paths, set(tracked))
    revisions = history_revisions(options.since_commit, options.range)
    yield from scan_identities(rules, repo, revisions)
    yield from scan_messages(rules, repo, revisions)
    yield from scan_annotated_tags(rules, repo)
    yield from scan_ref_names(rules, repo)


def staged_check(rules: Rules, repo: str, options: argparse.Namespace, stats: ScanStats) -> Iterator[Finding]:
    yield from scan_staged_content(rules, repo, staged_paths(repo, "ACMT"), options.max_bytes, stats)
    yield from findings_in_paths(rules, staged_paths(repo, "A"))
    yield from scan_pending_commit(rules, repo)


def unique(findings: Iterable[Finding]) -> list:
    return list(dict.fromkeys(findings))


def report(findings: list, rule_count: int, stats: ScanStats, silent_when_clean: bool) -> int:
    for finding in findings:
        print("\t".join((finding.surface, mask_tokens(finding.location), finding.label, finding.excerpt)))
    if stats.skipped_large:
        listed = ", ".join(stats.skipped_large[:SKIPPED_LISTED])
        more = len(stats.skipped_large) - SKIPPED_LISTED
        tail = f" and {more} more" if more > 0 else ""
        print(f"org-boundaries: not scanned (over --max-bytes or unreadable): {listed}{tail}", file=sys.stderr)
    if not findings:
        if not silent_when_clean:
            print(f"org-boundaries: clean ({rule_count} rules)", file=sys.stderr)
        return EXIT_CLEAN
    per_surface = Counter(finding.surface for finding in findings)
    breakdown = ", ".join(f"{surface} {per_surface[surface]}" for surface in SURFACE_ORDER if per_surface[surface])
    print(f"org-boundaries: {len(findings)} findings ({breakdown})", file=sys.stderr)
    return EXIT_FINDINGS


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="scan_boundary.py",
        description="Report another organisation's markers in a git repository: tracked content, paths, "
        "commit identities and messages, tags, and branch and tag names. Exit 0 clean, 1 findings, 2 usage error.",
    )
    parser.add_argument("repo", nargs="?", default=".", help="repository to scan (default: current directory)")
    parser.add_argument("--org", action="append", default=[], help="read ~/.config/org-boundaries/ORG.txt (repeatable)")
    parser.add_argument("--patterns", action="append", default=[], help="patterns file outside the repository (repeatable)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="pre-commit mode: added lines, staged paths, next commit identity, branch")
    mode.add_argument("--message-file", help="commit-msg mode: scan this commit message file only")
    parser.add_argument("--all-refs", action="store_true", help="also scan file content and paths at every branch and tag tip")
    parser.add_argument("--untracked", action="store_true", help="also scan untracked files that are not ignored")
    history = parser.add_mutually_exclusive_group()
    history.add_argument("--since-commit", help="history surfaces cover only commits not reachable from this commit")
    history.add_argument("--range", help="history surfaces cover only this revision range, e.g. origin/main..HEAD")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES, help="skip files larger than this (reported on stderr)")
    options = parser.parse_args(argv)
    hook_mode = options.staged or options.message_file
    if hook_mode and (options.all_refs or options.untracked or options.since_commit or options.range):
        parser.error("--staged and --message-file take no sweep options")
    return options


def main(argv: Sequence[str]) -> int:
    options = parse_arguments(argv)
    try:
        repo = options.repo
        root = repository_root(repo)
        files = pattern_files(repo, options.org, options.patterns)
        ensure_outside_repository(files, root)
        rules = load_rules(files)
        stats = ScanStats(skipped_large=[])
        if options.message_file:
            findings = scan_message_file(rules, repo, options.message_file)
        elif options.staged:
            findings = staged_check(rules, repo, options, stats)
        else:
            findings = full_sweep(rules, repo, root, options, stats)
        hook_mode = bool(options.staged or options.message_file)
        return report(unique(findings), len(rules.deny), stats, silent_when_clean=hook_mode)
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return EXIT_FINDINGS
    except UsageError as problem:
        print(f"org-boundaries: {problem}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
