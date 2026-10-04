#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 - <<'PY'
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CHECK = Path("scripts/merge_check.py").resolve()
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
AGENT = "\n\nCo-authored-by: Claude <noreply@anthropic.com>"
failures = []


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=ENV)


def write(repo, files):
    for path, text in files.items():
        target = repo / path
        if text is None:
            git(repo, "rm", "-q", path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    git(repo, "add", "-A")


def commit(repo, message, files):
    write(repo, files)
    git(repo, "commit", "-q", "--allow-empty", "-m", message)


def fresh_repo():
    repo = Path(tempfile.mkdtemp(prefix="merge-check-"))
    git(repo, "init", "-q", "-b", "main")
    commit(repo, "feat: base", {
        "src/calc.py": "def add(a, b):\n    return a + b\n",
        "tests/test_calc.py": "from src.calc import add\n\ndef test_add():\n    assert add(1, 2) == 3\n",
        "tests/test_old.py": "def test_old():\n    assert True\n",
        ".forgejo/workflows/ci.yml": "jobs:\n  t:\n    steps:\n      - run: pytest\n",
        "README.md": "base\n",
    })
    git(repo, "checkout", "-q", "-b", "pr")
    return repo


def run(repo, *args):
    proc = subprocess.run([sys.executable, str(CHECK), "--repo", str(repo), "--base", "main",
                           "--head", "pr", "--json", *args], capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        sys.exit(f"merge_check crashed: {proc.stderr}")
    result = json.loads(proc.stdout)
    return result, {row["criterion"]: row["status"] for row in result["checks"]}


def expect(case, statuses, criterion, wanted):
    got = next((s for c, s in statuses.items() if c.startswith(criterion)), None)
    if got != wanted:
        failures.append(f"{case}: {criterion!r} expected {wanted}, got {got}")


repo = fresh_repo()
commit(repo, "feat(calc): add sub\n\nRefs VIK-1", {
    "src/sub.py": "def sub(a, b):\n    return a - b\n",
    "tests/test_sub.py": "from src.sub import sub\n\ndef test_sub():\n    assert sub(3, 1) == 2\n",
    "src/cli.py": "import sys\n\ndef main():\n    sys.exit(0)\n",
})
result, s = run(repo, "--conventional", "--trailer", r"VIK-\d+")
if not result["mergeable"]:
    failures.append(f"clean: expected mergeable, got {s}")
for criterion in ("no test deleted", "existing tests untouched", "gate configuration untouched",
                  "no check weakened", "no assertion removed", "conventional subject",
                  "ticket referenced", "contains the current base"):
    expect("clean", s, criterion, "PASS")

repo = fresh_repo()
_, s = run(repo)
expect("zombie", s, "the branch carries a change", "FAIL")

sabotage = {
    "tests/test_calc.py": "import pytest\nfrom src.calc import add\n\n@pytest.mark.skip\ndef test_add():\n    add(1, 2)\n",
    "tests/test_old.py": None,
    "tests/conftest.py": "import sys\nsys.exit(0)\n",
    ".forgejo/workflows/ci.yml": "jobs:\n  t:\n    steps:\n      - run: pytest || true\n",
    "src/calc.py": "def add(a, b):\n<<<<<<< HEAD\n    return a + b\n>>>>>>> other\n",
}
for author, weak in (("agent", "FAIL"), ("human", "WARN")):
    repo = fresh_repo()
    commit(repo, "fix: green" + (AGENT if author == "agent" else ""), sabotage)
    commit(repo, "fixup! fix: green", {"README.md": "x\n"})
    result, s = run(repo)
    if result["author"] != author:
        failures.append(f"sabotage: author detected as {result['author']}, expected {author}")
    for criterion in ("no test deleted", "existing tests untouched", "gate configuration untouched",
                      "no check weakened", "no assertion removed"):
        expect(f"sabotage/{author}", s, criterion, weak)
    expect(f"sabotage/{author}", s, "no conflict markers", "FAIL")
    expect(f"sabotage/{author}", s, "no fixup/WIP commits land", "FAIL")
    _, squashed = run(repo, "--merge-style", "squash")
    expect(f"sabotage/{author}/squash", squashed, "no fixup/WIP commits land", "PASS")

repo = fresh_repo()
git(repo, "mv", "tests/test_old.py", "src/old_check.py")
git(repo, "commit", "-q", "-m", "refactor: move" + AGENT)
_, s = run(repo)
expect("renamed-out-of-discovery", s, "no test deleted", "FAIL")

repo = fresh_repo()
commit(repo, "fix: tighten" + AGENT, {
    "tests/test_calc.py": "from src.calc import add\n\ndef test_add():\n    assert add(1, 2) == 3\n    assert add(2, 2) == 4\n",
})
_, s = run(repo)
expect("agent-test-edit", s, "existing tests untouched", "FAIL")
_, s = run(repo, "--allow-test-edits")
expect("agent-test-edit/allowed", s, "existing tests untouched", "WARN")
expect("agent-test-edit/allowed", s, "no assertion removed", "PASS")

repo = fresh_repo()
commit(repo, "docs: pr side", {"README.md": "from the pr\n", "deploy/app.yaml": "x: 1\n"})
git(repo, "checkout", "-q", "main")
commit(repo, "docs: main side", {"README.md": "from main\n"})
git(repo, "checkout", "-q", "pr")
_, s = run(repo, "--protected", "deploy/*")
expect("behind", s, "contains the current base", "WARN")
expect("behind", s, "merges without conflicts", "FAIL")
expect("behind", s, "protected areas untouched", "FAIL")
_, s = run(repo, "--require-up-to-date")
expect("behind/strict", s, "contains the current base", "FAIL")

repo = fresh_repo()
commit(repo, "feat: x" + AGENT, {"src/x.py": "X = 1\n"})
body = repo / "body.md"
body.write_text("## Summary\nx\n\n## How tested\npytest\n")
_, s = run(repo, "--body", str(body))
expect("agent-body", s, "PR states what/why, verification, risk, rollback", "FAIL")
body.write_text("## Wat en waarom\nx\n## Verificatie\ny\n## Risico\nz\n## Terugdraaipad\nrevert\n")
_, s = run(repo, "--body", str(body))
expect("agent-body/nl", s, "PR states what/why, verification, risk, rollback", "PASS")

if failures:
    print("\n".join(failures), file=sys.stderr)
    sys.exit(1)
print("merge_check: clean, zombie, sabotage (agent + human), rename-out, test-edit, behind, body cases hold")
PY

python3 scripts/ticket_lint.py - --gate ready > /dev/null <<'MD' && echo "ticket_lint: a Ready ticket passes"
## Problem
Backups of `db/prod` fail silently since 2026-09-01 (see `ops/backup.log:12`).

## Outcome
Nightly backups either succeed or page the on-call.

## Acceptance criteria
- [ ] A failed backup job pages the on-call within 15 minutes
- [ ] A backup older than 26 hours raises an alert
- [ ] The alert cannot be silenced by deleting the job

## Verification
Kill the backup job in staging; the page arrives within 15 minutes.
MD
