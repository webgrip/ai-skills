---
name: vikunja-product-owner
description: Run a Vikunja board as product owner through the `vikunja` MCP — ticket CRUD, Definition-of-Ready refinement, prioritization/do-next curation, dependency sequencing, backlog top-up/inventory, and the agent work protocols (ticket-reference trailers, claim/completion). Use when creating/updating/completing/listing Vikunja tickets, "make a ticket for X", "what's on the board/roadmap", refining/grooming tickets to the Definition of Ready, splitting an oversized ticket, prioritizing or triaging the backlog, "take inventory"/"top up the roadmap", "what should we work on next", handling a stale-premise ticket, or when the vikunja MCP fails to connect / returns 401.
---

# Vikunja product owner — the board operating manual

**Resolve the board contract first**: the consuming repo's `AGENTS.md` (or CLAUDE.md) carries a
**Board contract** — MCP server name, project name/id, ticket prefix, label taxonomy, caps,
top-up ground-truth commands, ops-runbook pointer. If absent: `projects_list`, ask which project,
and suggest adding the contract (template in this plugin's README).

Tool schemas are deferred: `ToolSearch "select:mcp__vikunja__tasks_list,mcp__vikunja__task_create"`
before calling. For bulk work or when MCP tools aren't loaded in-session, run
[scripts/mcp_client.py](scripts/mcp_client.py).

## The PO loop

**intake** (create, `needs-refinement`) → **refine** to DoR ([refine.md](refine.md)) →
**prioritize** (heuristics below) → **sequence** (`precedes` relations, not prose) →
**dispatch-ready** (`agent-ready` gate) → **close with evidence** ([playbook.md](playbook.md)).
Periodic: **top-up/inventory** (recipe in [playbook.md](playbook.md)) keeps the backlog at the
contract's open target and honest.

## Board conventions (defaults — the contract may override)

| Concept | Convention |
|---|---|
| Priority | P0/P1/P2/P3 → task `priority` 5/4/3/2 (Vikunja shows 4+ as "Urgent") |
| Tags | labels `theme/<kebab>`, `impact/H\|M\|L`, `effort/S\|M\|L` — every open ticket has all three |
| Top of stack | label `do-next`, hard cap 10 |
| Lifecycle | `needs-refinement` → `ready` (DoR met) → done via `task_complete` + evidence comment |
| Kanban | buckets `Backlog / Ready / In progress (agent) / Review / Done` |
| Descriptions | TipTap **HTML only** — raw markdown renders literally; first para = `<p><strong>theme</strong> — <code>[P · I · E]</code></p>` |
| Titles | plain text, no links; rename only with reason + a comment (others reference by title) |

## Definition of Ready (all seven, or it isn't `ready`)

1. **Problem** — what's wrong *today* + evidence (`file:line`, live symptom, decision record); no evidence found = say so.
2. **Outcome** — one sentence.
3. **Acceptance criteria** — 2–6 HTML checkboxes, each verifiable against real state ("improve X" is not one).
4. **Approach** — 3–7 steps naming real repo paths + applicable skills.
5. **Verification** — the exact command/check proving it live (never a proxy).
6. **Gates & links** — blockers by exact title, decision-record/runbook paths.
7. **Sized** — honest S/M; an L names its first shippable slice or gets split.

**Agent-assignability gate** (grants `agent-ready`): also states allowed paths/blast radius · a
verification an agent can run itself · the escalation point (what needs a human) · size ≤ M.

## Prioritization heuristics

- **P0** = live risk or cheap correctness *now* — don't inflate; there are rarely more than a few.
- Within a band, order by impact/effort; `effort/S` unblocked tickets are do-next bait.
- **do-next** = highest-leverage *unblocked* tickets — remove stale picks when adding.
- The open target is a **forcing function**: keep finding real work; if you genuinely can't, hold
  fewer and say so — never pad.
- Stale premise ≠ done: rewrite as verify-and-close (the verification IS the remaining work);
  never silently complete. Refinement's chief value is invalidating stale work.

## Board invariants (audit recipes in [playbook.md](playbook.md))

open ⇒ theme+impact+effort labels · `ready` ⇒ DoR sections present · `do-next` ≤ cap · dependencies
as `precedes`/`blocked` relations · every completion has an evidence comment · "Found N" from
`tasks_list` matches expected board size (pagination gotcha below).

## Agent work protocols

- **Linking**: commits touching a ticket carry a `<PREFIX>-<taskID>` trailer (prefix from the
  contract; webgrip default `VIK`); PR bodies reference it; bare Vikunja task URLs autolink in
  Forgejo/Gitea.
- **Completion**: HTML comment with commit/PR links → `task_complete`. Never claim done without
  the ticket's own Verification evidence.
- **Claim** (agents): add `agent/<name>` label + comment with session id + move to
  "In progress (agent)"; progress comments at milestones; on done → completion comment + "Review"
  bucket (a human accepts). One ticket per agent run; skip if a claim comment exists.

## Gotchas (details → [reference.md](reference.md))

- `tasks_list`/`search` return ONE server page (Vikunja `maxitemsperpage`, default 50 — the
  contract states your instance's cap; `limit: 0` falls back to 50; search only matches in-window)
  — always check the reported "Found N".
- Tools return **formatted text, not JSON**: creates emit `ID: <n>`; list entries end
  `[ID: <n>, Project: <m>]`; `labels_list` appends hex colors to titles.
- Deletes are soft (server safe mode; Vikunja has no trash): `project_delete`→archive,
  `task_delete`→complete, `label_delete`→blocked.
- `labels_bulk_set_on_task` REPLACES the whole label set — include everything you want kept.
- 401/403 = API token expired or under-scoped — token ops live with the instance (the contract's
  ops-runbook pointer), not in this skill.
