# product-owner

Run any ticket board as product owner — one discipline, per-tool adapters. Ticket
intake, refinement to a research-backed Definition of Ready, binary acceptance criteria
with verification, an **agent-ready gate** for work AI coding agents execute,
prioritization and pick-up ordering, WIP limits anchored on review capacity, dependency
sequencing, splitting, backlog sweeps, evidence-based closing on a Definition of Done,
and flow metrics (Work Item Age, Cycle Time, Throughput, SLE).

The skill carries the **role** (loop, gates, heuristics, protocols — every major rule
traced to 2026 evidence in `rationale.md`). Adapters carry the **tool mechanics**
(Vikunja MCP, ClickUp MCP — both verified live). Your repo carries the **instance
facts** in a Board contract (below). Instance *operations* (MCP deployment, token
rotation) stay in your instance's ops runbook.

It consolidates and supersedes the earlier `vikunja-product-owner` plugin (this repo)
and generalizes the craft of the code14 `clickup-product-owner` / `team-c-grooming`
skills.

## Install

**Claude Code plugin** — wires the webgrip `vikunja` MCP server for you:

```json
// .claude/settings.json
"enabledPlugins": { "product-owner@ai-skills": true }
```

The bundled `.mcp.json` points at `https://mcp-vikunja.webgrip.dev/mcp` (LAN-only); a
repo-level `.mcp.json` entry named `vikunja` overrides it. ClickUp boards: add your own
ClickUp MCP server to the consuming repo's `.mcp.json`. Scripts override via
`VIKUNJA_MCP_URL`.

**`npx skills`** — works in every agent, but registers no MCP server; add one yourself:

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s product-owner -g
```

## Board contract — where it can live

The skill first pins the *context* (which org/team/board the task is about — explicit
mention > repo contract > user contracts' `Applies when:` headers > connected MCP; ask
when ambiguous), then merges the layers, most specific fact wins:

1. `.agents/contracts/product-owner.md` in the consuming repo — rich/bulky data you
   don't want in always-loaded context
2. the block below in the repo's `AGENTS.md` — small, always-relevant facts
3. `~/.agents/contracts/product-owner/<context>.md` — **user level**, for one person
   working across orgs/teams with globally installed skills: one file per context
   (`webgrip.md`, `code14.md`, `code14-team-c.md`), each opening with `Context:`,
   `Applies when:` (repo remotes, MCP names, board ids, keywords) and optionally
   `Extends: code14.md` so a team file carries only its deltas
4. a `product-owner-contract` skill in your org's own skills repo, installed alongside
   this one — org-wide defaults, published once

Contracts carry **facts** (ids, caps, language, policies). A team that wants different
*behavior* — another DoR, its own rework loop — gets a **team overlay skill** that
composes with this one (code14's `team-c-grooming` is the live example), not a bigger
contract. Layering guide: [docs/contract-pattern.md](../../docs/contract-pattern.md).
Without any layer, the skill inspects the connected MCP, lists projects/boards, and
asks. Delete lines that don't apply to your tracker.

```markdown
## Board contract (product-owner)

- Tracker: vikunja | clickup · MCP server: `vikunja` | `clickup`
- Board: project/list `<name>` (id <N>) · [vikunja] instance list cap (maxitemsperpage): <50|250>
- Ticket language: <en|nl|...> · ticket prefix / commit trailer: `VIK-<id>` | `Refs CU-<id>`
- Statuses/stages: <the board's own set, mapped to caught/refining/ready/started/review/finished>
  [vikunja default: labels needs-refinement / ready / agent-ready / review + done]
- Taxonomy: <theme/area labels or tags> · impact/H|M|L · effort/S|M|L · time/hours|days|weeks ·
  uncertainty/low|med|high · [custom fields the space actually has]
- WIP caps: started ≤ <3> · agent tickets in flight per human reviewer ≤ <3-5> · review ≤ <N>
- do-next cap: <10> · pick-up queue: <where it lives, e.g. project description> · open target: ≈<N>
- Risk tiers: human-review-mandatory paths: <auth, billing, migrations, ...>
- DoD: <link to the team's own, else the skill's portable default applies>
- Top-up ground truth: `git log --oneline <last-sweep>..HEAD` · <verification scripts> ·
  audit dimensions: <security · reliability · CI/DX · ...>
- Instance ops (tokens, MCP deployment): <runbook path/URL>
```

## Example prompts

- "make a ticket for the flaky backup job" · "maak een ticket voor de trage pipeline"
- "what should we work on next?" · "refine the next 10 tickets" · "split this, it's too big"
- "is this ticket ready for an agent to pick up?" · "prepare these tickets for Copilot/Claude"
- "run a board-health audit" · "what's our cycle time — can we state an SLE?"
- "take inventory and top up the roadmap" · "groom the customer backlog"

## Files

`SKILL.md` (role core: contract, loop, skeleton, gates, DoD, prioritization, invariants) ·
`refine.md` (refinement execution: interview, criteria craft, EARS, templates, splitting,
bulk fan-out) · `agents.md` (AI-executor layer: agent-ready gate, claim/evidence/accept,
risk tiers, anti-reward-hacking) · `playbook.md` (operation recipes) · `flow.md` (flow
metrics + SLE) · `rationale.md` (the 2026 evidence base, sourced) ·
`adapters/vikunja.md` + `adapters/clickup.md` (tool mechanics) ·
`scripts/ticket_lint.py` (offline DoR/agent-ready gate check, EN+NL, markdown+HTML) ·
`scripts/flow_metrics.py` (offline flow metrics from normalized JSON) ·
`scripts/mcp_client.py` (streamable-HTTP MCP client for bulk work).
