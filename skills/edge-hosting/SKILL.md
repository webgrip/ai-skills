---
name: edge-hosting
description: Ships static sites, Workers and private pages on Cloudflare's free edge tier with wrangler - Workers static assets over Pages, routes vs custom domains, www-to-apex redirects, DNS as code (DNSControl, OpenTofu, external-dns), Zero Trust Access gating and expiring per-recipient share links, preview deploys, least-privilege CI tokens, free-tier limits, a wrangler config linter and live-site prober, and when Netlify, GitHub Pages, Bunny or an EU host wins instead. Use when deploying or migrating a site to Cloudflare Workers or Pages; writing or reviewing wrangler.toml or wrangler.jsonc; a Cloudflare-hosted site or its www returns 522, times out or deploys green but serves nothing; wiring a custom domain, DNS records or a redirect; putting Cloudflare Access, a login or Zero Trust in front of a site, staging, preview or homelab service; sending a client a private or expiring web page; choosing free static, edge or serverless hosting; or asking what Cloudflare's free plan covers.
---

# Edge hosting — free Cloudflare edge, deployed so it stays up

## Pick the shape

| Need | Shape | Cost driver |
|---|---|---|
| Static / SSG site (Astro, Hugo, Vite build) | **Assets-only Worker**: no `main`, `assets.directory` | none — asset requests are free and unmetered |
| Site plus a few endpoints (form, signup, webhook) | Worker + assets, `run_worker_first: ["/api/*"]`, `assets.binding: "ASSETS"` | only matched paths count toward 100k/day |
| SPA | assets with `not_found_handling: "single-page-application"` | none |
| SSR framework | its adapter (`@astrojs/cloudflare`, `@opennextjs/cloudflare`) | every request is an invocation |
| Page only named people may read, expiring | [private-pages.md](private-pages.md) + [assets/private-pages/](assets/private-pages/) | Access seats |
| Staging, previews, internal tool, homelab service | Worker-level Access or Tunnel + Access → [access.md](access.md) | Access seats |
| Nameservers can't move to Cloudflare, EU-owned vendor required, or no Cloudflare at all | [alternatives.md](alternatives.md) | — |

New projects go on **Workers**, not Pages: Cloudflare says "start new projects with Workers"; Pages keeps running, so migrate an existing Pages site only for a Workers-only feature. Workers needs the zone's nameservers on Cloudflare; Pages does not.

## Default config (static site)

