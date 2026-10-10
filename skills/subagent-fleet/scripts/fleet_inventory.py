#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SEVERITY_RANK = {"warn": 2, "note": 1}
AGENT_BRANCH_PREFIX = "worktree-"
AGENT_WORKTREE_SEGMENT = "/.claude/worktrees/"
OPERATION_MARKERS = (
    ("MERGE_HEAD", "merge"),
    ("rebase-merge", "rebase"),
    ("rebase-apply", "rebase or am"),
    ("CHERRY_PICK_HEAD", "cherry-pick"),
    ("REVERT_HEAD", "revert"),
    ("BISECT_LOG", "bisect"),
)
LSOF_TIMEOUT_SECONDS = 30


class GitError(Exception):
    pass


@dataclass
class Finding:
    severity: str
    rule: str
    where: str
    message: str


@dataclass
class Worktree:
    path: str
    head: str
    branch: Optional[str]
    is_main: bool
    locked: bool
    missing: bool
    dirty: int = 0
    operation: Optional[str] = None
    unpushed: Optional[int] = None
    processes: List[Dict[str, object]] = field(default_factory=list)


@dataclass
class Branch:
    name: str
    upstream: str
    upstream_gone: bool
    unpushed: Optional[int]
    unmerged: Optional[int]
    checked_out_at: Optional[str]
    last_commit: str


@dataclass
class RepoInventory:
    path: str
    base: Optional[str]
    stash_entries: int
    worktrees: List[Worktree]
    branches: List[Branch]
    findings: List[Finding] = field(default_factory=list)
    prune_plan: List[str] = field(default_factory=list)


def git(repo: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} in {repo}: {result.stderr.strip()}")
    return result.stdout


def git_or_none(repo: str, *args: str) -> Optional[str]:
    try:
        return git(repo, *args).strip()
    except GitError:
        return None


def parse_worktrees(porcelain: str) -> List[Worktree]:
    worktrees: List[Worktree] = []
    for block in porcelain.strip().split("\n\n"):
        fields: Dict[str, str] = {}
        for line in block.splitlines():
            key, _, value = line.partition(" ")
            fields[key] = value
        if "worktree" not in fields:
            continue
        branch = fields.get("branch", "")
        worktrees.append(Worktree(
            path=fields["worktree"],
            head=fields.get("HEAD", ""),
            branch=branch[len("refs/heads/"):] if branch.startswith("refs/heads/") else None,
            is_main=not worktrees,
            locked="locked" in fields,
            missing="prunable" in fields or not Path(fields["worktree"]).is_dir(),
        ))
    return worktrees


