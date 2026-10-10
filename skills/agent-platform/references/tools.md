# Scoped agent tools — tool servers, the data proxy, proofs

Contents: [Scope model](#scope-model) · [One tool server per scope](#one-tool-server-per-scope) ·
[vmauth: the boundary](#vmauth-the-boundary) · [Replay, then attack](#replay-then-attack) ·
[What "read-only" means per server](#what-read-only-means-per-server) ·
[Network routes](#network-routes) · [Surfaces that keep no tools](#surfaces-that-keep-no-tools) ·
[Sources](#sources)

## Scope model

- **Confidentiality or noise?** Clients, contracts and per-person data need an enforced boundary
  per scope. "Too many dashboards" needs personal home dashboards and playlists, not plumbing.
- **A scope is coarse:** a team today, a client group later. A label-filtering proxy enforces one
  value of one label per credential and decides by credential, not by viewer, so per-person
  scoping needs a credential (and a datasource) per scope.
- **Grants live in a reviewable entitlement model** that renders identity-provider groups. Leads
  get several scopes by grant, not by a wider role.
- **Agents act for a person.** An agent key gets a scope only when the human starting the session
  holds it, so the agent never sees more than that human. A service principal acts as itself; a
  machine account holds only grants given to it by name; a kiosk is its own identity and never a
  person's session.
- **Group names say the access:** `observability-read-<scope>` holds `metrics_<scope>` and
  `logs_<scope>`; write access lives in separate `<system>-write-<scope>` groups, never granted
  alongside read by default. A wide group that reads every scope is platform-only.

## One tool server per scope

Each scope runs its own small read-only tool server that can reach only the filtering proxy, with
that scope's credential, and no route of its own (reachable in-cluster through the gateway only).
For `mcp-victoriametrics`:

```yaml
env:
  - {name: VM_INSTANCE_ENTRYPOINT, value: "http://vmauth.observability.svc.cluster.local:8427"}
  - {name: VM_INSTANCE_TYPE, value: "single"}
  - name: VM_INSTANCE_BEARER_TOKEN
    valueFrom: {secretKeyRef: {name: vmauth-agents-scope-a, key: token}}
  - {name: MCP_SERVER_MODE, value: "http"}
  - {name: MCP_LISTEN_ADDR, value: "0.0.0.0:8080"}
  - {name: MCP_DISABLED_TOOLS, value: "export,rules,alerts,flags,metric_statistics,active_queries,top_queries,tsdb_status,tenants,metrics_metadata,metric_relabel_debug,downsampling_filters_debug,retention_filters_debug,test_rules,prettify_query,documentation"}
```

- **`MCP_PASSTHROUGH_HEADERS` stays unset.** It forwards named request headers to the database
  and overrides the configured ones on collision, and the gateway forwards client
  `x-mcp-<server>-<header>` headers, so a caller could replace the scope's credential. The same
  holds for any tool server with a header passthrough option.
- **Disable tools the proxy refuses anyway**, so the agent is not handed tools that only fail. The
  proxy's refusal, not this list, is the boundary.
- **Separate proxy users for agents and dashboards**, so either can be revoked, rate-limited or
  audited alone.
- **Measure memory with the documentation tool disabled.** `mcp-victoriametrics` embeds its docs
  and builds an in-memory search index at startup: one deployment was OOM-killed at 128 Mi and
  sat near 510 Mi of 512 Mi with it, and ran at 11 Mi with `documentation` in
  `MCP_DISABLED_TOOLS`.
- `mcp-victorialogs` takes `VL_INSTANCE_ENTRYPOINT` and `VL_INSTANCE_BEARER_TOKEN`.

## vmauth: the boundary

Measured against VictoriaMetrics v1.152.0 through vmauth:

| Parameter | Combines | Client can |
| --- | --- | --- |
| `extra_label=team=<scope>` | ANDed; overrides a client-supplied `extra_label` | only narrow |
| `extra_filters[]={team="<scope>"}` | ORed with a client's own `extra_filters[]` | widen to another scope |
| VictoriaLogs `extra_stream_filters` | ANDed, inside subqueries too | only narrow |

```yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMUser
metadata:
  name: agents-scope-a
  labels: {vmauth: agents}
spec:
  username: agents-scope-a
  generatePassword: true
  targetRefs:
    - static: {url: http://vmsingle.observability.svc.cluster.local:8428}
      paths: [/api/v1/query, /api/v1/query_range, /api/v1/series, /api/v1/labels, "/api/v1/label/[^/]+/values"]
      target_path_suffix: "?extra_label=team%3Dscope-a"
    - static: {url: http://vlsingle.observability.svc.cluster.local:9428}
      paths: ["/select/logsql/(query|hits|stats_query|stats_query_range|field_names|field_values|stream_field_names|stream_field_values|streams|stream_ids)"]
      target_path_suffix: "?extra_stream_filters=%7Bteam%3D%22scope-a%22%7D"
```

- The `VMAuth` selects users by label with `selectAllByDefault: false`. `generatePassword: true`
  writes Secret `vmuser-<name>`; `tokenRef` gives a bearer token instead, which the MCP servers
  send.
- Allowlist query paths; everything else (export, federate, admin, rules, `/vmui`) stays
  unreachable.
- Series without the scope label vanish for every scope. Copy the ones boards need with one
  recording rule per scope that sets the label (`record: board:probe_success:min`,
  `labels: {team: scope-a}`), and point the panels at the recorded series.
- A GitOps substitution step (Flux `postBuild`) eats `$`, `{` and `%` sequences: disable it for
  the Kustomization that holds these suffixes.
- Grafana's own org and datasource boundaries: the grafana-access skill.

## Replay, then attack

Prove the proxy before anyone relies on it. Run each port-forward as its own background task; a
long replay can drop one.

1. **Replay** every query on the scope's dashboards at one fixed timestamp, with and without the
   proxy, and list each answer that changes. Expect only the unlabelled series to differ.
2. **Negative replay:** run another scope's dashboard queries through this scope's credential;
   none may return the other scope's data.
3. **Label values:** compare `/api/v1/label/<label>/values` and `/api/v1/labels` with and without
   the proxy; the counts must shrink to the scope.
4. **Attack:**
   - no credentials and a wrong password: 401;
   - the client adds its own filter, overrides the label, or relabels with `label_replace`:
     still only the scope;

```sh
curl -s -u "agents-scope-a:$P" -G http://127.0.0.1:18427/api/v1/query \
  --data-urlencode 'query=count by (team) (up)' \
  --data-urlencode 'extra_filters[]={team="scope-b"}'
curl -s -u "agents-scope-a:$P" -G http://127.0.0.1:18427/api/v1/query \
  --data-urlencode 'query=count by (team) (label_replace(up, "team", "scope-a", "team", ".*"))'
```

   - refused paths: `/api/v1/export`, `/federate`, `/api/v1/status/tsdb`, `/api/v1/rules`,
     `/api/v1/alerts`, `/api/v1/admin/tsdb/delete_series`, `/vmui`, the `/prometheus/...` alias
     forms of each, and path traversal (`/api/v1/query/../export`);
   - log queries for another scope's pods return nothing.
5. **Through the gateway:** a scoped key queries only its scope; a key without the grant gets
   403 (`scripts/mcp_probe.py --expect denied`).

## What "read-only" means per server

Only RBAC on the server's own credential is something the workload cannot undo. Treat any flag
change on a server holding a write-capable token as a privilege change, and list the advertised
tools after each one: `scripts/mcp_probe.py ... --forbid 'update_|create_|delete_|manage|write'`.

| Server | Enforcement |
| --- | --- |
| mcp-grafana | Grafana OSS has no fine-grained RBAC, so its service account is often Editor. Read-only rests on `--disable-write` together with an explicit `--enabled-tools` list; a category list alone has still advertised write tools such as `update_dashboard`. It validates the `Host` header on every route: set `--allowed-hosts` and pin `Host` in probes |
| mcp-victoriametrics, mcp-victorialogs | read-only APIs behind the scoped proxy user |
| a Kubernetes MCP server | bound to the built-in `view` ClusterRole (no Secrets), with its destructive operations disabled and Secrets denied as a second guard |

## Network routes

One tool server reachable without login undoes every boundary built elsewhere.

1. Inventory every MCP or tool server's routes (ingress, HTTPRoute, LoadBalancer, NodePort) and
   their auth policy.
2. Make the authenticated gateway the only door.
3. Before removing a route, read its access and DNS logs for real use.
4. After removing it, verify from outside: `curl -sk -m8 -o /dev/null -w '%{http_code}\n'
   https://<host>/mcp` gives `000` and the name no longer resolves. Remove the hostname from the
   server's own host allowlist too.

## Surfaces that keep no tools

- **A surface that reads untrusted content** (web search, inbound mail, public issues, a cloned
  repository) gets no write-capable tools. An injected page can then leak at most the
  conversation it lands in; with a write tool it acts in the organisation's name. Granting tools
  there is a recorded decision, not a config change. The threat model (the lethal trifecta) is in
  the agent-instructions skill.
- **Servers that act with each caller's own credential stay off the shared gateway.** A shared
  service token would erase the per-person audit trail they give.

## Sources

- VictoriaMetrics `extra_label` and `extra_filters[]`: <https://docs.victoriametrics.com/victoriametrics/#prometheus-querying-api-enhancements>
- vmauth: <https://docs.victoriametrics.com/victoriametrics/vmauth/>
- mcp-victoriametrics: <https://github.com/VictoriaMetrics-Community/mcp-victoriametrics>
- mcp-grafana: <https://github.com/grafana/mcp-grafana>
- LiteLLM MCP header forwarding: <https://docs.litellm.ai/docs/mcp>
