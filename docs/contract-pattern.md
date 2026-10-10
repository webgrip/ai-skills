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
resolves a **contract** before acting. This estate's skills use the four layers below.

## The four contract layers — most specific wins

| Layer | Where | Use it for |
| --- | --- | --- |
| **1 · Repo contract file** | `.agents/contracts/<skill>.md` in the consuming repo | Anything too big, too detailed, or too situational for always-on context: dashboard catalogs, id tables, team rosters, policy text. Loaded **only when the skill fires** — costs nothing until then. |
| **2 · `AGENTS.md` block** | `## <Skill> contract` section in the consuming repo's `AGENTS.md`/CLAUDE.md | The handful of small facts every session benefits from (which tracker, ticket language, WIP cap). Keep it short — this file is always-loaded context. |
| **3 · User contract, per context** | `~/.agents/contracts/<skill>/<context>.md` on your own machine | One person working across orgs and teams with globally installed skills — see the next section. |
| **4 · Org contract skill** | A `<skill>-contract` skill directory in your org's own skills repo (e.g. `acme/ai-skills`), installed alongside the generic skill via `npx skills add <org>/<repo>` or your marketplace | Org-wide defaults shared by *all* repos and users: the Grafana base URL, the standard board conventions, the measurement charter. Publish once, everyone inherits. |

Resolution order: the skill checks **1 → 2 → 3 → 4** — a repo-specific fact beats your
personal default, which beats the org default. Layers combine: the org skill carries
defaults, the more specific layers carry only what differs.

## User level — one person, many orgs and teams

Globally installed skills have no repo to read a contract from — and one person often
works several contexts from the same terminal: base `product-owner` for webgrip, an
acme flavor for an employer's boards, and within acme different facts for Team A than for
Team B. That is what layer 3 solves — a directory of **named contexts**:

```text
~/.agents/contracts/product-owner/
├── webgrip.md
├── acme.md            ← org base
├── acme-team-a.md     ← Extends: acme.md — only the Team A deltas
└── acme-team-b.md     ← Extends: acme.md — only the Team B deltas
```

Each file opens with two or three header lines the skill matches on:

```markdown
Context: acme / Team A
Applies when: ClickUp MCP, boards in workspace <workspace-id>, client boards
  by name, or the user says "acme" or "team A"
Extends: acme.md
```

**Context selection** happens before any merge: an explicit mention ("make an acme
ticket") wins; else the repo's own contract pins it; else the skill matches the
`Applies when:` headers; else it looks at the connected MCP and its boards; still
ambiguous → it asks one question rather than guessing. `Extends:` keeps team files
small: the team file carries only its deltas over the org file.

## Facts go in contracts — behavior goes in overlay skills

A contract parameterizes the *same* procedure with different facts (ids, caps,
language, policies). When a team genuinely wants a **different procedure** — its own
Definition of Ready, an extra rework loop, different ticket types — that is a **team
overlay skill** in the org's skills repo, composing with the base skill, not a fatter
contract. The test: *could you express it as a key–value fact?* Yes → contract. No, it
changes the steps → overlay skill. The test cuts both ways: a `team-a-grooming`
skill can look like a behavior overlay while everything in it is facts and
parameters — then it belongs in a `product-owner-contract`, a layer-4 contract skill.

**Nothing secret goes in any layer** — all four are git-committed files. A contract
may *name* where a credential lives (the secret manager path); never the credential.

## The two live examples

- **Board contract** — used by the `product-owner` skill: tracker + MCP server,
  project/list ids, status roles, ticket language, WIP caps, DoD location. Template +
  layer file shapes: [skills/product-owner/contracts.md](../skills/product-owner/contracts.md)
- **Measurement contract** — used by the `kpi-groomer` skill: where KPI definitions
  live, the measurement charter, dashboard base URL + access, teams in scope,
  person-level metrics policy. Template:
  [skills/kpi-groomer/README.md](../skills/kpi-groomer/README.md)

## Adding a contract

1. Copy the template from the skill's README.
2. Small and always-relevant? → paste as a block in your repo's `AGENTS.md`.
   Rich or bulky? → save as `.agents/contracts/<skill>.md` instead.
   Personal, cross-repo (globally installed skills)? →
   `~/.agents/contracts/<skill>/<context>.md` with `Context:`/`Applies when:` headers.
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

## If you must fork anyway

Sometimes an org forks a skill regardless — say Acme wants its colleagues on one install
of `product-owner` that already carries Acme's board section. A fork stays cheap only with
byte-equal discipline and a scripted port; without them it drifts within weeks.

- **The invariant:** only a listed set of paths and one named `SKILL.md` section (here
  `## Acme boards`) may differ from upstream. Every other file is byte-identical.
- **Upstream into the fork, by script:** copy the upstream files, re-insert the fork
  section before its anchor heading, `cmp` every other file, and prove `SKILL.md` differs
  only in that section:

  ```bash
  diff <(awk '/^## Acme boards/{s=1} /^## The loop/{s=0} !s' "$FORK/SKILL.md") "$UP/SKILL.md" \
    && echo "identical apart from the fork section"
  ```

- **Fork into upstream:** pull first (the release bot commits back) · `cmp` each file ·
  grep the candidates for org terms · copy the byte-equal files and hand-port the rest ·
  rewrite evals without org names · leave the org section and contract layers behind.
- **Corrections to upstream-owned text go upstream** (a PR) or into the fork-owned
  section — never edited in place, which breaks the invariant. Keep upstream's mentions of
  trackers you don't use.
- **Re-run the proof after every fork edit.** The first edit for a new rule is where the
  invariant usually breaks.

A fork that keeps needing more than its one section is a sign the difference is a fact
(move it into a contract layer) or a procedure (an overlay skill), not a fork.
