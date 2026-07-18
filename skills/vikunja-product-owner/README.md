# vikunja-product-owner

Run a Vikunja board as product owner, end-to-end, through the `vikunja` MCP server: ticket CRUD,
Definition-of-Ready refinement, prioritization/do-next curation, dependency sequencing, backlog
top-up/inventory, board-health audits, and the agent work protocols (ticket-reference commit
trailers, claim/completion with evidence).

The skill carries the **role** — loop, DoR, heuristics, invariants, API mechanics (all verified
live against the `@aimbitgmbh/vikunja-mcp` server). Your repo carries the **instance facts** in a
Board contract (below). Instance *operations* (MCP deployment, API-token creation/rotation) stay
in your instance's ops runbook — not in this plugin.

## Install

**Claude Code plugin** — the only route that wires the MCP server for you:

```json
// .claude/settings.json
"enabledPlugins": { "vikunja-product-owner@ai-skills": true }
```

The plugin ships the webgrip `vikunja` MCP server config (`.mcp.json` at plugin root —
`https://mcp-vikunja.webgrip.dev/mcp`, LAN-only). A repo-level `.mcp.json` entry with the same
server name overrides it; scripts can override via the `VIKUNJA_MCP_URL` env var.

**`npx skills`** — works in every agent, but the skill is useless without a `vikunja` MCP server,
and the CLI copies the bundled `.mcp.json` without registering it:

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s vikunja-product-owner -g
```

Add the server yourself to the consuming repo's `.mcp.json` (point `url` at your own instance):

```json
{ "mcpServers": { "vikunja": { "type": "http", "url": "https://mcp-vikunja.example.com/mcp" } } }
```

## Board contract (add to your repo's AGENTS.md)

The skill resolves this block first; without it, it lists projects and asks.

```markdown
## Board contract (vikunja-product-owner)

- MCP server: `vikunja` · project: `<name>` (id <N>) · instance list cap (maxitemsperpage): <50|250|…>
- Ticket prefix: `VIK` (commit trailers `VIK-<taskID>`)
- Labels: `theme/<...list your themes...>` · `impact/H|M|L` · `effort/S|M|L` · `do-next` (≤10) ·
  `ready` / `needs-refinement` / `agent-ready` · `agent/<name>` (claims)
- Open target: ≈<N> tickets · buckets: Backlog / Ready / In progress (agent) / Review / Done
- Top-up ground truth: `git log --oneline <last-sweep>..HEAD` · `<repo verification scripts>` ·
  audit dimensions: <e.g. security · reliability · CI/DX>
- Instance ops (token rotation, MCP deployment issues): <runbook path/URL>
```

## Example prompts

- "make a ticket for the flaky backup job" · "what should we work on next?"
- "refine the next 10 tickets" · "split this ticket, it's too big"
- "take inventory and top up the roadmap" · "run a board-health audit"

## Files

`SKILL.md` (role core: loop, conventions, DoR, heuristics, invariants, protocols, gotchas) ·
`reference.md` (MCP response formats, pagination, tool catalog) · `refine.md` (DoR execution +
HTML template + bulk fan-out) · `playbook.md` (call-sequence recipes incl. top-up sweep) ·
`scripts/mcp_client.py` (streamable-HTTP MCP client for bulk work).
