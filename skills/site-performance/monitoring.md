# Monitoring: RUM, synthetic checks and the Worker side

CrUX covers only Chrome users outside iOS, only above an undisclosed traffic threshold, 28 days late. Real user monitoring (RUM) fills those gaps with your own visitors, by template, browser and build. Vendors' descriptions of their own products are Strong as statements of what they offer; their claims about the law are vendor claims. Prices and features checked 2026-10-04.

Contents: what to run by site size · RUM products · Cloudflare Web Analytics · the DIY kit · synthetic and uptime · the Worker side · privacy in the EU · alerting

## What to run by site size

| Site | Run |
| --- | --- |
| Pre-launch or too small for CrUX | Lighthouse CI and `perf_scan.py site` on every pull request; Unlighthouse monthly; Cloudflare Web Analytics switched on **with EU visitors included**; uptime from two regions |
| Small (up to ~100k page views a day) | the above, plus the DIY kit below for LCP subparts, INP phases, templates and build ids; CrUX API and CrUX Vis once the site qualifies |
| Larger, or revenue depends on speed | a RUM vendor (RUMvision is the EU-stored choice; DebugBear if you want RUM and scheduled lab tests in one tool); keep Lighthouse CI as the pull-request gate |
| Already running Datadog, Dynatrace or New Relic for a backend | their RUM can make sense, at 47–63 KB of script, session cookies and per-session pricing |

## RUM products

| Product | Collects | Data in the EU | Cookies | Price | Script (gzip) |
| --- | --- | --- | --- | --- | --- |
| RUMvision (NL) | CWV with attribution, LCP subparts, Long Animation Frames, soft navigations, 45+ dimensions, templates, daily regression alerts | "Stored in the EU" | none; no IPs stored (vendor) | Growth €150/month for 1.5M page views and 2 domains; Scale €700/month; no free tier | configurable, not published |
| DebugBear (UK) | CWV with attribution, script attribution, soft navigations; scheduled lab tests | IP proxy in Germany on request; storage region not stated | none by default | plan plus RUM add-ons; trial | < 10 KB (vendor) |
| SpeedCurve | CWV, LoAF, LCP subparts; synthetic | not stated | session cookies | from $90/month | — |
| Sentry | LCP, CLS, INP, TTFB, errors, traces | yes, Frankfurt (chosen at signup) | configurable | free tier: 5k errors, 5M spans | 31 KB errors, 52 KB with tracing |
| Grafana Faro (open source) | web-vitals, errors, traces | Grafana Cloud EU or self-hosted | browser storage session | 50k sessions/month free | 40 KB |
| Request Metrics (US) | CWV | no | none stored (vendor) | free for one small site, $37+/month | 13 KB |
| Datadog, New Relic, Dynatrace | full RUM and session replay | EU regions available | session cookies | per session or per GB | 47–63 KB (Datadog) |
| Cloudflare Web Analytics | LCP, INP, CLS at p50–p99 with top-five element selectors | no (US processor) | none | free, 10 sites | 10 KB |
| DIY kit | everything `web-vitals` exposes, your dimensions | Cloudflare (US processor) | none | free up to ~100k page views a day | ~6 KB |

Vercel Speed Insights works only on Vercel-hosted projects; OpenTelemetry browser instrumentation is still experimental.

## Cloudflare Web Analytics

Cookieless and free, but limited:

