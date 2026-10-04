#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SKILL="$(pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

python3 - <<'PY'
import json, subprocess, sys

def parse(*arguments):
    return json.loads(subprocess.run(["python3", "scripts/measure.py", "parse", *arguments], check=True, capture_output=True, text=True).stdout)

simple = parse("fixtures/claude-simple.jsonl")
assert simple["valid"] and simple["processed_input"] == 23986 and simple["output"] == 66, simple
assert abs(simple["cost_usd"] - simple["reported_cost_usd"]) < 1e-6, "simple run must reproduce the CLI's own cost"

subagent = parse("fixtures/claude-subagent.jsonl")
assert subagent["processed_input"] == 51805 and subagent["cache_read"] == 38958 and subagent["output"] == 571, subagent
assert any("2 result events" in note for note in subagent["notes"]), "must use the last of several result events"
assert subagent["subagent_share"] > 0 and subagent["tool_calls"].get("Agent") == 1, subagent
haiku = subagent["per_model"]["claude-haiku-4-5-20251001"]
assert haiku["cache_write_1h"] == 6538 and haiku["cache_write_5m"] == 0, "1-hour split must come from per-step usage"
assert abs(haiku["cost_usd"] - 0.0186515) < 1e-5, haiku
sonnet = subagent["per_model"]["claude-sonnet-5"]
assert abs(sonnet["cost_usd"] - 0.017833) < 1e-5, "Sonnet 5 must be priced at the current $2/$10, not the CLI's stale $3/$15"

codex = parse("--adapter", "codex", "--model", "claude-sonnet-5", "fixtures/codex.jsonl")
assert codex["processed_input"] == 42000 and codex["cache_read"] == 30000 and codex["fresh_input"] == 12000, "codex cached tokens sit inside input_tokens"

report = json.loads(subprocess.run(["python3", "scripts/measure.py", "report", "fixtures/runs", "--json", "--refactor-cost-usd", "6", "--changes-per-month", "20"],
                                   check=True, capture_output=True, text=True).stdout)
rows = {row["ref"]: row for row in report["rows"]}
after = rows["step-15"]
assert after["valid"] == 5 and after["trials"] == 6 and after["pass_rate"] == 0.8, after
low, high = after["input_ratio_ci"]
assert low < after["input_ratio"] < high < 1, after
assert 70 < after["break_even_changes"] < 90 and after["payback_months"] > 3, after
assert after["cost_per_passing_change"] > after["cost_usd"][1], "cost per passing change must account for failures"

roi = json.loads(subprocess.run(["python3", "scripts/roi.py", "--model", "claude-sonnet-5", "--baseline-input", "159564", "--baseline-output", "1705",
                                 "--after-input", "27360", "--after-output", "2113", "--cache-read-share", "0", "--refactor-input", "5000000",
                                 "--changes-per-month", "20", "--json"], check=True, capture_output=True, text=True).stdout)
assert round(roi["scenarios"][0]["break_even_changes"]) == 38, roi
scenarios = json.loads(subprocess.run(["python3", "scripts/roi.py", "--model", "claude-sonnet-5", "--baseline-input", "159564", "--refactor-input", "5000000",
                                       "--changes-per-month", "20", "--json"], check=True, capture_output=True, text=True).stdout)["scenarios"]
assert [s["verdict"] for s in scenarios] == ["wait", "wait", "refactor"], scenarios
print("measure.py and roi.py: parser, adapters, report and break-even hold")
PY

REPO="$WORK/repo"
git init -q "$REPO"
git -C "$REPO" config user.email test@example.com
git -C "$REPO" config user.name test
mkdir -p "$REPO/src"
seq 1 400 > "$REPO/src/store.rs"; echo a > "$REPO/src/api.rs"; echo b > "$REPO/src/cold.rs"; echo '{}' > "$REPO/package-lock.json"
git -C "$REPO" add . && git -C "$REPO" commit -qm "initial"
for i in 1 2 3 4 5 6; do
  echo "change $i" >> "$REPO/src/store.rs"; echo "api $i" >> "$REPO/src/api.rs"; echo "lock $i" >> "$REPO/package-lock.json"
  git -C "$REPO" commit -qam "feat: store change $i" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
done
echo human >> "$REPO/src/store.rs"; git -C "$REPO" commit -qam "fix: by hand"
echo bot >> "$REPO/src/cold.rs"; git -C "$REPO" commit -qam "chore(release): v1 [skip ci]"

python3 scripts/hotspots.py --json --coupling --min-revs 2 --min-shared 2 --agent-pattern "Co-Authored-By: Claude" "$REPO" > "$WORK/hot.json"
python3 - "$WORK/hot.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
files = {row["file"]: row for row in data["files"]}
assert data["files"][0]["file"] == "src/store.rs", data["files"]
assert files["src/store.rs"]["commits"] == 8 and abs(files["src/store.rs"]["agent_share"] - 0.75) < 0.01, files["src/store.rs"]
assert "package-lock.json" not in files, "lockfiles are excluded by default"
assert files["src/cold.rs"]["commits"] == 1, "release-bot commits are ignored by default"
pair = data["coupling"][0]
assert {pair["left"], pair["right"]} == {"src/api.rs", "src/store.rs"} and pair["shared_commits"] == 7, pair
print("hotspots.py: ranking, agent share, exclusions and coupling hold")
PY

echo "add an index" > "$WORK/prompt.md"
python3 scripts/measure.py run --repo "$REPO" --refs HEAD~1,HEAD --prompt "$WORK/prompt.md" --check "test -f src/store.rs" \
    --repeats 2 --agent-cmd "cat $SKILL/fixtures/claude-simple.jsonl" --out "$WORK/runs" 2> /dev/null
python3 - "$WORK/runs" "$REPO" <<'PY'
import json, subprocess, sys
from pathlib import Path
runs, repo = Path(sys.argv[1]), sys.argv[2]
trials = [json.loads(p.read_text()) for p in runs.glob("*.json") if p.name != "experiment.json"]
assert len(trials) == 4 and all(t["valid"] and t["passed"] for t in trials), trials
assert json.loads((runs / "experiment.json").read_text())["baseline"] == "HEAD~1"
worktrees = subprocess.run(["git", "-C", repo, "worktree", "list"], capture_output=True, text=True).stdout.strip().splitlines()
assert len(worktrees) == 1, f"trial worktrees must be removed: {worktrees}"
print("measure.py run: interleaved trials in throwaway worktrees, cleaned up")
PY
