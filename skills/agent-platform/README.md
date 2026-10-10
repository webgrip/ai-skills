# agent-platform

Run coding agents for a team with each control where neither the agent nor a developer's
settings can move it: an LLM gateway (LiteLLM teams as code, per-key budgets and deny-by-default
MCP grants minted with the team id, Claude Code routed through it without breaking prompt
caching), scoped read-only agent tools (one MCP server per scope behind a VictoriaMetrics proxy
that enforces `extra_label`, proven by replay and attack, no unauthenticated tool routes, no write
tools on surfaces that read untrusted content), and Claude Code usage telemetry (enabled at user
or managed level, the organisation boundary as an OTTL filter in the collector, identifiers
stripped there, dashboards built query-first, leaks audited and cleaned, usage attributed to
teams honestly).

Person-level visibility and works-council consent belong to `kpi-groomer`; Grafana org and
datasource design to `grafana-access`; instruction files and agent config to
`agent-instructions`.

Ships:

- `scripts/mcp_probe.py` — runs the MCP streamable-HTTP handshake for one key against a gateway
  or tool server: grant present, grant revoked, forbidden write tools advertised, required tools
  missing, one real call. Reads the token from an environment variable and never prints it.
- `scripts/otlp_cases.py` — posts twelve synthetic OTLP cases (the organisation, nested groups,
  lookalike owners, no repository, other services, Claude events) to a local collector and reads
  its debug output back: `leak`, `overblock` and `identifier` findings.
- `assets/org-only-filter.alloy` — a tested Alloy pipeline: owner filter, identifier transform,
  debug exporter. `test.sh` checks both scripts against stub servers and real Alloy output.

**Install:**

```text
/plugin install agent-platform@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s agent-platform`.

**Try:** "put LiteLLM in front of our Claude Code and opencode agents", "our agent's key gets 403
on /mcp", "give agents read-only access to their own team's metrics", "roll out Claude Code
telemetry to the team", "the collector is receiving my personal repos' usage", "telemetry in our
repo's .claude/settings.json stopped arriving", "what do agents cost per team?".
