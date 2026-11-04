# Webgrip on Vikunja — how the house rules are spelled

How [../board.md](../board.md) lands on webgrip's Vikunja instance. Tool mechanics are the
product-owner skill's Vikunja adapter; this file holds only webgrip's choices.

## Board facts (a cache to re-verify, never truth)

- MCP server `vikunja` (LAN/VPN only — off-VPN it fails to connect; say so instead of
  retrying) · instance list cap 250 per page, and `tasks_list` returns one page: count
  before concluding you have them all
- Ticket prefix and commit trailer: `VIK-<id>`; bare task URLs autolink in Forgejo
- Project ids live in each repo's overlay, not here. No repo at hand → `projects_list` and
  ask which one; never guess a project
- Labels are **instance-wide**: a new value costs every board

## Stages — derived from labels, never stored separately

| Stage | Derived from |
|---|---|
| Backlog | `needs-refinement`, or no lifecycle label |
| To Do | `ready` (and optionally `agent-ready`) |
| Doing | `agent/<name>` claim, or an assignee who started |
| Reviewing | `review` |
| Done | completed |

Kanban buckets, where a project uses them, mirror these stages; labels are authoritative,
buckets are display.

## Taxonomy spelling

| Dimension | Spelling |
|---|---|
| `theme` · `repo` · `kind` · `value` | `theme/<kebab>` · `repo/<repo>` · `kind/<kind>` · `value/<value>` |
| `impact` | `impact/H` · `impact/M` · `impact/L` |
| estimation | `effort/S\|M\|L` · `time/hours\|days\|weeks` · `uncertainty/low\|med\|high` |
| `do-next` · agent claim · epic | `do-next` · `agent/<name>` · `meta` |

Enumerate with `labels_list` before applying any. `kind/*` and `value/*` must exist on the
instance before they gate anything.

## Epics and queue

- Epic children: `subtask` relations, parent → child. Epic label: `meta`.
- Pick-up queue: in each project's **description**, entries as `VIK-<id> — title`.
