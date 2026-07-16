#!/usr/bin/env python3
"""Scaffold a new skill (as its own plugin) in this monorepo.

Usage:
    python scripts/new_skill.py my-skill-name "One-line description of the skill."

Creates (the skill directory IS the plugin — SKILL.md at the plugin root):
    skills/<name>/.claude-plugin/plugin.json    (the single source of truth)
    skills/<name>/SKILL.md                      (stub with frontmatter)
    skills/<name>/README.md                     (stub)
    skills/<name>/evals/evals.json              (3 stub cases — lint requires ≥3)
and regenerates .claude-plugin/marketplace.json from the plugin manifests.

Then: write the SKILL.md and evals (the lint fails while TODOs remain), fill
in the README, and optionally add a test.sh for plugin-specific behavior —
generic quality rules are already enforced by scripts/lint_skills.py.
"""

import json
import re
import sys
from pathlib import Path

import sync_marketplace

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    name, description = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        sys.exit("name must be lowercase-with-hyphens, e.g. spec-review")

    skill = ROOT / "skills" / name
    if skill.exists():
        sys.exit(f"skills/{name} already exists")

    mp = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    owner = mp.get("owner", {})

    (skill / ".claude-plugin").mkdir(parents=True)
    (skill / "evals").mkdir()

    (skill / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": name,
        "displayName": name.replace("-", " ").title(),
        "description": description,
        "version": "0.1.0",
        "license": "MIT",
        "author": owner,
        "keywords": [],
    }, indent=2) + "\n")

    (skill / "SKILL.md").write_text(f"""---
name: {name}
description: {description} TODO: append 'Use when …' trigger phrases — this field is what makes the agent load the skill (and it must contain 'Use when').
---

# {name.replace('-', ' ').title()}

TODO: instructions the agent follows when this skill triggers.
""")

    (skill / "README.md").write_text(f"""# {name}

{description}

TODO: what the skill does, install instructions, example prompts.
""")

    (skill / "evals" / "evals.json").write_text(json.dumps({
        "skill_name": name,
        "_format": "skill-creator eval format — see https://agentskills.io/skill-creation/evaluating-skills",
        "evals": [
            {
                "id": f"case-{i}",
                "prompt": "TODO: a realistic user prompt that should trigger this skill",
                "assertions": ["TODO: an objective, verifiable assertion about the behavior"],
            }
            for i in (1, 2, 3)
        ],
    }, indent=2, ensure_ascii=False) + "\n")

    sync_marketplace.sync()

    print(f"scaffolded skills/{name} and regenerated marketplace.json")
    print("next: write the SKILL.md, evals, and README (lint fails while TODOs remain)")


if __name__ == "__main__":
    main()
