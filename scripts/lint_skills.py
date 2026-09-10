#!/usr/bin/env python3
"""Lint every skills/*/SKILL.md against the house skill-quality rules.
Exits non-zero on any violation. (The rules are the skillsmith skill's own,
enforced marketplace-wide — see skills/skillsmith.)

Enforced rules:
- frontmatter `name` matches the skill directory name (the /command comes from
  the directory; a mismatch confuses users and tooling), 1-64 chars of
  [a-z0-9] with single hyphens (agentskills.io spec)
- `description` present, ≤ 1024 chars (agentskills.io spec cap, also the
  claude.ai skill-upload cap), containing "Use when …" trigger text — the
  description is a router; triggers live inside it
- no `when_to_use` frontmatter — it is a Claude-Code-only field that opencode
  (and every other flat-tree consumer) silently drops, so trigger text there
  is invisible to half this repo's consumers; fold it into `description`
- no angle brackets in `name`/`description` (injection surface — the text is
  inlined into consumers' system prompts)
- no TODO: markers left in any skill file (the scaffold stubs; the bare word
  "TODO" is legitimate content, e.g. "open items become a TODO list")
- SKILL.md under 500 lines (official guidance; split into reference files)
- SKILL.md never contains the literal bang-backtick shell-injection token —
  the loader executes that pattern at skill-load time, so a documentation
  example would self-trigger (sibling files are safe; only SKILL.md is scanned
  for injection)
- relative markdown links in SKILL.md resolve to files that exist
- evals/evals.json present with ≥ 3 cases (skill-creator format: skill_name
  matching the dir, each case with id/prompt/assertions) — a skill without
  evals is documentation for an imagined problem
- every skill has a row in the root README's catalog table

Frontmatter values must be single-line `key: value` pairs (multiline YAML
would silently break the char-budget checks, so it is rejected by omission).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAX_DESCRIPTION = 1024
MAX_LINES = 500
MIN_EVALS = 3
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
INJECTION_TOKEN = "!" + chr(96)  # bang-backtick, built so this file never contains it either

errors = []


def err(msg):
    errors.append(msg)


def unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    return {
        km.group(1): unquote(km.group(2).strip())
        for line in m.group(1).splitlines()
        if (km := re.match(r"([A-Za-z_-]+):\s*(.*)", line))
    }


def check_yaml_scalars(text, rel):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return
    for line in m.group(1).splitlines():
        km = re.match(r"([A-Za-z_-]+):\s*(.*)", line)
        if not km:
            continue
        key, raw = km.group(1), km.group(2).strip()
        if not raw or raw[0] in "'\"|>&*!":
            continue
        if ": " in raw or raw.endswith(":"):
            err(
                f"{rel}: {key} is an unquoted YAML scalar containing ': ' - a strict YAML "
                f"parser rejects it and installers skip the whole skill. Wrap the value in "
                f"single quotes."
            )


def check_skill(skill_dir: Path):
    md = skill_dir / "SKILL.md"
    rel = md.relative_to(ROOT)
    text = md.read_text()

    check_yaml_scalars(text, rel)

    fm = frontmatter(text)
    if fm is None:
        err(f"{rel}: no YAML frontmatter")
        return

    name = fm.get("name")
    if name != skill_dir.name:
        err(f"{rel}: frontmatter name {name!r} != directory name {skill_dir.name!r}")
    if name and (not NAME_RE.fullmatch(name) or len(name) > 64):
        err(f"{rel}: name must be 1-64 chars of [a-z0-9] with single hyphens (spec)")

    description = fm.get("description", "")
    if not description:
        err(f"{rel}: frontmatter missing description")
    elif len(description) > MAX_DESCRIPTION:
        err(f"{rel}: description is {len(description)} chars (max {MAX_DESCRIPTION}, spec + claude.ai cap)")
    elif "use when" not in description.lower():
        err(f"{rel}: description needs 'Use when …' trigger text (the description is the router)")

    if "when_to_use" in fm:
        err(f"{rel}: when_to_use is Claude-Code-only — opencode and the flat skills/ "
            f"consumers drop it; fold the trigger text into description")

    for key in ("name", "description"):
        if any(c in fm.get(key, "") for c in "<>"):
            err(f"{rel}: {key} contains angle brackets (injection surface; forbidden in frontmatter)")

    lines = text.count("\n") + 1
    if lines >= MAX_LINES:
        err(f"{rel}: {lines} lines (must stay under {MAX_LINES} — split into a reference file)")

    if INJECTION_TOKEN in text:
        err(f"{rel}: contains the literal bang-backtick injection token "
            f"(the loader executes it at skill-load time; document it in a sibling file)")

    # relative links must resolve — in SKILL.md and every sibling doc
    # (assets/ holds templates copied into OTHER repos, whose placeholder
    # links resolve at the destination; NNNN is a filename-pattern placeholder)
    for doc in sorted(skill_dir.rglob("*.md")):
        if "assets" in doc.relative_to(skill_dir).parts:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", doc.read_text()):
            if re.match(r"[a-z]+:", target) or target.startswith("#") or "NNNN" in target:
                continue  # absolute URL, in-page anchor, or placeholder
            if not (doc.parent / target.split("#")[0]).exists():
                err(f"{doc.relative_to(ROOT)}: broken relative link ({target})")

    for f in sorted(skill_dir.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts and "TODO:" in f.read_text(errors="ignore"):
            err(f"{f.relative_to(ROOT)}: contains a TODO: marker")

    check_evals(skill_dir)


def check_evals(skill_dir: Path):
    evals_json = skill_dir / "evals" / "evals.json"
    rel = evals_json.relative_to(ROOT)
    if not evals_json.exists():
        err(f"{skill_dir.relative_to(ROOT)}: missing evals/evals.json (≥ {MIN_EVALS} cases required)")
        return
    try:
        data = json.loads(evals_json.read_text())
    except json.JSONDecodeError as exc:
        err(f"{rel}: invalid JSON — {exc}")
        return
    if data.get("skill_name") != skill_dir.name:
        err(f"{rel}: skill_name {data.get('skill_name')!r} != {skill_dir.name!r}")
    cases = data.get("evals")
    if not isinstance(cases, list) or len(cases) < MIN_EVALS:
        err(f"{rel}: needs an evals[] array with ≥ {MIN_EVALS} cases")
        return
    for i, case in enumerate(cases):
        missing = {"id", "prompt", "assertions"} - set(case)
        if missing:
            err(f"{rel}: evals[{i}] missing {', '.join(sorted(missing))}")


def main():
    skill_dirs = [
        d for d in sorted((ROOT / "skills").iterdir()) if (d / "SKILL.md").exists()
    ]
    if not skill_dirs:
        sys.exit("no skills found under skills/")
    for d in skill_dirs:
        check_skill(d)

    readme = (ROOT / "README.md").read_text()
    for d in skill_dirs:
        if d.name not in readme:
            err(f"README.md: no catalog entry for {d.name} (every skill gets a row in the Skills table)")

    if errors:
        print("skill lint FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"skill lint OK ({len(skill_dirs)} skill(s))")


if __name__ == "__main__":
    main()
