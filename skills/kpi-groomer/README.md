# kpi-groomer

Define, groom and facilitate KPI sets for teams, organizations, projects and people —
definition hygiene, Goodhart pairs, KPI-choosing workshops, dashboard traceability, and
the ethics gate for person-level metrics.

The skill carries the *craft*; your organization's *instance facts* (which teams, which
dashboards, where definitions live) live in a **Measurement contract** the skill
resolves before acting — most specific wins:

1. `.agents/contracts/kpi-groomer.md` in the consuming repo — rich or bulky data you
   don't want in always-loaded context
2. a `## Measurement contract` block in the repo's `AGENTS.md` (or CLAUDE.md) — the few
   small, always-relevant facts
3. a `kpi-groomer-contract` skill in your org's own skills repo, installed alongside
   this one — org-wide defaults, published once for every repo

Layering guide: [docs/contract-pattern.md](../../docs/contract-pattern.md).

## Measurement contract template

Fill in and place per the layering above:

```markdown
## Measurement contract
- KPI definitions live at: <repo path, e.g. docs/kpi/>
- Measurement charter (ethics/usage rules): <path, ADR id, or "not ratified yet">
- Dashboards: <base URL, UID convention, access requirements (VPN/SSO)>
- Teams in scope: <team → lead/contact, one per line>
- Existing data sources: <exporters, boards, APIs already flowing>
- Person-level metrics policy: <ratified audience + conditions, or "not ratified — treat as team-level only">
```

## Example prompts

- "Prepare a KPI-choosing session for the support team."
- "Review our KPI set — is this steering anything?"
- "We want per-developer metrics on a dashboard — is that OK?"
- "Which KPIs should the organization track, and what's missing from our dashboards?"

## Install

Claude Code (marketplace): `/plugin install kpi-groomer`. Other agents: copy this
directory; `SKILL.md` is the entry point.
