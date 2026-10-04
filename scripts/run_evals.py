#!/usr/bin/env python3
"""Trigger-accuracy probe for the estate's evals.

For every skills/<name>/evals/evals.json case, launch headless Claude Code
sessions with ONLY that skill loaded (--plugin-dir, the sanctioned local test
path), give each the eval prompt verbatim, and detect whether the skill
actually fired (a Skill tool call naming it in the stream). This automates
the *triggering* half of the eval contract — the half that regresses
silently. Output QUALITY still needs the with/without grading described in
CONTRIBUTING.md (Claude Code's skill-creator plugin automates that loop).

Usage:
    python3 scripts/run_evals.py                     # every skill (costs tokens!)
    python3 scripts/run_evals.py adr-writer ...      # subset
    python3 scripts/run_evals.py --repeats 5         # default 3 runs per case
    python3 scripts/run_evals.py --model opus        # default sonnet
    python3 scripts/run_evals.py --case create-ticket-with-conventions

Notes:
- every session is isolated: an empty temp cwd (no repo CLAUDE.md, nothing
  to explore), no user/project/local settings (no installed plugins, no
  ~/.claude/CLAUDE.md), no MCP servers, and Skill as the only tool — so a
  sibling skill can't steal the trigger and a timeout can't come from the
  agent wandering the repo
- a case is PASS when every run behaved as expected, FAIL when none did,
  FLAKY otherwise; single runs mislead, so tune a description only on FAIL
  or a FLAKY that stays flaky at --repeats 5
- sonnet is the default because haiku under-triggers on skills known to work
  (it failed the already-released expressive-design), which makes it a
  broken probe rather than a cheap one; calibrate any other model on a
  known-good skill first
- "expect_trigger": false marks should-NOT-trigger probes; null marks
  output-quality-only cases the trigger probe skips
- requires the claude CLI, logged in
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_CALL_RE = re.compile(r'"name"\s*:\s*"Skill"')
SKILL_NAME_RE = re.compile(r'"skill"\s*:\s*"([^"]+)"')
TIMEOUT = 180
ISOLATION = [
    "--setting-sources", "",
    "--strict-mcp-config",
    "--tools", "Skill",
    "--allowedTools", "Skill",
    "--no-session-persistence",
]


def probe(skill: str, prompt: str, model: str) -> tuple[bool, str]:
    cmd = [
        "claude", "-p", prompt,
        "--model", model,
        "--plugin-dir", str(ROOT / "skills" / skill),
        *ISOLATION,
        "--output-format", "stream-json",
        "--verbose",
    ]
    with tempfile.TemporaryDirectory(prefix="trigger-probe-") as cwd:
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=TIMEOUT, cwd=cwd
            )
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except FileNotFoundError:
            sys.exit("claude CLI not found — install and log in first")
    out = proc.stdout + proc.stderr
    fired = [m for m in SKILL_NAME_RE.findall(out) if skill in m]
    if SKILL_CALL_RE.search(out) and fired:
        return True, "fired"
    if proc.returncode != 0 and not SKILL_CALL_RE.search(out):
        return False, f"session error rc={proc.returncode}"
    return False, "quiet"


def verdict(as_expected: int, runs: int) -> str:
    if as_expected == runs:
        return "PASS"
    if as_expected == 0:
        return "FAIL"
    return "FLAKY"


def tally(details: list[str]) -> str:
    counts: dict[str, int] = {}
    for detail in details:
        counts[detail] = counts.get(detail, 0) + 1
    return ", ".join(f"{name}×{n}" for name, n in counts.items())


def main() -> None:
    sys.stdout.reconfigure(line_buffering=True)
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skills", nargs="*", help="subset of skill names (default: all)")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--repeats", type=int, default=3, help="runs per case (default 3)")
    parser.add_argument("--jobs", type=int, default=4, help="sessions in parallel (default 4)")
    parser.add_argument("--case", help="run only the case with this id")
    args = parser.parse_args()
    if args.repeats < 1 or args.jobs < 1:
        sys.exit("--repeats and --jobs must be at least 1")

    suites = sorted(ROOT.glob("skills/*/evals/evals.json"))
    if args.skills:
        suites = [s for s in suites if s.parent.parent.name in args.skills]
    if not suites:
        sys.exit("no eval suites matched")

    cases: list[tuple[str, dict]] = []
    for suite_path in suites:
        skill = suite_path.parent.parent.name
        for case in json.loads(suite_path.read_text()).get("evals", []):
            if args.case and case.get("id") != args.case:
                continue
            if case.get("expect_trigger", True) is None:
                print(f"SKIP   {skill} :: {case['id']}  (output-quality case; not trigger-gated)")
                continue
            cases.append((skill, case))
    if not cases:
        sys.exit("no cases matched")

    print(f"probing {len(cases)} cases × {args.repeats} runs with {args.model}, "
          f"{args.jobs} at a time\n")
    verdicts = {"PASS": 0, "FLAKY": 0, "FAIL": 0}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        runs: list[list[Future]] = [
            [pool.submit(probe, skill, case["prompt"], args.model) for _ in range(args.repeats)]
            for skill, case in cases
        ]
        for (skill, case), futures in zip(cases, runs):
            expect = case.get("expect_trigger", True)
            results = [f.result() for f in futures]
            as_expected = sum(1 for fired, _ in results if fired == expect)
            mark = verdict(as_expected, args.repeats)
            verdicts[mark] += 1
            want = "fire" if expect else "stay quiet"
            print(f"{mark:6} {skill} :: {case['id']}  {as_expected}/{args.repeats} "
                  f"(expected {want}; {tally([d for _, d in results])})")
            if mark != "PASS":
                print(f"       prompt: {case['prompt'][:100]}")

    print(f"\ntrigger probe ({args.model}, {args.repeats} runs/case): "
          f"{verdicts['PASS']} pass, {verdicts['FLAKY']} flaky, {verdicts['FAIL']} fail "
          f"of {len(cases)}")
    if verdicts["FLAKY"] or verdicts["FAIL"]:
        print("FLAKY: re-run that case with --repeats 5 before touching the description.\n"
              "FAIL with 'quiet': the description lacks the prompt's phrasing — lead with the "
              "outcome the user asks for and name the request shape (skillsmith skill), then "
              "re-probe.\nFAIL with 'timeout' or 'session error': a probe problem, not a "
              "description miss.")
        sys.exit(1)


if __name__ == "__main__":
    main()
