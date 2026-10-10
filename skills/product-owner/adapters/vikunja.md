# Vikunja adapter — MCP mechanics (instance-independent)

Tools `mcp__vikunja__*`, served by the webgrip `mcp-vikunja` server (the plugin's
`.mcp.json` default — not the upstream `@aimbitgmbh/vikunja-mcp`). The tool surface
varies by server version: **resolve it with a live `tools/list`**; the catalog below is
indicative. Schemas are deferred:
`ToolSearch "select:mcp__vikunja__tasks_list,mcp__vikunja__task_create"` before calling.
Instance operations (deployment, token creation/rotation) belong to the instance's ops
runbook — the Board contract points there.

Contents: concept map · HTML description template · pick-up queue · semantics ·
scripted access · tool catalog.

## How the generic concepts map here

| Skill concept | Vikunja realization |
|---|---|
| Ticket body | `description`, TipTap **HTML only** — raw markdown renders literally |
| Skeleton headings | `<h3>` sections; criteria as the taskList checkbox markup below; section set per [refine.md](../refine.md)'s templates |
| Status/stage | DERIVED from labels + done, never stored: Backlog (`needs-refinement`) → To Do (`ready`) → Doing (`agent/<name>` claim) → Reviewing (`review`) → Done (completed + DoD). Stock-UI kanban buckets, if used, mirror this — labels are authoritative |
| Priority | P0/P1/P2/P3 → `priority` 5/4/3/2 (integer 1..5; Vikunja shows 4+ as "Urgent") |
| Taxonomy | labels: `theme/<kebab>`, `impact/H\|M\|L`, `effort/S\|M\|L`, `time/hours\|days\|weeks`, `uncertainty/low\|med\|high`, `do-next`, `agent-ready`, `agent/<name>` |
| Dependencies | `task_relation_add {task_id, other_task_id, relation_kind}` — kinds `precedes`/`follows`/`blocked`/`blocking`/`subtask`/`parenttask`/`related` |
| Pick-up order | the pick-up-queue section in the **project description** (below) — no position tools exist |
| Evidence comment | `task_comment_add {task_id, comment}` — TipTap HTML |
| Completion | `task_complete {id}` (agents never complete their own work — [agents.md](../agents.md)) |
| Commit trailer | `<PREFIX>-<taskID>` from the contract (webgrip default `VIK`); bare task URLs autolink in Forgejo/Gitea |
| Cross-reference | full URL `<task web base><taskID>` from the contract, in descriptions and comments |

Titles are **plain text, no links**; rename only with a reason + a comment (others
reference tickets by title).

## HTML description template

Verified round-trip on the webgrip instance: `<h3>`, `<p>`, `<code>`, `<ul>`, and the
checkbox markup survive sanitization; the checklist renders with an x/y counter. Escape
`&` as `&amp;`, shell `<`/`>` as `&lt;`/`&gt;`. 1500–3500 chars. Sections per
[refine.md](../refine.md)'s templates; the load-bearing markup:

```html
<p><strong>&lt;theme&gt;</strong> — <code>[P1 · impact H · effort M · time d · unc low]</code></p>
<h3>Problem</h3><p>… evidence as <code>path/file:12</code> …</p>
<h3>Acceptance criteria</h3>
<ul data-type="taskList">
  <li data-checked="false" data-type="taskItem"><label><input type="checkbox"><span></span></label><div><p>criterion</p></div></li>
</ul>
```

(`data-checked="true"` + `checked` on the input for a pre-ticked box.)

## The pick-up queue (ordering without a position API)

The server exposes **no position or bucket tools** — UI drag-order is cosmetic. The
total order lives as `<h3>Pick-up queue</h3>` + `<ol>` of `<PREFIX>-<id> — title` in the
**project description** (top = picked up first; composition and refresh triggers per
[playbook.md](../playbook.md)). A consuming repo's board UI may rewrite this same
section on drag (marker `refreshed <date> (board)`) — treat whichever write is newest as
current and never fight it.

