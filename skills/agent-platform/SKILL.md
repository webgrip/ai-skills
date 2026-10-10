---
name: agent-platform
description: Runs coding agents for a team - an LLM gateway (LiteLLM virtual keys, teams, budgets, MCP tool grants), scoped read-only agent tools enforced in the data proxy (one MCP server per scope, vmauth extra_label), and Claude Code usage telemetry with the organisation boundary in the collector (OpenTelemetry, Alloy OTTL filter, dashboards, cost per team). Use when putting LiteLLM or another gateway in front of Claude Code, Codex or opencode; minting agent keys or giving agents MCP tools; agents see no tools, get 403 on /mcp, or the gateway crash-loops after an MCP config change; limiting which metrics or logs an agent may query; locking down MCP servers reachable without login; rolling out Claude Code OpenTelemetry or an AI usage dashboard; personal or other organisations' sessions showing up in the collector, or telemetry set in .claude/settings.json no longer arriving; or asking what agents cost per team or repo.
---

# Agent platform — gateway, scoped tools, usage telemetry

Each plane has one boundary that neither the agent nor a developer's settings can move. Put the
control there and prove it with an attack, never with a happy-path demo.

| Plane | The boundary | Not a boundary |
| --- | --- | --- |
| Inference and spend | the gateway key: team id, budget, its own MCP grant | a model allowlist behind an auto-routing alias, a prompt |
| Agent tools | the data proxy behind a per-scope tool server (`extra_label`) | tool-server flags, `extra_filters[]`, a hidden dashboard |
| Usage telemetry | the collector filter on the repository owner | `.claude/settings.json` in a repo, a developer's opt-in |

