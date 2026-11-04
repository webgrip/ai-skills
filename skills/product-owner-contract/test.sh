#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 - <<'PY'
import json
import re
import subprocess
import sys
from pathlib import Path

LINT = Path("../product-owner/scripts/ticket_lint.py").resolve()
failures = []

golden = Path("assets/golden-tickets.md")
text = golden.read_text()
titles = re.findall(r"^Title:\s+(.+)$", text, re.M)
blocks = re.findall(r"```markdown\n(.*?)\n```\n", text, re.S)
if not blocks:
    failures.append(f"{golden}: no markdown ticket blocks")
if len(titles) != len(blocks):
    failures.append(f"{golden}: {len(titles)} titles for {len(blocks)} tickets")
for n, (title, block) in enumerate(zip(titles, blocks), 1):
    proc = subprocess.run([sys.executable, str(LINT), "-", "--json", "--gate", "ready",
                           "--title", title], input=block, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        sys.exit(f"ticket_lint crashed: {proc.stderr}")
    result = json.loads(proc.stdout)
    flagged = [c["criterion"] for c in result["checks"] if c["status"] in ("FAIL", "WARN")]
    if not result["passes"] or flagged:
        failures.append(f"{golden} ticket {n}: {flagged}")

trackers = sorted(Path("trackers").glob("*.md"))
if not trackers:
    failures.append("no trackers/*.md found")
for doc in [Path("SKILL.md"), Path("board.md"), *trackers, *sorted(Path("assets").glob("*.md"))]:
    for link in re.findall(r"\]\(([^)#]+)\)", doc.read_text()):
        if not link.startswith("http") and not (doc.parent / link).exists():
            failures.append(f"{doc}: broken link {link}")

for heading in ("## Stages", "## Taxonomy spelling", "## Epics and queue"):
    for doc in trackers:
        if heading not in doc.read_text():
            failures.append(f"{doc}: missing {heading!r}")

if failures:
    print("product-owner-contract: FAIL")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
print(f"product-owner-contract: OK — {len(titles)} golden tickets pass ready, {len(trackers)} tracker files")
PY
