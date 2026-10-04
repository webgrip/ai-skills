#!/usr/bin/env python3
"""Rank refactoring targets by how often changes touch them and how much an agent must read.

Usage:
    hotspots.py [--since "12 months ago"] [--path PREFIX] [--top N] [--exclude GLOB ...]
                [--ignore-message REGEX ...] [--agent-pattern REGEX] [--chars-per-token 4]
                [--coupling] [--min-revs 5] [--min-shared 5] [--json] [REPO]

For every file that exists at HEAD, counts the non-merge commits touching it in
the window (change frequency), lines added plus deleted (churn), current lines
and an estimated token size (bytes / chars-per-token; a rough proxy, so rank by
it, never bill by it). Exposure = commits x estimated tokens: what agents would
read if each change opened the whole file once. Files are ranked by exposure and
each row reports its share of all commits in the window, so the head of the
power law is visible. Commits whose message matches --ignore-message (release
bots by default) are left out. With --agent-pattern (for example
"Co-Authored-By: Claude"), each row also reports the share of its commits made
with an agent, the changes a refactoring for agents would actually serve. With
--coupling, pairs of files that change together are listed with code-maat's
degree (shared commits over the pair's mean commits), the hidden read set of a
change; files under --min-revs commits, pairs under --min-shared and commits
touching more than 30 files are ignored. Rename history is not followed: a
renamed file counts from its rename onward.
"""

import argparse
import fnmatch
import json
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

DEFAULT_EXCLUDES = ["*.lock", "*lock.json", "*.min.*", "*.map", "*.svg", "*.png", "*.jpg", "*.gif", "*.ico", "*.pdf",
                    "vendor/*", "node_modules/*", "dist/*", "build/*", "*.snap", "*.generated.*", "*_pb2.py", "CHANGELOG.md"]
COMMIT_MARKER = "@@commit@@"
DEFAULT_IGNORED_MESSAGES = [r"^chore\(release\)", r"\[skip ci\]"]
MAX_FILES_PER_COMMIT_FOR_COUPLING = 30


def git(repo, *arguments):
    return subprocess.run(["git", "-C", repo, *arguments], capture_output=True, text=True, check=True).stdout


def excluded(path, patterns):
    return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(Path(path).name, pattern) for pattern in patterns)


def matching_commits(repo, since, pattern, path_prefix):
    command = ["log", "--no-merges", f"--since={since}", "-E", f"--grep={pattern}", "--format=%H"]
    if path_prefix:
        command += ["--", path_prefix]
    return set(git(repo, *command).split())


def read_history(repo, since, path_prefix, ignored_messages):
    command = ["-c", "diff.renames=false", "log", "--no-merges", f"--since={since}", "--numstat", f"--format={COMMIT_MARKER}%H"]
    if ignored_messages:
        command += ["-E", "--invert-grep"] + [f"--grep={pattern}" for pattern in ignored_messages]
    if path_prefix:
        command += ["--", path_prefix]
    commits, current = [], None
    for line in git(repo, *command).splitlines():
        if line.startswith(COMMIT_MARKER):
            current = {"sha": line[len(COMMIT_MARKER):], "files": {}}
            commits.append(current)
            continue
        parts = line.split("\t")
        if current is None or len(parts) != 3:
            continue
        added, deleted, name = parts
        churn = (int(added) if added.isdigit() else 0) + (int(deleted) if deleted.isdigit() else 0)
        current["files"][name] = churn
    return commits


def tracked_files(repo):
    return set(git(repo, "ls-files").splitlines())


def size_of(repo, name):
    try:
        data = (Path(repo) / name).read_bytes()
    except OSError:
        return 0, 0
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0), len(data)


