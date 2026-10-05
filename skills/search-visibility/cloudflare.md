# Cloudflare: settings that decide what crawlers see

Deployment itself belongs to the `edge-hosting` skill. This file covers the edge behaviour that changes search and AI visibility without touching the repository. All facts come from Cloudflare's own documentation and blog (Strong) unless marked. The dashboard paths and Terraform fields move; check the linked page before changing anything.

Contents: AI bot policies · robots.txt Cloudflare writes · bot protection · Markdown for Agents · 404 handling · trailing slashes · mirror hostnames · speed features · infrastructure as code

## AI bot policies

Dashboard: zone → **Security → Settings → Configure AI bot policies**, or **AI Crawl Control**. Three behaviours (Search, Agent, Training), each Allow, Block on pages with ads, or Block; Training also has **Disallow AI Training** ([block AI bots](https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/), [2026-09-15 change](https://blog.cloudflare.com/accountable-mixed-use-ai-crawlers/)).

| Setting | Effect | For a site that wants search traffic |
| --- | --- | --- |
| Search: Allow | AI search crawlers (OAI-SearchBot, Claude-SearchBot, PerplexityBot) reach the site | yes |
| Agent: Allow | fetches on a person's request in an assistant (ChatGPT-User, Claude-User) work | yes, unless there is a reason |
| Training: **Disallow AI Training** | publishes the no-training preference in robots.txt (Google-Extended, Applebot-Extended) and blocks training-only crawlers (GPTBot, ClaudeBot, Meta, Amazon) at the edge; Googlebot, Bingbot and Applebot stay allowed for search | the safe opt-out |
| Training: **Block**, or **Block on pages with ads** | since 2026-09-15 also blocks the mixed-use crawlers: "It will stop Applebot, Bingbot, and Googlebot from reaching your site — search included" | **never** |
| Legacy "Block AI bots" toggle | deprecated 2026-09-15; mixed-use crawlers fall under the same blocking | migrate to the policy above |

- New domains get a policy at signup, and defaults since 2026-09-15 depend on whether pages carry ads. Check every zone; don't assume.
- **A spoofed user agent can't tell Disallow AI Training from Block**: both refuse GPTBot. The robots.txt can: Disallow AI Training writes a Cloudflare-managed `Google-Extended` group. `seo_scan.py live` warns when training crawlers are refused at the edge and no such group exists.
- The owner decides the training stance. Ask, record it in infrastructure as code, and never flip it silently.

## robots.txt Cloudflare writes

- **Managed robots.txt** prepends a block (`Content-Signal: search=yes, ai-train=no`, then `Disallow: /` for Amazonbot, Applebot-Extended, Bytespider, CCBot, ClaudeBot, Google-Extended, GPTBot, meta-externalagent) before the origin's own file ([managed robots.txt](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/)).
- **Bot Preference Sync** (on by default for new customers since 2026-08) prepends directives generated from the AI bot policies, wrapped in `# BEGIN/END Cloudflare Bot Preference Sync` ([blog](https://blog.cloudflare.com/bot-preference-sync/)).
- **Free zones with no robots.txt** get the Content Signals Policy served for them: comments only, harmless, but a sign the origin is not answering.
- **Content-Signal** lines (`search`, `ai-input`, `ai-train`) are a Cloudflare proposal; no crawler has committed to them, and Search Console may report "Syntax not understood" without effect on crawling (Cloudflare's statement).

The repository's `public/robots.txt` is therefore not what crawlers read. Diff the live file against it after every deploy (`seo_scan.py live` reports managed content and Content-Signal lines).

## Bot protection

- **Bot Fight Mode** (Free) cannot be skipped by WAF rules; verified bots sit on a global allowlist, but reports of false positives exist (Consistent). Turn it off for a public marketing site when crawlers or link previews fail.
- **Super Bot Fight Mode** (Pro+) has a "Verified bots: Block" option that blocks Googlebot and Bingbot. Keep it on Allow.
- **Managed Challenge, JS challenge or Under Attack Mode on HTML** blocks every crawler that doesn't run JavaScript, including social link previews (Slack ignores robots.txt but cannot pass a challenge). Exclude verified bots (`not cf.client.bot`) in broad WAF rules.
- **AI Crawl Control → Block** creates a WAF custom rule; the free plan detects crawlers by user agent only.
- **AI Labyrinth** serves link mazes to non-compliant bots; it targets unverified crawlers (not re-verified for search impact).

## Markdown for Agents

Pro plan and up: on `Accept: text/markdown` Cloudflare converts the HTML to Markdown ([docs](https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/)). **When the origin sends no `content-signal` header it adds `Content-Signal: ai-train=yes, search=yes, ai-input=yes`**, contradicting a managed robots.txt that says `ai-train=no`. Set the header in `_headers` if the feature is on. It also drops `ETag` and `Last-Modified`. Google does not use it.

## 404 handling

| Config | Unknown URL answers | Verdict |
| --- | --- | --- |
| Workers `not_found_handling: "404-page"` | nearest `404.html`, status 404 | right for every content site |
| Workers `"none"` (default) | empty 404 | correct status, no way back for people |
| Workers `"single-page-application"` | `/index.html` with **200** | soft 404 and a duplicate home page for every typo |
| Pages without a top-level `404.html` | SPA mode: every path matches the root | same trap ([serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/)) |

## Trailing slashes

`assets.html_handling` decides which form answers 200; every other form gets a **307** ([HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/)).

| Request | `auto-trailing-slash` (default) | `force-trailing-slash` | `drop-trailing-slash` |
| --- | --- | --- | --- |
| `/about` (from `about.html`) | 200 | 307 → `/about/` | 200 |
| `/about/` | 307 → `/about` | 200 | 307 → `/about` |
| `/docs` (from `docs/index.html`) | 307 → `/docs/` | 307 → `/docs/` | 200 |
| `/docs/index.html` | 307 → `/docs` → 307 → `/docs/` (two hops) | 307 → `/docs/` | 307 → `/docs` |

Configure the generator's URL format to match (Astro `trailingSlash` and `build.format`, Hugo `uglyURLs`), then make canonicals, links, hreflang and sitemap entries use the 200 form. Pages redirects `.html` and `/index.html` forms similarly.

## Mirror hostnames

| Hostname | Public? | Fix, in order of preference |
| --- | --- | --- |
| `<worker>.<subdomain>.workers.dev` | when `workers_dev` is not `false` | `workers_dev: false` |
| Version URLs, custom-domain Preview URLs | yes, no noindex | `preview_urls: false`, or Access |
| Workers Previews on workers.dev | sends `X-Robots-Tag: noindex` | fine as is |
| Production `<project>.pages.dev` | yes, no noindex | host-scoped `_headers`: `https://:project.pages.dev/*` → `X-Robots-Tag: noindex` |
| Pages preview deployments | send noindex by default | fine as is |
| `staging.` and other hostnames | as configured | Access in front (crawlers get a login page, never content) |

Host-scoped `_headers` rules (`https://example-org.example-account.workers.dev/*`) apply only on that host, so production is untouched; an unscoped `/*  X-Robots-Tag: noindex` hides production too (`headers-noindex-all`). `_headers` covers asset responses only, not responses a Worker builds. A canonical pointing at production softens a public mirror but is only a hint. AI Crawl Control's "Redirects for AI Training" (Pro+) 301s training crawlers to the canonical, so wrong canonicals spread there too.

## Speed features

Core Web Vitals are a minor ranking signal and a real user-experience one ([evidence.md](evidence.md#claim-table)). Speed, caching, compression, Early Hints, speculation rules and monitoring belong to the `site-performance` skill. One search-specific point: Crawler Hints pings IndexNow on cache misses, and static assets bypass the zone cache, so it may never fire for an assets-only Worker (inference, undocumented). Ping IndexNow from CI instead ([crawl-index.md](crawl-index.md#submitting)).

## Infrastructure as code

Every setting above is a field on `cloudflare_bot_management` (Terraform or OpenTofu) or `PUT /zones/{zone_id}/bot_management`: `ai_training` (`disabled | disallow | block | only_on_ad_pages`), `aisearch`, `ai_user`, `bot_preference_sync_enabled`, `is_robots_txt_managed`, `cf_robots_variant`, `crawler_protection`, `fight_mode`, `sbfm_verified_bots`. Put the chosen stance there so a dashboard click cannot drift it.