- **On the Free plan the automatic setup excludes visitors from the EEA, the UK and Switzerland** ([Observatory](https://developers.cloudflare.com/speed/observatory/)). A Dutch site on the default sees almost none of its audience. Choose "Enable" (all visitors) or add the snippet manually ([get started](https://developers.cloudflare.com/web-analytics/get-started/)).
- No LCP subparts, INP phases, Long Animation Frame scripts, build or template segmentation, or alerts. Data is unsampled for 7 days, then aggregated; six months available. Ad blockers block it.

## The DIY kit

[assets/rum/](assets/rum/) is a working setup: `src/vitals.js` (the `web-vitals` 6 attribution build, one `sendBeacon` when the page is hidden), `src/worker.js` (a `/rum` endpoint that writes one Workers Analytics Engine data point per page view), `queries.sql` (p75 by template and device, LCP subparts, INP by target, regressions by build) and Node tests.

1. Install `web-vitals` in the site and import `vitals.js` from the base layout (Astro: `<script>import "../rum/vitals.js";</script>`). Put `data-template="event"` and `data-build="<git sha>"` on `<html>` so pages group by template and every value is tied to a deploy.
2. Add the Worker: `main: "src/worker.js"`, `assets.binding: "ASSETS"`, `run_worker_first: ["/rum"]`, the `analytics_engine_datasets` binding, and `observability.logs.invocation_logs: false` so request metadata is not logged ([wrangler.jsonc](assets/rum/wrangler.jsonc)). Only `/rum` invokes the Worker; static assets stay free.
3. Query with the SQL API: `POST https://api.cloudflare.com/client/v4/accounts/<account_id>/analytics_engine/sql` with a token holding Account Analytics Read. p75 is `quantileExactWeighted(0.75)(double1, _sample_interval)`; missing metrics are stored as −1, so filter `>= 0`.

Limits: Analytics Engine on Workers Free includes 100,000 data points and 10,000 queries a day (not yet billed; Paid includes 10M points a month), keeps data three months, and allows 20 blobs and 20 doubles per point ([pricing](https://developers.cloudflare.com/analytics/analytics-engine/pricing/), [limits](https://developers.cloudflare.com/analytics/analytics-engine/limits/)). Each beacon is also a Worker request, counted in the account's 100,000 a day. There is no upsert: a visitor who returns through the back/forward cache sends a second beacon.

## Synthetic and uptime

- **Lighthouse CI** on every pull request ([measurement.md](measurement.md#budgets-in-ci)); **Unlighthouse** monthly over the whole site; **sitespeed.io** for scheduled runs with history on your own box.
- **Uptime** from at least two regions, alerting on two consecutive failures: Uptime Kuma (self-hosted), Better Stack or Checkly free tiers, or Oh Dear (data in Belgium) paid. An uptime check from one box says little about the edge.
- Synthetic alone is enough before launch and for sites without interactive UI; INP needs real interactions, so RUM is needed once there is JavaScript worth measuring.

## The Worker side

For the few endpoints a static site runs (forms, signups, the RUM endpoint):

- **Workers Logs and Traces**: logs free up to 200,000 a day (3 days retention); traces in beta, OpenTelemetry-shaped. From 2026-12-01 Observability moves to per-GB pricing (Free: 0.5 GB ingested a day, 7 days). Export via OTLP to Grafana Cloud, Sentry, Honeycomb and others ([OTel export](https://developers.cloudflare.com/workers/observability/exporting-opentelemetry-data/)).
- **Tail Workers** and **Logpush** are Workers Paid features in the docs (a 2026-10-02 blog says Logpush reaches all self-serve plans; Contested until the docs agree).
- **Sentry** (`@sentry/cloudflare`) for errors; server spans show 0 ms because Worker clocks advance only across I/O.
- Write `CF_VERSION_METADATA.id` into Analytics Engine points and `Server-Timing` so Worker regressions line up with deploys. Baselime was folded into Workers Observability; don't recommend it as a product.

## Privacy in the EU

- **Sending measured values is device access too.** The EDPB's Guidelines 2/2023 treat a script that makes the browser send locally measured values as "gaining access" under ePrivacy Art. 5(3), cookies or not. Whether consent is needed then depends on an exemption (Strong).
- **In the Netherlands the exemption covers RUM**: Telecommunicatiewet art. 11.7a lid 3(b) exempts access that measures the quality or effectiveness of the service when it has "geen of geringe gevolgen" for privacy; the Autoriteit Persoonsgegevens applies the same reasoning to limited analytics (Strong for the statute; applying it to RUM is Consistent). Other member states differ.
- **GDPR still applies** because every beacon carries an IP address: legitimate interest as the basis, a processor agreement with the vendor or Cloudflare, and a line in the privacy statement (what, why, retention, processor).

A low-risk setup, as the kit is built: no cookies or storage, no user or session id, IP never stored (country from `request.cf.country` only), query strings stripped, selectors but no element text, aggregated, not combined with marketing data or shared, short retention, EU processing where the options are equal. A proposed EU exemption for audience measurement (Digital Omnibus) is still pending (Contested). This is not legal advice; the owner decides.

## Alerting

- Watch p75 per template × phone/desktop, the top two or three countries, and browser engine. Never averages.
- Alert only with enough data (n ≥ 300–500 in the window) and on a state change across a "good" threshold, or on p75 worse by 15–20 % against the previous 28 days for two days running (practitioner rule of thumb, Anecdotal).
- Group p75 by build id to tie a regression to a deploy; confirm by re-running the lab on the previous and current versions (Cloudflare version preview URLs).
- CrUX and Search Console lag 28 days: weekly trend, not an alarm.
