# Authorization for remote MCP servers

Contents: roles · the request flow · token validation · client registration · when the IdP falls short · OAuth proxy options · scopes and step-up · lazy auth · non-OAuth options · verification

## Roles

- **MCP server = OAuth 2.1 resource server.** It validates tokens and serves metadata. It does not issue tokens, store client registrations or show login pages.
- **Authorization server = an existing IdP or AS** (Keycloak, Entra, Okta, Auth0, WorkOS, Authentik, Cloudflare's workers-oauth-provider, an SDK-provided AS). It must publish RFC 8414 or OIDC discovery metadata.
- **A gateway** (Envoy, an API gateway, an MCP gateway) may do the resource-server work in front of the server, as long as it returns the same 401 and metadata a compliant server would.

## The request flow

1. Client calls the MCP endpoint without a token.
2. Server answers **401** with `WWW-Authenticate: Bearer resource_metadata="https://mcp.example.org/.well-known/oauth-protected-resource", scope="tickets:read"`.
3. Client fetches **Protected Resource Metadata** (RFC 9728): `resource` (the canonical server URL, exactly what the user typed, no trailing slash mismatch), `authorization_servers` (primary first; some clients use only the first), `scopes_supported` (minimal baseline), `bearer_methods_supported: ["header"]`. Clients that miss the header try `/.well-known/oauth-protected-resource/<path>` and then the root; serve both when the endpoint has a path.
4. Client fetches the AS metadata, registers or identifies itself (below), runs authorization code + **PKCE S256**, sending `resource` (RFC 8707) in the authorization and token requests.
5. Client validates `iss` in the authorization response (RFC 9207) and keys credentials by issuer.
6. Client sends `Authorization: Bearer …` on every request. Never accept tokens in the query string.

## Token validation on every request

- Signature against the issuer's JWKS (cache with rotation), or introspection for opaque tokens.
- `iss` equals the expected issuer.
- **Audience**: `aud` contains this server's canonical URL (RFC 8707). When the IdP ignores `resource` and sets `aud` to the OAuth client ID, accept exactly the client IDs registered for this server, and record that this is a weaker binding.
- `exp`, `nbf` with small clock skew; required scopes for the tool being called.
- Map the subject to a principal for authorization and audit.
- Reject everything else with 401 (invalid or expired) or 403 `insufficient_scope` (valid but not enough).

**No token passthrough.** The token the client sent is for this server only. To call an upstream API, use the server's own credentials scoped per user, or an RFC 8693 token exchange that mints a token for the upstream audience. Forwarding the client's token makes the upstream trust a token that was never issued for it and lets a compromised MCP server replay it.

## Client registration

Spec priority: **pre-registered → Client ID Metadata Document (CIMD) → Dynamic Client Registration (DCR, deprecated) → ask the user**.

- **CIMD**: the client's `client_id` is an HTTPS URL to a JSON metadata document; the AS fetches it. The AS advertises `client_id_metadata_document_supported: true`. Claude also requires `none` in `token_endpoint_auth_methods_supported` before it uses CIMD.
- **DCR**: deprecated in 2026-07-28; still the fallback many clients use. Unbounded anonymous registrations are a DoS and policy problem; DCR clients must send `application_type`.
- **Pre-registered**: you create one OAuth client per MCP client type in the IdP and give users (or the client config) the client ID, and a secret only for confidential clients.

## When the IdP falls short

Check the IdP for: CIMD, anonymous DCR, RFC 8707 `resource` support, RFC 9207 `iss`, enforced PKCE S256, refresh rotation. For each gap:

| Gap | Response |
|---|---|
| No CIMD, no anonymous DCR | pre-register one client per MCP client (hosted connector, each IDE, one public client for CLIs) with that client's redirect URIs ([clients.md](clients.md)) |
| `resource` ignored, `aud` = client ID | validate `aud` against the set of client IDs registered for this server; give each MCP server its own clients so tokens do not cross servers |
| No `iss` in the authorization response | accept for now, note it, prefer an AS that adds it |
| PKCE advertised but not enforced | configure the client as public with PKCE required, or front it with a thin AS |
| Arbitrary third-party clients must connect | put a thin AS or OAuth proxy that speaks CIMD/DCR in front of the IdP |

## OAuth proxy options

An OAuth proxy acts as the AS for MCP clients and as one confidential client toward the upstream IdP. It solves registration but creates a **confused deputy**: every MCP client shares the proxy's upstream client ID, so the upstream consent screen proves nothing about which client asked. A proxy with a static upstream client ID **must** show its own per-client consent screen (client name, redirect URI, scopes), bind consent to the user with a cookie, and validate redirect URIs exactly.

Choices, smallest first: an SDK's built-in proxy (FastMCP `OAuthProxy`/`OIDCProxy` with consent on by default and CIMD support; Cloudflare `workers-oauth-provider` with CIMD and RFC 8707), a dedicated proxy (`mcp-auth-proxy` style services with DCR, RFC 8707 and consent), an MCP gateway that serves PRM and validates JWTs (Envoy AI Gateway `MCPRoute`, agentgateway, Pomerium). Verify the version you deploy for consent, PKCE and audience handling before trusting it.

## Scopes and step-up

- `scopes_supported` is the minimal baseline; do not include `offline_access` in challenges.
- 401 challenges carry `scope="…"` for what this call needs; without it some clients request everything in `scopes_supported` plus `offline_access`.
- A valid token with too little scope gets **403** with `WWW-Authenticate: Bearer error="insufficient_scope", scope="all scopes still needed"`; the client re-authorizes.
- Optionally filter `tools/list` by granted scopes so the model never sees tools it cannot call.

## Lazy auth

Public tools can work before sign-in. The gate for protected tools must return **HTTP 401 from the HTTP handler before the MCP SDK runs**. A 200 response with an `isError` "please sign in" result shows text instead of a Connect button, and clients ignore `WWW-Authenticate` on 200. Discovery results are cached per server URL, so changing metadata needs a reconnect.

## Non-OAuth options

- **Static bearer or API key** in a header: fine for a personal server or a machine client on a private network; no per-user identity, rotate it like any secret, and some clients then skip OAuth entirely.
- **Client credentials (M2M)**: an extension, not supported by hosted Claude connectors.
- **Enterprise-managed authorization**: IdP-issued identity assertions without a consent screen; an extension with growing client support.
- **Network position alone** ("only on the LAN") is not authentication.

## Verification

- `curl -i` the endpoint with no token: 401, `WWW-Authenticate` with `resource_metadata`.
- `curl` the PRM URL unauthenticated: 200 JSON, `resource` byte-equal to the configured URL.
- Token for another audience or client: 401. Too few scopes: 403 `insufficient_scope`.
- Inspector and the conformance suite's auth scenarios ([evaluate.md](evaluate.md)).
- A full sign-in in each target client, including refresh after expiry.
