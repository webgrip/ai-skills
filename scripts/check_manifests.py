#!/usr/bin/env python3
"""Check plugin manifest structure. Exits non-zero on any problem.

Enforced invariants:
- marketplace.json is valid JSON with name/owner/plugins
- every skills/<name> dir has a valid .claude-plugin/plugin.json whose name
  matches the dir and carries the fields marketplace entries are generated from
- every skill dir has SKILL.md at its root (the skill dir IS the plugin root)

Drift between marketplace.json and the plugin manifests is checked by
scripts/sync_marketplace.py --check (the catalog is generated, never edited);
skill-quality rules live in scripts/lint_skills.py.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_PLUGIN_FIELDS = ("name", "description", "version", "license", "keywords")
errors = []


def err(msg):
    errors.append(msg)


mp_path = ROOT / ".claude-plugin" / "marketplace.json"
try:
    mp = json.loads(mp_path.read_text())
except Exception as e:  # noqa: BLE001
    sys.exit(f"cannot parse {mp_path}: {e}")

for field in ("name", "owner", "plugins"):
    if field not in mp:
        err(f"marketplace.json missing field {field!r}")

plugin_dirs = [d for d in sorted((ROOT / "skills").iterdir()) if d.is_dir()]
for pdir in plugin_dirs:
    name = pdir.name
    pj_path = pdir / ".claude-plugin" / "plugin.json"
    if not pj_path.exists():
        err(f"{name}: missing {pj_path.relative_to(ROOT)}")
        continue
    try:
        pj = json.loads(pj_path.read_text())
    except Exception as e:  # noqa: BLE001
        err(f"{name}: plugin.json invalid JSON: {e}")
        continue
    if pj.get("name") != name:
        err(f"{name}: plugin.json name is {pj.get('name')!r}")
    for field in REQUIRED_PLUGIN_FIELDS:
        if field not in pj:
            err(f"{name}: plugin.json missing field {field!r}")

    if not (pdir / "SKILL.md").exists():
        err(f"{name}: no SKILL.md at the skill/plugin root")

if errors:
    print("manifest check FAILED:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"manifest check OK ({len(plugin_dirs)} plugin(s))")
