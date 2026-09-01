---
name: domain-language
description: Define, maintain, and publish a project's domain language (ubiquitous language) — the shared vocabulary of terms, entities, relationships, business rules, and events — and generate specs and documentation from it. Use when the user wants to build a glossary, define domain terms or concepts, model entities and their lifecycles, capture business rules, resolve naming ambiguity, write a feature spec grounded in domain vocabulary, generate domain documentation or diagrams, check the health/quality of a domain model, or audit a codebase/docs for inconsistent terminology. Trigger even if the user doesn't say "domain model" — phrases like "we keep calling this thing three different names", "grill me about my domain", "document our concepts", "define what an Order means here", "score our glossary", or "turn our terminology into docs" all apply.
---

# Domain Language — one vocabulary, one YAML file, generated docs

## The single source of truth

Everything lives in one YAML file in the user's project, by convention at `docs/domain/model.yaml` (respect an existing location if the project already has one). Docs are *generated* from it — never hand-edit generated docs; edit the model and regenerate.

The model has seven sections, all optional except `project`:

```yaml
project: Order Management
contexts:      # bounded contexts — subareas where words may mean different things
terms:         # the glossary: names, definitions, synonyms, terms to avoid
entities:      # domain objects: attributes, lifecycle states, relationships
rules:         # business rules / invariants, with rationale
events:        # domain events: what happened, what it triggers
ambiguities:   # open naming conflicts and vague concepts, with recommendations
dialogues:     # short example exchanges showing terms used precisely
```

Read `references/schema.md` for the full schema with all fields before writing or editing a model file. A complete worked example lives at `assets/example-model.yaml` — skim it when starting a model from scratch so the shape is fresh in mind.

## Workflows

Figure out which of these the user needs; they often chain together (grill → generate → health check → spec).

### 1. Bootstrap or sharpen the model by grilling

Extract the language the team hasn't articulated yet — a grilling session, not form-filling.

**Gather raw material first.** Scan whatever is available — the current conversation, code (entity/model/type definitions, database schemas, API routes), READMEs, wikis, specs. Collect candidate terms: domain-relevant nouns and verbs, not generic programming concepts (skip "array", "endpoint") unless they carry domain meaning. Code often contains legacy names the team wants to kill, so never assume code naming is the desired language.

**Then grill, in short rounds.** Ask 2–3 pointed questions at a time, never a wall of them. Rotate through these attack angles until the answers stop changing the model:

- **Collision hunting**: the same word used for two concepts ("does 'account' mean the Customer or the login identity?") and different words for one concept ("you've said Basket, Cart, and Bag — are those one thing?").
- **Boundary probing**: for each pair of neighboring terms, ask what distinguishes them and when one becomes the other ("what exactly turns a Cart into an Order?").
- **Edge-case stress tests**: pick a lifecycle or rule and push on it ("what happens to a Shipment if its Order is cancelled mid-transit?", "can an Order have zero line items, even transiently?"). These questions surface states, rules, and events the user didn't know they knew.
- **Vagueness attacks**: when the user says "the thing that tracks status" or an overloaded word like "job" or "process", stop and name it properly.

**Be opinionated.** When multiple words exist for one concept, propose the best canonical name yourself with a one-line reason, and demote the rest to `synonyms` or `avoid`. They can overrule.

**Record what isn't settled.** When the user can't resolve a collision on the spot, don't force it: add an `ambiguities` entry with the options and your recommendation, and move on. Open ambiguities render prominently in the generated docs so they can't be quietly forgotten.

Write the confirmed result to `docs/domain/model.yaml`. Start small — 5–15 well-defined terms beat 60 vague ones. Also capture one or two `dialogues`: short (3–5 exchange) dev/domain-expert conversations demonstrating boundary cases between related terms. These teach new readers faster than definitions alone.

### 2. Add or change language

When the user defines a new term, renames something, or refines a definition: edit `docs/domain/model.yaml`, then check consistency (below), then offer to regenerate docs so nothing drifts.

**Writing good definitions.** A definition should let a new team member use the term correctly. State what the thing *is* (not what it does), what distinguishes it from neighbors, and when it applies. One to two sentences; if it needs more, the concept probably needs splitting.

- Weak: `Order: A customer's order.`
- Strong: `Order: A confirmed request by a Customer to purchase one or more Products at agreed prices. Distinct from a Cart, which is uncommitted and has no Order Number.`

