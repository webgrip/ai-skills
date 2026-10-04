# Platform reference: free-plan limits, features, wrangler

Contents: [limits](#free-plan-limits) · [static assets](#static-assets) · [feature status](#feature-status) · [wrangler 4](#wrangler-4) · [sources](#sources)

Numbers move. Re-check the linked page before quoting a limit to a client or designing right at its edge.

## Free-plan limits

| Item | Free | Over the limit |
|---|---|---|
| Static asset requests | unlimited, not counted as invocations | — |
| Worker invocations | 100,000/day, reset 00:00 UTC | error 1027 (route fail-open/fail-closed setting); 429 on `run_worker_first` paths |
| CPU per HTTP invocation | 10 ms | exceeded error |
| Subrequests | 50 external + 1,000 to Cloudflare services | |
| Worker size | 64 MiB uncompressed | |
| Workers / cron triggers / vars | 100 per account / 5 / 64 per Worker | |
| Startup / memory | 1 s / 128 MB | |
| Routes / custom domains per zone | 1,000 / 100 | |
| Static assets | 20,000 files per version, 25 MiB per file | deploy fails |
| KV | 100k reads/day, 1k writes, 1k deletes, 1k lists; 1 GB; 25 MiB/value; 1 write/s per key; eventually consistent ~60 s | ops fail |
| D1 | 5M rows read/day, 100k rows written/day, 5 GB total, 10 DBs × 500 MB, 50 queries/invocation | queries fail |
| R2 (Standard) | 10 GB-month, 1M class A, 10M class B ops/month, egress free | |
| Durable Objects | SQLite-backed only; 100k req/day, 13,000 GB-s/day, 5 GB | |
| Queues | 10,000 ops/day, 24 h retention | |
| Workflows | 100k req/day, 3,000 steps/day, 1,024 steps per instance | |
| Workers AI | 10,000 neurons/day | ops fail |
| Browser Rendering | 10 min/day, 3 concurrent | |
| Hyperdrive / Vectorize | 100k queries/day / 30M queried + 5M stored dims | |
| Images | 5,000 unique transformations/month | error 9422, no charge |
| Workers Logs | 200k events/day, 3-day retention | |
| Workers Builds | 3,000 min/month, 1 concurrent, 20 min timeout | |
| Worker Previews | 100 per Worker, 100 deployments per Preview | |
| Access (Zero Trust) | 50 seats; 500 apps, 500 reusable policies; logs 24 h | new users blocked |
| Redirect Rules / Bulk Redirects | 10 rules / 15 rules, 5 lists, 10,000 URLs | |
| Transform / Cache Rules / Page Rules | 10 / 10 / 3 (Page Rules deprecated) | |
| Email Routing | 200 rules per domain, 200 destination addresses | |
| Turnstile | 20 widgets, 10 hostnames each, unlimited challenges | |
| Web Analytics | unlimited proxied sites, 10 non-proxied | |
| Paid only | Containers, Sandbox SDK, Snippets, Data Localization Suite (Enterprise) | |

## Static assets

| Key | Values |
|---|---|
| `assets.directory` | build output dir |
| `assets.binding` | exposes `env.ASSETS.fetch()` to Worker code |
| `assets.not_found_handling` | `"none"` (default) · `"404-page"` (nearest `404.html`) · `"single-page-application"` (`/index.html`, 200) |
| `assets.html_handling` | `"auto-trailing-slash"` (default) · `"force-trailing-slash"` · `"drop-trailing-slash"` · `"none"`; redirects are **307** |
| `assets.run_worker_first` | `false` (default) · `true` · array of globs, `!` negation wins, ≤ 100 entries |

- Assets are served **before** the Worker (the reverse of Pages Functions); put auth/middleware paths in `run_worker_first`.
- SPA mode: from compatibility date `2025-04-01`, navigation requests (`Sec-Fetch-Mode: navigate`) skip the Worker; a `run_worker_first` array turns that detection off.
- `_headers`: 100 rules, 2,000 chars per line. `_redirects`: 2,000 static + 100 dynamic rules, 1,000 chars each, default 302, `200` proxies relative paths only.
- Default asset `Cache-Control: public, max-age=0, must-revalidate`; ETag is the content hash.
- Astro static: `output: 'static'`, no adapter. `build.format: 'file'` + `trailingSlash: 'never'` pairs with `html_handling: "auto-trailing-slash"`.
- Pages → Workers migration: `pages_build_output_dir` → `assets.directory`; `functions/` must become one Worker; `_routes.json` → `run_worker_first`; dev port 8788 → 8787.

## Feature status

| Feature | Status | Free |
|---|---|---|
| Workers static assets | GA, the recommended host for new sites | yes |
| Pages | supported, de-emphasised; no end-of-life date | yes |
| Worker Previews (`wrangler preview`, per-branch env/vars/secrets/URL) | open beta, wrangler ≥ 4.135 | yes |
| Version URLs (`versions upload --preview-alias`) | GA; not generated for Workers with DO, Containers or Sandbox | yes |
| Access on a Worker (covers routes, custom domains, workers.dev, previews) | GA; 403 on WebSocket upgrades | yes |
| `ctx.access` identity in Worker | GA; not passed through service bindings, RPC, or Workers with static assets | yes |
| Auto-provisioning of KV/D1/R2/Queues | GA (wrangler ≥ 4.45) | yes |
| Autoconfig (`wrangler deploy` detects framework; `wrangler setup`) | GA | yes |
| Remote bindings in `wrangler dev` (`"remote": true`) | GA | yes |
| `nodejs_compat` default on | from compatibility date 2026-08-04 | yes |
| Workers VPC | beta, free while beta | yes |
| Smart Placement, automatic tracing | GA / open beta | yes |
| Python Workers | GA-ish | yes |
| Durable Objects (SQLite) / Agents SDK | GA | yes |
| Secrets Store | open beta | check |
| `cf` CLI (whole Cloudflare API, `cf migrate` from wrangler config) | beta, coexists with wrangler | yes |
| Containers, Sandbox SDK | GA | **no** |

Open issues worth knowing: `wrangler preview` ignores `not_found_handling: "404-page"` and `_headers` (workers-sdk#16047); each `wrangler preview` drops that Preview's secrets — pass `--secrets-file` every time (#15942); Workers Builds fails non-production builds when the config lacks a `previews` block (#15979).

## Wrangler 4

- One major line (v4, near-daily minors; `legacy` tag is v3). Pin it.
- `wrangler types` generates `Env` types for every environment; `wrangler types --check` fails CI on drift.
- `deploy --strict` refuses when the remote has dashboard edits the config would clobber; `--keep-vars` keeps dashboard vars.
- `wrangler secret bulk` (≤ 100 per call); `secrets` config key declares required secret names; `deploy --secrets-file` is additive.
- `wrangler tail` needs the Metadata Read role; `observability.head_sampling_rate` thins logs.
- `wrangler versions upload` + `wrangler versions deploy` for gradual rollouts (percentage split between versions).
- Hidden/experimental flags: `--x-provision` and `--x-auto-create` (default on; `--no-x-provision` to opt out), `--x-deploy-helpers`, `--x-new-config` (`cloudflare.config.ts`), `--x-route-zones`. `--x-remote-bindings` and `--x-autoconfig` are gone (GA).
- Account-owned API tokens can fail the `/memberships` lookup; setting `CLOUDFLARE_ACCOUNT_ID` skips it.

## Sources

All under `https://developers.cloudflare.com`: `/workers/platform/limits/` · `/workers/platform/pricing/` · `/workers/static-assets/billing-and-limitations/` · `/workers/static-assets/routing/` · `/workers/static-assets/headers/` · `/workers/static-assets/redirects/` · `/workers/static-assets/migration-guides/migrate-from-pages/` · `/workers/wrangler/configuration/` · `/workers/previews/` · `/workers/configuration/previews/` · `/workers/configuration/cloudflare-access/` · `/kv/platform/limits/` · `/d1/platform/limits/` · `/r2/pricing/` · `/workers/ci-cd/builds/limits-and-pricing/` · `/rules/url-forwarding/` · `/cloudflare-one/account-limits/` · `/changelog/product/workers/`.
