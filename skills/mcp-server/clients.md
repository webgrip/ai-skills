# Client facts and limits

Checked against vendor docs in October 2026. These move with every client release: re-read the linked page before relying on a number, and record what you verified in the server's own docs.

## Protocol era support

- Current spec: **2026-07-28** (stateless). Hosted Claude documentation still lists the **2025-03-26, 2025-06-18 and 2025-11-25** auth specs and no support for sampling, resource subscriptions or draft capabilities. Serve both eras; Tier-1 SDKs do this when configured.
- Extensions (MCP Apps, Skills over MCP, Tasks, client credentials, enterprise-managed auth) vary per client: [client matrix](https://modelcontextprotocol.io/extensions/client-matrix).

## Claude Code

- Transports: stdio, Streamable HTTP (HTTP+SSE deprecated).
- Auth: `/mcp` or `claude mcp login [--no-browser]`; CIMD and DCR automatic; pre-registered client via `--client-id`, `--client-secret` (or `MCP_CLIENT_SECRET`), `--callback-port`; config keys `oauth.clientId`, `oauth.scopes`, `oauth.authServerMetadataUrl`.
- Redirect: loopback `http://localhost:PORT/callback`, any port (register `localhost` and `127.0.0.1`, or pin one with `--callback-port` when the IdP needs exact URIs).
- CIMD client ID: `https://claude.ai/oauth/claude-code-client-metadata`.
- Static headers via `--header`, or `headersHelper` for short-lived tokens (10 s timeout, re-run on 401/403). A static `Authorization` header disables the OAuth fallback.
- Limits: tool output capped at ~25,000 tokens (`MAX_MCP_OUTPUT_TOKENS`), timeout via `MCP_TOOL_TIMEOUT`. Tool definitions are deferred behind tool search, so large surfaces cost less here than elsewhere.
- Not verified: whether it sends RFC 8707 `resource` in every flow (an older issue reported it missing).
- Docs: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)

## claude.ai, Claude Desktop, mobile (custom connectors)

- Remote only, brokered from Anthropic's cloud: the MCP server **and the authorization server** must be reachable from Anthropic's egress range (published on [IP addresses](https://platform.claude.com/docs/en/api/ip-addresses)). A LAN-only IdP cannot work; private networks need the MCP tunnels preview.
- Registration choices: Claude's published identity (CIMD; used only when AS metadata has `client_id_metadata_document_supported: true` and `none` in `token_endpoint_auth_methods_supported`), automatic DCR (a new client per fresh connection), or your own pre-registered client ID with optional secret.
- Redirect: `https://claude.ai/api/mcp/auth_callback`.
- Strictness: sign-in starts only on **401** (`WWW-Authenticate` on 200 is ignored); only the first `authorization_servers` entry is used; PKCE S256 always; `resource` in PRM must equal the URL entered; 10 s budget for discovery, registration and token calls, 30 s for refresh; refresh failures must be `invalid_grant`; the token endpoint must accept form-urlencoded; no `client_credentials`; never credentials in the query string.
- Limits: tool result ~150,000 characters; tool call timeout ~240 s.
- Static request headers: beta, limited orgs, approved header names only, never `Authorization` on OAuth connections.
- Directory review: read and write in separate tools, `title` plus read-only or destructive hints on every tool, names ≤ 64 chars, descriptions that do not instruct Claude, actionable errors, reasonable response sizes.
- Docs: [building](https://claude.com/docs/connectors/building), [authentication](https://claude.com/docs/connectors/building/authentication), [lazy authentication](https://claude.com/docs/connectors/building/lazy-authentication), [review criteria](https://claude.com/docs/connectors/building/review-criteria), [add unlisted](https://claude.com/docs/connectors/custom/add-unlisted)

## VS Code (Copilot agent mode)

- Config in `mcp.json`: `headers`, `inputs` for prompted secrets, `oauth.clientId`, enterprise-managed auth (preview).
- Auth: reads RFC 9728 PRM; CIMD preferred over DCR; falls back to prompting for client ID and secret; step-up via `WWW-Authenticate`; built-in GitHub and Entra providers.
- Redirects: `http://127.0.0.1:33418` and `https://vscode.dev/redirect`. CIMD client ID reported as `https://vscode.dev/oauth/client-metadata.json` (secondary source).
- AS metadata may be fetched from a browser context, so CORS on the AS metadata endpoints matters for vscode.dev.
- Not verified: RFC 8707 `resource` in requests.
- Docs: [MCP configuration](https://code.visualstudio.com/docs/agents/reference/mcp-configuration), [MCP extension guide](https://code.visualstudio.com/api/extension-guides/ai/mcp), [1.106 notes](https://code.visualstudio.com/updates/v1_106)

## Cursor

- OAuth for Streamable HTTP with DCR; static `auth` block (`CLIENT_ID`, optional `CLIENT_SECRET`, `scopes`) with `${env:…}` interpolation for pre-registered clients; `headers` with `${env:…}`.
- **No CIMD** (staff: no timeline). Pre-register or allow DCR.
- Redirects: desktop `http://localhost:8787/callback`; web and Cloud Agents `https://www.cursor.com/agents/mcp/oauth/callback`.
- Compares PRM `resource` strictly against the configured URL.
- Hard cap on total tools across all servers (about 40–45); beyond it tools are silently dropped. Keep the surface small or offer toolsets.
- Not verified: RFC 8707 `resource` in requests.
- Docs: [cursor.com/docs/context/mcp](https://cursor.com/docs/context/mcp), [CIMD forum thread](https://forum.cursor.com/t/mcp-oauth-cimd-support-plans-and-timelines/148096)

## Pre-registration cheat sheet

| Client | Redirect URIs to register | Client type |
|---|---|---|
| Claude Code | `http://localhost:PORT/callback`, `http://127.0.0.1:PORT/callback` | public with PKCE, or confidential with the secret in the keychain |
| claude.ai / Desktop | `https://claude.ai/api/mcp/auth_callback` | confidential |
| VS Code | `http://127.0.0.1:33418`, `https://vscode.dev/redirect` | public with PKCE |
| Cursor | `http://localhost:8787/callback`, `https://www.cursor.com/agents/mcp/oauth/callback` | public with PKCE |
