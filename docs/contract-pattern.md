# The contract pattern — one generic skill, your facts layered in

How a shared skill (like `product-owner` or `kpi-groomer`) works for *your* team
without anyone forking or editing it — and where to put facts you do **not** want in
`AGENTS.md`.

## The problem it solves

A skill is a procedure an AI agent loads: how to refine a ticket, how to groom a KPI
set. That craft is the same everywhere. But the *facts* differ per organization and per
repo: which board, which ids, which dashboards, which teams. Bake one org's facts into
the skill and it breaks for everyone else. Fork the skill per org and the copies drift
apart within a month.

The wider ecosystem has no native answer: `npx skills` ([vercel-labs/skills](https://github.com/vercel-labs/skills))
vendors skill folders into per-agent directories (`.claude/skills/`, `.agents/skills/`,
symlink or copy), tracks them in `.skills.json` + `skills-lock.json`, and refreshes them
with `npx skills update` — which **overwrites local edits**. Neither the CLI nor the
[agentskills spec](https://agentskills.io) defines overrides, config files, or
inheritance. So extension is a *convention the skill itself implements*: the skill
resolves a **contract** before acting. This estate's skills use the three layers below.

## The three contract layers — most specific wins

| Layer | Where | Use it for |
| --- | --- | --- |
| **1 · Repo contract file** | `.agents/contracts/<skill>.md` in the consuming repo | Anything too big, too detailed, or too situational for always-on context: dashboard catalogs, id tables, team rosters, policy text. Loaded **only when the skill fires** — costs nothing until then. |
| **2 · `AGENTS.md` block** | `## <Skill> contract` section in the consuming repo's `AGENTS.md`/CLAUDE.md | The handful of small facts every session benefits from (which tracker, ticket language, WIP cap). Keep it short — this file is always-loaded context. |
| **3 · Org contract skill** | A `<skill>-contract` skill directory in your org's own skills repo (e.g. `code14/ai-skills`), installed alongside the generic skill via `npx skills add <org>/<repo>` or your marketplace | Org-wide defaults shared by *all* repos: the Grafana base URL, the standard board conventions, the measurement charter. Publish once, every repo inherits — no per-repo `AGENTS.md` edits. |

Resolution order: the skill checks **1, then 2, then 3** — a repo-specific fact beats
the org default. Layers combine: the org skill carries defaults, the repo file carries
what differs here.

**Nothing secret goes in any layer** — all three are git-committed files. A contract
may *name* where a credential lives (the secret manager path); never the credential.

## The two live examples

- **Board contract** — used by the `product-owner` skill: tracker + MCP server,
  project/list ids, status roles, ticket language, WIP caps, DoD location. Template:
  [skills/product-owner/README.md](../skills/product-owner/README.md)
- **Measurement contract** — used by the `kpi-groomer` skill: where KPI definitions
  live, the measurement charter, dashboard base URL + access, teams in scope,
  person-level metrics policy. Template:
  [skills/kpi-groomer/README.md](../skills/kpi-groomer/README.md)

## Adding a contract

1. Copy the template from the skill's README.
2. Small and always-relevant? → paste as a block in your repo's `AGENTS.md`.
   Rich or bulky? → save as `.agents/contracts/<skill>.md` instead.
   Org-wide? → put it in a `<skill>-contract` skill in your org's skills repo.
3. Unknown facts get `TBD — owner: <name>`, never a guess. Commit like any change —
   facts travel with the repo, reviewed in MRs.

## Rules of thumb — what goes where

- **Craft** (true in any organization) → the skill. Improve it upstream, once, for all.
- **Instance facts** (only true here) → a contract layer, never the skill.
- **Operational procedures** (how to restart X) → the origin repo's runbook; the
  contract points at it.
- **Always-on repo rules** (build commands, invariants) → the repo's own
  CLAUDE.md/AGENTS.md, outside the contract block.

The test: *would this line be true in a different organization using the same skill?*
True → skill. Only true here → contract. Too big for every session? → layer 1 or 3,
not `AGENTS.md`.