Emitting it: `project_get {id}` → take the current description, replace **only** the
queue section, keep everything else verbatim → `project_update {id, description}` —
naming `description` replaces that whole field. **Verify the extracted description is
non-empty before writing** (a failed extraction clobbers the project description), and
spot-check with `project_get` after.

## Semantics worth knowing (from the live schemas)

- **The output is formatted text, and a list position is not an id.** `labels_list`
  returns lines like `36. ready (46a758)` followed by `[ID: 28]`; `task_get` returns a
  formatted string, not JSON. Parse the explicit `[ID: n]` field, never the position — a
  position used as an id puts the wrong label on the ticket, and one that matches a label
  you can't see answers 403 and fails the whole bulk call. Load a tool's schema before
  the first call instead of guessing parameters (guessed `tasks_list` parameters answer
  400), and read the object back after every write.

- `task_update` / `project_update` **read first — fields you do not name survive.** A
  named `description` still replaces that field wholesale: read → merge → write.
- `task_get` returns the task **with its description and relations** — relations are
  verifiable by reading, no tricks needed.
- Labels are addressed **by title**: `task_create {labels: [...]}` creates missing ones;
  `labels_bulk_set_on_task {task_id, labels, create_missing}` **REPLACES the whole
  set** — read the task's current labels first, merge, then set the complete list.
  There are no single-label add/remove tools on this server.
- Safe-mode deletes: `task_delete` → completes instead, `project_delete` → archives
  instead, `label_delete` → **refuses** (a label delete would strip it instance-wide).
- `tasks_list` returns **ONE server page** — check the reported count against expected
  board size; `page` continues, `filter` takes Vikunja filter syntax, `search` matches
  task text. `projects_list` hides archived unless `include_archived`.
- **Auth is per client since server v1.0.0**: initialize and tools/list are
  anonymous, but every tools/call needs `Authorization: Bearer <vikunja-api-token>` —
  the server no longer holds a server-side token for HTTP callers. The plugin's
  `.mcp.json` sends `Bearer ${VIKUNJA_API_TOKEN}` (env expansion — export it before
  launching the client); [mcp_client.py](../scripts/mcp_client.py) reads
  `$VIKUNJA_API_TOKEN`, else the file named by `$VIKUNJA_TOKEN_FILE`. `No token` on a
  tool call means the header never arrived. Token minting/rotation stays with the
  instance (the contract's ops-runbook pointer). A connect timeout means the endpoint
  is unreachable from here (VPN/LAN?) or the service is down — also instance ops.
- **Flow-metrics normalization** (for [../scripts/flow_metrics.py](../scripts/flow_metrics.py)):
  Vikunja records no started timestamp — use `created` from the task and `finished` from
  its done date, and label the result the lead-time proxy it is; where the claim
  protocol posts a claim comment, that comment's date is the honest `started`.

## Scripted access (bulk work)

Run [../scripts/mcp_client.py](../scripts/mcp_client.py) — minimal streamable-HTTP MCP
client (`init()` + `call(tool, args)`); handles the session-id handshake and SSE
parsing. Endpoint: `VIKUNJA_MCP_URL` env, else the webgrip default baked into the
script. Bulk passes: **sequential calls, generous timeouts** — parallel sessions stress
bridged MCP deployments — a threaded sweep has crash-looped a gateway.

## Tool catalog (indicative — `tools/list` is the truth)

Names vary by server version: `task_comment_add` may be `comment_create`,
`task_relation_add` may be `relation_create`, `whoami` may be absent, and a newer surface
adds `tasks_bulk_update`, `tasks_list_all`, single-label `label_add_to_task` /
`label_remove_from_task`, and buckets/views/filters/assignees/notifications.

| Area | Tools |
|---|---|
| Tasks | `tasks_list`, `task_get`, `task_create`, `task_update`, `task_complete`, `task_delete`* |
| Relations | `task_relation_add` |
| Comments | `task_comment_add` |
| Projects | `projects_list`, `project_get`, `project_update`, `project_delete`* |
| Labels | `labels_list`, `label_create`, `label_delete`*, `labels_bulk_set_on_task` |
| Session | `whoami` |

\* safe-mode behavior as above. Never call a name `tools/list` did not return.
