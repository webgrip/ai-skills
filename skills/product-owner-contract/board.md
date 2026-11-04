# Webgrip boards — the house rules on any tracker

Stages · Pull criteria · Taxonomy · Epics · Queue · WIP · Invariants. These hold on every
webgrip board, whatever tracker it runs on. How each rule is spelled on a tracker (status or
label, `repo/x` or `repo:x`, the commit trailer) is in that tracker's file:
[trackers/vikunja.md](trackers/vikunja.md) · [trackers/clickup.md](trackers/clickup.md). A
repo adds its own rules in its overlay. The craft itself is the `product-owner` skill (its
refine.md, playbook.md and agents.md); this file holds the facts and house rules.

**English board.** Titles, headings, criteria, comments, splits. A Dutch request still yields
an English ticket; quotes stay original in a quote block (`>`), log lines in a code block.

**Read [assets/definition-of-ready.md](assets/definition-of-ready.md) before gating a ticket
and [assets/ticket-template.md](assets/ticket-template.md) before writing one** — they are the
ratified text. Worked examples: [assets/golden-tickets.md](assets/golden-tickets.md) — **form
is the norm, content is illustrative**. Closing: [assets/definition-of-done.md](assets/definition-of-done.md).

## Stages

Every webgrip board walks the same five stages. The tracker file maps each one onto that
tracker's statuses or labels.

| Stage | Meaning |
|---|---|
| Backlog | caught, or still being refined |
| To Do | `ready` (and optionally `agent-ready`): pullable |
| Doing | started — counts against WIP |
| Reviewing | built; a human accepts against the DoD |
| Done | finished — the only stage completion counts use |

Moving a ticket back a stage is the gate working, not failure.

## Pull criteria per stage

Gates are cumulative. Check the content half with the product-owner skill's
`ticket_lint.py --gate ready` (or `--gate agent-ready`); check the taxonomy half against this
table.

| Into | Must be true | Who |
|---|---|---|
| Backlog | Title per the convention + a Source line or TL;DR. Nothing else. | Anyone |
| Refining (still Backlog) | Outcome · `theme` · `repo` · `kind` · `value` · `impact` | Writer |
| To Do (`ready`) | The DoR's four rules · bug: reproduction + environment · spike: timebox + decider · `effort` `time` `uncertainty` all set | Refinement |
| `agent-ready` | Ready + the agent-ready gate (agents.md) · `uncertainty` high never qualifies — spike first | Refinement |
| Doing | WIP below the cap · claim placed (agent claim or assignee) | Executor |
| Reviewing | PR link in a comment or under Technical context · executor's evidence comment | Executor |
| Done | The Definition of Done, in full, as an evidence comment | Executor + reviewer |

## Taxonomy — the dimensions are contract, the values are board state

Read the board's existing values before applying any. If no existing value fits, that is a
taxonomy decision for a human — raise it; **never create a label or tag to unblock a write.**

| Dimension | Values | When |
|---|---|---|
| `theme` | whatever the board defines | exactly one per ticket |
| `repo` | the repo the work lands in | exactly one per ticket; routes agents |
| `kind` | change · bug · spike · chore | every ticket at refining — a spike is a kind, never a `SPIKE:` title prefix |
| `value` | saves-time · reduces-risk · unblocks · compliance | every ticket at refining — prioritize on value, not volume |
| `impact` | high · medium · low | every ticket at refining |
| `effort` · `time` · `uncertainty` | small medium large · hours days weeks · low med high | at refinement, gate `ready`; effort large names its first slice or is split |
| `do-next` | — | at most 10 per board, all in the pick-up queue |
| agent claim | — | an agent's claim on a ticket |

A dimension the tracker file marks as not realized yet gates nothing: name it in the
ticket's TL;DR, flag the gap once, and carry on.

## Epics

`Epic: <subject>` titles; children wired as the tracker's parent–child relation (one parent
per child). An epic keeps `theme` + `impact`, holds the overall outcome, has no criteria of
its own, is exempt from estimation and stages, is never agent-workable, and closes only when
every child closes.

## Pick-up queue

Each board carries one ordered `Pick-up queue` (where it lives: the tracker file), top =
picked up first, covering every `do-next` holder plus a short next-up tail. Executors take
the topmost eligible entry; the PO inserts new tickets where they fit and drops entries on
close. Raw drag order in the tracker's UI is not the queue.

## WIP

Doing ≤ 3 per executor pool · agent tickets in flight ≤ 3–5 per human reviewer · a full
Reviewing column means clear review first, never start more.

## What NOT to groom

- **Fixture projects** a repo overlay names as such (test task sources, benchmark boards)
  — they are inputs to tooling, not backlogs.
- **Epics' criteria** — the outcome lives on the epic, the criteria on the children.
- Anything another session marks as in progress: leave it.

When in doubt, skip and report the doubt.

## House parameters on the generic pass

- **Ground in the project's checkout** on the development branch, else `main`; stamp
  `Researched against <branch> @ <short sha>`. GitOps premises are checked against the
  reconciled cluster state too, not only the repo.
- **Splits** follow `<area>: <subject> - Part n/m - <part outcome>`; the epic keeps the
  outcome, children the criteria, order as relations.
- **Secrets never land on a ticket** — name the vault path or the level, never the value.
- Requester material gets worked in, not parked: files attached, the essence quoted with its
  date as checkable evidence.

## Board invariants (audit recipe: the product-owner playbook)

Doing ≤ 3 · every open ticket exactly one `theme` and one `repo` · refining+ has `kind` +
`value` + `impact` · `ready`+ has the estimation trio, binary criteria and a Verification ·
spike has timebox + decider · bug has reproduction + environment · no `uncertainty` high
with `agent-ready` · `do-next` ≤ 10 and all in the queue · a ticket's stage has exactly one
source (the tracker file says which) · no product-name titles · dependencies as relations,
not prose · nothing completed without a DoD evidence comment.
