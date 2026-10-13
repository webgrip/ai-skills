---
name: mcp-server
description: Designs, builds, secures, deploys and evaluates Model Context Protocol (MCP) servers on the stateless 2026-07-28 spec while still serving 2025-11-25 clients - agent stories, remote vs local, tool surface by size, names, descriptions, schemas, outputs, errors and annotations, least privilege against the lethal trifecta, OAuth resource-server auth (protected resource metadata, audience checks, CIMD, pre-registered clients when the IdP lacks CIMD or DCR), versioning, Inspector, the conformance suite, agent evals and a tools/list linter. Use when building, scaffolding or reviewing an MCP server, connector or MCP tools; wrapping an API, CLI or database for agents; choosing stdio vs Streamable HTTP; an agent picks the wrong tool, tool output is too big or tool definitions eat the context; adding OAuth, SSO or a login to an MCP server, or sign-in fails in Claude Code, claude.ai, VS Code or Cursor; migrating off MCP sessions; or testing and evaluating an MCP server.
---

# MCP server — a UI for agents, judged by agent task success

An MCP server is measured by whether an agent with only its tools finishes realistic tasks, not by API coverage. Every step below serves that measure.

## 1. Interview before code

Ask, a few at a time, and record the answers:

1. **Agent stories**: 5–15 jobs in the agent's words ("find the failing deploy for service X and show its last 50 log lines"). Each becomes a candidate tool or an eval task.
2. **What it touches**: a remote API, a shared database, the user's own machine.
3. **Who uses it**: just me, a team, anyone through a directory.
4. **Upstream auth**: none, a service credential, or each user's own account.
5. **Mid-call input**: confirmations, picking among matches, a rich UI (MCP Apps).

Already have a good CLI or API and only one agent? A skill that drives it may be enough; say so before building.

## 2. Deployment

- **Remote Streamable HTTP is the default.** Wrapping a remote API is never a reason to run locally.
- **Local (stdio, or an MCPB bundle for distribution)** only when it must touch the machine: files, desktop apps, localhost services, hardware. Credentials from env or the OS keychain, never HTTP OAuth over stdio. stdout carries JSON-RPC only; log to stderr.
- **Local HTTP** (rare): validate `Origin`, bind `127.0.0.1`, require a token or a unix socket.
- One codebase serving both transports is normal: stdio for local QA, remote for users.

## 3. Tool pattern by surface size

| Distinct operations | Pattern |
|---|---|
| up to ~15 | one tool per outcome, not per endpoint |
| 15–30 | audit for merges; group by resource with a `method` enum, reads and writes still separate tools |
| 30+ or a whole API | search/discover → details → `*_read` + `*_write`, or code mode in a sandbox; promote the 3–5 hottest operations to dedicated tools; offer toolsets and a read-only mode |

Count tokens of the whole `tools/list`; the agent pays them on every turn, alongside every other server it has.

## 4. Tool contract

- **Name** `service_verb_resource`, snake_case, `[A-Za-z0-9_.-]`, ≤ 64 chars (spec allows 128, the Claude directory 64), deterministic `tools/list` order.
- **Description**: when to use it, what it returns, what it does not do and which sibling to use instead, prerequisites. Nothing that steers the model beyond this tool.
- **Input schema**: flat primitives, enums, bounds, defaults, ID patterns, a description on every property, `additionalProperties: false`, 1–3 realistic examples for tricky params. Never make the model guess an ID or account scope.
- **Output**: high-signal fields, readable names next to the IDs a follow-up call needs, pagination (`limit` default 20–50, cursor, `has_more`), truncation that says how to narrow, `outputSchema` + `structuredContent` with a text mirror, `resource_link` for large payloads. A mutation returns the new or changed ID.
- **Errors**: tool failures as `isError: true` results stating what went wrong and the next call ("Ticket T-9 not found; use tickets_search to find IDs"). Protocol errors only for malformed requests. No stack traces, no bare "Internal Server Error".
- **Annotations on every tool, explicit**: `title`, `readOnlyHint`, `destructiveHint`, `openWorldHint`, `idempotentHint` when true. Unset means worst case: `destructiveHint` and `openWorldHint` default to true. Clients auto-approve read-only tools and prompt on destructive ones; hints are never a security control.
- **State**: no sessions. Mint opaque handles (`basket_id`), bind them to the caller, re-authorize every call, state the lifetime in the creating tool's description, answer an expired handle with "create a new one".

Detail, examples and MRTR/elicitation rules → [design.md](design.md).

## 5. Least privilege and threat model

- Name which legs of the **lethal trifecta** the server supplies: private data, untrusted content, a way to send data out. All three in one server, or alongside likely companions, needs a leg removed or a human gate.
- Enforce on the server: read and write tools split, read-only mode, `tools/list` filtered by the caller's scopes, step-up with 403 `insufficient_scope`, out-of-band approval for high-impact writes.
- Every tool input is attacker-influenced: path containment, argv not shell, URL allowlists against SSRF, size and time caps, rate limits.
- Returned third-party text is untrusted data. Secrets, tokens and stray PII never appear in results or `x-mcp-header` mirrors.

