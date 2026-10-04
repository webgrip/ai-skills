#!/usr/bin/env python3
"""Scaffold a new skill (as its own plugin) in this monorepo.

Usage:
    python scripts/new_skill.py my-skill-name "One-line description of the skill."
    python scripts/new_skill.py my-skill-name "..." --allow-published-name

Before scaffolding, the name is looked up on the skills.sh registry: a slug
another publisher already uses means two same-named skills on any machine
that installs both, and plugin slugs are immutable once published, so a
clash found later costs a rename mid-build. An exact match stops the
scaffold unless --allow-published-name is passed; an unreachable registry
only warns.

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

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import sync_marketplace

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_SEARCH = "https://skills.sh/api/search?q={}&limit=50"


def published_twins(name: str) -> list[str] | None:
    url = REGISTRY_SEARCH.format(urllib.parse.quote(name))
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            found = json.load(response).get("skills", [])
    except (OSError, ValueError):
        return None
    return [
        f"{entry.get('source')} ({entry.get('installs', 0)} installs)"
        for entry in found
        if entry.get("name") == name
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name")
    parser.add_argument("description")
    parser.add_argument("--allow-published-name", action="store_true")
    args = parser.parse_args()
    name, description = args.name, args.description
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        sys.exit("name must be lowercase-with-hyphens, e.g. spec-review")

    skill = ROOT / "skills" / name
    if skill.exists():
        sys.exit(f"skills/{name} already exists")

    twins = published_twins(name)
    if twins is None:
        print(f"warning: skills.sh unreachable; check the name by hand: npx skills find {name}")
    elif twins and not args.allow_published_name:
        sys.exit(f"'{name}' is already published by: {'; '.join(twins)}\n"
                 "pick a distinct name (slugs are immutable once published), "
                 "or pass --allow-published-name")

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
