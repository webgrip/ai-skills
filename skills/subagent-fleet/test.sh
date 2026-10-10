#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SKILL_DIR=$PWD
WORK=$(mktemp -d)
SLEEPER=""
trap '[ -n "$SLEEPER" ] && kill "$SLEEPER" 2>/dev/null; rm -rf "$WORK"' EXIT
export HOME="$WORK/home" GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=fleet GIT_AUTHOR_EMAIL=fleet@example.org GIT_COMMITTER_NAME=fleet GIT_COMMITTER_EMAIL=fleet@example.org
mkdir -p "$HOME"
INVENTORY=(python3 -I "$SKILL_DIR/scripts/fleet_inventory.py")
TRANSCRIPTS=(python3 -I "$SKILL_DIR/scripts/transcript_calls.py" --root "$SKILL_DIR/fixtures/projects")

fail() { echo "subagent-fleet: $*" >&2; exit 1; }

git init -q --bare "$WORK/origin.git"
git clone -q "$WORK/origin.git" "$WORK/careful" 2>/dev/null
git -C "$WORK/careful" checkout -q -b main
echo "shop" > "$WORK/careful/README"
git -C "$WORK/careful" add README
git -C "$WORK/careful" commit -q -m "feat: initial"
git -C "$WORK/careful" push -q -u origin main
git -C "$WORK/origin.git" symbolic-ref HEAD refs/heads/main
git -C "$WORK/careful" remote set-head origin main

"${INVENTORY[@]}" "$WORK/careful" --fail-on note > "$WORK/careful.out" \
  || { cat "$WORK/careful.out"; fail "a clean repository raised findings"; }

C="$WORK/careless"
git clone -q "$WORK/origin.git" "$C"
echo "half-done" >> "$C/README"
git -C "$C" stash -q

git -C "$C" worktree add -q -b worktree-agent-abc "$C/.claude/worktrees/agent-abc" origin/main
echo "agent work" > "$C/.claude/worktrees/agent-abc/agent.txt"
git -C "$C/.claude/worktrees/agent-abc" add agent.txt
git -C "$C/.claude/worktrees/agent-abc" commit -q -m "feat: agent work"
echo "never staged" > "$C/.claude/worktrees/agent-abc/scratch.txt"

git -C "$C" worktree add -q -b conflict "$WORK/careless-conflict" origin/main
echo "theirs" > "$WORK/careless-conflict/shared.txt"
git -C "$WORK/careless-conflict" add shared.txt
git -C "$WORK/careless-conflict" commit -q -m "feat: theirs"
echo "ours" > "$C/shared.txt"
git -C "$C" add shared.txt
git -C "$C" commit -q -m "feat: ours"
git -C "$WORK/careless-conflict" merge -q main > /dev/null 2>&1 && fail "the conflict fixture merged cleanly"

git -C "$C" branch --no-track merged-topic origin/main
git -C "$C" branch --no-track worktree-agent-old origin/main
git -C "$C" branch --no-track gone-topic origin/main
git -C "$C" push -q -u origin gone-topic 2>/dev/null
git -C "$C" push -q origin --delete gone-topic 2>/dev/null
git -C "$C" fetch -q --prune

git -C "$C" worktree add -q -b vanished "$WORK/vanished" origin/main
rm -rf "$WORK/vanished"
git -C "$C" worktree add -q --detach "$WORK/locked" origin/main
git -C "$C" worktree lock "$WORK/locked"

SLEEPER=$(python3 -I -c 'import subprocess, sys; print(subprocess.Popen(["sleep", "120"], cwd=sys.argv[1], start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid)' "$C/.claude/worktrees/agent-abc")

if "${INVENTORY[@]}" "$C" --fail-on warn > /dev/null; then
  fail "the careless repository passed --fail-on warn"
fi
INVENTORY_JSON=$("${INVENTORY[@]}" "$C" --json)
python3 -I -c '
import json, sys
found = {finding["rule"] for repo in json.loads(sys.argv[2]) for finding in repo["findings"]}
expected = {line.strip() for line in open(sys.argv[1]) if line.strip()}
if found != expected:
    sys.exit(f"inventory: missing {sorted(expected - found)}, unexpected {sorted(found - expected)}")