Threat checklist, OWASP MCP Top 10 mapping, local-server isolation → [security.md](security.md).

## 6. Auth by the book (remote)

1. The MCP server is an **OAuth 2.1 resource server**. A real authorization server or IdP issues tokens; the MCP server never hand-rolls registration.
2. Serve **RFC 9728 Protected Resource Metadata** unauthenticated at `/.well-known/oauth-protected-resource`; `resource` equals the exact URL users enter; the primary issuer first in `authorization_servers`.
3. Unauthenticated protected call → **HTTP 401** with `WWW-Authenticate: Bearer resource_metadata="…", scope="…"`, returned in the HTTP layer before the SDK runs.
4. **Validate audience** (RFC 8707 `resource`, or the client ID when the IdP ignores `resource`), issuer, expiry, scopes. Accept only tokens issued for this server. **Never pass a client's token upstream**; use your own credentials or token exchange.
5. Client registration in priority order: **pre-registered → CIMD → DCR** (deprecated). An IdP without CIMD or anonymous DCR means pre-registered clients per MCP client, or an OAuth proxy that shows its own **per-client consent** screen.
6. PKCE S256, RFC 9207 `iss`, refresh rotation, `invalid_grant` on dead refresh tokens, every auth endpoint answering in under 10 s.

IdP gap handling, proxy options, step-up, lazy auth for public tools → [auth.md](auth.md). Per-client registration, redirect URIs and limits → [clients.md](clients.md).

## 7. Protocol era

Build on a Tier-1 SDK release that speaks **2026-07-28** (stateless: no `initialize`, no `Mcp-Session-Id`; mandatory `server/discover`; `resultType`; MRTR for mid-call input; `ttlMs`/`cacheScope` on lists) and let it also answer **2025-era initialize-based clients**: hosted Claude surfaces still list the 2025 auth specs. New work uses no Roots, Sampling, Logging, HTTP+SSE or DCR-only registration.

## 8. Deploy, observe, version

Stateless behind any load balancer, JSON responses unless progress streams; OpenTelemetry from `_meta` `traceparent`; per-tool metrics and an audit log of mutations with principal and correlation ID; schema snapshots in CI, deprecated aliases for renamed tools, pinned SDK. → [operate.md](operate.md)

## 9. Evaluate

1. Lint the surface: `python3 scripts/tools_lint.py tools.json` (a `tools/list` result or a snapshot dir; rules → [evaluate.md](evaluate.md#tools_lint-rules)).
2. Inspector CLI `--method tools/list --strict` and the official conformance suite against `--requirements 2026-07-28` in CI.
3. Agent eval set: ≥ 10 realistic multi-hop tasks with string-checkable answers plus direct, indirect and negative selection prompts; hold out a split; measure accuracy, tool-choice precision/recall, calls, tokens, errors; change one description at a time; repeat runs.
4. Test in every target client, auth flow included.

Commands, eval format, transcript review → [evaluate.md](evaluate.md).

## Stale advice to ignore

- "Keep state in the MCP session", session-keyed token stores, `Mcp-Session-Id` routing, SSE resumability: gone in 2026-07-28.
- "Register clients with DCR": deprecated in favour of CIMD; pre-registration is first in line.
- Server-initiated sampling, elicitation or roots requests: replaced by MRTR (`input_required`).
- "Prioritize comprehensive API coverage" / one tool per endpoint: curate around outcomes; long tail behind search.
- HTTP+SSE transport, `ping`, `logging/setLevel`: removed or deprecated.

## Gotchas

- **Lazy auth**: a protected tool that returns 200 + `isError` "please sign in" never shows the client's Connect button; only a 401 starts sign-in.
- **PRM `resource` mismatch** with the URL the user typed fails sign-in in strict clients; trailing slash included.
- **Generic `api_request` with a `method` param** mixing reads and writes fails Claude directory review and defeats auto-approval.
- **Content filters and dynamic toolsets are not an authorization boundary**; scopes and server-side checks are.
- **`requestState` and handles are attacker-controlled**: HMAC or AEAD them, add anti-replay, bind to the token's `sub`.
- **Form-mode elicitation never asks for secrets or PII**; use URL mode, which is still no substitute for MCP auth.

## Additional resources

- Tool design, outputs, errors, state, MRTR → [design.md](design.md)
- Threat model, input hardening, local isolation → [security.md](security.md)
- OAuth resource server, IdP gaps, proxies, step-up → [auth.md](auth.md)
- Client facts and limits (Claude Code, claude.ai and Desktop, VS Code, Cursor) → [clients.md](clients.md)
- SDKs, deploy, observability, versioning → [operate.md](operate.md)
- Inspector, conformance, eval sets, `tools_lint.py` rules → [evaluate.md](evaluate.md)
- Credits and source list → [sources.md](sources.md)
- Webgrip estate: Authentik, Envoy Gateway, LiteLLM, Go SDK → [case-webgrip.md](case-webgrip.md)
