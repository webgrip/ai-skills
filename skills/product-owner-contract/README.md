# product-owner-contract

Webgrip's contract layer for the [product-owner](../product-owner) skill: the facts and house
rules for webgrip's boards, kept out of the generic skill so that one stays
organisation-free.

- `board.md` — the house rules on any tracker: stages, pull criteria per stage, the taxonomy
  dimensions, epics, the pick-up queue, WIP and board invariants.
- `trackers/vikunja.md`, `trackers/clickup.md` — how those rules are spelled on each tracker:
  statuses or labels, tag syntax, commit trailer, where the queue lives.
- `assets/` — the ratified Definition of Ready, the fill-in ticket template (two halves:
  functional on top, technical below the rule), four golden tickets and the Definition of
  Done.
- **Repo overlay** — a repo adds its own rules in `.agents/product-owner/board.md`
  (`Extends: webgrip`, `Tracker:`, additions only) and optional `assets/`; see SKILL.md.

## Install

Install it next to `product-owner`:

```json
"enabledPlugins": { "product-owner@ai-skills": true, "product-owner-contract@ai-skills": true }
```

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s product-owner -s product-owner-contract -g
```

## Test

`bash test.sh` runs the golden tickets through the product-owner skill's
`ticket_lint.py --gate ready` and checks every relative link in `board.md` and
`trackers/`.
