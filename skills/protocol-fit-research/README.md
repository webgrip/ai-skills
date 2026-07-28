# protocol-fit-research

A skill for answering **"does this protocol matter to us?"** — the question that arrives every time a new agent standard, spec, or competing product shows up. It turns a landscape question into a parallel research fan-out and a verdict-led report, then lands that verdict in the repo's own survey docs so it is never re-litigated from scratch.

What it teaches the agent:

- **Scope triage** — a single-fact lookup gets one fetch; "does X matter to *us*" gets the full sweep
- **A four-angle fan-out** — spec crawl, source-repo dig, ecosystem/adoption with explicit absence checks, and a local seam map, all launched in parallel with raw-data prompt discipline
- **Absence as evidence** — "zero mentions across every component we run" is a finding, and often the decisive one
- **The two verdict axes** — maturity and fit are independent; a 1.0 spec with foundation governance still loses if it claims a seam the project does not have
- **Report anatomy** — verdict sentence first, then a layer-map table that marks the seams nobody claims (usually where the honest scenario hides), component-by-component fit citing the project's own files, and a phased implementation path with an explicit *never* list
- **Landing the verdict** — dossier, ledger row, and conditional watchlist item written in the same session, with falsifiable re-evaluation triggers instead of "keep an eye on it"

## The consumer-repo contract

The skill carries the *role*; each repo carries its *instance facts*. Add a block like this to the consuming repo's `AGENTS.md` or `CLAUDE.md` so findings land in the right files:

```markdown
## Protocol research contract

- Ledger: `docs/design.md` §8 "Alternatives considered" — one dated row per surveyed option
- Watchlist: `docs/backlog.md` — numbered item when adoption is conditional
- Dossiers: `docs/research/<date>-<topic>-fit.md`
- Bets already placed: <protocol> at the <seam> seam (backlog #<id>)
```

Without the block the skill infers these (design doc's alternatives table, backlog, `docs/research/`) and states the inference in its report.

## Install

**`npx skills` (recommended — works in every agent, not just Claude):**

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s protocol-fit-research -g
```

**Claude Code plugin:**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install protocol-fit-research@ai-skills
```

**Claude Code (manual):** copy `skills/protocol-fit-research/` into your project's `.claude/skills/` (shared with your team via git) or `~/.claude/skills/` (just you).

**Claude app / claude.ai:** grab `protocol-fit-research.skill` from the [latest release](https://forgejo.webgrip.dev/webgrip/ai-skills/releases/latest), upload it via Settings → Skills (or attach it in a chat), and hit *Save skill*.

## Use

Open your agent in the project and say, for example:

- *"How does A2A fit into this repo's design? How could we implement it? Do deep research."*
- *"Does MCP matter to us, or is it orthogonal to what we run?"*
- *"Do insane amounts of research on this spec and tell me if we should adopt it."*
- *"Someone posted a new agent protocol — is it a competitor to the one we bet on?"*
- *"Survey the landscape for alternatives to our dispatch layer."*

The report arrives in the conversation and, in the same session, as a dated dossier plus a ledger row (and a watchlist item when adoption is conditional) in the repo.

## Why

Protocol questions get asked once and answered forever — badly. The failure mode is not missing research, it is research that vanishes: a verdict delivered in a chat window, parked in per-user agent memory, or written without triggers, so the next person re-runs the whole sweep six months later and reaches a different conclusion. This skill makes the sweep exhaustive (parallel angles, absence checks, shipped-vs-press-release adoption) and then makes the verdict durable and falsifiable — in the repo, with named conditions that would flip it.

## Contributing

Issues and PRs welcome. Before submitting: run `npm run check` from the repo root (CI runs the same via `.forgejo/workflows/ci.yml`), and keep the skill generic — instance facts belong in the consumer repo's contract block, never baked into the instructions. Use a release-triggering conventional commit (`fix(protocol-fit-research): ...`) — the release pipeline bumps the version and rebuilds the dist zip automatically.

## License

MIT
