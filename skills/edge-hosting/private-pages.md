# Private pages that expire

One self-contained HTML file (proposal, briefing, demo, vendor comparison) for named recipients, behind a Cloudflare login, gone after N days. Everything inside the free plan.

Template: [assets/private-pages/](assets/private-pages/), copied into its own repo:

| File | Role |
|---|---|
| [src/index.js](assets/private-pages/src/index.js) | Worker: serves `/p/<24 hex>` only, validates the Access JWT against the page's own AUD, 410 after expiry, `private, no-store` |
| [wrangler.jsonc](assets/private-pages/wrangler.jsonc) | custom domain, `workers_dev`/`preview_urls` off, KV binding auto-provisioned on first deploy |
| [share.py](assets/private-pages/share.py) | `publish` / `revoke` / `list` / `sweep` against the Cloudflare API, stdlib only |
| [test/](assets/private-pages/test/) | Worker tests (`node --test`) and `share.py` tests (`python3 -m unittest`) |

## Design

- **Per page**: one reusable Access policy (recipients + owner) and one self-hosted app on `share.example.org/p/<name>`. App count is not the constraint (500); seats are (50).
- **Gate before content.** `share.py publish` creates policy → app → uploads; the upload carries the app's `aud` in KV metadata, and the Worker serves nothing whose metadata lacks an `aud` or whose request lacks a valid JWT for it. A page can't go public by misordering, a forgotten app, or a stray workers.dev URL.
- **Expiry twice**: metadata `expires` gives a clean **410 Gone**; KV `expiration` = expiry + 7 days deletes the stored copy on its own.
- **Revoke content first, gate second**: a half-revoked page is already unreadable, and `sweep` finishes any app whose content is gone or expired. Run `sweep` on a schedule (cron Worker or CI).
- Republish (`--name <existing>`) replaces content and expiry under the same link and gate.

## Setup

1. Domain on Cloudflare; Zero Trust org created (team domain `<team>.cloudflareaccess.com`); One-time PIN enabled; "Remove inactive users from seats" on.
2. Copy the template; set `routes[0].pattern` to the share host and `vars.ACCESS_TEAM_DOMAIN`. `pnpm add -D wrangler && pnpm exec wrangler deploy` (creates the KV namespace; read its id from the config or `wrangler kv namespace list`).
3. Optional extra layer: Worker-level Access with a policy that admits only the owner, so the bare host and any preview URL demand a login too. Per-page apps are more specific and take precedence on `/p/<name>`.
4. Token (account-owned): Access: Apps and Policies Edit + Workers KV Storage Edit.
5. Publish:

```bash
export CLOUDFLARE_API_TOKEN=… CLOUDFLARE_ACCOUNT_ID=… SHARE_HOST=share.example.org SHARE_KV_NAMESPACE_ID=… SHARE_OWNER=me@example.org
python3 share.py publish briefing.html --to alex@client.example --expires 30d
python3 share.py publish briefing.html --name <name> --expires 14d
python3 share.py revoke <name>
python3 share.py sweep
```

6. Open the link in a private window with an address on the list (page) and one off it (no code arrives). Then send it.

## Limits of the guarantee

- Expiry stops serving; it does not recall what a recipient saved or printed.
- Every outside recipient takes a seat until removed. Sharing widely: rely on inactive-user removal, or use HMAC-signed expiring links (Cloudflare's "signing requests" Worker example) for low-sensitivity pages — no seat, but anyone holding the link can read it.
- One HTML file per page: styles and images inlined (data URIs), ≤ 25 MiB per KV value.
- Before trusting the template against a real account, publish one page to yourself and verify allowed, refused and expired paths. `share.py` is tested against a fake API, not a live account.

## Alternatives considered

| Primitive | Why not the default |
|---|---|
| One wildcard app `/p/*` + per-page email list checked in the Worker | Access must then admit the union of all recipients; anyone on any list can log in |
| R2 presigned URLs (≤ 7 days) / HMAC links | bearer links, no identity |
| R2 lifecycle rules | day granularity, no 410 |
| Access temporary authentication | manual approval per request |
