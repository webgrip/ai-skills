#!/usr/bin/env python3
"""Export a domain model YAML file to Context Mapper DSL (CML).

Usage:
    python generate_cml.py docs/domain/model.yaml -o docs/domain/model.cml

Mapping:
    contexts        -> ContextMap + one BoundedContext each (entities with no
                       context go into a BoundedContext named after the project)
    entities        -> one Aggregate per entity, entity as aggregateRoot
    attributes      -> typed attributes (common types mapped to CML/Sculptor
                       basic types; enum(...) becomes a CML enum; unknown types
                       fall back to String with the original kept in a comment)
    relationships   -> domain object references (- Target / - List<Target>)
    states          -> an enum marked aggregateLifecycle; transitions are kept
                       as comments (CML attaches transitions to operations,
                       which this model doesn't define)
    terms, rules    -> comment blocks, so no information is lost (CML has no
                       native glossary/rule construct)

The output opens in Context Mapper (VS Code / Eclipse plugin), unlocking its
PlantUML generators, architectural refactorings, and service decomposition
tooling. Validate the file there; this exporter aims for valid CML but cannot
run the Context Mapper validator itself.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml --break-system-packages")

BASIC_TYPES = {
    "string": "String", "str": "String", "text": "String", "uuid": "String",
    "int": "int", "integer": "int", "long": "long",
    "bool": "boolean", "boolean": "boolean",
    "float": "double", "double": "double",
    "decimal": "BigDecimal", "money": "BigDecimal", "currency": "BigDecimal",
    "date": "Date", "datetime": "DateTime", "timestamp": "Timestamp",
}


def ident(name):
    """CML identifier: strip anything that isn't a word character."""
    parts = re.split(r"[^A-Za-z0-9]+", str(name).strip())
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def attr_ident(name):
    i = ident(name)
    return i[:1].lower() + i[1:] if i else "value"


