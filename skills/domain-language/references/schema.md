# docs/domain/model.yaml — full schema

All sections except `project` are optional. Field names are lowercase. Names of terms/entities are case-sensitive and should be written in their canonical capitalization (usually Title Case for domain concepts).

```yaml
project: string            # required — project or product name
description: string        # optional — one-paragraph elevator pitch of the domain
version: string            # optional — bump when the language changes meaningfully

contexts:                  # optional — bounded contexts
  - name: string           # e.g. "Ordering", "Fulfillment"
    description: string    # what this subarea covers and why it's separate

retired:                   # optional — words that are gone from the product entirely
  - word: string           # required — the dead word, matched case-insensitively
    use: string            # required — the term that replaces it
    because: string        # required — why the constraint exists, in the present tense

terms:                     # the glossary
  - name: string           # canonical name (required)
    definition: string     # required — see SKILL.md for what makes a good one
    context: string        # optional — a contexts[].name; omit for project-wide terms
    synonyms: [string]     # acceptable alternates that map to this term
    avoid: [string]        # terms the team must NOT use for this concept
    examples: [string]     # optional concrete examples
    see_also: [string]     # related term names

entities:                  # domain objects with structure/lifecycle
  - name: string           # required; usually also appears in terms
    description: string    # short — the full definition belongs in terms
    context: string        # optional bounded context
    attributes:
      - name: string
        type: string       # freeform: "string", "Money", "enum(draft, placed, shipped)"
        description: string
        required: bool     # optional, default false
    states:                # lifecycle transitions; presence generates a state diagram
      - from: string       # state name; use "[start]" for the initial transition
        to: string
        trigger: string    # what causes the transition
    relationships:
      - to: string         # target entity name
        kind: string       # one of: has_one, has_many, belongs_to, references
        description: string

rules:                     # business rules / invariants
  - id: string             # required, stable — e.g. "R1"; specs cite these ids
    statement: string      # required — the rule, phrased in canonical terms
    rationale: string      # why the rule exists (worth its weight in gold later)
    applies_to: [string]   # entity or term names this constrains
    context: string        # optional bounded context

events:                    # domain events (things that happened)
  - name: string           # past tense by convention: "OrderPlaced"
    description: string
    entity: string         # optional — the entity it primarily concerns
    triggers: string       # optional — what the event causes downstream

ambiguities:               # unresolved naming conflicts / vague concepts — DELETE once decided
  - phrase: string         # required — the contested word or vague phrase
    issue: string          # required — what's ambiguous about it
    options: [string]      # candidate resolutions (canonical names, splits)
    recommendation: string # the opinionated pick, with a one-line reason
    status: string         # "open" (default) or "resolved"
    resolution: string     # required once status is resolved — what was decided

dialogues:                 # example exchanges showing precise term usage
  - title: string          # e.g. "Order vs Cart at checkout"
    context: string        # optional bounded context
    lines:
      - speaker: string    # e.g. "Dev", "Domain expert"
        text: string       # bold canonical terms with **Term** for emphasis
```

## Validation rules the generator enforces

- `terms[].name` and `entities[].name` must be unique within their section.
- `rules[].id` must be unique.
- References must resolve, or a warning is emitted: `context` values → `contexts[].name`; `see_also` → term names; `relationships[].to` → entity names; `rules[].applies_to` → entity or term names; `events[].entity` → entity names; `dialogues[].context` → `contexts[].name`.
- `ambiguities[]`: a `resolved` entry without a `resolution` gets a warning, as does an entry whose `phrase` matches a defined term name (resolve or rename it). `status` defaults to `open`.
- `states[].from`/`to` are free-form, but every state should appear in at least one transition on each side it's used (unreachable/dead-end states get warnings, except `[start]` sources and terminal states that only appear as `to`).

Warnings never block generation; they are printed to stderr so they can be relayed to the user.
