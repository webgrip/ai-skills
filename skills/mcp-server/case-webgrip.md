# Case: the Webgrip estate

Instance facts for MCP servers that run on Webgrip's homelab or are built in its repos. Read with [auth.md](auth.md) and [clients.md](clients.md). Not a template for other estates. Re-check versions in the linked manifests before acting on them.

## Where things stand

| Thing | Fact | Source |
|---|---|---|
| Identity broker | Authentik **2026.5.2**, reachable on the LAN and VPN only (route on `envoy-internal`) | [authentik helmrelease](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/kubernetes/apps/authentik/app/helmrelease.yaml) |
| Gateways | `envoy-internal` (LAN + WireGuard), `envoy-external` (public through the Cloudflare tunnel); a Kyverno policy allowlists which namespaces may attach to `envoy-external` | [envoy-gateway helmrelease](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/kubernetes/apps/network/envoy-gateway/app/helmrelease.yaml), [network-exposure policy](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/kubernetes/apps/kyverno/policies/app/network-exposure-cel.yaml) |
| In-cluster MCP servers | grafana, victorialogs, k8s, opencost, vikunja, docs: HTTPRoutes on `envoy-internal` with **no auth** today | [RFC: MCP endpoints carry the caller's identity](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/docs/techdocs/docs/rfc/rfc-mcp-identity.md) |
| Plan for those servers | RFC, **Proposed**: one pre-registered confidential Authentik client `mcp`, an Envoy `SecurityPolicy` `jwt` per MCP route with audience `mcp`, gate group `mcp-users`, clients configured with `"oauth": {"clientId": "mcp"}` | same RFC |
| LiteLLM MCP gateway | for agent **Runs** with per-Run virtual keys and access groups; humans connect to MCP servers directly | [Ploeg ADR-0078](https://github.com/ploeg-hq/ploeg/blob/development/docs/adrs/0078-runs-reach-read-only-mcp-tools-only-through-the-gateway-bounded-by-a-litellm-team.md), VIK-263, [litellm-config](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/kubernetes/apps/ai/litellm/app/litellm-config.configmap.yaml) |
| ploeg-mcp | stdio, five read-only tools, operator token from env, go-sdk v1.8.0; remote transport explicitly not decided | [Ploeg ADR-0081](https://github.com/ploeg-hq/ploeg/blob/development/docs/adrs/0081-ploeg-serves-its-operator-reads-as-mcp-tools-through-ploeg-mcp.md), [cmd/ploeg-mcp](https://github.com/ploeg-hq/ploeg/tree/development/cmd/ploeg-mcp) |
| Unfold over MCP | phases: stdio token → Streamable HTTP with a static bearer on the internal gateway → OAuth 2.1 resource server for Authentik tokens with audience checks and no passthrough | [Unfold ADR-0011](https://forgejo.webgrip.dev/webgrip/unfold/src/branch/development/docs/adr/adr-0011-unfold-is-reachable-over-mcp-through-a-read-first-server.md) |

## Authentik as the authorization server

| Capability | Authentik | Consequence |
|---|---|---|
| RFC 8414 metadata | yes, `/.well-known/oauth-authorization-server/application/o/SLUG/` | clients can discover it |
| DCR | only from **2026.8**, and only with a bearer token holding scope `goauthentik.io/oidc/dcr`: no anonymous DCR | the homelab version has none; MCP clients cannot self-register either way |
| CIMD | not implemented | Claude, VS Code fall back to DCR or a pre-registered ID |
| RFC 8707 `resource` | not implemented (token exchange rejects it) | `aud` is the provider's **client ID**; validate `aud` against the client IDs registered for this server |
| RFC 9207 `iss` in the authorization response | not implemented | note it; clients that require it will fail |
| PKCE | advertises `plain` and `S256`; enforcement not confirmed | configure public clients to require S256 |

Rules that follow:

- **Pre-register one Authentik provider per MCP client type** (Claude Code loopback, claude.ai callback, VS Code, Cursor; redirect URIs in [clients.md](clients.md#pre-registration-cheat-sheet)), each scoped to the MCP servers it may reach. Client secrets go to OpenBao and reach machines per the `secrets-levels` skill; never into a repo.
- **Hosted Claude connectors cannot sign in** while Authentik is LAN-only: Anthropic's cloud must reach both the MCP server and the authorization server. Publishing Authentik is its own decision record (the searxng ADR already deferred it). Until then, remote MCP here serves Claude Code, VS Code and Cursor on the LAN or VPN.
- A **thin AS in front of Authentik** (CIMD and DCR toward clients, Authentik upstream, with per-client consent) is the path once arbitrary clients must connect; see the proxy options in [auth.md](auth.md#oauth-proxy-options).

## Envoy Gateway in front of an MCP server

- The **cookie-session OIDC `SecurityPolicy`** used for apps without a login ([ADR-0060](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/docs/techdocs/docs/adr/adr-0060-gateway-oidc-for-apps-without-a-login.md)) is the wrong shape for MCP: MCP clients send bearer tokens and expect a 401 with metadata, not a browser redirect to a login page.
- The **`jwt` provider** fits: issuer, audiences (the registered client IDs), remote JWKS through a `Backend` to Authentik, `claimToHeaders` to pass the caller's email to the server for audit.
- Serve **PRM unauthenticated**: a separate HTTPRoute rule for `/.well-known/oauth-protected-resource` (and its path-suffixed form) without the policy, served by the MCP server or a static response. Envoy's own 401 does not carry `resource_metadata`, so clients find PRM through the well-known fallback; adding the header with a response override is possible but unverified here.
- The audience check at the gateway replaces none of the server's own authorization: the server still maps the caller to a principal and checks scopes per tool.

## Review points for the open RFC

Check these against [auth.md](auth.md) before the RFC is accepted:

- **One shared audience `mcp` for six servers**: a token for one server is valid at all of them. Per-server client IDs (or audiences) keep the spec's "token issued for this server" rule.
- **Token passthrough to the Kubernetes API (decision M4)** is what the MCP spec forbids. The alternatives are an RFC 8693 exchange (Authentik is not an STS), or `k8s-mcp` calling the API with its own identity plus impersonation of the verified user, which the RFC notes the server does not support.

## Go SDK helpers (ploeg-mcp, go-sdk v1.8.0)

- `mcp.NewStreamableHTTPHandler` with `StreamableHTTPOptions{Stateless: true, JSONResponse: true}`; localhost DNS-rebinding protection is on by default (`DisableLocalhostProtection` turns it off for a server behind a gateway).
- `auth.RequireBearerToken(verifier, &auth.RequireBearerTokenOptions{ResourceMetadataURL: …, Scopes: …})` wraps the handler; the verifier returns `*auth.TokenInfo{Scopes, Expiration, UserID, Extra}` and handles the 401 with `resource_metadata`.
- `auth.ProtectedResourceMetadataHandler(&oauthex.ProtectedResourceMetadata{…})` serves PRM with permissive CORS.
- `oauthex.MatchesResource(audiences, resource)` for the audience check; with Authentik, compare against the registered client IDs instead.
- No authorization server ships in the SDK; Authentik or a thin AS issues tokens.
- Example: [examples/auth/server](https://github.com/modelcontextprotocol/go-sdk/tree/main/examples/auth/server).