' "$SKILL_DIR/fixtures/inventory-careless.expect" "$INVENTORY_JSON"

REPORT=$("${INVENTORY[@]}" "$C" --prune-plan --no-processes)
PLAN=$(sed -n '/prune plan/,$p' <<< "$REPORT")
grep -q "branch -d merged-topic" <<< "$PLAN" || fail "prune plan misses the merged branch"
grep -q "worktree prune" <<< "$PLAN" || fail "prune plan misses the vanished worktree"
grep -q "agent-abc" <<< "$PLAN" && fail "prune plan offers to delete a dirty, unpushed agent worktree"
grep -q "$WORK/locked" <<< "$PLAN" && fail "prune plan offers to delete a locked worktree"
echo "fleet_inventory: careful clean, careless fired $(wc -l < fixtures/inventory-careless.expect | tr -d ' ') rules, prune plan safe"

WINDOW=(--since 2026-10-01T10:00:00Z --until 2026-10-01T10:15:00Z)
IN_WINDOW=$("${TRANSCRIPTS[@]}" "${WINDOW[@]}")
BASH_CALLS=$("${TRANSCRIPTS[@]}" "${WINDOW[@]}" --tool Bash)
PUSHES=$("${TRANSCRIPTS[@]}" "${WINDOW[@]}" --grep 'git push')
SHOP=$("${TRANSCRIPTS[@]}" "${WINDOW[@]}" --project shop)
AT=$("${TRANSCRIPTS[@]}" --at 2026-10-01T10:06:00Z --minutes 0.5)
touch "$WORK/marker" && TZ=UTC touch -t 202610011010 "$WORK/marker"
AROUND=$("${TRANSCRIPTS[@]}" --around "$WORK/marker" --minutes 1 2> /dev/null)
HANDBACKS=$("${TRANSCRIPTS[@]}" --handbacks)
EDITS=$("${TRANSCRIPTS[@]}" --tool Edit --json)

[ "$(grep -c . <<< "$BASH_CALLS")" = 3 ] || fail "window should hold three Bash calls"
grep -q "5e55a0a1/a1b2c3d4  Bash: git stash drop" <<< "$BASH_CALLS" || fail "subagent call not attributed to its agent"
grep -q "checkout.py" <<< "$IN_WINDOW" && fail "a call outside the window leaked in"
[ "$(grep -c . <<< "$PUSHES")" = 1 ] || fail "--grep should keep only the push"
[ "$(grep -c . <<< "$SHOP")" = 2 ] || fail "--project should drop the other project"
[ "$AT" = "$(grep 'rm -rf build' <<< "$AT")" ] && [ -n "$AT" ] || fail "--at window wrong: $AT"
grep -q "git stash drop" <<< "$AROUND" || fail "--around did not centre on the file time"
[ "$(grep -c '^=== ' <<< "$HANDBACKS")" = 1 ] || fail "hand-backs should be read once, deduplicated"
grep -q "^Changed checkout.py:12" <<< "$HANDBACKS" || fail "hand-back report not de-indented"
python3 -I -c 'import json, sys; calls = json.loads(sys.argv[1]); sys.exit(0 if [c["summary"] for c in calls] == ["/home/dev/shop/checkout.py"] else "json output wrong")' "$EDITS"
echo "transcript_calls: window, grep, project, file time, hand-backs and json all hold"

python3 -I - "$SKILL_DIR" <<'PY'
import re, sys
from pathlib import Path
skill = Path(sys.argv[1])
docs = "".join(path.read_text() for path in [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))])
rules = set(re.findall(r'Finding\("(?:warn|note)", "([a-z-]+)"', (skill / "scripts" / "fleet_inventory.py").read_text()))
undocumented = sorted(rule for rule in rules if f"`{rule}`" not in docs)
if undocumented:
    sys.exit(f"fleet_inventory rules missing from the docs: {undocumented}")
print(f"fleet_inventory: {len(rules)} rules documented")
PY
