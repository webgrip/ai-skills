# Build, deploy, observe, version

Contents: SDK choice · build hygiene · deploy · observability · versioning and distribution · migrating a sessionful server

## SDK choice

Use a Tier-1 official SDK release that supports 2026-07-28 and still answers 2025-era clients; pin the exact version. Tiers: [modelcontextprotocol.io SDKs](https://modelcontextprotocol.io/docs/2026-07-28/sdk).

| Stack | Shape |
|---|---|
| TypeScript | official SDK; `createMcpHandler` for stateless HTTP (works on Workers, Node, Vercel); Zod `.strict()` input models |
| Python | official SDK v2, or FastMCP 4.x (built on it; transforms, per-component auth, CIMD, OAuth proxy, OpenTelemetry); pin the exact version |
| Go | official go-sdk ≥ 1.8: `mcp.AddTool` with typed structs and `jsonschema` tags (schema inferred, input validated, typed output becomes `structuredContent`); `StreamableHTTPOptions{Stateless: true, JSONResponse: true}`; `auth.RequireBearerToken`, `auth.ProtectedResourceMetadataHandler`, `oauthex.MatchesResource`; no AS included |
| C#, Rust, Ruby | official SDKs, Tier 1; check the 2026-07-28 support level of the release you pin |

## Build hygiene

- One API client module with timeouts, retries for idempotent calls only, and upstream error mapping into teaching errors.
- `server/discover` implemented (SDKs do it); deterministic `tools/list` order (prompt-cache hits); `ttlMs` and `cacheScope` on list results.
- Secrets from a secret store or env injected at runtime, never in config files, images or query strings.
- stdio servers log to stderr only.

## Deploy

- Stateless Streamable HTTP: any instance serves any request, so scale horizontally behind a plain load balancer; JSON responses unless a tool streams progress.
- Durable state in application storage, not in memory tied to a connection.
- Gateways and WAFs can route and rate-limit on the `Mcp-Method` and `Mcp-Name` headers that 2026-07-28 clients send.
- Serve PRM unauthenticated; put auth on the MCP endpoint only.
- Health endpoint outside the MCP path; readiness that checks upstream reachability.
- Serverless and edge are viable (Workers, Vercel functions, Cloud Run) now that no session needs pinning.

## Observability

- OpenTelemetry: continue the trace from `_meta` `traceparent`/`tracestate`; one span per tool call with tool name, principal, result status.
- Per-tool metrics: calls, latency, error class (input, auth, upstream, internal), response size in bytes and estimated tokens, truncations.
- Audit log of every mutation and every scope elevation: principal, client, tool, arguments (redacted), correlation ID.
- Internal errors go to the error tracker with full detail; the model gets a generic message.
- Review production tool-call analytics regularly: tools never called, tools called and then retried with corrected arguments, frequent `isError` causes. Each is a description or schema fix.

## Versioning and distribution

- Tool names, parameter names, schemas and annotations are an API for agents and for users' allowlists. Snapshot them (one JSON per tool) and fail CI on unreviewed drift.
- Renames keep the old name as a deprecated alias for a release window.
- Previews behind a feature flag, an "insiders" route or a toolset, not in the default surface.
- Track spec deprecation windows: deprecated features get at least 12 months; plan off DCR, Roots, Sampling, Logging and HTTP+SSE.
- Distribution: a remote URL (plus a directory listing if public), an MCPB bundle for local servers, an MCP Registry `server.json`; ship a plugin with skills where the workflow matters.

## Migrating a sessionful server

1. Run a strict stateless route beside the legacy session route.
2. Move each feature that used session state to explicit handles or application storage.
3. Point clients at the stateless route; watch legacy traffic drain.
4. Remove the legacy route inside the deprecation window.