def rank(repo, since, path_prefix, excludes, chars_per_token, ignored_messages, agent_pattern):
    commits = read_history(repo, since, path_prefix, ignored_messages)
    agent_commits = matching_commits(repo, since, agent_pattern, path_prefix) if agent_pattern else set()
    present = tracked_files(repo)
    frequency, churn, by_agent = Counter(), Counter(), Counter()
    for commit in commits:
        for name, lines in commit["files"].items():
            if name in present and not excluded(name, excludes):
                frequency[name] += 1
                churn[name] += lines
                by_agent[name] += commit["sha"] in agent_commits
    rows = []
    for name, count in frequency.items():
        lines, size = size_of(repo, name)
        tokens = round(size / chars_per_token)
        rows.append({"file": name, "commits": count, "churn": churn[name], "lines": lines,
                     "est_tokens": tokens, "exposure": count * tokens,
                     "commit_share": round(count / len(commits), 3) if commits else 0.0,
                     "agent_share": round(by_agent[name] / count, 2) if agent_pattern else None})
    rows.sort(key=lambda row: (-row["exposure"], row["file"]))
    return commits, present, rows


def coupling(commits, present, excludes, min_shared, min_revs, frequency):
    shared = Counter()
    for commit in commits:
        files = sorted(name for name in commit["files"] if name in present and not excluded(name, excludes) and frequency[name] >= min_revs)
        if len(files) > MAX_FILES_PER_COMMIT_FOR_COUPLING:
            continue
        for pair in combinations(files, 2):
            shared[pair] += 1
    pairs = []
    for (left, right), count in shared.items():
        if count < min_shared:
            continue
        degree = count / ((frequency[left] + frequency[right]) / 2)
        pairs.append({"left": left, "right": right, "shared_commits": count, "degree": round(degree, 2)})
    pairs.sort(key=lambda pair: (-pair["shared_commits"], -pair["degree"], pair["left"]))
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--since", default="12 months ago")
    parser.add_argument("--path", default="", help="restrict to a directory or file prefix")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--exclude", action="append", default=[], help="glob to ignore; repeatable, added to the defaults")
    parser.add_argument("--chars-per-token", type=float, default=4.0)
    parser.add_argument("--ignore-message", action="append", help="regex of commit messages to leave out; repeatable; replaces the release-bot defaults")
    parser.add_argument("--agent-pattern", help="regex matching agent-made commit messages, for example 'Co-Authored-By: Claude'")
    parser.add_argument("--coupling", action="store_true")
    parser.add_argument("--min-revs", type=int, default=5)
    parser.add_argument("--min-shared", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    excludes = DEFAULT_EXCLUDES + arguments.exclude
    try:
        ignored = DEFAULT_IGNORED_MESSAGES if arguments.ignore_message is None else arguments.ignore_message
        commits, present, rows = rank(arguments.repo, arguments.since, arguments.path, excludes, arguments.chars_per_token,
                                      ignored, arguments.agent_pattern)
    except subprocess.CalledProcessError as error:
        sys.exit(f"git failed: {error.stderr.strip()}")
    frequency = Counter({row["file"]: row["commits"] for row in rows})
    pairs = coupling(commits, present, excludes, arguments.min_shared, arguments.min_revs, frequency) if arguments.coupling else []
    total_exposure = sum(row["exposure"] for row in rows) or 1
    top = rows[:arguments.top]

    if arguments.json:
        print(json.dumps({"commits": len(commits), "since": arguments.since, "files": top, "coupling": pairs[:arguments.top]}, indent=2))
        return
    covered = sum(row["exposure"] for row in top) / total_exposure
    print(f"{len(commits)} commits since {arguments.since}; top {len(top)} files carry {covered:.0%} of read exposure.\n")
    agent_column = arguments.agent_pattern is not None
    print("| # | File | Commits | Commit share |" + (" Agent share |" if agent_column else "") + " Churn | Lines | Est. tokens | Exposure |")
    print("| --- | --- | --- | --- |" + (" --- |" if agent_column else "") + " --- | --- | --- | --- |")
    for index, row in enumerate(top, 1):
        agent = f" {row['agent_share']:.0%} |" if agent_column else ""
        print(f"| {index} | {row['file']} | {row['commits']} | {row['commit_share']:.0%} |{agent} {row['churn']:,} | "
              f"{row['lines']:,} | {row['est_tokens']:,} | {row['exposure']:,} |")
    if arguments.coupling:
        print("\n| Changes with | Also changes | Shared commits | Degree |")
        print("| --- | --- | --- | --- |")
        for pair in pairs[:arguments.top]:
            print(f"| {pair['left']} | {pair['right']} | {pair['shared_commits']} | {pair['degree']:.2f} |")


if __name__ == "__main__":
    main()
