# Playbook — exact call sequences for common PO operations

All via MCP tools (or `scripts/mcp_client.py` `call(tool, args)` for bulk). Response parsing:
creates → `ID: <n>`; lists → `[ID: <n>, Project: <m>]`; strip ` (xxxxxx)` from label titles.
`<pid>` = the contract's project id.

## Create a ticket end-to-end

1. `task_create {title, projectId: <pid>, priority: <5|4|3|2>, description: "<HTML first para: theme + tag>"}`
2. `labels_bulk_set_on_task {taskId, labelIds: [<theme>, <impact>, <effort>, <needs-refinement>]}`
   — REPLACES the whole set; always pass everything.
3. New tickets are `needs-refinement`; refinement ([refine.md](refine.md)) is a separate pass.

## Split an oversized ticket

1. `task_create` each child (inherit theme/impact labels; honest per-child effort).
2. `relation_create {taskId: <parent>, otherTaskId: <child>, relationKind: "subtask"}` per child.
3. `relation_create {taskId: <first>, otherTaskId: <second>, relationKind: "precedes"}` where order matters.
4. Parent keeps the outcome; children carry the ACs. Re-label parent `effort` honestly.

## Close with evidence

1. `comment_create {taskId, comment: "<p>Done: <evidence — commit hash, live check output, link>.</p>"}`
2. `task_complete {id}` — never without the ticket's own Verification satisfied.
3. If the ticket held a pick-up-queue entry, drop its line (queue emit below).

## Pick-up queue emit / insert

The queue lives in the **project description** (conventions in SKILL.md) because the MCP has no
position API. `project_update` REPLACES the whole description — always round-trip:

1. `project_get {id: <pid>}` → current description; keep everything OUTSIDE the
   `<h3>Pick-up queue</h3>` section verbatim.
2. Rebuild the section:
   `<h3>Pick-up queue</h3><p><em>top = picked up first · refreshed <date></em></p>`
   `<ol><li><PREFIX>-<id> — <exact title></li>…</ol>` — every `do-next` holder first, then the
   next-up tail (≤ 2× the do-next cap total); never rank a ticket above its blocker.
3. `project_update {id: <pid>, description: "<merged HTML>"}`; spot-check with `project_get`.
4. Inserting one ticket = same round-trip with the new `<li>` where it fits (not appended).

Refresh triggers: do-next rebalance · a queue ticket closes · a new/refined ticket outranks an
existing entry · top-up sweep step 4.

## Stale-premise verify-and-close

1. Research says the work already shipped → `task_update` the description: Problem becomes
   "Premise stale — shipped in <commit/date>; remaining work = verify"; ACs become the
   verification checks.
2. Run the checks now if cheap → close with evidence; else leave `ready` as a quick win.

## Top-up / inventory sweep (periodic; keeps the backlog at the contract's open target)

1. **Ground truth** — the contract's commands (typically: `git log --oneline <last-sweep>..HEAD`,
   the repo's posture/verification scripts, live read-only checks). Don't trust ticket text.
2. **Read the board** — `tasks_list {projectId: <pid>, show: "all", limit: <cap>}`; index open AND
   recent completions by title (the dedup pool); verify "Found N" covers the board.
3. **Fan out parallel Explore audits** (one message) over the contract's audit dimensions, each
   briefed with the full ALREADY-DONE list so they only return open gaps; ask for candidates as
   `title · file:line · Impact · Effort`; tell them to verify, not guess (they over-report).
4. **Reconcile** — shipped → close with evidence · stale premise → verify-and-close rewrite ·
   new findings → filter against the repo, dedupe against ALL open+recent titles, then create
   (`needs-refinement`) · re-tag honestly · do-next rebalance (below).
5. **Report** counts + the new do-next set + any audit evidence that belongs in docs, not tickets.
   This sweep *plans*; implementing a ticket is a separate change.

## Board-health audit (invariants from SKILL.md)

Fetch `tasks_list {projectId: <pid>, show: "all", limit: <cap>}` once, then:

- **Count**: reported "Found N" ≈ the contract's open target — pagination sanity.
- **Label coverage**: every open ticket parses `theme/`, `impact/`, `effort/` from its labels.
- **do-next ≤ cap**: count holders.
- **Queue**: `project_get` → every `do-next` holder has a queue line, every queue line's ID is an
  open ticket, no entry above its blocker.
- **ready ⇒ DoR**: `ready` tickets' descriptions contain `<h3>Problem</h3>`,
  `data-type="taskList"`, `<h3>Verification</h3>`.
- **Relations**: spot-verify via duplicate-create → expect
  `409: The task relation already exists` (relations never render in `task_get`).

## do-next rebalance

1. List current holders; drop any now-blocked/stale (`label_remove_from_task`).
2. Add highest-leverage unblocked (`label_add_to_task`) up to the contract's cap.
3. Re-emit the pick-up queue (membership changed ⇒ order changed).
4. Say what changed and why in the run report.

## Bulk relabel / bulk update

- Same label to many: loop `label_add_to_task` (safe, additive).
- Same field to many: `tasks_bulk_update {taskIds: [...], fields: ["priority"], values: {priority: 3}}`.
- Full label-set rewrite: `labels_bulk_set_on_task` with the COMPLETE intended set per task.

## Dedupe sweep

1. Build a title map from the full list; near-duplicates (same outcome, different words) →
   keep the better-refined one.
2. Loser: `comment_create` pointing at the survivor by exact title → `task_complete`
   (soft "closed as duplicate"; `duplicateof` relation optional for the record).
