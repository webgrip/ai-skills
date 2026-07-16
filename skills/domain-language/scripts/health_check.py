#!/usr/bin/env python3
"""Score a domain model's health 0-10 and list what costs points.

Usage:
    python health_check.py docs/domain/model.yaml

Five dimensions, 2 points each:
  Coverage            - entities are also glossary terms; contexts are used
  Definition quality  - definitions exist, aren't circular, aren't one-liners
                        like "A customer's order", aren't essays
  Structure           - entities carry attributes/relationships; stateful
                        entities have lifecycles
  Rules & rationale   - rules exist, have rationale, and are anchored to
                        entities/terms
  Hygiene             - no dangling references, duplicates, stale ambiguities

The script measures only what's objectively measurable. A human (or Claude)
should add judgment on top: do the definitions actually teach the concept,
are the contexts pulling their weight, do the rules capture what matters.
Exit code is always 0; the score is information, not a gate (pipe to a CI
threshold yourself if you want one).
"""

import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml --break-system-packages")


def frac_score(good, total, points=2.0):
    """Scale a pass fraction to points; empty sections score 0."""
    if total == 0:
        return 0.0
    return round(points * good / total, 2)


def is_circular(name, definition):
    """Definition adds nothing beyond the term itself, e.g. 'Order: the customer's order.'"""
    words = re.findall(r"[a-z]+", definition.lower())
    name_words = set(re.findall(r"[a-z]+", name.lower()))
    content = [w for w in words if w not in name_words and w not in {
        "a", "an", "the", "of", "for", "to", "is", "are", "s"}]
    return len(content) < 4


