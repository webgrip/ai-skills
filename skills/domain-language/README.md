# domain-language

A Claude skill for building and maintaining a project's **ubiquitous language** — one agreed vocabulary, kept in a single structured YAML file, from which all documentation and specs are generated.

Define your domain once in `docs/domain/model.yaml`:

```yaml
project: Order Management
contexts:      # bounded contexts
terms:         # glossary: definitions, synonyms, terms to avoid
entities:      # attributes, lifecycle states, relationships
rules:         # business rules with ids and rationale
events:        # domain events
ambiguities:   # open naming conflicts, with recommendations
dialogues:     # example exchanges showing precise term usage
```

…and Claude plus the bundled scripts turn it into everything else:

- **Documentation** — glossary, entity reference with attribute tables, business rules with rationale, plus Mermaid ER and state diagrams (`scripts/generate_docs.py`)
- **Context Mapper export** — a `.cml` file mapping contexts → BoundedContexts and entities → Aggregates, unlocking [Context Mapper](https://contextmapper.org)'s PlantUML generators and refactorings (`scripts/generate_cml.py`)
- **Health score** — an objective 0–10 scorecard across coverage, definition quality, structure, rules, and hygiene, with the findings that cost points (`scripts/health_check.py`)
- **Feature specs** — written in the canonical vocabulary, citing rules by id, refusing to build on unresolved terms (`assets/spec-template.md`)
- **Grilling sessions** — Claude interviews you with collision hunting, boundary probing, and edge-case stress tests to extract language your team hasn't articulated yet
- **Terminology audits** — find forbidden and non-canonical terms in code and docs

Everything generated is plain markdown/CML in your repo. No lock-in: the model file is the asset; the tooling is replaceable.

## Install

**Claude Code (as a plugin, recommended):**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills.git
/plugin install domain-language@webgrip-ai-skills
```

**Claude Code (manual):** copy `skills/domain-language/` into your project's `.claude/skills/` (shared with your team via git) or `~/.claude/skills/` (just you).

**Claude app / claude.ai:** grab `domain-language.skill` from the [latest release](https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills/releases/latest), upload it via Settings → Skills (or attach it in a chat), and hit *Save skill*.

The bundled scripts require Python 3 with PyYAML (`pip install pyyaml`).

## Use

Open Claude in a project and say, for example:

- *"grill me about my domain"* / *"bootstrap a domain model from this codebase"*
- *"add Invoice to the domain model"*
- *"regenerate the domain docs"* → `docs/domain/`
- *"check our domain model health"*
- *"export the domain model to CML"*
- *"write a spec for split shipments in our domain language"*
- *"audit the codebase against the glossary"*

Commit `docs/domain/model.yaml` and the regenerated `docs/domain/` in the same change so they never drift. See `skills/domain-language/references/schema.md` for the full model schema and `assets/example-model.yaml` for a complete worked example.

## Why

When the same word means the same thing in conversation, code, and docs, misunderstandings and rework drop — for humans and for AI agents, which otherwise re-derive your jargon every session. Existing tools cover parts of this (prose glossary extraction, DDD coaching, spec-to-code pipelines); this skill covers the middle: a machine-readable single source of truth with deterministic generation, validation of dangling references, and rules that specs can cite by id.

Pairs well with [Laravel Boost](https://laravel.com/docs/boost) (framework knowledge vs. this skill's business vocabulary), [OpenSpec](https://github.com/Fission-AI/OpenSpec) or [Spec Kit](https://github.com/github/spec-kit) (their specs get written in your model's vocabulary), and [Context Mapper](https://contextmapper.org) via the CML export.

## Prior art & credits

Ideas gratefully borrowed from:

- [mattpocock/skills](https://github.com/mattpocock/skills) — the interview-driven approach to glossary extraction (collision hunting, example dialogues)
- the DDD community's model-health scoring and bounded-context discipline, per Eric Evans' and Vaughn Vernon's books
- [Context Mapper](https://contextmapper.org) — the CML notation this skill exports to

## Contributing

Issues and PRs welcome. Before submitting: run the smoke tests locally (`bash test.sh` from this directory — CI runs the same script via `.forgejo/workflows/ci.yml`), and if you change the schema, update `references/schema.md`, the example model, and all three generators together. Use a release-triggering conventional commit (`fix(domain-language): ...`) — the release pipeline bumps the version and rebuilds the dist zip automatically.

## License

MIT
