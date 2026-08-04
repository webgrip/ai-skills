#!/usr/bin/env python3
"""Regenerate .claude-plugin/marketplace.json from skills/*/.claude-plugin/plugin.json.

Each skill directory IS its plugin (SKILL.md at the plugin root, manifest in
.claude-plugin/). Each plugin.json is the single source of truth for its
plugin's metadata; the marketplace catalog is derived from them (entries
sorted by name, top-level name/owner/metadata preserved). Never edit the
plugins[] array by hand.

Usage:
    python3 scripts/sync_marketplace.py            # rewrite marketplace.json
    python3 scripts/sync_marketplace.py --check    # exit non-zero on drift (CI)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
ENTRY_FIELDS = ("description", "version", "license", "keywords")


def entry_from(pj_path: Path, source: str) -> dict:
    pj = json.loads(pj_path.read_text())
    missing = [f for f in ("name", *ENTRY_FIELDS) if f not in pj]
    if missing:
        sys.exit(f"{pj_path.relative_to(ROOT)}: missing field(s) {', '.join(missing)}")
    entry = {"name": pj["name"], "source": source}
    entry.update({f: pj[f] for f in ENTRY_FIELDS})
    return entry


def render() -> str:
    mp = json.loads(MARKETPLACE.read_text())
    # The repo root is itself a plugin — the bundle. It ships every skill
    # namespaced <bundle>:<skill>, which is what lets this estate sit alongside
    # another estate's same-named skills. It leads the catalog; the per-skill
    # plugins follow, for consumers who want a minimal surface instead.
    entries = [entry_from(ROOT / ".claude-plugin" / "plugin.json", "./")]
    for pdir in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        entries.append(entry_from(pdir / ".claude-plugin" / "plugin.json", f"./skills/{pdir.name}"))
    mp["plugins"] = entries
    return json.dumps(mp, indent=2, ensure_ascii=False) + "\n"


def sync(check: bool = False) -> None:
    rendered = render()
    if rendered == MARKETPLACE.read_text():
        print(f"marketplace.json in sync ({len(json.loads(rendered)['plugins'])} plugin(s))")
        return
    if check:
        sys.exit(
            "marketplace.json is out of sync with skills/*/.claude-plugin/plugin.json — "
            "run scripts/sync_marketplace.py and commit the result"
        )
    MARKETPLACE.write_text(rendered)
    print("marketplace.json regenerated")


if __name__ == "__main__":
    sync(check="--check" in sys.argv[1:])
