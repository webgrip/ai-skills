# Case: the Webgrip estate

Three Astro sites on Workers static assets, deployed from Forgejo Actions through one reusable workflow. Worked examples of the shapes in [SKILL.md](SKILL.md), and the failures that produced its gotchas. Not a template for other estates' ids or hostnames.

## The sites

| Site | Shape | Files worth opening |
|---|---|---|
| webgrip.nl | assets-only Worker, route on the apex, PR previews via `versions upload`, deploy gated on Lighthouse + axe, smoke test of 19 paths, a 404 and every `_redirects` rule | [wrangler.toml](https://forgejo.webgrip.dev/webgrip/webgrip.nl/src/branch/main/wrangler.toml) · [public/_headers](https://forgejo.webgrip.dev/webgrip/webgrip.nl/src/branch/main/public/_headers) · [astro.config.mjs](https://forgejo.webgrip.dev/webgrip/webgrip.nl/src/branch/main/astro.config.mjs) · [ADR-0001](https://forgejo.webgrip.dev/webgrip/webgrip.nl/src/branch/main/docs/adrs/0001-astro-on-cloudflare-workers-static-assets.md) · [go-live runbook](https://forgejo.webgrip.dev/webgrip/webgrip.nl/src/branch/main/docs/runbooks/go-live.md) |
| twente.dev | assets-only Worker, bilingual (`_redirects`: `/ /nl 302`), release-driven staging (rc tag) and production (stable tag), DNSControl with nightly drift check | [wrangler.toml](https://forgejo.webgrip.dev/webgrip/twente.dev/src/branch/main/wrangler.toml) · [ops/dns/dnsconfig.js](https://forgejo.webgrip.dev/webgrip/twente.dev/src/branch/main/ops/dns/dnsconfig.js) · [on_release_published.yml](https://forgejo.webgrip.dev/webgrip/twente.dev/src/branch/main/.forgejo/workflows/on_release_published.yml) · [ADR-0018](https://forgejo.webgrip.dev/webgrip/twente.dev/src/branch/main/docs/adrs/0018-account-and-zone-resources-in-opentofu.md) |
| unfoldhq.dev | Worker + assets, `run_worker_first: ["/api/*"]` for a signup endpoint on D1, cron cleanup, DNSControl `CF_SINGLE_REDIRECT` www→apex | [apps/site/wrangler.toml](https://forgejo.webgrip.dev/webgrip/unfold/src/branch/development/apps/site/wrangler.toml) · [apps/site/ops/dns/dnsconfig.js](https://forgejo.webgrip.dev/webgrip/unfold/src/branch/development/apps/site/ops/dns/dnsconfig.js) · [apps/site/src/worker/app.ts](https://forgejo.webgrip.dev/webgrip/unfold/src/branch/development/apps/site/src/worker/app.ts) |

Shared deploy workflow: [cloudflare-deploy.yml](https://forgejo.webgrip.dev/webgrip/workflows/src/branch/main/.forgejo/workflows/cloudflare-deploy.yml). DNS workflow: [dnscontrol.yml](https://forgejo.webgrip.dev/webgrip/workflows/src/branch/main/.forgejo/workflows/dnscontrol.yml). Homelab tunnel: [cloudflare-tunnel helmrelease](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/kubernetes/apps/network/cloudflare-tunnel/app/helmrelease.yaml). Token placement and rotation: the `secrets-levels` skill.

## Failures behind the gotchas

| What happened | Root cause | Rule now |
|---|---|---|
| Deploy green, every path 522, Cloudflare's managed `robots.txt` served | `workers_dev = false` and no route: "No targets deployed" | `no-public-target` |
| Custom domain refused to attach | stale proxied A record from the previous host | route over placeholder until the zone is clean |
| Routes silently ignored | `routes =` written below `[assets]` in TOML | `misplaced-top-level-key` |
| Smoke test 522 seconds after a good deploy | route propagation | poll before asserting |
| Upload succeeded, route bind failed | token lacked Workers Routes Edit on the zone | per-zone route scope |
| `www` answered 522 | proxied `www` CNAME with no route and no redirect rule | every hostname needs a claimant |
| Apex placeholder was a registrar parking IP | copied from the registrar's defaults | `192.0.2.1` / `100::` |
| Two zone configs drifted within a week | two writers | one writer per record set |
| Declared CAA / `_domainconnect` records fought the API | DNSControl sees the API, not `dig` | don't declare Cloudflare-managed records |
| Staging signups landed in the production table | staging bound to the production D1 id | `shared-binding-across-envs` |
| Deploy failed after a date bump | `compatibility_date` newer than pinned workerd | bump wrangler first |
| Second Email Routing rule for an address never delivered | first rule wins | one rule per address |
| Signup body cap bypassed without `Content-Length` | cap read the header instead of counting bytes | count the streamed bytes |