def const(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", str(name).strip()).upper()


def wrap_comment(text, indent=""):
    words, out, line = str(text).split(), [], indent + "// "
    for w in words:
        if len(line) + len(w) > 78:
            out.append(line.rstrip())
            line = indent + "// "
        line += w + " "
    out.append(line.rstrip())
    return out


def map_type(raw, entity_name, attr_name, enums):
    """Return (cml_type, trailing_comment_or_None). Registers enums as a side effect."""
    raw = str(raw or "String").strip()
    m = re.match(r"enum\((.*)\)$", raw)
    if m:
        enum_name = ident(entity_name) + ident(attr_name)
        values = [const(v) for v in m.group(1).split(",") if v.strip()]
        enums[enum_name] = (values, False)
        return enum_name, None
    if raw.lower() in BASIC_TYPES:
        return BASIC_TYPES[raw.lower()], None
    return "String", f"original type: {raw}"


def render_entity(e, entity_ctx, current_ctx, out, indent="        "):
    enums = {}
    name = ident(e.get("name"))
    body = []

    for a in e.get("attributes", []) or []:
        t, note = map_type(a.get("type"), e.get("name"), a.get("name"), enums)
        line = f"{indent}    {t} {attr_ident(a.get('name'))}"
        comments = [c for c in (str(a.get("description", "")).strip() or None, note) if c]
        if comments:
            line += "  // " + " — ".join(comments)
        body.append(line)

    for r in e.get("relationships", []) or []:
        target = ident(r.get("to"))
        if r.get("to") not in entity_ctx:
            continue
        if entity_ctx[r.get("to")] != current_ctx:
            # Cross-context: reference by id, per aggregate design practice.
            tgt_ctx = entity_ctx[r.get("to")]
            ctx_note = "" if tgt_ctx == "__default__" else f" in context {tgt_ctx}"
            if r.get("kind") == "has_many":
                body.append(f"{indent}    List<String> {attr_ident(r.get('to'))}Ids  "
                            f"// has_many {target}{ctx_note}")
            else:
                body.append(f"{indent}    String {attr_ident(r.get('to'))}Id  "
                            f"// {r.get('kind', 'references')} {target}{ctx_note}")
        elif r.get("kind") == "has_many":
            body.append(f"{indent}    - List<{target}> {attr_ident(r.get('to'))}List")
        else:
            body.append(f"{indent}    - {target} {attr_ident(r.get('to'))}")

    states = e.get("states", []) or []
    state_names = []
    for s in states:
        for key in ("from", "to"):
            v = s.get(key)
            if v and v not in ("[start]", "[end]") and const(v) not in state_names:
                state_names.append(const(v))
    if state_names:
        # If an existing enum (e.g. a status attribute) has the same values,
        # mark that one as the lifecycle instead of emitting a duplicate.
        for enum_name, (values, _) in enums.items():
            if set(values) == set(state_names):
                enums[enum_name] = (values, True)
                break
        else:
            enums[name + "Lifecycle"] = (state_names, True)

    if e.get("description"):
        out.extend(wrap_comment(e["description"], indent))
    out.append(f"{indent}Entity {name} {{")
    out.append(f"{indent}    aggregateRoot")
    out.extend(body)
    out.append(f"{indent}}}")

    for enum_name, (values, is_lifecycle) in enums.items():
        out.append(f"{indent}enum {enum_name} {{")
        if is_lifecycle:
            out.append(f"{indent}    aggregateLifecycle")
        out.append(f"{indent}    {', '.join(values)}")
        out.append(f"{indent}}}")
    if states:
        out.append(f"{indent}// Lifecycle transitions:")
        for s in states:
            frm = s.get("from") if s.get("from") != "[start]" else "(start)"
            trigger = str(s.get("trigger", "")).strip()
            out.append(f"{indent}//   {frm} -> {s.get('to')}" + (f" : {trigger}" if trigger else ""))


def generate(model):
    out = ["// Generated from model.yaml by the domain-language skill — do not edit by hand.",
           "// Open with Context Mapper (contextmapper.org) for diagrams and refactorings.", ""]

    project = model.get("project", "Domain")
    contexts = [c.get("name") for c in model.get("contexts", []) or []]
    entities = model.get("entities", []) or []
    entity_names = {e.get("name") for e in entities}
    default_ctx = ident(project) + ("Core" if contexts else "")

    by_ctx = {}
    entity_ctx = {}
    for e in entities:
        ctx = e.get("context") if e.get("context") in contexts else None
        by_ctx.setdefault(ctx or "__default__", []).append(e)
        entity_ctx[e.get("name")] = ctx or "__default__"
    ctx_idents = [ident(c) for c in contexts]
    if "__default__" in by_ctx:
        ctx_idents.append(default_ctx)

    # Glossary as a comment block: CML has no native glossary construct.
    terms = model.get("terms", []) or []
    if terms:
        out.append("/* GLOSSARY (ubiquitous language)")
        for t in sorted(terms, key=lambda t: str(t.get("name", "")).lower()):
            out.append(f" * {t.get('name')}: {str(t.get('definition', '')).strip()}")
            if t.get("avoid"):
                out.append(f" *     (do not use: {', '.join(t['avoid'])})")
        out.append(" */")
        out.append("")

    rules = model.get("rules", []) or []
    if rules:
        out.append("/* BUSINESS RULES")
        for r in rules:
            out.append(f" * {r.get('id')}: {str(r.get('statement', '')).strip()}"
                       + (f" [{', '.join(r.get('applies_to', []))}]" if r.get("applies_to") else ""))
        out.append(" */")
        out.append("")

    if ctx_idents:
        out.append(f"ContextMap {ident(project)}Map {{")
        for c in ctx_idents:
            out.append(f"    contains {c}")
        out.append("}")
        out.append("")

    def emit_context(ctx_key, ctx_ident, description, ents):
        out.append(f"BoundedContext {ctx_ident} {{")
        if description:
            vision = str(description).strip().replace('"', "'")
            out.append(f'    domainVisionStatement "{vision}"')
        for e in ents:
            out.append(f"    Aggregate {ident(e.get('name'))}Aggregate {{")
            render_entity(e, entity_ctx, ctx_key, out)
            out.append("    }")
        out.append("}")
        out.append("")

    for c in model.get("contexts", []) or []:
        emit_context(c.get("name"), ident(c.get("name")), c.get("description"),
                     by_ctx.get(c.get("name"), []))
    if "__default__" in by_ctx:
        emit_context("__default__", default_ctx,
                     f"Entities of {project} not assigned to a bounded context.",
                     by_ctx["__default__"])

    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("model", help="Path to domain model YAML")
    ap.add_argument("-o", "--out", default="docs/domain/model.cml", help="Output .cml path")
    args = ap.parse_args()

    with open(args.model) as f:
        model = yaml.safe_load(f) or {}
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate(model))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
