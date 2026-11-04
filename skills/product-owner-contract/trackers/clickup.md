# Webgrip on ClickUp — how the house rules are spelled

How [../board.md](../board.md) lands on webgrip's ClickUp workspace. Tool mechanics are the
product-owner skill's ClickUp adapter; this file holds only webgrip's choices.

## Board facts (a cache to re-verify, never truth)

- MCP server `clickup` · one workspace; a product gets a **Space**, its Folders group areas
  and its **Lists are the themes** (`Sessions, editors & AI clients`, `Observability`)
- Ticket reference and commit trailer: `CU-<task-id>` (the short id from
  `app.clickup.com/t/<id>`); Ploeg names an agent branch `agent/CU-<id>`
- Space, List and status ids live on the board or in a repo's overlay, never here. Resolve
  them with `clickup_get_workspace_hierarchy` and `clickup_get_list`
- Tags are **Space-wide**: a new value costs every List in that Space

## Stages — the status is the only source

Statuses differ per Space. Map the board's own set onto the five stages before acting, state
the mapping, and ask when a stage has no status:

| Stage | Status names webgrip uses |
|---|---|
| Backlog | `backlog`, `to do` |
| To Do | `ready` |
| Doing | `in progress` |
| Reviewing | `in review` |
| Done | `done` (`Closed` is archive, not a completion) |

A Space may add a waiting status such as `needs you`: it is Doing that waits on a person,
and it still counts against WIP. Lifecycle never lives in a tag on ClickUp: a `ready` tag
next to a `backlog` status is drift — report it, and the status wins.

## Taxonomy spelling

Tags are lowercase `dimension:value`. An unknown tag is silently dropped by ClickUp, so read
the Space's tags first.

| Dimension | Spelling |
|---|---|
| `theme` | the List the ticket lives in — no tag |
| `repo` | `repo:<repo>` |
| `kind` | `spike` for a spike; change, bug and chore are not realized yet |
| `value` | not realized yet |
| `impact` | `impact:h` · `impact:m` · `impact:l` |
| estimation | `effort:s\|m\|l` · `time:hours\|days\|weeks` · `uncertainty:low\|med\|high` |
| refining | `needs-refinement` marks a Backlog ticket that is not refined yet |
| epic | `epic` + `meta` |
| `do-next` · agent claim | not realized yet; the claim is the assignee |

Not realized yet = TBD — owner: the board owner. Until then the dimension gates nothing (see
[../board.md](../board.md)).

## Epics and queue

- Epic children: `clickup_create_task {parent: <epic-id>}`; one parent per child.
- Pick-up queue: not realized yet on ClickUp — TBD, owner: the board owner. Until then,
  `ready` ordered by priority is the queue, and say so.