def check(model):
    findings = {k: [] for k in ("coverage", "definitions", "structure", "rules", "hygiene")}
    scores = {}

    contexts = {c.get("name") for c in model.get("contexts", []) or []}
    terms = model.get("terms", []) or []
    entities = model.get("entities", []) or []
    rules = model.get("rules", []) or []
    ambiguities = model.get("ambiguities", []) or []
    term_names = {t.get("name") for t in terms}
    entity_names = {e.get("name") for e in entities}
    known = term_names | entity_names

    # ---- Coverage (2 pts): entities defined as terms; declared contexts used
    checks_pass, checks_total = 0, 0
    for e in entities:
        checks_total += 1
        if e.get("name") in term_names:
            checks_pass += 1
        else:
            findings["coverage"].append(f"entity '{e.get('name')}' has no glossary definition in terms")
    used_ctx = {x.get("context") for x in terms + entities + rules if x.get("context")}
    for c in contexts:
        checks_total += 1
        if c in used_ctx:
            checks_pass += 1
        else:
            findings["coverage"].append(f"context '{c}' is declared but nothing is assigned to it")
    if not terms:
        findings["coverage"].append("no terms defined — the glossary is the heart of the model")
        checks_total = max(checks_total, 1)
    scores["coverage"] = frac_score(checks_pass, checks_total)

    # ---- Definition quality (2 pts)
    good, total = 0, 0
    for t in terms:
        total += 1
        name, d = t.get("name", ""), str(t.get("definition", "") or "").strip()
        if not d:
            findings["definitions"].append(f"'{name}' has no definition")
        elif is_circular(name, d):
            findings["definitions"].append(f"'{name}' definition is circular/empty: \"{d[:60]}\"")
        elif len(d) < 40:
            findings["definitions"].append(f"'{name}' definition is too thin to teach the concept ({len(d)} chars)")
        elif len(d) > 600:
            findings["definitions"].append(f"'{name}' definition is an essay ({len(d)} chars) — split the concept?")
        else:
            good += 1
    scores["definitions"] = frac_score(good, total)

    # ---- Structure (2 pts): entities have substance; enum-status entities have lifecycles
    good, total = 0, 0
    for e in entities:
        total += 1
        has_body = bool(e.get("attributes") or e.get("relationships"))
        needs_lifecycle = any("enum(" in str(a.get("type", "")) and "status" in str(a.get("name", "")).lower()
                              for a in e.get("attributes", []) or [])
        if not has_body:
            findings["structure"].append(f"entity '{e.get('name')}' has no attributes or relationships")
        elif needs_lifecycle and not e.get("states"):
            findings["structure"].append(f"entity '{e.get('name')}' has a status enum but no lifecycle states")
        else:
            good += 1
    scores["structure"] = frac_score(good, total)

    # ---- Rules & rationale (2 pts)
    good, total = 0, 0
    for r in rules:
        total += 1
        rid = r.get("id", "?")
        if not str(r.get("statement", "") or "").strip():
            findings["rules"].append(f"rule {rid} has no statement")
        elif not str(r.get("rationale", "") or "").strip():
            findings["rules"].append(f"rule {rid} has no rationale — future readers won't know why it exists")
        elif not r.get("applies_to"):
            findings["rules"].append(f"rule {rid} is anchored to nothing (applies_to is empty)")
        else:
            good += 1
    if not rules:
        findings["rules"].append("no business rules captured — every domain has invariants worth writing down")
        total = 1
    scores["rules"] = frac_score(good, total)

    # ---- Hygiene (2 pts): start at 2, subtract 0.25 per issue
    issues = 0

    def hygiene(msg):
        nonlocal issues
        issues += 1
        findings["hygiene"].append(msg)

    for label, names in (("term", [t.get("name") for t in terms]),
                         ("entity", [e.get("name") for e in entities]),
                         ("rule id", [r.get("id") for r in rules])):
        seen = set()
        for n in names:
            if n in seen:
                hygiene(f"duplicate {label}: '{n}'")
            seen.add(n)
    for t in terms:
        if t.get("context") and t["context"] not in contexts:
            hygiene(f"term '{t.get('name')}' references unknown context '{t['context']}'")
        for ref in t.get("see_also", []) or []:
            if ref not in term_names:
                hygiene(f"term '{t.get('name')}' see_also -> unknown term '{ref}'")
    for e in entities:
        for rel in e.get("relationships", []) or []:
            if rel.get("to") not in entity_names:
                hygiene(f"entity '{e.get('name')}' relationship -> unknown entity '{rel.get('to')}'")
    for r in rules:
        for target in r.get("applies_to", []) or []:
            if target not in known:
                hygiene(f"rule {r.get('id')} applies_to unknown '{target}'")
    for ev in model.get("events", []) or []:
        if ev.get("entity") and ev["entity"] not in entity_names:
            hygiene(f"event '{ev.get('name')}' -> unknown entity '{ev['entity']}'")
    for a in ambiguities:
        if a.get("status") == "resolved" and not a.get("resolution"):
            hygiene(f"ambiguity '{a.get('phrase')}' marked resolved without resolution text")
    n_open = sum(1 for a in ambiguities if a.get("status", "open") == "open")
    if n_open > 3:
        hygiene(f"{n_open} open ambiguities — schedule a grilling session to burn them down")
    scores["hygiene"] = round(max(0.0, 2.0 - 0.25 * issues), 2)

    return scores, findings, n_open


LABELS = {
    "coverage": "Coverage",
    "definitions": "Definition quality",
    "structure": "Structure",
    "rules": "Rules & rationale",
    "hygiene": "Hygiene",
}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1]) as f:
        model = yaml.safe_load(f) or {}

    scores, findings, n_open = check(model)
    total = round(sum(scores.values()), 1)

    print(f"Domain model health: {total}/10  ({model.get('project', 'unnamed project')})")
    print()
    for key, label in LABELS.items():
        print(f"  {label:<20} {scores[key]:>4}/2")
        for msg in findings[key]:
            print(f"      - {msg}")
    print()
    counts = {s: len(model.get(s, []) or []) for s in
              ("contexts", "terms", "entities", "rules", "events", "dialogues")}
    summary = ", ".join(f"{v} {k}" for k, v in counts.items() if v)
    print(f"  Contents: {summary or 'empty model'}"
          + (f"; {n_open} open ambiguit{'y' if n_open == 1 else 'ies'}" if n_open else ""))
    if total < 10:
        print("  Note: score reflects measurable structure only — pair it with a")
        print("  qualitative read of whether definitions actually teach the concepts.")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
