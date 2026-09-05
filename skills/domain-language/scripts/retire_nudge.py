#!/usr/bin/env python3
"""PostToolUse hook: catch a name that left the domain model without being retired.

The failure this exists for is renaming. A term loses its name, the model is
saved, and the old word lives on in filenames, CSS classes, generated artifacts
and prose until someone happens to grep for it. `check_retired.py` catches that
in CI; this catches it one second after the edit, while the rename is still the
thing being worked on.

Compares the saved model against the version in git HEAD and reports every name,
synonym, context or entity that disappeared without landing in `retired`.

Exit 2 with the report on stderr so Claude Code feeds it back. Any other path
exits 0: this is a nudge, and a broken git or a missing parser must never stop
an edit.
"""
import json
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit(0)


def names(model):
    found = set()
    for term in model.get("terms") or []:
        if not isinstance(term, dict):
            continue
        if term.get("name"):
            found.add(str(term["name"]))
        for synonym in term.get("synonyms") or []:
            found.add(str(synonym))
    for section in ("contexts", "entities"):
        for item in model.get(section) or []:
            if isinstance(item, dict) and item.get("name"):
                found.add(str(item["name"]))
    return found


def head_version(path):
    real = os.path.realpath(path)
    repo = os.path.dirname(real) or "."
    try:
        top = subprocess.run(
            ["git", "-C", repo, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
        rel = os.path.relpath(real, os.path.realpath(top))
        blob = subprocess.run(
            ["git", "-C", top, "show", f"HEAD:{rel}"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError, ValueError):
        return None
    try:
        return yaml.safe_load(blob) or {}
    except yaml.YAMLError:
        return None


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith("model.yaml") or "domain" not in path.replace("\\", "/"):
        return 0
    if not os.path.exists(path):
        return 0

    before = head_version(path)
    if before is None:
        return 0
    try:
        with open(path, encoding="utf-8") as handle:
            after = yaml.safe_load(handle) or {}
    except (OSError, yaml.YAMLError):
        return 0

    retired = {
        str(entry.get("word", "")).lower()
        for entry in (after.get("retired") or [])
        if isinstance(entry, dict)
    }
    lost = sorted(n for n in names(before) - names(after) if n.lower() not in retired)
    if not lost:
        return 0

    print(
        "Names left the domain model without being retired: "
        + ", ".join(lost)
        + ".\nA name that is gone still lives in filenames, CSS classes, generated artifacts and "
        "prose. Add each one to `retired` with `use` and `because`, then run "
        "scripts/check_retired.py and sweep what it lists. If the name was only reshaped rather "
        "than dropped, ignore this.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