**Consistency checks** to run mentally on every edit:
- Two names for one concept → pick one canonical name, demote the other to `synonyms` or `avoid`.
- One name for two concepts → split them, scope each with a bounded `context`, or file an ambiguity.
- A term used in a definition, rule, or spec that isn't itself defined → add it or flag it.
- Renames → grep the model (and, if asked, the docs/codebase) for the old name.
- An ambiguity that this edit resolves → mark it `resolved` with a `resolution`.

### 3. Generate documentation

Run the bundled generator — do not hand-write these docs:

```bash
python scripts/generate_docs.py docs/domain/model.yaml -o docs/domain/
```

It produces `overview.md` (context map, Mermaid ER diagram, and any **open ambiguities** front and center), `glossary.md` (alphabetized, cross-referenced, with example dialogues and a flagged-ambiguities section), `entities.md` (attribute tables, relationships, Mermaid state diagrams for lifecycles), and `rules.md` (rules grouped by entity, with rationale). It also validates the model and prints warnings for dangling references — surface those warnings to the user and offer to fix them.

If the user wants a Word/PDF deliverable of these docs, generate the markdown first, then use the docx/pdf skill to convert.

**Context Mapper export.** When the user wants standard DDD notation, diagrams beyond Mermaid, or Context Mapper's toolchain (PlantUML generation, architectural refactorings, service decomposition):

```bash
python scripts/generate_cml.py docs/domain/model.yaml -o docs/domain/model.cml
```

This maps contexts → BoundedContexts, entities → Aggregates with typed attributes and lifecycle enums, same-context relationships → object references, and cross-context relationships → id references (per aggregate design practice). Glossary terms and rules are preserved as comment blocks since CML has no native construct for them. Tell the user to open the .cml in the Context Mapper VS Code/Eclipse plugin and validate there — the exporter targets valid CML but can't run Context Mapper's own validator.

### 4. Check model health (0–10 score)

Run the health checker whenever the user asks how good their model is, after any substantial editing session, and before generating a formal deliverable:

```bash
python scripts/health_check.py docs/domain/model.yaml
```

It scores five dimensions worth 2 points each — coverage, definition quality, structure, rules & rationale, hygiene — and prints a 0–10 total with the specific findings that cost points. The script measures what's objectively measurable (definition length and circularity, missing rationale, dangling references, open ambiguities, entities without lifecycles). Present the scorecard, then add the judgment a script can't: read a sample of definitions and say whether they'd actually let a newcomer use the term correctly, whether the bounded contexts are pulling their weight, and whether the rules capture the invariants that matter. Finish with the two or three fixes that would raise the score most, and offer to make them. Don't chase 10/10 on a young model — a 6 with honest open ambiguities beats a 9 achieved by deleting the hard questions.

### 5. Write a spec in the domain language

Use `assets/spec-template.md` as the skeleton for feature specs. The rules that make a spec worth reading:

- Use canonical terms exactly as defined in the model — capitalize them as glossary terms are capitalized, and never use a term listed under `avoid`.
- Reference business rules by id (e.g., "must satisfy **R3**") instead of restating them, so a rule change doesn't invalidate every spec.
- If the spec needs a concept the model lacks, stop and add it to the model first (with the user), then continue the spec. The spec should never be the only place a term is defined.
- If the spec touches an open ambiguity, resolving that ambiguity is part of the spec work — a spec built on an unresolved term is built on sand.
- End the spec with the auto-generated "Language used" section listing every glossary term referenced, so reviewers can spot undefined vocabulary at a glance.

### 6. Audit terminology

When asked to check a codebase, docs, or a document against the model: search for `avoid`-listed terms and non-canonical synonyms, report each finding with file/location and the canonical replacement, and note any prominent code concepts absent from the model (candidates to add). Present findings as a short report; only make replacements when explicitly asked, since renames in code can be breaking.

## Keeping it healthy

- Keep the model in version control alongside the code; suggest regenerating docs in the same commit that changes the model.
- Definitions in the model are prose for humans; the structure (attributes, states, relationships) is for generation and consistency. Don't cram structure into prose or prose into structure.
- Bounded contexts are the escape hatch for genuine ambiguity: if Sales and Support legitimately mean different things by "Ticket", define it twice with different `context` values rather than forcing a mushy shared definition.
- Ambiguities are working memory, not a graveyard: revisit open ones at the start of each grilling session.
