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


def regex_outcome(grader, summary):
    haystack = summary["tools"] if grader.get("target") == "tools" else summary["result"]
    return re.search(grader["pattern"], haystack, re.S) is not None


def grade(case, summary, worktree):
    outcomes = []
    for grader in case.get("graders", []):
        if grader["type"] == "regex":
            outcomes.append(regex_outcome(grader, summary))
        elif grader["type"] == "command":
            completed = subprocess.run(grader["run"], shell=True, cwd=worktree, capture_output=True, text=True)
            outcomes.append(completed.returncode == 0)
    return bool(outcomes) and all(outcomes)


def regrade(case, record):
    graders = case.get("graders", [])
    if not graders or any(grader["type"] != "regex" for grader in graders) or "result" not in record:
        return None
    return all(regex_outcome(grader, record) for grader in graders)


UNESCAPED_ANCHOR = re.compile(r"(?<!\\)[\^$]")
MULTILINE_FLAG = re.compile(r"\(\?[a-zA-Z]*m[a-zA-Z]*[):]")


def anchors_inside(pattern):
    body = re.sub(r"\[\^", "[", pattern)
    body = body[1:] if body.startswith("^") else body
    body = body[:-1] if body.endswith("$") and not body.endswith("\\$") else body
    return bool(UNESCAPED_ANCHOR.search(body))


def grader_warnings(cases):
    warnings = []
    for case in cases:
        for grader in case.get("graders", []):
            pattern = grader.get("pattern", "")
            if grader["type"] == "regex" and anchors_inside(pattern) and not MULTILINE_FLAG.search(pattern):
                warnings.append(f"{case['id']}: pattern {pattern!r} anchors with ^ or $ inside the pattern but has no (?m); there they match only the start and end of the whole text")
    return warnings


def run_once(repo, arm, case, arguments):
    worktree = Path(tempfile.mkdtemp(prefix="probe-"))
    shutil.rmtree(worktree)
    git(repo, "worktree", "add", "--detach", str(worktree), arm["commit"])
    try:
        command = [
            arguments.claude_bin, "-p", case["prompt"],
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
    parser.add_argument("--arm", action="append", default=[], help="name=REF[,noinstructions]; REF is a git ref or WORKTREE for uncommitted tracked changes")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--model", default="haiku", help="start with the cheapest model that shows the mistake, and the model the team really runs; default haiku")
    parser.add_argument("--max-turns", type=int, default=25)
    parser.add_argument("--max-budget-usd", type=float, default=1.0)
    parser.add_argument("--max-total-usd", type=float, default=5.0)
    parser.add_argument("--claude-bin", default=os.environ.get("CLAUDE_BIN", "claude"), help="the Claude Code binary to run, for example the IDE extension's bundled one; default $CLAUDE_BIN or claude on PATH")
    parser.add_argument("--yes", action="store_true", help="start the runs; without it the plan and its cost cap are printed and nothing runs")
    parser.add_argument("--regrade", metavar="RESULTS", help="regrade the runs recorded in RESULTS (an --out file) with the current regex graders; runs nothing and costs nothing")
    parser.add_argument("--allowed-tools", default="Read,Grep,Glob")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--keep-worktrees", action="store_true")
    parser.add_argument("--out", help="append one JSON line per run to this file")
    arguments = parser.parse_args()

    cases = json.loads(Path(arguments.cases).read_text())["cases"]
    for warning in grader_warnings(cases):
        print(f"warning: {warning}", file=sys.stderr)
    if arguments.regrade:
        return report_regrade(cases, arguments.regrade)
    if not arguments.arm:
        parser.error("--arm is required unless --regrade is given")
    total = len(cases) * len(arguments.arm) * arguments.runs
    print(f"Plan: {total} runs ({len(cases)} cases x {len(arguments.arm)} arms x {arguments.runs}) on {arguments.model} with {arguments.claude_bin}; each run capped at ${arguments.max_budget_usd:.2f}, all runs at ${arguments.max_total_usd:.2f}.", file=sys.stderr)
    if not arguments.yes:
        print("Nothing ran. State this cost to whoever pays for it, then add --yes.", file=sys.stderr)
        return 0
    repo = Path(git(Path(arguments.repo), "rev-parse", "--show-toplevel"))
    arms = [resolve_arm(repo, spec) for spec in arguments.arm]
    spent, lock, results = 0.0, threading.Lock(), []

    def job(case, arm):
        nonlocal spent
        with lock:
            if spent >= arguments.max_total_usd:
                return None
        outcome = run_once(repo, arm, case, arguments)
        record = {"case": case["id"], "arm": arm["name"], **{key: outcome[key] for key in ("passed", "cost", "turns", "tokens", "error", "result", "tools")}}
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

    print_table(cases, [arm["name"] for arm in arms], results)
    print(f"\ntotal cost ${spent:.2f}; p compares each arm with the first; errors: {sum(record['error'] for record in results)}")
    return 0


def print_table(cases, arm_names, results):
    print(f"\n{'case':30} {'arm':14} {'pass':>7} {'p':>6} {'med tok':>9} {'med turns':>9}")
    for case in cases:
        rows = {name: [record for record in results if record["case"] == case["id"] and record["arm"] == name] for name in arm_names}
        first = rows[arm_names[0]] if arm_names else []
        for index, name in enumerate(arm_names):
            runs = rows[name]
            passed = sum(record["passed"] for record in runs)
            p_value = "" if index == 0 or not runs or not first else f"{fisher_two_sided(sum(r['passed'] for r in first), len(first), passed, len(runs)):.3f}"
            tokens = statistics.median([record["tokens"] for record in runs]) if runs else 0
            turns = statistics.median([record["turns"] for record in runs]) if runs else 0
            print(f"{case['id'][:30]:30} {name[:14]:14} {passed:>3}/{len(runs):<3} {p_value:>6} {tokens:>9.0f} {turns:>9.1f}")


def report_regrade(cases, path):
    records = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    by_case = {case["id"]: case for case in cases}
    regraded, skipped = [], 0
    for record in records:
        case = by_case.get(record["case"])
        outcome = regrade(case, record) if case else None
        if outcome is None:
            skipped += 1
            continue
        regraded.append({**record, "passed": outcome})
    arm_names = list(dict.fromkeys(record["arm"] for record in regraded))
    print_table([case for case in cases if any(record["case"] == case["id"] for record in regraded)], arm_names, regraded)
    print(f"\nregraded {len(regraded)} runs from {path}; skipped {skipped} (command graders, unknown cases or runs recorded without their result text)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
