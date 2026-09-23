#!/usr/bin/env python3
import argparse
import concurrent.futures
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

WORKING_TREE = "WORKTREE"
NO_INSTRUCTIONS = "noinstructions"


def git(repo, *arguments):
    return subprocess.run(["git", "-C", str(repo), *arguments], capture_output=True, text=True, check=True).stdout.strip()


def resolve_arm(repo, spec):
    name, _, rest = spec.partition("=")
    reference, _, flag = rest.partition(",")
    if reference == WORKING_TREE:
        reference = git(repo, "stash", "create") or "HEAD"
    return {"name": name, "commit": git(repo, "rev-parse", reference), "no_instructions": flag == NO_INSTRUCTIONS}


def parse_events(stdout):
    events = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.extend(parsed if isinstance(parsed, list) else [parsed])
    return events


def summarise(events):
    tool_inputs, result = [], {}
    for event in events:
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []) or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_inputs.append(f"{block.get('name')} {json.dumps(block.get('input', {}))}")
        if event.get("type") == "result":
            result = event
    tokens = 0
    for usage in (result.get("modelUsage") or {}).values():
        tokens += sum(usage.get(key, 0) or 0 for key in ("inputTokens", "cacheCreationInputTokens", "cacheReadInputTokens", "outputTokens"))
    return {
        "tools": "\n".join(tool_inputs),
        "result": result.get("result", "") or "",
        "cost": result.get("total_cost_usd", 0.0) or 0.0,
        "turns": result.get("num_turns", 0) or 0,
        "tokens": tokens,
        "error": bool(result.get("is_error")) or not result,
    }


def grade(case, summary, worktree):
    outcomes = []
    for grader in case.get("graders", []):
        if grader["type"] == "regex":
            haystack = summary["tools"] if grader.get("target") == "tools" else summary["result"]
            outcomes.append(re.search(grader["pattern"], haystack, re.S) is not None)
        elif grader["type"] == "command":
            completed = subprocess.run(grader["run"], shell=True, cwd=worktree, capture_output=True, text=True)
            outcomes.append(completed.returncode == 0)
    return bool(outcomes) and all(outcomes)


def run_once(repo, arm, case, arguments):
    worktree = Path(tempfile.mkdtemp(prefix="probe-"))
    shutil.rmtree(worktree)
    git(repo, "worktree", "add", "--detach", str(worktree), arm["commit"])
    try:
        command = [
            "claude", "-p", case["prompt"],
            "--output-format", "stream-json", "--verbose",
            "--no-session-persistence",
            "--setting-sources", "project,local",
            "--model", arguments.model,
            "--max-turns", str(case.get("max_turns", arguments.max_turns)),
            "--max-budget-usd", str(arguments.max_budget_usd),
        ]
        if arguments.allowed_tools:
            command += ["--allowedTools", arguments.allowed_tools]
        environment = dict(os.environ)
        if arm["no_instructions"]:
            environment["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] = "1"
        completed = subprocess.run(command, cwd=worktree, capture_output=True, text=True, env=environment, timeout=arguments.timeout)
        summary = summarise(parse_events(completed.stdout))
        summary["passed"] = grade(case, summary, worktree)
        return summary
    except subprocess.TimeoutExpired:
        return {"tools": "", "result": "", "cost": 0.0, "turns": 0, "tokens": 0, "error": True, "passed": False}
    finally:
        if not arguments.keep_worktrees:
            subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)], capture_output=True)


def fisher_two_sided(passed_a, total_a, passed_b, total_b):
    failed_a, failed_b = total_a - passed_a, total_b - passed_b
    row_one, column_one, grand = total_a, passed_a + passed_b, total_a + total_b

    def probability(cell):
        return math.comb(column_one, cell) * math.comb(grand - column_one, row_one - cell) / math.comb(grand, row_one)

    observed = probability(passed_a)
    low, high = max(0, row_one + column_one - grand), min(row_one, column_one)
    return min(1.0, sum(probability(cell) for cell in range(low, high + 1) if probability(cell) <= observed * (1 + 1e-9)))


def main():
    parser = argparse.ArgumentParser(description="A/B an instruction-file change with headless Claude Code sessions: fresh worktree per run, deterministic graders, pass rate per arm with a Fisher exact p, median tokens and turns, total cost.")
    parser.add_argument("--cases", required=True, help="JSON file: {\"cases\": [{\"id\", \"prompt\", \"max_turns\"?, \"graders\": [{\"type\": \"regex\", \"target\": \"tools|result\", \"pattern\"} | {\"type\": \"command\", \"run\"}]}]}")
    parser.add_argument("--arm", action="append", required=True, help="name=REF[,noinstructions]; REF is a git ref or WORKTREE for uncommitted tracked changes")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--max-turns", type=int, default=25)
    parser.add_argument("--max-budget-usd", type=float, default=1.0)
    parser.add_argument("--max-total-usd", type=float, default=20.0)
    parser.add_argument("--allowed-tools", default="Read,Grep,Glob")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--keep-worktrees", action="store_true")
    parser.add_argument("--out", help="append one JSON line per run to this file")
    arguments = parser.parse_args()

    repo = Path(git(Path(arguments.repo), "rev-parse", "--show-toplevel"))
    arms = [resolve_arm(repo, spec) for spec in arguments.arm]
    cases = json.loads(Path(arguments.cases).read_text())["cases"]
    spent, lock, results = 0.0, threading.Lock(), []

    def job(case, arm):
        nonlocal spent
        with lock:
            if spent >= arguments.max_total_usd:
                return None
        outcome = run_once(repo, arm, case, arguments)
        record = {"case": case["id"], "arm": arm["name"], **{key: outcome[key] for key in ("passed", "cost", "turns", "tokens", "error")}}
        with lock:
            spent += outcome["cost"]
            results.append(record)
            if arguments.out:
                with open(arguments.out, "a") as handle:
                    handle.write(json.dumps(record) + "\n")
        print(f"{record['case']:30} {record['arm']:14} {'PASS' if record['passed'] else 'fail'}  ${record['cost']:.3f}", file=sys.stderr)
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=arguments.jobs) as pool:
        futures = [pool.submit(job, case, arm) for case in cases for arm in arms for _ in range(arguments.runs)]
        concurrent.futures.wait(futures)

    print(f"\n{'case':30} {'arm':14} {'pass':>7} {'p':>6} {'med tok':>9} {'med turns':>9}")
    for case in cases:
        rows = {arm["name"]: [record for record in results if record["case"] == case["id"] and record["arm"] == arm["name"]] for arm in arms}
        first = rows[arms[0]["name"]]
        for arm in arms:
            runs = rows[arm["name"]]
            passed = sum(record["passed"] for record in runs)
            p_value = "" if arm is arms[0] or not runs or not first else f"{fisher_two_sided(sum(r['passed'] for r in first), len(first), passed, len(runs)):.3f}"
            tokens = statistics.median([record["tokens"] for record in runs]) if runs else 0
            turns = statistics.median([record["turns"] for record in runs]) if runs else 0
            print(f"{case['id'][:30]:30} {arm['name'][:14]:14} {passed:>3}/{len(runs):<3} {p_value:>6} {tokens:>9.0f} {turns:>9.1f}")
    print(f"\ntotal cost ${spent:.2f}; p compares each arm with the first; errors: {sum(record['error'] for record in results)}")


if __name__ == "__main__":
    main()