def resolve_base(repo: str, requested: Optional[str]) -> Optional[str]:
    if requested:
        return requested if git_or_none(repo, "rev-parse", "--verify", "-q", requested) else None
    symbolic = git_or_none(repo, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD")
    if symbolic:
        return symbolic
    for candidate in ("origin/main", "origin/master"):
        if git_or_none(repo, "rev-parse", "--verify", "-q", candidate):
            return candidate
    return None


def operation_in_progress(worktree_path: str) -> Optional[str]:
    for marker, name in OPERATION_MARKERS:
        relative = git_or_none(worktree_path, "rev-parse", "--git-path", marker)
        if relative and (Path(worktree_path) / relative).exists():
            return name
    return None


def count_dirty(worktree_path: str) -> int:
    return len([line for line in git(worktree_path, "status", "--porcelain").splitlines() if line.strip()])


def count_unpushed(repo: str, revision: str, has_remotes: bool) -> Optional[int]:
    if not has_remotes:
        return None
    return int(git(repo, "rev-list", "--count", revision, "--not", "--remotes").strip())


def count_unmerged(repo: str, base: Optional[str], revision: str) -> Optional[int]:
    if not base:
        return None
    return sum(1 for line in git(repo, "cherry", base, revision).splitlines() if line.startswith("+"))


def list_branches(repo: str, base: Optional[str], has_remotes: bool, worktrees: List[Worktree]) -> List[Branch]:
    checked_out = {worktree.branch: worktree.path for worktree in worktrees if worktree.branch}
    output = git(repo, "for-each-ref", "--format=%(refname:short)%00%(upstream:short)%00%(upstream:track)%00%(committerdate:relative): %(subject)", "refs/heads")
    branches = []
    for line in output.splitlines():
        name, upstream, track, last_commit = (line.split("\0") + ["", "", ""])[:4]
        branches.append(Branch(
            name=name,
            upstream=upstream,
            upstream_gone=track == "[gone]",
            unpushed=count_unpushed(repo, f"refs/heads/{name}", has_remotes),
            unmerged=count_unmerged(repo, base, f"refs/heads/{name}"),
            checked_out_at=checked_out.get(name),
            last_commit=last_commit[:100],
        ))
    return branches


def proc_cwds() -> Optional[List[Tuple[int, str, str]]]:
    proc = Path("/proc")
    if not (proc / "self" / "cwd").exists():
        return None
    rows = []
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            cwd = os.readlink(entry / "cwd")
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
        except OSError:
            continue
        rows.append((int(entry.name), command, cwd))
    return rows


def lsof_cwds() -> Optional[List[Tuple[int, str, str]]]:
    try:
        scan = subprocess.Popen(
            ["lsof", "-a", "-nP", "-u", str(os.getuid()), "-d", "cwd", "-Fpcn"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        )
        output, _ = scan.communicate(timeout=LSOF_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        scan.kill()
        return None
    except OSError:
        return None
    rows = []
    pid, command = None, ""
    for line in output.splitlines():
        tag, value = line[:1], line[1:]
        if tag == "p":
            pid, command = int(value), ""
        elif tag == "c":
            command = value
        elif tag == "n" and pid is not None and pid != scan.pid:
            rows.append((pid, command, value))
    return rows


def process_cwds() -> Optional[List[Tuple[int, str, str]]]:
    rows = proc_cwds()
    return rows if rows is not None else lsof_cwds()


def is_this_scan(pid: int) -> bool:
    if pid in (os.getpid(), os.getppid()):
        return True
    try:
        return os.getpgid(pid) == os.getpgrp()
    except OSError:
        return True


def attach_processes(worktrees: List[Worktree], processes: List[Tuple[int, str, str]]) -> None:
    roots = sorted(
        ((os.path.realpath(worktree.path), worktree) for worktree in worktrees if not worktree.missing),
        key=lambda pair: len(pair[0]), reverse=True,
    )
    for pid, command, cwd in processes:
        if is_this_scan(pid):
            continue
        real_cwd = os.path.realpath(cwd)
        for root, worktree in roots:
            if real_cwd == root or real_cwd.startswith(root + os.sep):
                worktree.processes.append({"pid": pid, "command": command[:120]})
                break


def is_agent_worktree(worktree: Worktree) -> bool:
    return AGENT_WORKTREE_SEGMENT in worktree.path + "/" or (worktree.branch or "").startswith(AGENT_BRANCH_PREFIX)


def worktree_findings(worktree: Worktree) -> List[Finding]:
    if worktree.missing:
        return [Finding("note", "missing-worktree", worktree.path, "registered worktree whose directory is gone; `git worktree prune` drops it")]
    findings = []
    if worktree.operation:
        findings.append(Finding("warn", "operation-in-progress", worktree.path, f"a {worktree.operation} is in progress; finish or abort it before reusing this worktree"))
    if worktree.dirty:
        findings.append(Finding("warn", "dirty-worktree", worktree.path, f"{worktree.dirty} uncommitted change(s); work here exists on no ref"))
    if worktree.branch is None and worktree.unpushed:
        findings.append(Finding("warn", "unpushed-commits", worktree.path, f"detached HEAD with {worktree.unpushed} commit(s) on no remote"))
    if worktree.locked:
        findings.append(Finding("note", "locked-worktree", worktree.path, "locked: a running agent or a person holds it; leave it alone"))
    if not worktree.is_main and is_agent_worktree(worktree):
        findings.append(Finding("note", "agent-leftover", worktree.path, "worktree created by agent tooling"))
    if not worktree.is_main and worktree.processes:
        listed = ", ".join(f"{process['pid']} {process['command']}" for process in worktree.processes[:5])
        findings.append(Finding("note", "process-in-worktree", worktree.path, f"{len(worktree.processes)} process(es) running here: {listed}"))
    return findings


def branch_findings(branch: Branch, base: Optional[str]) -> List[Finding]:
    findings = []
    if branch.unpushed:
        findings.append(Finding("warn", "unpushed-commits", branch.name, f"{branch.unpushed} commit(s) on no remote; last: {branch.last_commit}"))
    if branch.upstream_gone:
        findings.append(Finding("note", "upstream-gone", branch.name, f"upstream {branch.upstream} was deleted on the remote"))
    if branch.checked_out_at is None:
        base_name = base.split("/", 1)[-1] if base else None
        if base and branch.name != base_name and branch.unmerged == 0:
            findings.append(Finding("note", "merged-branch", branch.name, f"every patch is already on {base}; prune candidate"))
        if branch.name.startswith(AGENT_BRANCH_PREFIX):
            findings.append(Finding("note", "agent-leftover", branch.name, "branch created by agent tooling and checked out nowhere"))
    return findings


def prune_plan(repo: str, inventory: RepoInventory) -> List[str]:
    quoted_repo = shlex.quote(repo)
    plan = []
    branches = {branch.name: branch for branch in inventory.branches}
    for worktree in inventory.worktrees:
        if worktree.is_main or worktree.missing:
            continue
        branch = branches.get(worktree.branch or "")
        settled = (branch.unmerged == 0 and branch.unpushed == 0) if branch else worktree.unpushed == 0
        if settled and not (worktree.dirty or worktree.operation or worktree.locked or worktree.processes):
            plan.append(f"git -C {quoted_repo} worktree remove {shlex.quote(worktree.path)}")
            if branch:
                plan.append(f"git -C {quoted_repo} branch -d {shlex.quote(branch.name)}")
    for finding in inventory.findings:
        if finding.rule == "merged-branch":
            plan.append(f"git -C {quoted_repo} branch -d {shlex.quote(finding.where)}")
    if any(worktree.missing for worktree in inventory.worktrees):
        plan.append(f"git -C {quoted_repo} worktree prune")
    return plan


def inventory_repo(repo: str, requested_base: Optional[str], processes: Optional[List[Tuple[int, str, str]]]) -> RepoInventory:
    main_path = git(repo, "worktree", "list", "--porcelain").split("\n", 1)[0].partition(" ")[2]
    has_remotes = bool(git(main_path, "remote").strip())
    base = resolve_base(main_path, requested_base)
    worktrees = parse_worktrees(git(main_path, "worktree", "list", "--porcelain"))
    for worktree in worktrees:
        if worktree.missing:
            continue
        worktree.dirty = count_dirty(worktree.path)
        worktree.operation = operation_in_progress(worktree.path)
        if worktree.branch is None and worktree.head:
            worktree.unpushed = count_unpushed(main_path, worktree.head, has_remotes)
    if processes:
        attach_processes(worktrees, processes)
    branches = list_branches(main_path, base, has_remotes, worktrees)
    stash_entries = len(git(main_path, "stash", "list").splitlines())
    inventory = RepoInventory(main_path, base, stash_entries, worktrees, branches)
    for worktree in worktrees:
        inventory.findings.extend(worktree_findings(worktree))
    for branch in branches:
        inventory.findings.extend(branch_findings(branch, base))
    if stash_entries:
        inventory.findings.append(Finding("note", "shared-stash", main_path, f"{stash_entries} stash entr(y/ies); every worktree and session shares this one list"))
    inventory.prune_plan = prune_plan(main_path, inventory)
    return inventory


def print_text(inventories: List[RepoInventory], show_plan: bool) -> None:
    for inventory in inventories:
        linked = sum(1 for worktree in inventory.worktrees if not worktree.is_main)
        print(f"{inventory.path}  base={inventory.base or 'none'}  linked worktrees={linked}  branches={len(inventory.branches)}  stash={inventory.stash_entries}")
        for finding in sorted(inventory.findings, key=lambda item: (-SEVERITY_RANK[item.severity], item.rule, item.where)):
            print(f"  {finding.severity:<4}  {finding.rule:<22} {finding.where}: {finding.message}")
        if not inventory.findings:
            print("  nothing left behind")
        if show_plan:
            print("  prune plan (review, then run by hand):" if inventory.prune_plan else "  prune plan: nothing safe to prune")
            for command in inventory.prune_plan:
                print(f"    {command}")


def exceeds(inventories: List[RepoInventory], fail_on: str) -> bool:
    if fail_on == "never":
        return False
    threshold = SEVERITY_RANK[fail_on]
    return any(SEVERITY_RANK[finding.severity] >= threshold for inventory in inventories for finding in inventory.findings)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="List the worktrees, branches, stashes and processes that agent runs left behind in git repositories, with a prune plan that only prints commands. Read-only.")
    parser.add_argument("repos", nargs="*", default=["."], help="repository paths (any worktree of a repo works)")
    parser.add_argument("--base", help="ref that counts as merged (default: origin/HEAD, then origin/main, origin/master)")
    parser.add_argument("--json", action="store_true", help="print the full inventory as JSON")
    parser.add_argument("--prune-plan", action="store_true", help="print the commands that would prune clean, merged leftovers")
    parser.add_argument("--no-processes", action="store_true", help="skip the process scan")
    parser.add_argument("--fail-on", choices=("warn", "note", "never"), default="never", help="exit 1 when a finding at or above this severity exists")
    args = parser.parse_args(argv)

    processes = None if args.no_processes else process_cwds()
    if processes is None and not args.no_processes:
        print("process scan unavailable (no /proc and no lsof); continuing without it", file=sys.stderr)
    inventories, failed = [], False
    for repo in args.repos:
        try:
            inventories.append(inventory_repo(repo, args.base, processes))
        except GitError as error:
            print(f"skip {repo}: {error}", file=sys.stderr)
            failed = True
    if args.json:
        print(json.dumps([asdict(inventory) for inventory in inventories], indent=2))
    else:
        print_text(inventories, args.prune_plan)
    if failed and not inventories:
        return 2
    return 1 if exceeds(inventories, args.fail_on) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
