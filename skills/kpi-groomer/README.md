# kpi-groomer

Define, groom and facilitate KPI sets for teams, organizations, projects and people —
definition hygiene, Goodhart pairs, KPI-choosing workshops, dashboard traceability, and
the ethics gate for person-level metrics.

The skill carries the *craft*; your organization's *instance facts* (which teams, which
dashboards, where definitions live) belong in a **Measurement contract** block in the
consuming repo's `AGENTS.md` (or CLAUDE.md). The skill resolves that block first, the
same way the `product-owner` skill resolves its Board contract.

## Measurement contract template

Copy into the consuming repo's `AGENTS.md` and fill in:

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
