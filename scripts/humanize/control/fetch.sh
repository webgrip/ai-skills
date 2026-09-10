#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mode=${1:---committed}

python3 - "$mode" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

committed_only = sys.argv[1] != "--all"
for row in json.load(open("manifest.json")):
    target = Path(row["file"])
    if committed_only and not row["committed"]:
        continue
    if target.exists():
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sfL", "-A", "Mozilla/5.0 (Macintosh)", "--max-time", "60", row["url"], "-o", str(target)], check=True)
    print(f"  fetched {target} ({target.stat().st_size} bytes)")
PY
