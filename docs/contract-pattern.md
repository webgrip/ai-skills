# The contract pattern — one generic skill, your facts in your repo

How a shared skill (like `product-owner` or `kpi-groomer`) works for *your* team
without anyone forking or editing it.

## The problem it solves

A skill is a procedure an AI agent loads: how to refine a ticket, how to groom a KPI
set. That craft is the same everywhere. But the *facts* differ per organization and per
repo: which board, which ids, which language, which dashboards, who the teams are. Bake
one org's facts into the skill and it breaks for everyone else — and every fact change
needs a skill release. Fork the skill per org and the copies drift apart within a month.

## The split

| Layer | What lives there | Where |
| --- | --- | --- |
| **Skill** | The craft: procedures, gates, heuristics, gotchas. Generic, versioned, shared by everyone. | This marketplace (`skills/<name>/`) |
| **Contract block** | Your instance facts: ids, URLs, team names, language, caps, policies. | *Your* repo's `AGENTS.md` (or CLAUDE.md) |
| **Adapter** | Tool mechanics (Vikunja vs ClickUp API traps). | Shipped inside the skill |

At runtime the skill **resolves the contract first**: it reads your repo's `AGENTS.md`,
finds the contract block, and only then acts — with your board, your dashboards, your
rules. No contract block? The skill says so and helps you add one.

So "extending a skill with our data" = **adding a contract block to your repo**. One
markdown block, no skill edit, no release, and the next person (junior included) who
runs the skill in that repo gets all of it automatically.

## The two live examples

- **Board contract** — used by the `product-owner` skill: tracker + MCP server,
  project/list ids, status roles, ticket language, WIP caps, DoD location. Template:
  [skills/product-owner/README.md](../skills/product-owner/README.md)
- **Measurement contract** — used by the `kpi-groomer` skill: where KPI definitions
  live, the measurement charter, dashboard base URL + access, teams in scope,
  person-level metrics policy. Template:
  [skills/kpi-groomer/README.md](../skills/kpi-groomer/README.md)

## Adding one to your repo

1. Open the skill's README in this marketplace and copy its contract template.
2. Paste it into your repo's `AGENTS.md` and fill in the facts. Unknown yet? Write
   `not ratified yet` / `TBD — owner: <name>` rather than guessing.
3. Done. Commit it like any other change — the facts now travel with the repo, are
   reviewed in MRs, and stay next to the code they describe.

## Rules of thumb — what goes where

- **Craft** (how to do the work, anywhere) → the skill. Improve it here, once, for all.
- **Instance facts** (ids, URLs, names, policies) → the contract block in the consuming
  repo. Never into the skill.
- **Operational procedures** (how to restart X, rotate Y) → the origin repo's runbook;
  the contract may point at it.
- **Always-on repo rules** (build commands, invariants) → that repo's own
  CLAUDE.md/AGENTS.md, outside the contract block.

One test when you're unsure: *would this line be true in a different organization using
the same skill?* True → skill. Only true here → contract.
