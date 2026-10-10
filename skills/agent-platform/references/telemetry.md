# Agent usage telemetry — settings, metrics, collector, dashboards

Contents: [Where telemetry can be set](#where-telemetry-can-be-set) ·
[Rollout snippets](#rollout-snippets) · [Metrics and attributes](#metrics-and-attributes) ·
[Events, content and traces](#events-content-and-traces) ·
[The collector boundary](#the-collector-boundary) · [Prove the filter](#prove-the-filter-with-otlp_casespy) ·
[After the rollout](#after-the-rollout) · [Audit and clean leaked data](#audit-and-clean-leaked-data) ·
[Dashboards](#dashboards-query-first) · [Reading the numbers](#reading-the-numbers) · [Sources](#sources)

## Where telemetry can be set

Claude Code 2.1.282 and later drop the variables that turn export on, choose its destination or
capture content when they come from a repository's `.claude/settings.json` or
`.claude/settings.local.json`.

| Variable | Managed, `--settings`, shell, `~/.claude/settings.json` | Project and local settings |
| --- | --- | --- |
| `CLAUDE_CODE_ENABLE_TELEMETRY`, `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA` | applies | ignored, `0` included |
| `OTEL_{METRICS,LOGS,TRACES}_EXPORTER` | applies | only `none` applies |
| `OTEL_EXPORTER_OTLP_*` ending `_ENDPOINT`, `_HEADERS`, `_PROTOCOL`, `_CERTIFICATE`, `_CLIENT_KEY`, `_INSECURE` | applies | ignored |
| `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT` | applies | only an off value such as `0` applies |
| `OTEL_LOG_ASSISTANT_RESPONSES`, `OTEL_LOG_RAW_API_BODIES` | applies | ignored |
| `OTEL_METRICS_INCLUDE_REPOSITORY`, `OTEL_RESOURCE_ATTRIBUTES`, interval, temporality | applies | applies after workspace trust (not on the ignore list) |

- Precedence, highest first: managed, `--settings`, local, project, user. A settings `env` value
  overwrites the same shell export.
- A project off value overrides user settings, never managed settings, a `--settings` file or the
  launch environment. Put the exporter selectors in managed settings only when nobody may opt out.
- Interactive sessions show a startup notice for ignored variables, and `/status` or
  `claude doctor` list them. `-p` and SDK runs show nothing: after an upgrade, confirm the
  collector still receives data.
- `OTEL_*` variables are not passed to subprocesses (Bash tool, hooks, MCP servers).
- The VS Code extension runs its own bundled binary, which can be far ahead of `claude` on `PATH`.
  The agent-instructions skill covers checking the version per entrypoint.

## Rollout snippets

User or managed settings, every session on the machine:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://otlp.example.org",
    "OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE": "cumulative",
    "OTEL_METRIC_EXPORT_INTERVAL": "60000",
    "OTEL_METRICS_INCLUDE_REPOSITORY": "true"
  }
}
```

- `OTEL_EXPORTER_OTLP_PROTOCOL` has no default; set it for every `otlp` exporter.
- Cumulative temporality suits backends queried with `increase()`; the default is delta.
- No `OTEL_LOGS_EXPORTER`: no events, no prompt text. Add events only for a question that needs them.
- `OTEL_METRICS_INCLUDE_REPOSITORY` (2.1.269+) adds `vcs.owner.name`, `vcs.repository.name`,
  `vcs.provider.name` and `vcs.repository.url.full`, derived from `origin` and lowercased. Without
  it the collector filter drops everything as "no repository".
- A collector that needs a credential: set the whole export in managed settings, or use
  `otelHeadersHelper` for a rotating token. Managed endpoint, protocol or headers remove the
  developer's conflicting per-signal values.
- An endpoint reachable only on the office network or VPN undercounts "developers sending".

Opt-out for one repository, in its `.claude/settings.local.json`:

```json
{ "env": { "OTEL_METRICS_EXPORTER": "none", "OTEL_LOGS_EXPORTER": "none" } }
```

## Metrics and attributes

| Metric | Unit | Extra attributes |
| --- | --- | --- |
| `claude_code.session.count` | count | `start_type` |
| `claude_code.cost.usage` | USD | `model`, `query_source`, `speed`, `effort`, `agent.name`, `skill.name`, `plugin.name`, `marketplace.name`, `mcp_server.name`, `mcp_tool.name` |
| `claude_code.token.usage` | tokens | `type` (`input` without cache, `output`, `cacheRead`, `cacheCreation`) plus the cost set |
| `claude_code.lines_of_code.count` | count | `type` (`added`, `removed`), `model` |
| `claude_code.commit.count` | count | standard only |
| `claude_code.pull_request.count` | count | standard only; merge requests count too |
| `claude_code.code_edit_tool.decision` | count | `tool_name`, `decision`, `source`, `language` |
| `claude_code.active_time.total` | s | `type` (`user`, `cli`) |

- **Names in the backend:** a store that keeps OpenTelemetry names over OTLP stores the dots;
  select with `{__name__="claude_code.cost.usage"}`. Dashboards written for Prometheus-normalised
  names (`claude_code_cost_usage_USD_total`) then show no data. List what was stored before
  writing a panel: `count by (__name__) ({__name__=~"claude_code.*"})`.
- **Identity, on every datapoint and event record, not on the resource:** `user.email` (always
  when available; no switch), `user.account_uuid` and `user.account_id`
  (`OTEL_METRICS_INCLUDE_ACCOUNT_UUID`, default on), `user.id`, `session.id` (default on),
  `organization.id`, `terminal.type`. With API-key, Bedrock or Vertex auth only `user.id` and
  `session.id` are set; identity then comes from `OTEL_RESOURCE_ATTRIBUTES`.
- **Resource:** `service.name` (`claude-code`, or `claude-code-desktop`), `service.version`,
  `os.type`, `host.arch`, plus `OTEL_RESOURCE_ATTRIBUTES` keys (also copied onto datapoints by
  default).
- **Name redaction without `OTEL_LOG_TOOL_DETAILS=1`:** user-defined skill names appear verbatim,
  third-party plugin skills become `third-party`, user-defined agents and user-configured MCP
  servers become `custom`. Real names everywhere need the flag (2.1.273+), which also logs
  commands and paths in events.

## Events, content and traces

Events need `OTEL_LOGS_EXPORTER`. Useful ones: `api_request` (cost and tokens per request),
`tool_result`, `mcp_server_connection`, `skill_activated`, `subagent_completed`.

| Content | Gate |
| --- | --- |
| prompt text (`prompt` and `prompt_text` attributes) | `OTEL_LOG_USER_PROMPTS` |
| response text | `OTEL_LOG_ASSISTANT_RESPONSES` |
| Bash commands, file paths, URLs, real skill and MCP names | `OTEL_LOG_TOOL_DETAILS` |
| full request and response bodies | `OTEL_LOG_RAW_API_BODIES` |
| file contents and command output, trace spans only | `OTEL_LOG_TOOL_CONTENT` |

- Metrics carry no branch. With `OTEL_LOG_TOOL_DETAILS=1`, a successful `git commit`
  `tool_result` carries `vcs.ref.head.revision`, `.name` and `.type`, so per-branch cost is a join
  on `session.id`, at the price of logging every command and path.
- Traces (beta): `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` plus `OTEL_TRACES_EXPORTER=otlp` give
  `interaction > llm_request / tool > tool.execution / blocked_on_user / hook` spans. GenAI
  semantic conventions are still in development; normalise attribute names in the collector, not
  in dashboards.

## The collector boundary

[assets/org-only-filter.alloy](../assets/org-only-filter.alloy) is a complete, tested Alloy
pipeline: OTLP receiver, filter, identifier transform, debug exporter. For production, keep the
`otelcol.processor.filter` and `otelcol.processor.transform` blocks, replace `example-org`, and
wire their output to the real exporter or batch processor. Traces pass untouched unless wired in.

- **Filter:** drops `claude_code.*` datapoints unless `vcs.owner.name`, as a datapoint or a
  resource attribute, matches `^example-org(/.*)?$` (nested groups pass, `example-orgx` does not);
  drops every Claude Code log record. Other services' telemetry passes.
- **Transform:** `delete_matching_keys` removes `user.email`, `user.account_uuid`,
  `user.account_id`, `user.id` and `session.id` from datapoints and log records. Stripping them
  also removes any "developers sending" count; whether to keep an identifier is the kpi-groomer
  skill's decision.
- **Syntax:** `metric_conditions` and `log_conditions` (Alloy 1.15+, collector 0.146+) replace the
  deprecated `metrics { datapoint }` and `logs { log_record }` blocks; the two forms cannot be
  mixed in one component. If any condition matches, the item is dropped.
- **OTTL semantics:** `IsMatch` is unanchored, so anchor the regex; it returns false for a missing
  attribute, so `not IsMatch` also drops data without repository labels; `not` binds tightest; a
  metric whose datapoints are all dropped is dropped.
- **Escaping:** write `[.]` instead of `\\.`; a YAML block scalar, an Alloy backtick string and
  an OTTL string each treat backslashes differently.
- **OpenTelemetry Collector equivalent:**

```yaml
processors:
  filter/org_only:
    error_mode: ignore
    metric_conditions:
      - 'IsMatch(metric.name, "^claude_code[.]") and not (IsMatch(datapoint.attributes["vcs.owner.name"], "^example-org(/.*)?$") or IsMatch(resource.attributes["vcs.owner.name"], "^example-org(/.*)?$"))'
    log_conditions:
      - 'resource.attributes["service.name"] == "claude-code"'
```

## Prove the filter with otlp_cases.py

1. Syntax: `docker run --rm -v "$PWD:/etc/alloy:ro" grafana/alloy:<cluster version> fmt /etc/alloy/<file>.alloy`.
   For config embedded in YAML, extract it first.
2. Run the cluster's Alloy version locally with the filter feeding `otelcol.exporter.debug` at
   `verbosity = "detailed"`. The debug exporter is experimental:
   `docker run -d --name filtertest -p 14318:4318 -v "$PWD:/etc/alloy:ro" grafana/alloy:<version> run --stability.level=experimental /etc/alloy/<file>.alloy`.
   The GA alternative is `livedebugging { enabled = true }` and the Alloy UI.
3. `python3 scripts/otlp_cases.py send --org example-org --endpoint http://127.0.0.1:14318`
   posts twelve cases, each with a unique `probe-case-*` marker: the organisation as datapoint
   owner, as resource owner and as a nested group; three lookalikes; another owner; no
   repository; a non-Claude metric; Claude events from the organisation and from another owner; a
   non-Claude log.
4. `docker logs filtertest 2>&1 | python3 scripts/otlp_cases.py check - --org example-org --expect-stripped`
   - `leak`: a case that must be dropped reached the exporter.
   - `overblock`: a case that must pass is missing.
   - `identifier`: a synthetic `user.email` or account id reached the exporter (`--expect-stripped`).
   - Exit 0 clean, 1 findings, 2 unusable output (no markers: wrong verbosity or wiring).
   - `--keep-claude-logs` when the pipeline keeps the organisation's events.
5. `fixtures/careless-filter.alloy` is a plausible wrong filter (unanchored, datapoint-only, no
   log rule, no transform); `fixtures/collector-careless.log` is its output and raises all three
   kinds.

A component that fails to build shows up where it is referenced as "does not exist or is out of
scope". In-cluster config (Kubernetes discovery) cannot run locally; `fmt` is the local check
there, and wiring is checked after deploy.

## After the rollout

- In GitOps, a mounted ConfigMap reaches the pod after the kubelet sync period. Confirm the new
  component in Alloy's own API before calling it live: port-forward `12345` and read
  `curl -s http://127.0.0.1:12345/api/v0/web/components` for the filter's id and a healthy state.
- Then: the OTLP endpoint still answers, and unrelated signals still arrive
  (`count(timestamp({__name__=~"<an app metric>"}) > time() - 120)`).
- Sessions already running keep their old environment until restarted.

## Audit and clean leaked data

List owners over a long window right after enabling, and again after every settings change:

```sh
curl -s http://127.0.0.1:8428/api/v1/series \
  --data-urlencode 'match[]={__name__=~"claude_code.*", vcs.owner.name!~"example-org(/.*)?"}' \
  --data-urlencode 'start=-90d'
```

Count per owner first, then delete with the same negative match. Hand the delete commands to a
human; an agent's permission classifier refuses mass deletes, and a refusal is a stop.

```sh
curl -s http://127.0.0.1:8428/api/v1/admin/tsdb/delete_series \
  --data-urlencode 'match[]={__name__=~"claude_code.*", vcs.owner.name!~"example-org(/.*)?"}'
Q='service.name:"claude-code" NOT vcs.owner.name:~"^example-org(/.*)?$"'
curl -s http://127.0.0.1:9428/select/logsql/query --data-urlencode "query=$Q | stats count()"
curl -s http://127.0.0.1:9428/delete/run_task --data-urlencode "filter=$Q"
```

VictoriaLogs deletes only when the deployment enables its delete API; check the flag for your
version.

## Dashboards query-first

1. Port-forward the TSDB and run every panel expression through `/api/v1/query`: label values,
   filtered selectors, ratios.
2. Put the organisation regex in every selector, and build the repository variable from it.
3. Show totals per repository, model, skill and subagent, and a **count** of developers, never
   names. Person-level views: the kpi-groomer skill.
4. `OR on() vector(0)` makes an empty stat panel read 0.
5. Ship the dashboard as a GitOps resource (for grafana-operator a `GrafanaDashboard` CR); verify
   with `kubectl kustomize`, the reconciler's status, and the CR's synchronised condition.

```text
sum(increase({__name__="claude_code.cost.usage", vcs.owner.name=~"example-org(/.*)?", vcs.repository.name=~"$repository"}[$__range])) OR on() vector(0)
sum(increase({__name__="claude_code.token.usage", type="cacheRead", vcs.owner.name=~"example-org(/.*)?"}[$__range])) / sum(increase({__name__="claude_code.token.usage", vcs.owner.name=~"example-org(/.*)?"}[$__range]))
count(count by (user.email) (increase({__name__="claude_code.session.count", vcs.owner.name=~"example-org(/.*)?"}[$__range]) > 0))
```

The last query needs `user.email` at ingest; it disappears when the collector strips identifiers.

## Reading the numbers

- **Cost is an estimate.** `claude_code.cost.usage` is computed at list price for every auth
  method; on subscription seats it is the API value of the work, not the bill. Managed
  `modelPricing` reprices it and it stays an estimate. Billing data comes from the provider.
- **Cache reads dominate.** In one team's measured week, cache reads were about 97 % of all
  tokens. Every always-loaded line (instruction files, unscoped rules, skill descriptions, MCP
  tool definitions) is re-read on every request; the agent-instructions skill owns trimming it.
- **Teams:** map usage to teams through the people roster (a vendor API answers in email
  addresses), give each person one primary team so organisation totals do not double-count, list
  the people with several teams, use every active person as the adoption denominator, and exclude
  kiosk, bot and service accounts from head counts.
- **Agent-assisted commits** from trailers, independent of any gateway (the count is only as
  complete as the convention, so make agents add the trailer):

```sh
git log --no-merges --since=30.days -i -E \
  --grep='^co-authored-by:.*(claude|copilot|codex|cursor|gemini|aider|devin|openhands|jules)' \
  --grep='^(assisted|generated)-by:' --format=%h | wc -l
git rev-list --no-merges --count --since=30.days HEAD
```

- **Per person, locally:** ccusage reads `~/.claude/projects/**/*.jsonl` (and other agent CLIs'
  local logs) on the laptop and uploads no usage; its only network calls fetch price tables, and
  `--offline` stops those. `npx -y ccusage@latest daily --since 2026-01-01 --breakdown`;
  `--instances` groups by project, `--project-aliases` merges worktrees of one repository. Its
  costs are estimates too.
- **Never re-send cumulative aggregates** (a whole daily table every hour) to a backend that sums
  them: every interval inflates the total. Send events or deltas.

## Sources

- Monitoring: <https://code.claude.com/docs/en/monitoring-usage>
- Variables ignored in project settings:
  <https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env>
- Costs: <https://code.claude.com/docs/en/costs>
- Collector filter processor:
  <https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/filterprocessor/README.md>
- Alloy filter: <https://grafana.com/docs/alloy/latest/reference/components/otelcol/otelcol.processor.filter/>
- Alloy debug exporter: <https://grafana.com/docs/alloy/latest/reference/components/otelcol/otelcol.exporter.debug/>
- ccusage: <https://github.com/ccusage/ccusage>
