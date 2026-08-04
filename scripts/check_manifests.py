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

# The bundle plugin: the repo root is itself a plugin, so installing it loads
# every skill namespaced <bundle>:<skill> — the prefix that lets this estate sit
# alongside another estate's same-named skills.
bundle_pj_path = ROOT / ".claude-plugin" / "plugin.json"
try:
    bundle_pj = json.loads(bundle_pj_path.read_text())
except Exception as e:  # noqa: BLE001
    bundle_pj = None
    err(f"bundle: cannot parse .claude-plugin/plugin.json: {e}")
if bundle_pj is not None:
    for field in REQUIRED_PLUGIN_FIELDS:
        if field not in bundle_pj:
            err(f"bundle: plugin.json missing field {field!r}")
    bundle_name = bundle_pj.get("name")
    if bundle_name and (ROOT / "skills" / bundle_name).exists():
        err(
            f"bundle: name {bundle_name!r} collides with skills/{bundle_name} — "
            "the catalog would carry two entries with that name"
        )

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

# Bundle hook coverage. A skill's hooks/hooks.json resolves ${CLAUDE_PLUGIN_ROOT}
# to the skill dir — correct for its own plugin, wrong under the bundle, where
# that root is the repo. So the bundle must re-declare every skill hook with a
# skills/<name>/ prefix, or installing the bundle ships the hooks silently dead.
CMD_ROOT = "${CLAUDE_PLUGIN_ROOT}/"


def hook_commands(hooks_json: Path) -> list:
    """Every command string in a hooks.json, across events and matchers."""
    try:
        data = json.loads(hooks_json.read_text())
    except Exception as e:  # noqa: BLE001
        err(f"{hooks_json.relative_to(ROOT)}: invalid JSON: {e}")
        return []
    return [
        h["command"]
        for matchers in data.get("hooks", {}).values()
        for entry in matchers
        for h in entry.get("hooks", [])
        if isinstance(h, dict) and "command" in h
    ]


bundle_hooks = ROOT / "hooks" / "hooks.json"
bundle_cmds = set(hook_commands(bundle_hooks)) if bundle_hooks.exists() else set()
for skill_hooks in sorted(ROOT.glob("skills/*/hooks/hooks.json")):
    sname = skill_hooks.parent.parent.name
    for cmd in hook_commands(skill_hooks):
        expected = cmd.replace(CMD_ROOT, f"{CMD_ROOT}skills/{sname}/", 1)
        if expected not in bundle_cmds:
            err(
                f"hooks/hooks.json: missing the {sname} hook — the bundle plugin "
                f"must re-declare it rooted at the repo: {expected}"
            )

if errors:
    print("manifest check FAILED:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"manifest check OK ({len(plugin_dirs)} plugin(s))")
