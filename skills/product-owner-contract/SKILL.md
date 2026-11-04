---
name: product-owner-contract
description: Webgrip's board contract for the product-owner skill - the house rules every webgrip board follows on Vikunja or ClickUp (stages, pull criteria per stage, taxonomy of theme, repo, kind, value, impact and estimation, epics, pick-up queue, WIP), the ratified Definition of Ready, ticket template, golden tickets and Definition of Done, how each tracker spells them, and the repo overlay hook. Use when working a webgrip board alongside product-owner - making, refining, grooming, gating, splitting or closing a VIK or CU ticket, "make a ticket for X" in a webgrip repo, asking which tags, labels or statuses a webgrip ticket needs, or deciding what a repo's own ticket rules add on top of the webgrip default.
---

# Webgrip board contract

Facts only; the craft is the `product-owner` skill. Load it first — this skill is its
contract layer for webgrip and never replaces a step of its procedure. The order in which
the layers combine is the product-owner skill's ("Resolve the board contract first");
this skill is its organisation layer.

## Context

```text
Context: webgrip
Applies when: the `vikunja` or `clickup` MCP is in play, a repo remote points at the
  webgrip Forgejo, a ticket id looks like VIK-<id> or CU-<id>, or the user says "webgrip"
```

## What to read

1. [board.md](board.md) — the house rules, true on every tracker.
2. The tracker file for the board at hand — [trackers/vikunja.md](trackers/vikunja.md) or
   [trackers/clickup.md](trackers/clickup.md): how those rules are spelled there. Pick it
   from the repo overlay's `Tracker:` line, else from the connected MCP; both connected and
   no overlay → ask.
3. [assets/](assets/) — the ratified hand-over docs, before writing, gating or closing.
4. The repo overlay, when the repo has one — it wins over everything here.

## The repo overlay

A repo adds its own rules in `.agents/product-owner/board.md`:

```markdown
Extends: webgrip
Tracker: clickup

## Additions
- Board: Space `<name>`
- Extra kind: migration — needs a Rollback section and a dry-run Verification
- Protected paths for agents: `deploy/`, `.forgejo/`
- Into `ready`: a linked ADR for any change under `docs/adr/`
```

- Only additions and overrides; anything it does not mention falls through to this skill.
  `Extends: webgrip/default` is the older spelling of `Extends: webgrip`.
- An optional `assets/` next to it adds files; a file named like one of [assets/](assets/)
  **replaces** it for that repo — say so when you use it.
- A rule that would hold for every webgrip repo belongs in [board.md](board.md) instead —
  propose it there.

State the resolved layers in one line before the first write ("webgrip on ClickUp + overlay
`.agents/product-owner/`"), so a wrong layer is caught before it costs a ticket.

## Gates

- Ready: `python3 <product-owner>/scripts/ticket_lint.py body.md --gate ready --title "…"`,
  then the taxonomy half against the pull-criteria table in [board.md](board.md), spelled
  per the tracker file.
- The overlay's extra criteria are checked by hand and reported as MANUAL lines.
- Golden tickets are the regression set: `test.sh` holds them to the ready gate.
