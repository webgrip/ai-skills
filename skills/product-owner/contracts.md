# Board contracts — the template and the layer file shapes

The resolution order and the facts-vs-behavior rule are in [SKILL.md](SKILL.md); this
file is what each layer *looks like*. Contracts carry facts; nothing secret goes in any
layer (name where a credential lives, never the credential).

## The template (any layer)

Delete lines that don't apply to your tracker; unknown facts get `TBD — owner: <name>`,
never a guess.

```markdown
## Board contract (product-owner)

- Tracker: vikunja | clickup · MCP server: `vikunja` | `clickup`
- Board: project/list `<name>` (id <N>) · [vikunja] instance list cap (maxitemsperpage): <50|250>
- Ticket language: <en|nl|...> · ticket prefix / commit trailer: `VIK-<id>` | `Refs CU-<id>`
- Task web base (cross-references): `https://app.clickup.com/t/` | `<instance>/tasks/`
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

Small and always-relevant → paste as this block in the repo's `AGENTS.md`. Rich or
bulky (id tables, status ladders, field catalogs) → `.agents/contracts/product-owner.md`
instead — loaded only when the skill fires.

## Layer 3 — user contexts (one person, many orgs/teams)

Globally installed skills have no repo to read from. A directory of named contexts:

```text
~/.agents/contracts/product-owner/
├── webgrip.md
├── code14.md          ← org base
└── code14-team-c.md   ← Extends: code14.md — only the Team C deltas
```

Each file opens with headers the skill matches on before any merge:

```markdown
Context: code14 / Team C
Applies when: ClickUp MCP, boards in workspace <id>, klant boards by name,
  or the user says "code14" or "team C"
Extends: code14.md
```

`Extends:` keeps team files small — a team file carries only its deltas over the org
file.

## Layer 4 — the org contract skill

An org that ships its own skills estate publishes its facts once, for every colleague,
as a sibling skill named `product-owner-contract` (the base skill matches
`product-owner-contract*`). Shape:

```text
skills/product-owner-contract/
├── SKILL.md                    ← routes the org's boards; per-team Context /
│                                 Applies when blocks; facts only, no craft
├── teams/<team>/board.md       ← that team's contract: statuses, gates, field
│                                 ids, tags, house rules
└── teams/<team>/assets/        ← that team's hand-over docs (ratified DoR,
                                  golden tickets, fill-in template)
```

Its SKILL.md description names the org's boards, teams and customers — that is what
routes it; the base skill stays org-free. Board files reference the base skill's
playbook/refine **by name, never by relative path** (sibling skills don't share a
directory once installed). Everything in it must pass the fact test: *would this line
be true in a different organization?* True → it belongs in the base skill instead —
contribute it upstream.

## Behavior is not a contract

A team wanting a genuinely different *procedure* — another DoR, an extra rework loop,
its own ticket types — writes a **team overlay skill** in the org's estate that
composes with this one, and keeps facts in the contract. The test: *could you express
it as a key–value fact?* Yes → contract. No, it changes the steps → overlay skill.
