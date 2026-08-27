---
name: product-owner
description: Run any ticket board as product owner — Vikunja, ClickUp, or another tracker. Refinement to the Definition of Ready, agent-ready gating for AI-executed work, review-capacity WIP limits, dependency sequencing, backlog sweeps, the Definition of Done, and flow metrics. Use when creating, updating, closing or listing tickets, "make a ticket for X", "maak een ticket (aan) voor", "wat staat er op het bord", "wat pakken we op", asking what is on the board or what to pick up next, refining or grooming a backlog, writing acceptance criteria or a verification, prioritizing or triaging, ordering pick-up, moving a ticket to another status, running a board-health or WIP audit, measuring the board's cycle time or deriving a service level expectation (SLE), preparing tickets for an AI coding agent, splitting an oversized ticket, handling a stale or obsolete ticket, or when a ticket is just a product name with no definition of finished. NOT for agile-theory questions or articles about PO practice — this runs a live board.
---

# Product owner — the board operating manual

> **A ticket is done when someone else — human or AI agent — can pick it up without
> calling you.** Evidence per rule: [rationale.md](rationale.md).

## Resolve the board contract first

The consuming repo's `AGENTS.md` (or CLAUDE.md) carries a **Board contract**: which
tracker + MCP server, project/list ids, status roles or label taxonomy, ticket language,
WIP caps, queue conventions, DoD location, ground-truth commands, ops-runbook pointer
(template in this plugin's README). Then load the matching adapter —
[adapters/vikunja.md](adapters/vikunja.md) or [adapters/clickup.md](adapters/clickup.md) —
for tool mechanics. Without a contract: see which MCP is connected, list its
projects/boards, ask which one, and suggest adding the contract block.

- **Never assume a list, status, field, label, or tag exists** — resolve *this* board's
  own set first and state the mapping before acting on it. A gate on a status that
  doesn't exist is worse than no gate; a field the board lacks is not a defect to fix by
  creating it.
- **Language: match the board** (contract says; else the language of its existing
  tickets). Everything that lands on the board — titles, headings, criteria, comments —
  in that language. Reason in any language; quotes and log lines stay original inside a
  code block.
- **Where a board has its own agreement, that agreement wins** — follow it and say which
  part you're overriding, rather than silently drifting.

## The PO loop

**catch** (title + Problem — deliberately cheap, nothing else) → **refine** to Ready
([refine.md](refine.md)) → **prioritize** → **sequence** (dependencies as relations,
never prose) → **order** (pick-up queue where the contract has one) → **execute**,
WIP-limited (AI-agent execution → [agents.md](agents.md)) → **review** against evidence →
**close** on the DoD. Periodic: **sweep** + flow metrics ([playbook.md](playbook.md),
[flow.md](flow.md)). Catching is nearly free; pulling is expensive — that asymmetry is
deliberate. **Moving a ticket back is not failure; it's the gate working.**

## The skeleton

Headings that stay empty: **delete them**. One screen is the cap — on agent-executed
tickets, longer descriptions measurably *reduce* success; carry **pointers, not
payloads** (name the file to imitate, link the doc — don't paste it).

| Section | When | What |
|---|---|---|
| **Problem** | always | What goes wrong today, for whom, what it costs — with evidence someone can check (`file:line`, metric, support ticket + date, decision record). No solution. |
| **Outcome** | always | One sentence: the end state, not the activity. |
| **Acceptance criteria** | to be Ready | 2–7 binary checkboxes. At least one closes the cheap way out; feature work gets at least one error-path criterion. |
| **Verification** | to be Ready | Who/what proves it, where, with which concrete case and expected result. A runnable command when an agent executes. Not the criteria restated. |
| **Context** | to be Ready | Pointers: repo path, ADR/runbook, dashboard, support ticket. |
| **Approach** | route not obvious; mandatory for agent-ready | 3–7 steps naming real repo paths; records the design decisions already made. Direction, not a recipe. |
| **Not in scope** | someone could assume otherwise | With where it goes instead (separate ticket, later part). |
| **Open questions** | anything nobody can answer now | Each with an owner (the customer may be one). Three owned open questions is an honest ticket, not a bad one. |
| **Protected areas** | agent-bound work | Do-not-touch files/behaviors — tests, CI config, unrelated modules. The cheapest guard against silent scope drift and gamed criteria. |
| **Rollback** | anything above the lowest risk tier | Feature flag, clean revert, or migration down-path. |

**Titles**: `area: what changes`, ≤ 70 chars — a usable commit subject. The test: can
someone who wasn't there tell what it's about? A bare product name (`Kepler`,
`Longhorn`) describes an installation, not a result — the most common board defect.
The user-story line (*As a role, I want X so that Y*) may open **Problem** on end-user
work where it reads naturally; it never replaces the skeleton, and platform work skips
it (a story about etcd backups is a story about nobody).

## Definition of Ready — understandable, then plannable, then machine-executable

Three separate concerns; gate them separately.

**1 · Ready (understandability — the field-free kernel).** A ticket may be pulled when:

1. **Problem stated, with checkable evidence.** *(Spike: the one question plus its occasion.)*
2. **Outcome in one sentence.** *(Spike: the decision to be made.)*
3. **Binary criteria — two readers, one conclusion — and at least one closes the cheap
   way out.** The test question: *"how do I finish this ticket WITHOUT solving the
   problem?"* — the answer is your missing criterion.
4. **Verification stated.** Without a measuring point, a criterion is an opinion.

Extras where applicable: **bug** → reproduction (expected vs actual; an executable repro
script beats prose) + environment (where, since when, how often) · **spike** → timebox +
named decider; done = **decided and recorded**, not researched · **split-child** → its
own outcome + a criterion protecting what already works + order as a dependency.

**2 · Plannable (deliberately NOT in the DoR):** estimate, priority, sprint/queue
placement, assignee. Planning decisions come *after* understandability. Anything that
touches every ticket is Definition of Done, not DoR.

**3 · Agent-ready** (grants dispatch to an AI executor): Ready plus the seven-criterion
gate — approach, runnable verification, protected areas, escalation, size,
self-containedness, concision — and the human-only routing exclusions. The gate lives in
[agents.md](agents.md); read it before dispatching or marking anything agent-ready.

**The ten-minute rule.** Doesn't meet the gate but completable in ten minutes? Do it and
pull it through. More → back with a comment naming exactly what's missing. This keeps
gates conversations, not queues — and it is not a rubber stamp: a ticket missing most of
its skeleton is a refinement conversation.

Like the DoD, the DoR is **not negotiable per ticket** — only per team, in the retro —
and structurally missing it means the definition is wrong, not the team. Evaluate it
periodically on one number: how often work bounced because the ticket was unclear; if
the DoR moves nothing, drop it.

Check mechanically: `python3 scripts/ticket_lint.py body.md --gate ready|agent-ready
--title "..."` — PASS/FAIL/WARN per criterion, MANUAL for what needs the board or a human.

## WIP — and where the limit now sits

Enforce the contract's WIP cap (default: 3 started per executor pool). Refuse to move
an item in over the cap; name the oldest in-flight item (by Work Item Age) as the one to
finish first. **When AI agents execute, the binding constraint is human review capacity,
not agent availability** — cap dispatched agent tickets per human reviewer (start at
3–5), give the review column its own cap, and when review is full the answer to "what
next?" is *clear the review queue*, never *start more*. Twelve items in doing means
nothing is in hand and everything is half done.

## Definition of Done

One list per team, every ticket, regardless of size — per-ticket conditions are
acceptance criteria, not DoD lines. The portable default (contract may point at the
team's own):

- **Result** — all acceptance criteria met · the ticket's Verification actually
  *executed*, not promised. Green CI alone never closes a ticket.
- **Code** — MR/PR merged, pipeline green · reviewed by someone other than the author
  (for agent work: a fresh-context reviewer checks the diff against *intent and scope*,
  including nothing changed outside the ticket's named files) · no new critical/high
  vulnerabilities.
- **Deployed** — running in the target environment and seen there *(or explicitly not
  deployed, with the reason)* · rollback path known and written down.
- **Knowledge** — behavior changed ⇒ runbook/ADR/docs updated *(or: not needed,
  because …)* · commit/MR references the ticket (trailer per the contract).
- **Accountability** — incident? cause + lessons recorded · security touched? classified
  per the board's scheme.

Three rules that keep it standing: **not negotiable per ticket** (only per team, in the
retro) · **every rule has an escape with a reason** — "not deployed, because the
customer wants it after the holidays" is fine; "not deployed" alone is not · **missed
structurally ⇒ the DoD is wrong, not the team** — lower it deliberately, never ignore it.

## Prioritization

- **P0 = live risk or cheap correctness now.** Six simultaneous P0s means there is no
  P0. Priority is an order, not a feeling.
- Sequence by **cost-of-delay class** (expedite / fixed-date / standard / intangible),
  then shortest-job-first within a class. Scoring frameworks (RICE/WSJF) structure
  arguments; they never auto-rank — summed ordinal scores are fake math, and confidence
  claims need an evidence tier (opinion / anecdote / data / experiment).
- A ticket never ranks above one that blocks it. Small unblocked tickets are pick-up bait.
- Bands are a coarse filter; the pick-up queue (where the contract has one) is the total
  order. Don't stack-rank the whole backlog — that precision is fake and rots.
- **Queue time is the economic lever**: an item aging past the SLE wants a decision
  (split, swarm, unblock, or drop), not another day of ageing.
- At a WIP/portfolio cap, **every yes names what it displaces**.
- **A stale premise is a first-class finding, not a completion.** Work already shipped?
  Rewrite as verify-and-close — the verification *is* the remaining work. Never silently
  close. Invalidating stale work is refinement's chief value.
- Keep the backlog small and honest: hold fewer tickets rather than pad toward a target.

Board invariants + the audit recipe that checks them → [playbook.md](playbook.md).

## Writing to the board

Reads are free. **Confirm before**: bulk status moves, closing anything, rewriting a
description someone else wrote, or touching more than ~3 tickets at once — show the
intended diff first. Single-ticket creates and requested refinements need no ceremony.
Descriptions **replace** on write in both adapters: read → merge → write, never blind.

## Gotchas

- **Never invent.** Facts come from research (repo, live state, board history) or the
  requester; gaps become explicit MISSING questions — procedure in [refine.md](refine.md).
- **Ceremony scales with size × risk × ambiguity.** A chore is title + Problem, done —
  padding it with empty headings makes it worse. Full spec treatment on a one-file fix
  is a measured 10× productivity loss.
- **Refinement is grounded in the up-to-date repo**, stamped `researched against
  branch @ short-sha` — grounding procedure in [refine.md](refine.md).
- **Justify gates with wrong-work risk** — the measured cost of underspecified work
  reaching an executor ([rationale.md](rationale.md) has the numbers and the debunked
  folklore to avoid citing).
- Board-specific traps (pagination lies, payload bombs, HTML vs markdown, replace-on-
  write, position APIs) live in the adapter — read it before the first write.

## Additional resources

- Refinement execution: interview, criteria craft, EARS, templates, splitting, bulk
  fan-out → [refine.md](refine.md)
- AI-agent execution: agent-ready gate, claim/evidence/accept protocol, risk tiers,
  anti-reward-hacking → [agents.md](agents.md)
- Operation recipes: create, gate-check, close, sweeps, dedupe, queue, rework →
  [playbook.md](playbook.md)
- Flow metrics and the SLE → [flow.md](flow.md) + [scripts/flow_metrics.py](scripts/flow_metrics.py)
- Why each rule: the 2026 evidence base with sources → [rationale.md](rationale.md)
- Tool mechanics → [adapters/vikunja.md](adapters/vikunja.md) · [adapters/clickup.md](adapters/clickup.md)