Recipes and config: [references/gateway.md](references/gateway.md) ·
[references/tools.md](references/tools.md) · [references/telemetry.md](references/telemetry.md).
Scripts: `scripts/mcp_probe.py` (one key's MCP grant, end to end) and `scripts/otlp_cases.py`
(a collector filter against synthetic OTLP). Python 3.9+, stdlib only.

## Gateway: teams, keys, budgets

1. **Teams as code.** Keep each team (models, `max_budget`, `budget_duration`, rate limits,
   `mcp_access_groups`) in git with a fixed `team_id` equal to its alias, and converge it on a
   schedule through `/team/list`, `/team/new`, `/team/update`. Report a team found under another
   id; never delete it.
2. **Budgets cap spend.** Behind an auto-routing model alias the key's model list states intent,
   not a limit; the team budget is the control.
3. **Deny MCP by default:** `general_settings.require_key_mcp_access_defined: true`, and give every
   team an explicit group list. With no list at any level a key reaches every MCP server, and an
   empty team list never restricts. Keys that must have no tools at all (chat front-ends) get
   `object_permission.mcp_servers: ["no-mcp-servers"]`.
4. **Mint every key with** the team's **id** (the alias fails), `key_alias`, `user_id` for a
   person, `metadata` (application, session, operator), its own
   `object_permission.mcp_access_groups`, a `duration` and a `max_budget`. Agent products mint
   one key per session. A key without a grant still runs inference, so the session continues
   silently without tools.
5. **Name MCP servers with underscores.** LiteLLM prefixes tools with `<server>-` and refuses to
   start on a hyphen in a server name, taking all inference down with it. After every gateway
   config push, watch the pod's containers and `/health/liveliness` until restarts stop.
6. **Claude Code:** `ANTHROPIC_BASE_URL` is the gateway root (Claude Code appends
   `/v1/messages`); the key goes in `ANTHROPIC_AUTH_TOKEN` (Bearer) or `ANTHROPIC_API_KEY`
   (`x-api-key`). Distribute both through managed settings; managed
   `allowedProviders: ["customEndpoint"]` makes the gateway the only destination. The gateway
   forwards `anthropic-beta`, `anthropic-version` and `cache_control` untouched and streams SSE
   unbuffered, or prompt caching dies without an error. `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` adds
   per-subagent and per-prompt attribution headers.
7. **Pin the gateway image by digest** with a release-age delay
   ([references/gateway.md](references/gateway.md#gateway-config)).
8. **Answer "who uses it?" from data:** page `/key/list` (100 per page), and count `tools/call`
   in the tool servers' own logs. `initialize` and `tools/list` at proxy restarts are not use.

## Prove a key's grant

1. Mint a throwaway key: 1 hour, a $0.01 budget, an alias, the groups under test.
2. `PROBE_KEY=... python3 scripts/mcp_probe.py --url https://GATEWAY/mcp --token-env PROBE_KEY --auth-header x-litellm-api-key --forbid 'update_|create_|delete_|write'`
   runs `initialize`, `notifications/initialized` and `tools/list` (every page); add
   `--call TOOL --arguments '{...}'` for one real call and `--require TOOL` per tool that must
   be there.
3. Delete the key, then rerun with `--expect denied`: the answer must be 401.
4. A key in the same team without the grant, `--expect denied`: 403 or an empty list.

Exit 0 as expected, 1 expectation failed, 2 unusable. The token is read from the named variable
and never printed; the master key stays in a variable too.

## Scoped read-only tools

1. **Decide first: confidentiality or noise?** Only confidentiality (clients, contracts,
   per-person data) is worth a boundary per scope. Scopes stay coarse (a team, a client group):
   the proxy enforces one label value per credential.
2. **Grant like a delegate.** Read groups `observability-read-<scope>`, write groups separate
   and never granted with read by default. A scoped agent key is minted only when the human
   starting the session holds that scope.
3. **One read-only tool server per scope**, reachable only through the gateway, talking only to
   the filtering proxy with that scope's credential. Header passthrough stays off: LiteLLM
   forwards client `x-mcp-<server>-<header>` headers, so a passthrough lets a caller swap the
   credential. Disable tools the proxy refuses anyway.
4. **Enforce in the proxy with `extra_label=<label>=<scope>`** (ANDed, overrides the client), never
   `extra_filters[]` (ORed: a client widens it with its own). Allowlist the query paths, give
   agents and dashboards separate proxy users, and copy unlabelled series per scope with recording
   rules or they vanish.
5. **Prove it, then rely on it:** replay every dashboard query with and without the proxy, replay
   another scope's queries through this credential, then attack: no and wrong credentials, a
   client `extra_filters[]`, a label override, `label_replace`, export, federate, admin, rules,
   `/vmui`, `/prometheus/` aliases, traversal. Commands: [references/tools.md](references/tools.md#replay-then-attack).
6. **After any flag change** on a tool server holding a write-capable token, list its advertised
   tools with `--forbid`; only RBAC on its own credential is a guarantee.
7. **No unauthenticated tool server on the network.** Inventory every route, make the gateway the
   only door, check access logs before removing a route, and confirm afterwards that the route
   answers nothing and the name no longer resolves.
8. **A surface that reads untrusted content** (web search, inbound mail, public issues) gets no
   write-capable tools. Servers that act with each caller's own credential stay off the shared
   gateway.

In Grafana OSS any org member can query every datasource in the org, so hiding a dashboard hides
no data; org and datasource design is the grafana-access skill's.

## Usage telemetry (Claude Code OpenTelemetry)

1. **Enable at user or managed level.** From Claude Code 2.1.282 a repository's
   `.claude/settings.json` and `.claude/settings.local.json` cannot turn telemetry on, set its
   endpoint or capture content; `-p` runs give no warning. Check which binary people run: the VS
   Code extension bundles its own, often newer than `claude` on `PATH`.
2. **Tag with the repository:** `OTEL_METRICS_INCLUDE_REPOSITORY=true` (2.1.269+) in the same
   snippet; it still applies from project settings. Metrics only by default; events and content
   flags each need a question that justifies them.
3. **Opt-out per repository** is `OTEL_METRICS_EXPORTER=none` and `OTEL_LOGS_EXPORTER=none` in its
   `.claude/settings.local.json`. `CLAUDE_CODE_ENABLE_TELEMETRY=0` there does nothing, and no repo
   value beats a managed selector.
4. **The collector is the organisation boundary.** User-level settings cover every session on the
   laptop: personal repos, other organisations, sessions outside any repo. Drop `claude_code.*`
   datapoints whose `vcs.owner.name` (datapoint or resource) misses an anchored
   `^<org>(/.*)?$`, drop Claude Code events you do not use, and strip `user.email`, the account
   ids, `user.id` and `session.id` (Claude Code has no switch for the email). Start from
   [assets/org-only-filter.alloy](assets/org-only-filter.alloy); use `metric_conditions` and
   `log_conditions`, not the deprecated blocks.
5. **Prove the filter before it touches a shared collector:** `alloy fmt`, then the same Alloy
   version locally with a debug exporter, `python3 scripts/otlp_cases.py send --org <org>`, and
   `docker logs <container> 2>&1 | python3 scripts/otlp_cases.py check - --org <org> --expect-stripped`.
   Any `leak`, `overblock` or `identifier` finding blocks the rollout.
6. **Live means live:** after the GitOps deploy, the new component shows in the collector's own
   API, the endpoint still answers, and unrelated signals still arrive.
7. **Audit owners over 90 days** with a series query, right after enabling and after every
   settings change. Clean leaks by counting per owner, then deleting with the same negative
   match; hand the delete to a human.
8. **Dashboards query-first:** run each panel's query against the TSDB, select dotted names with
   `{__name__="claude_code.cost.usage"}`, put the owner regex in every selector, show a count of
   developers and never names, and ship the dashboard as a GitOps resource.

Who may see per-person usage, and whether the works council must consent first, is the
kpi-groomer skill's ethics gate; until it says yes, aggregate to team or repository.

## Reading the numbers

- `claude_code.cost.usage` is a list-price estimate for every auth method, not the bill.
- Cache reads are most of the tokens, so always-loaded context is paid on every request.
- Team usage: map people to teams through the roster, one primary team each, every active person
  in the denominator, kiosks, bots and service accounts excluded.
- Agent-assisted commits: count co-author and `Assisted-by` trailers with `git log --grep`.
- Per person, on their own laptop: ccusage (local transcripts, no upload).
- Per-branch cost needs events with tool details, which log commands and paths: a privacy
  trade-off, not a free switch.
- Send events or deltas; re-sending cumulative aggregates to a summing backend double-counts.

Details and queries: [references/telemetry.md](references/telemetry.md#reading-the-numbers).

## Gotchas

- Every MCP streamable-HTTP request needs `Accept: application/json, text/event-stream`, or the
  server answers 406; responses arrive as SSE `data:` lines.
- `IsMatch` is unanchored and false on a missing attribute: `code` in a regex also matches
  `codex`, and `not IsMatch` drops unlabelled data.
- Escape a literal dot as `[.]` in OTTL inside YAML; backslashes change meaning per layer.
- A dashboard built on Prometheus-style names (`claude_code_cost_usage_USD_total`) shows no data
  on a store that keeps OTel names.
- A harness may report a gateway error as a normal end of turn: check content, not stop reason.
- An embedded documentation tool can cost a tool server most of its memory; measure with it off.
