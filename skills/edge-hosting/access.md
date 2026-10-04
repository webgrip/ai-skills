# Cloudflare Access (Zero Trust) on the free plan

Contents: [choose the gate](#choose-the-gate) · [seats](#seats) · [apps and policies](#applications-and-policies) · [login methods](#login-methods) · [validate in the Worker](#validate-in-the-worker) · [API and IaC](#api-and-iac) · [Tunnel](#tunnel)

## Choose the gate

| Protect | Gate |
|---|---|
| A whole Worker: routes, custom domains, `*.workers.dev`, Version URLs, Previews | **Worker-level Access** (dashboard: Worker › Settings › "Protect with Access"; API destination type `worker` / `preview_worker`) |
| Every Worker's previews in the account | account-level destination `all_preview_workers` |
| One hostname or path on a zone | self-hosted application with a `public` destination `host/path` |
| A service in a private network (homelab) | Tunnel + self-hosted application on the tunnel hostname |
| Machines (CI, uptime checks) | service token + **Service Auth** policy |
| One page for named outsiders, expiring | [private-pages.md](private-pages.md) |

Precedence: hostname/path app → Worker-level → account-level. A hostname app protects only that hostname: workers.dev and preview URLs stay public unless the Worker itself is protected or `workers_dev`/`preview_urls` are `false`. Worker-level Access answers 403 to WebSocket upgrades; use a hostname app for WebSocket routes.

## Seats

- Free: **50 seats**, never billed; seat 51 is refused login.
- A seat is taken by any person who logs in to any app (or enrolls a WARP device) and is held **until removed**, not until their app or page expires.
- Revoke ends sessions and keeps the seat; **Remove** frees it.
- Turn on Settings › Admin controls › "Remove inactive users from seats" (window 1 month to 1 year).
- Service tokens and Bypass policies use no seat.

## Applications and policies

- Limits: 500 apps, 500 reusable policies, 1,000 rules per app, 50 service tokens, 50 IdPs (same on free).
- Paths: the more specific app wins and doesn't inherit from its parent. `example.org/p/*` does not match `/p` itself. One `*` per segment; no query strings or ports.
- New apps take **reusable policies** (`/access/policies`), attached as `{id, precedence}`.
- Rule logic: Include = OR, Require = AND, Exclude = NOT. Bypass and Service Auth evaluate first; Bypass is unlogged and can't use identity selectors.
- Sessions: global 15 min to 1 month (default 24 h); per-app/per-policy override.
- `cache-control: private, no-store` on every gated response so no shared cache keeps a copy.

## Login methods

- **One-time PIN** (default IdP): a code from `noreply@notify.cloudflare.com`, valid 10 minutes. Cloudflare sends it **only to addresses a policy allows**, yet the screen says "code sent" either way. Add recipients to the policy **before** sending the link.
- Corporate mail filters quarantine the sender, or link scanners burn the code before the person sees it: ask recipients to allowlist the sender, or offer Google / GitHub login (personal accounts work, free).
- Session length decides how often a recipient needs a new code.

## Validate in the Worker

Defense in depth: a Worker behind Access still checks the identity, so a missing app, a reachable workers.dev URL, or a misordered rollout fails closed.

- Read `Cf-Access-Jwt-Assertion` (or the `CF_Authorization` cookie).
- Keys: `https://<team>.cloudflareaccess.com/cdn-cgi/access/certs`, match `kid`, RS256. Keys rotate every 6 weeks with 7 days of overlap: cache, refetch on unknown `kid`.
- Check `iss == https://<team>.cloudflareaccess.com`, `aud` contains the app's AUD tag, `exp`/`nbf`.
- Reference implementation with tests: [assets/private-pages/src/index.js](assets/private-pages/src/index.js) (`verifyAccessJwt`).
- `ctx.access.getIdentity()` gives the identity without JWT parsing, but is absent in Workers that serve static assets and across service bindings/RPC; local dev uses an `access.dev` block in the wrangler config.

## API and IaC

- `/accounts/{id}/access/apps/{app}` has **no PATCH**: GET, strip read-only fields (`id`, `aud`, `created_at`, `updated_at`, expanded policy objects), PUT the whole object.
- `POST /accounts/{id}/access/policies` body: `{"name", "decision": "allow", "include": [{"email": {"email": "a@x"}}, {"email_domain": {"domain": "x"}}], "session_duration"}`.
- App body: `{"name", "type": "self_hosted", "domain": "host/path", "destinations": [{"type": "public", "uri": "host/path"}], "policies": [{"id", "precedence": 1}], "session_duration", "app_launcher_visible": false}`; the response's `aud` is the audience to validate.
- Terraform/OpenTofu v5: `cloudflare_zero_trust_access_application` (`destinations` replaces `self_hosted_domains`), `cloudflare_zero_trust_access_policy`, `cloudflare_zero_trust_access_service_token`. Expect plan drift on Access resources after apply; pin the provider.
- Token permission: Account › Access: Apps and Policies Edit.

## Tunnel

- `cloudflared` dials out (no open ports), free on all plans, 1,000 tunnels per account. Run 2 replicas with a remotely-managed tunnel token (from the secret store, never committed).
- Ingress is ordered, first match wins, last rule `http_status:404`. Tunnel CNAMEs (`<uuid>.cfargotunnel.com`) stay proxied.
- Pair every non-public tunnel hostname with an Access app. SSH can go through the tunnel with or without Access; decide per estate.
- Quick Tunnels (`cloudflared tunnel --url http://localhost:8080`, `trycloudflare.com`, no account) are for demos: random hostname each run, 200 in-flight requests, no SSE.
