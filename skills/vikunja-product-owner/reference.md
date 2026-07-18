# vikunja MCP — API mechanics (instance-independent)

The server behind the `vikunja` MCP is `@aimbitgmbh/vikunja-mcp` (behavior verified live
2026-07-12 against v0.1.0). Instance operations (deployment, token creation/rotation, network
reachability) belong to the instance's ops runbook — the board contract points there.

## Scripted access

Run [scripts/mcp_client.py](scripts/mcp_client.py) — minimal streamable-HTTP MCP client
(`init()` + `call(tool, args)`); handles the session-id handshake, SSE parsing, and server-side
session reaping (on a 404/410 mid-run: reset `session['id']` and `init()` again). Use for bulk
board passes and when `.mcp.json` changed mid-session (native tools need a restart). Endpoint:
`VIKUNJA_MCP_URL` env, else the webgrip default baked into the script.

**Etiquette for supergateway-bridged deployments** (stateless mode): sequential calls only, client
timeout ≥ 120 s. A client that disconnects before its response is ready crashes the whole gateway
(uncaught throw in `stdioToStatelessStreamableHttp.js` — verified 2026-07-18), killing every
session's in-flight calls; a threaded sweep with 60 s timeouts is enough to crash-loop it.

## Response formats

Tools return **formatted text, not JSON**:

- create tools → `Created <thing> "<title>"` then a line `ID: <n>`
- list tools → `Found <N> <thing>(s)` then blocks `<i>. <title>` / detail lines / `[ID: <n>]`
  (tasks: `[ID: <n>, Project: <m>]`)
- `task_get` → title line, then `Priority: …`, `Labels: <comma-joined>`, `Project ID: <n>` lines
- `labels_list` appends the hex color to colored label titles — `impact/M (f5a524)` — strip the
  trailing space-plus-`(xxxxxx)` before using titles as map keys
- **relations never render in `task_get`** — verify a `relation_create` persisted by re-creating
  it: `Vikunja API error (409): The task relation already exists` IS the confirmation
- errors → `isError` content `Error: … Vikunja API error (<code>): …`
- unset due dates render as `Due: 0001-01-01` — not a bug

## Ordering — no position API

Vikunja stores task order **per-view** (list/kanban drag positions); vikunja-mcp 0.1.0 exposes no
position read or write. The `tasks_bulk_update` schema *advertises* `position` and `bucketId`,
but both fail live (verified 2026-07-18): `position` → `Vikunja API error (400): The task field
'position' is invalid`; `bucketId` → vikunja-mcp crash `updatedTasks.forEach is not a function`.
Consequence: pick-up order cannot live in view positions — it's encoded as the pick-up queue in
the project description (SKILL.md conventions), and UI drag-order is cosmetic.

## Pagination

`tasks_list` returns ONE server page (Vikunja `maxitemsperpage`, default 50); `search` matches
only within that window; `limit: 0` does NOT mean "all" — it falls back to 50. Always sanity-check
the reported "Found N" against expected board size; fall back to `task_get` by ID.

## Troubleshooting

| Symptom | Cause / next step |
|---|---|
| 401 | API token expired/revoked — instance ops runbook (token rotation) |
| 403 on task ops | token missing that route-group permission — recreate token with wider scope |
| connect timeout | endpoint unreachable from here (VPN/LAN?) or the MCP service is down — instance ops |
| `tasks_list` misses known tasks | pagination (above) |

## Tool catalog

`mcp__vikunja__*` — names verified live via tools/list (trust this over the upstream README,
whose singular/plural naming is wrong for several tools).

| Area | Tools |
|---|---|
| Tasks | `tasks_list`, `tasks_list_all`, `task_get`, `task_create`, `task_update`, `task_complete`, `task_delete`*, `tasks_bulk_update` |
| Projects | `projects_list`, `project_get`, `project_create`, `project_update`, `project_archive`, `project_delete`*, `project_duplicate` |
| Labels | `labels_list`, `label_get`, `label_create`, `label_update`, `label_delete`*, `label_add_to_task`, `label_remove_from_task`, `labels_bulk_set_on_task` |
| Comments | `comments_list`, `comment_get`, `comment_create`, `comment_update`, `comment_delete` |
| Assignees | `assignees_list`, `assignee_add`, `assignees_add_bulk`, `assignee_remove` |
| Relations | `relation_create`, `relation_delete` (kinds: subtask/parenttask, related, blocking/blocked, precedes/follows, duplicateof/duplicates, copiedfrom/copiedto) |
| Views/Kanban | `views_list`, `view_get`, `view_create`, `view_update`, `view_delete`, `buckets_list`, `bucket_create`, `bucket_update`, `bucket_delete` |
| Filters | `filter_get`, `filter_create`, `filter_update`, `filter_delete` |
| Notifications | `notifications_list`, `notification_get`, `notification_delete` |
| Subscriptions | `subscription_get`, `subscription_create`, `subscription_delete` |

\* soft in safe mode: `project_delete`→archive, `task_delete`→complete, `label_delete`→blocked.
