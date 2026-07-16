#!/usr/bin/env python3
"""Validate the opencode/ config estate against the NATIVE v2 shape
(pinned 0.0.0-next-15495). This is the beta-churn tripwire: it hard-fails on
v1-era keys so a stale merge or a careless edit can't silently regress the
estate. Stdlib-only, mirrors the other check_* scripts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []

V1_KEYS = {"provider", "permission", "plugin", "small_model", "command", "agent"}
EFFECTS = {"allow", "ask", "deny"}


def load(path: Path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:  # noqa: PERF203
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON — {exc}")
        return None


def check_rules(rules, where: str) -> None:
    if not isinstance(rules, list):
        errors.append(f"{where}: permissions must be an ORDERED LIST of rules (v2)")
        return
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict) or set(rule) != {"action", "resource", "effect"}:
            errors.append(f"{where}: permissions[{i}] must be exactly {{action, resource, effect}}")
            continue
        if rule["effect"] not in EFFECTS:
            errors.append(f"{where}: permissions[{i}] effect {rule['effect']!r} not in {sorted(EFFECTS)}")
    # Floor assertion: sops-edit and sudo-shell denies must exist and sit AFTER
    # the last allow that could re-open them (last match wins).
    def last_index(pred):
        idx = -1
        for i, r in enumerate(rules):
            if isinstance(r, dict) and pred(r):
                idx = i
        return idx

    floor_checks = [
        ("edit", "**/*.sops.yaml"),
        ("shell", "sudo *"),
    ]
    for action, resource in floor_checks:
        deny_i = last_index(lambda r: r.get("action") == action and r.get("resource") == resource and r.get("effect") == "deny")
        if deny_i < 0:
            errors.append(f"{where}: missing floor rule {action}/{resource}/deny")
            continue
        open_i = last_index(lambda r: r.get("effect") == "allow" and r.get("action") in (action, "*"))
        if open_i > deny_i:
            errors.append(
                f"{where}: an allow rule at index {open_i} comes AFTER the {action} floor deny "
                f"(index {deny_i}) — last match wins, the floor is broken"
            )


def check_no_v1(data: dict, where: str) -> None:
    dead = V1_KEYS & set(data)
    if dead:
        errors.append(f"{where}: v1-era key(s) {sorted(dead)} — this estate is native v2")
    mcp = data.get("mcp")
    if isinstance(mcp, dict) and "servers" not in mcp:
        errors.append(f"{where}: mcp must nest under mcp.servers (v2 shape)")


org_path = ROOT / "opencode" / "org.opencode.json"
org = load(org_path)
if org is not None:
    where = "opencode/org.opencode.json"
    for key in ("providers", "model", "permissions", "instructions"):
        if key not in org:
            errors.append(f"{where}: missing required key '{key}'")
    check_no_v1(org, where)
    if "permissions" in org:
        check_rules(org["permissions"], where)
    if "__WEBGRIP_SKILLS_HOME__" not in json.dumps(org.get("instructions", [])):
        errors.append(
            f"{where}: instructions must reference __WEBGRIP_SKILLS_HOME__ "
            "(the bootstrap substitutes the clone path)"
        )

for profile in sorted((ROOT / "opencode" / "profiles").glob("*.json")):
    data = load(profile)
    if data is None:
        continue
    where = str(profile.relative_to(ROOT))
    unexpected = set(data) - {"permissions", "agents", "_comment"}
    if unexpected:
        errors.append(f"{where}: unexpected top-level keys {sorted(unexpected)} (profiles overlay permissions/agents only)")
    check_no_v1(data, where)
    if "permissions" in data:
        check_rules(data["permissions"], where)

for agent in sorted((ROOT / "opencode" / "agents").glob("*.md")):
    where = str(agent.relative_to(ROOT))
    text = agent.read_text()
    if not text.startswith("---\n") or text.count("---\n") < 2:
        errors.append(f"{where}: missing YAML frontmatter")
        continue
    fm = text.split("---\n")[1]
    if "description:" not in fm:
        errors.append(f"{where}: frontmatter lacks 'description:'")
    for v1_field in ("permission:", "prompt:", "maxSteps:", "tools:"):
        if any(line.startswith(v1_field) for line in fm.splitlines()):
            errors.append(f"{where}: v1 frontmatter field '{v1_field.rstrip(':')}' — use the v2 names (permissions/system/steps)")

if errors:
    for err in errors:
        print(f"FAIL: {err}", file=sys.stderr)
    sys.exit(1)
print("opencode config OK (native v2: org + profiles + agents)")
