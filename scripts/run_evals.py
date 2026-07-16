#!/usr/bin/env python3
"""Trigger-accuracy probe for the estate's evals.

For every skills/<name>/evals/evals.json case, launch a headless Claude Code
session with ONLY that skill loaded (--plugin-dir, the sanctioned local test
path), give it the eval prompt verbatim, and detect whether the skill
actually fired (a Skill tool call naming it in the stream). This automates
the *triggering* half of the eval contract — the half that regresses
silently. Output QUALITY still needs the with/without grading described in
CONTRIBUTING.md (Claude Code's skill-creator plugin automates that loop).

Usage:
    python3 scripts/run_evals.py                     # every skill (costs tokens!)
    python3 scripts/run_evals.py adr-writer ...      # subset
    python3 scripts/run_evals.py --model sonnet      # default haiku (cheap probe)
    python3 scripts/run_evals.py --case create-ticket-with-conventions

Notes:
- each case is one short model call (~10-20s); the full estate is a few
  minutes and a few cents — run on demand, not per-commit
- run in a clean environment for authoritative numbers: personal plugins and
  in-scope CLAUDE.md files can perturb triggering (a same-named installed
  skill firing still counts as a hit, so local runs remain indicative)
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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_CALL_RE = re.compile(r'"name"\s*:\s*"Skill"')
SKILL_NAME_RE = re.compile(r'"skill"\s*:\s*"([^"]+)"')
TIMEOUT = 180


def probe(skill: str, prompt: str, model: str) -> tuple[bool, str]:
    """Run one headless session; return (skill_fired, detail)."""
    cmd = [
        "claude", "-p", prompt,
        "--model", model,
        "--plugin-dir", str(ROOT / "skills" / skill),
        "--allowedTools", "Skill",
        "--output-format", "stream-json",
        "--verbose",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=TIMEOUT, cwd=ROOT
        )
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except FileNotFoundError:
        sys.exit("claude CLI not found — install and log in first")
    out = proc.stdout + proc.stderr
    fired = [m for m in SKILL_NAME_RE.findall(out) if skill in m]
    if SKILL_CALL_RE.search(out) and fired:
        return True, fired[0]
    if proc.returncode != 0 and not SKILL_CALL_RE.search(out):
        return False, f"session error (rc={proc.returncode})"
    return False, "no Skill call"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", help="subset of skill names (default: all)")
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--case", help="run only the case with this id")
    args = parser.parse_args()

    suites = sorted(ROOT.glob("skills/*/evals/evals.json"))
    if args.skills:
        suites = [s for s in suites if s.parent.parent.name in args.skills]
    if not suites:
        sys.exit("no eval suites matched")

    failures = 0
    total = 0
    for suite_path in suites:
        skill = suite_path.parent.parent.name
        suite = json.loads(suite_path.read_text())
        for case in suite.get("evals", []):
            if args.case and case.get("id") != args.case:
                continue
            expect = case.get("expect_trigger", True)
            if expect is None:
                print(f"SKIP  {skill} :: {case['id']}  (output-quality case; not trigger-gated)")
                continue
            total += 1
            fired, detail = probe(skill, case["prompt"], args.model)
            ok = fired == expect
            failures += 0 if ok else 1
            mark = "PASS" if ok else "FAIL"
            want = "fire" if expect else "stay quiet"
            print(f"{mark}  {skill} :: {case['id']}  (expected {want}; {detail})")
            if not ok:
                print(f"      prompt: {case['prompt'][:100]}")

    if total == 0:
        sys.exit("no cases matched")
    print(f"\ntrigger probe: {total - failures}/{total} as expected ({args.model})")
    if failures:
        print("under-triggering usually means the description lacks the prompt's "
              "phrasing — tune it with the skillsmith skill, then re-probe.")
        sys.exit(1)


if __name__ == "__main__":
    main()