`wrangler.jsonc` for new projects (some newer features are JSON-config-only); an existing `wrangler.toml` is fine.

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "example-org",
  "compatibility_date": "2026-10-01",
  "workers_dev": false,
  "preview_urls": false,
  "routes": [{ "pattern": "example.org/*", "zone_name": "example.org" }],
  "assets": { "directory": "./dist", "html_handling": "auto-trailing-slash", "not_found_handling": "404-page" },
  "observability": { "enabled": true }
}
```

- **Every public hostname needs a claimant**: a Worker route, a custom domain, or a redirect rule. A proxied record nobody claims answers **522 after ~20 s**. `www` gets a 301 single redirect rule to the apex (free plan: 10 rules). → [dns.md](dns.md)
- **Route or custom domain**: `{"pattern": "example.org", "custom_domain": true}` creates the DNS record and certificate itself but refuses while any A/AAAA/CNAME exists on that name. On a zone with leftovers, use a **route** over a proxied placeholder (`AAAA 100::` or `A 192.0.2.1`); switch to a custom domain once the zone is clean.
- **`workers_dev` and `preview_urls` explicit.** `true` only when those `*.workers.dev` URLs may be public or Worker-level Access gates them; they bypass zone redirects, WAF and hostname-scoped Access.
- **Environments**: bindings (`kv_namespaces`, `d1_databases`, `r2_buckets`, `vars`, …) are **not inherited** by `env.*`; give staging its own resources, never the production ID. `assets`, `routes`, `compatibility_date` are inherited.
- **Auto-provisioning**: declare a KV/D1/R2 binding without an id and `wrangler deploy` creates it and writes the id back.
- **`public/_headers`** (100 rules) for security headers and `Cache-Control: public, max-age=31536000, immutable` on hashed asset dirs (`/_astro/*`); **`public/_redirects`** (2,000 static + 100 dynamic, default **302**, write `301` explicitly). Both apply to asset responses only, never to responses your Worker code builds.
- **Secrets**: `wrangler secret put` / `secret bulk`, never `vars`. Where the value lives and how CI gets it → the `secrets-levels` skill.
- **`compatibility_date`**: pin it, no newer than the pinned wrangler's runtime supports. Crossing `2025-04-01` changes SPA navigation handling; crossing `2026-08-04` turns `nodejs_compat` on by default.

## Deploy

1. Pin wrangler as a devDependency and run `pnpm exec wrangler …` (or `npx wrangler` from the lockfile). Unpinned `dlx` floats onto near-daily releases and can hang on pnpm's build-script prompt.
2. Lint the config: `python3 scripts/edge_check.py config path/to/repo` (rules → [checks.md](checks.md)).
3. CI: `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`; token = Workers Scripts Edit on the account **and** Workers Routes Edit on each zone. → [ci.md](ci.md)
4. Previews: `wrangler versions upload --preview-alias <branch>` (Version URLs) or `wrangler preview` (per-branch Previews, open beta). Both are public unless the Worker is behind Access.
5. After deploy: poll until the edge serves the new build (a fresh route can 522 for a minute), then smoke-test key 200s, one real 404, and every `_redirects` rule. Probe the live hostnames: `python3 scripts/edge_check.py live example.org`.

## Free-plan facts that change decisions

- **Static asset requests: free, unlimited, not counted.** Worker invocations: 100,000/day, 10 ms CPU each. Over the limit: error 1027 (route can fail open to assets) or 429 on `run_worker_first` paths. The free plan **never bills**.
- 20,000 files per version, 25 MiB per file. KV 1,000 writes/day. D1 5 GB. R2 10 GB with free egress. Access 50 seats.
- Paid only: Containers, Sandbox, Snippets. Full table, feature status, wrangler flags → [platform.md](platform.md).

## Gotchas

- **Green deploy, dead site**: `workers_dev: false` and no route → wrangler prints "No targets deployed", exits 0, every path 522s.
- **TOML table capture**: a top-level key (`routes`, `workers_dev`) written after the first `[table]` header belongs to that table and is silently ignored.
- **Dashboard toggles revert**: workers.dev disabled in the dashboard comes back on the next deploy; dashboard-set vars are deleted unless `--keep-vars`. The config file is the truth.
- **Placeholder origins**: proxied placeholder records point at `192.0.2.1` / `100::`, never a parking or registrar IP — if the route drops, traffic goes to a third party.
- **One writer per record set**: DNSControl, OpenTofu or external-dns, never two on the same names. They diff against the Cloudflare API, not `dig`; records Cloudflare manages itself are invisible to them.
- **Trailing-slash redirects are 307** and not configurable; use a redirect rule where an SEO-permanent redirect matters.
- **Email Routing**: two rules for the same address deliver only the first.
- **Privacy**: Cloudflare is a processor to name in the privacy statement; it adds NEL `report-to` headers (switchable per zone); Web Analytics is cookieless. EU data localization is Enterprise-only.

## Additional resources

- Limits, feature status, wrangler 4 features and experimental flags → [platform.md](platform.md)
- Routes, custom domains, redirects, DNS as code, zone settings, API tokens → [dns.md](dns.md)
- Access, seats, JWT validation, Worker-level protection, Tunnel → [access.md](access.md)
- Private expiring pages, Worker + `share.py` → [private-pages.md](private-pages.md)
- CI pipeline, previews, smoke tests, token scopes → [ci.md](ci.md)
- `edge_check.py` rule catalog → [checks.md](checks.md)
- Other free hosts and when they win → [alternatives.md](alternatives.md)
- Worked examples from the Webgrip estate → [case-webgrip.md](case-webgrip.md)
