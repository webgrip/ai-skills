#!/usr/bin/env python3
"""Fail when a retired word from the domain model still appears in the tree.

Renaming rots a repo through the places nobody greps: filenames, CSS classes,
generated artifacts, log strings, prose in docs. This turns the model's
`retired` list into the cleanup list, so the sweep is enumerable instead of
remembered.

Exit 0 when clean, 1 when occurrences remain, 2 on a usage error.

The model file itself is always exempt: a list that forbids a word has to
contain it. Everything the doc generator renders from that list is exempt for
the same reason, so pass the generated docs directory with --exempt.
"""
import argparse
import os
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    print("check_retired: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

TEXT_SUFFIXES = {
    ".md", ".mdx", ".yaml", ".yml", ".json", ".ts", ".tsx", ".js", ".jsx", ".mjs",
    ".cjs", ".astro", ".vue", ".svelte", ".html", ".css", ".scss", ".py", ".go",
    ".rs", ".php", ".rb", ".java", ".kt", ".sh", ".toml", ".txt",
}
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".astro", "vendor", "__pycache__", ".venv"}


def retired_words(model_path):
    with open(model_path, encoding="utf-8") as handle:
        model = yaml.safe_load(handle) or {}
    entries = model.get("retired") or []
    words = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("word"):
            continue
        words.append((str(entry["word"]), str(entry.get("use") or "?")))
    return words


def tracked(root):
    """Files git knows about, or None when this is not a work tree.

    An ignored file is not part of the product, so scanning it reports words in
    scratch notes and local artifacts that never ship.
    """
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files", "-z"],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return None
    return [p for p in out.split("\0") if p]


def walk(root, exempt):
    listed = tracked(root)
    if listed is None:
        listed = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            listed.extend(
                os.path.relpath(os.path.join(dirpath, n), root) for n in filenames
            )
    for rel in listed:
        if any(rel == e or rel.startswith(e.rstrip("/") + os.sep) for e in exempt):
            continue
        if os.path.splitext(rel)[1].lower() not in TEXT_SUFFIXES:
            continue
        path = os.path.join(root, rel)
        if os.path.exists(path):
            yield rel, path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to scan")
    parser.add_argument("--model", default="docs/domain/model.yaml", help="path to the model, relative to root")
    parser.add_argument(
        "--exempt",
        action="append",
        default=[],
        help="path relative to root that may still carry retired words; repeatable",
    )
    args = parser.parse_args()

    model_rel = args.model
    model_path = os.path.join(args.root, model_rel)
    if not os.path.exists(model_path):
        print(f"check_retired: no model at {model_path}", file=sys.stderr)
        return 2

    words = retired_words(model_path)
    if not words:
        print("check_retired: the model declares no retired vocabulary")
        return 0

    exempt = [model_rel, *args.exempt]
    patterns = [(w, use, re.compile(rf"(?<![a-z]){re.escape(w)}", re.IGNORECASE)) for w, use, in words]

    findings = []
    for rel, path in walk(args.root, exempt):
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().split("\n")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            for word, use, pattern in patterns:
                if pattern.search(line):
                    findings.append((rel, number, word, use, line.strip()[:100]))

    if not findings:
        print(f"check_retired: {len(words)} retired word(s), 0 occurrences outside {model_rel}")
        return 0

    print(f"check_retired: {len(findings)} occurrence(s) of retired vocabulary\n", file=sys.stderr)
    for rel, number, word, use, snippet in findings:
        print(f"  {rel}:{number}  '{word}' is retired, use {use}", file=sys.stderr)
        print(f"      {snippet}", file=sys.stderr)
    print(
        "\nAdd an --exempt path for a decision register or planning note, or sweep the word.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
