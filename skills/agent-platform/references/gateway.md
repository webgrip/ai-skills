# LLM gateway recipes — LiteLLM teams, keys, MCP grants, clients

Contents: [Teams as code](#teams-as-code) · [Gateway config](#gateway-config) ·
[Mint, prove, revoke a key](#mint-prove-revoke-a-key) · [Audit who uses it](#audit-who-uses-it) ·
[After a config push](#after-a-config-push) · [Claude Code through the gateway](#claude-code-through-the-gateway) ·
[Headless and sandboxed agents](#headless-and-sandboxed-agents) · [Other harnesses](#other-harnesses) ·
[Sources](#sources)

Endpoints, LiteLLM proxy: OpenAI-compatible `/v1/...`, Anthropic-native `/v1/messages`, MCP
`/mcp`, admin `/key/*`, `/team/*`, `/spend/logs/v2`, liveness `/health/liveliness` (LiteLLM's
spelling). The master key starts with `sk-`; keep it in a variable and never print it.

## Teams as code

Teams, budgets and grants are database objects with no `config.yaml` stanza. Keep their spec in
git and converge it on a schedule, so an Admin UI edit drifts back and every change is reviewed.

```json
{
  "team_id": "agents-scope-a",
  "team_alias": "agents-scope-a",
  "models": ["tier-auto", "tier-standard"],
  "max_budget": 25,
  "budget_duration": "30d",
  "tpm_limit": 100000,
  "rpm_limit": 500,
  "mcp_access_groups": ["observability-read-scope-a"]
}
```

- Set `team_id` explicitly, equal to the alias. `/team/new` otherwise assigns a random UUID, and a
  recreated team breaks every config that pins the old id.
- Converge with `GET /team/list`, then `/team/new` for missing ids and `/team/update` for drift.
  Report, never delete, a team that exists under another id.
- `/team/list` shows `object_permission_id`, not the groups; read grants from the git spec or with
  a key's `tools/list`.
- During a database outage (`allow_requests_on_db_unavailable`) the proxy keeps serving with
  existing keys but cannot mint new ones.

## Gateway config

```yaml
general_settings:
  require_key_mcp_access_defined: true
litellm_settings:
  callbacks: ["prometheus"]
mcp_servers:
  metrics_scope_a:
    transport: "http"
    url: "http://mcp-metrics-scope-a.observability.svc.cluster.local:8080/mcp"
    description: "Scope A metrics, read-only, bounded by the data proxy"
    access_groups: ["observability-read-scope-a"]
```

- **MCP resolution:** key, team, end user, agent, internal user and organisation lists intersect;
  the organisation list is a ceiling. With no list at any level a request reaches every MCP
  server. A key with an empty list inherits its team's list unless
  `require_key_mcp_access_defined: true`, which makes the team a ceiling and the key's own grant
  the only grant. An empty team list never restricts, flag or not.
- `"object_permission": {"mcp_servers": ["no-mcp-servers"]}` on a key denies every MCP server
  regardless of team and groups: use it for chat keys and other surfaces that must have no tools.
- **Server names:** underscores. LiteLLM prefixes each tool with `<server>-`, and a hyphen in the
  server name stops startup in `_validate_config_server_names` ("Server name cannot contain -").
- **Client header forwarding:** LiteLLM forwards `x-mcp-<server alias>-<header>` and
  `x-mcp-<access group>-<header>` request headers to MCP servers, so a caller can send its own
  `Authorization` to a tool server. A scoped tool server must ignore incoming credentials
  ([tools.md](tools.md#one-tool-server-per-scope)). Never name a server after an access group it
  is not in; the two share the header namespace.
- **Prometheus:** `callbacks: ["prometheus"]` serves `/metrics` (a dedicated port from v1.101);
  at v1.104.2 the source has no licence check. Spend and token counters carry `api_key_alias`,
  `team`, `team_alias`, `user`, `user_email`; `end_user` only with
  `enable_end_user_cost_tracking_prometheus_only: true`. Check your version before building a
  separate ledger exporter. Gauges read from the ledger database are cumulative: use `delta()`.
- **Response caching** does nothing useful for agents; keep it `default_off`.
- **Supply chain:** LiteLLM's PyPI releases 1.82.7 and 1.82.8 shipped a credential stealer
  ([heise](https://heise.de/-11224139)). Pin the image by digest with a release-age delay; the
  renovate-pins skill covers digest pins a bot can still update.

## Mint, prove, revoke a key

```sh
M=$(kubectl -n ai get secret litellm-master -o jsonpath='{.data.LITELLM_MASTER_KEY}' | base64 -d)
export PROBE_KEY=$(curl -s -X POST https://gateway.example.org/key/generate \
  -H "Authorization: Bearer $M" -H 'Content-Type: application/json' \
  -d '{"key_alias":"grant-test-scope-a","team_id":"agents-scope-a","duration":"1h","max_budget":0.01,
       "object_permission":{"mcp_access_groups":["observability-read-scope-a"]}}' | jq -r .key)
python3 scripts/mcp_probe.py --url https://gateway.example.org/mcp --token-env PROBE_KEY \
  --auth-header x-litellm-api-key --forbid 'update_|create_|delete_|write' \
  --call metrics_scope_a-query --arguments '{"query":"count by (team) (up)"}'
curl -s -X POST https://gateway.example.org/key/delete -H "Authorization: Bearer $M" \
  -H 'Content-Type: application/json' -d "{\"keys\":[\"$PROBE_KEY\"]}" > /dev/null
python3 scripts/mcp_probe.py --url https://gateway.example.org/mcp --token-env PROBE_KEY \
  --auth-header x-litellm-api-key --expect denied
```

- `/key/generate` takes the team's **id**; the alias gives 400 "Unable to find team object in
  database". A key asking for a group its team does not allow is refused at mint with 403.
- Every human-started key: `key_alias` naming the person or product, `user_id` for the person
  (a request-body `user` is tracked as the end customer, not the key owner), and `metadata`
  such as `{"application": "...", "session_id": "...", "operator_id": "..."}`. Agent products
  mint one key per session.
- A key with a team but no grant gets 403 on `/mcp` `initialize` (with either auth header and
  any key type) while inference keeps working, so a session with it runs on without tools.
- `mcp_probe.py` exit codes: 0 as expected, 1 expectation failed (no tools, a forbidden or
  missing tool, a failing call, tools where `--expect denied`), 2 unusable (no token, unreachable,
  redirect, 406). It sends `Accept: application/json, text/event-stream` (without both, servers
  answer 406), keeps `Mcp-Session-Id`, pages `tools/list`, never follows a redirect and never
  prints the token.
- The same handshake reaches an MCP server whose tools did not load in the current session;
  MCP tools are fixed at session start.

## Audit who uses it

- Keys: `GET /key/list?return_full_object=true&size=100&page=N` (`size` above 100 is rejected);
  tabulate team, alias, groups, expiry, spend and `last_active`.
- Spend: `/spend/logs/v2` (paginated; `/spend/logs` is deprecated and truncates at 10,000 rows).
  `org_admin` and `team_admin` roles are Enterprise; an internal user sees only their own spend.
- Tool use: count JSON-RPC methods in the tool servers' own logs. `initialize` and `tools/list`
  from the gateway pod at each restart are not usage; only `tools/call` is.
- A chat front-end on one shared key hides who asked unless it forwards user headers; an actor
  header asserted by a client is only as trustworthy as that client.

## After a config push

```sh
kubectl -n ai rollout status deploy/litellm
kubectl -n ai logs deploy/litellm -c app --previous 2>/dev/null | grep -A5 Traceback
curl -s -o /dev/null -w '%{http_code}\n' https://gateway.example.org/health/liveliness
```

Watch every container in the pod (the proxy and any spend exporter sidecar) until restarts
stop. One invalid MCP server name takes down all inference, not only tools.

## Claude Code through the gateway

| Setting | Value |
| --- | --- |
| `ANTHROPIC_BASE_URL` | the gateway root; Claude Code appends `/v1/messages` itself |
| `ANTHROPIC_AUTH_TOKEN` | sent as `Authorization: Bearer`; or `ANTHROPIC_API_KEY`, sent as `x-api-key`. A 401 on a test request means the other variable |
| `apiKeyHelper` + `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | short-lived keys from a vault or SSO command; default cache five minutes |
| `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` | request class, agent type, compaction and prompt id headers (2.1.273+); `x-claude-code-session-id` and `x-claude-code-agent-id` are always sent |
| `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` | gateway models in `/model`; `GET /v1/models` must answer within 3 s without a redirect |
| managed `allowedProviders: ["customEndpoint"]` with the URL in managed `env` | the gateway is the only destination (2.1.285+) |

Distribute base URL and credential through managed settings and the secrets tooling; check with
`/status` (an `Anthropic base URL` line and an `Auth token` or `API key` line). Only
`ANTHROPIC_BASE_URL` without a gateway credential still bills the claude.ai login.

The gateway must:

- forward `anthropic-version` and `anthropic-beta` verbatim, without allowlisting values;
- forward `cache_control` unchanged and keep block-form `system` content, or prompt caching dies
  silently (high `input_tokens`, no cache reads);
- stream SSE unbuffered, `ping` events included, or sessions stall or hit the idle timeout;
- forward error bodies and `x-should-retry` unmodified;
- prefer the Anthropic pass-through route over translating to the OpenAI format.

Personal interactive tool access:
`claude mcp add --transport http gateway-tools https://gateway.example.org/mcp --header "x-litellm-api-key: Bearer $KEY"`,
with a key in the person's own team. Wide groups that read every team, client and per-person
series are for platform engineers only.

## Headless and sandboxed agents

- Tools are off by default; a team or repository opts in, and the runner checks that the human
  starting the session holds the scope before it mints `team_id` plus `mcp_access_groups`.
- The agent gets exactly one MCP server, the gateway, and only a placeholder key; a loopback proxy
  in the worker swaps it for the real key on `Authorization`, `X-Api-Key` and
  `X-Litellm-Api-Key`. The master key never enters a workspace.
- Fail at boot on half-configured grants (groups without a team, blank or duplicate groups), and
  wire MCP only when the credential carries groups.
- Claude Code: write the config to a 0600 file in the run's scratch directory and pass
  `--mcp-config <file> --strict-mcp-config`; keep the run's environment an allowlist.

```json
{"mcpServers":{"gateway":{"type":"http","url":"https://gateway.example.org/mcp","headers":{"X-Litellm-Api-Key":"Bearer PLACEHOLDER"}}}}
```

- opencode: `oauth: false` stops the automatic OAuth attempt after a 401 on an API-key server;
  `{env:VAR}` keeps the key out of the file. Tool names get the server prefix; permissions are
  session-wide only.

```json
{"mcp":{"gateway":{"type":"remote","url":"https://gateway.example.org/mcp","enabled":true,"oauth":false,
  "headers":{"x-litellm-api-key":"Bearer {env:LITELLM_API_KEY}"}}}}
```

## Other harnesses

- One gateway can meter several harnesses only where each honours a custom base URL; check per
  tool before promising per-team cost.
- Some harnesses report a gateway error (a 400 from the proxy) as a normal end of turn. An
  integration check reads the response content for the error, not only the stop reason.

## Sources

- LLM gateway connect: <https://code.claude.com/docs/en/llm-gateway-connect>
- Gateway protocol (headers, streaming, caching, discovery): <https://code.claude.com/docs/en/llm-gateway-protocol>
- LiteLLM MCP permissions: <https://docs.litellm.ai/docs/mcp_control>
- LiteLLM MCP overview (naming, header forwarding): <https://docs.litellm.ai/docs/mcp>
- LiteLLM virtual keys, spend, Prometheus: <https://docs.litellm.ai/docs/proxy/virtual_keys>,
  <https://docs.litellm.ai/docs/proxy/cost_tracking>, <https://docs.litellm.ai/docs/proxy/prometheus>
- opencode MCP servers: <https://opencode.ai/docs/mcp-servers/>
