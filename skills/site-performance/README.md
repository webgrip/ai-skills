# site-performance

Makes static sites on Cloudflare's edge fast for real users and proves it with field data. It is the speed sibling of `search-visibility` (findability), `edge-hosting` (deployment) and `product-ux` (interfaces).

What it does that the popular performance skills don't:

- **Field first, with evidence labels.** Real-user p75 per phone and desktop judges; lab traces diagnose; missing field data is unavailable, never passing. Every claim is labelled Strong, Consistent, Contested or Anecdotal. The famous numbers ("53 % leave after 3 s", "100 ms costs Amazon 1 %", Deloitte's 8 %) are traced to their sources and retired in favour of the randomised slowdown tests (0.2–0.6 % per 100 ms).
- **Diagnosis by subpart.** LCP by its four subparts, with the CrUX finding that slow origins spend under 10 % of LCP downloading the image; INP by phase with Long Animation Frames; CLS by its largest shift. Fixes are ranked by measured impact, with Astro, Hugo and Eleventy specifics.
- **Cloudflare's edge as it is.** Workers static assets revalidating hashed files on every visit, trailing-slash 307s in TTFB, Early Hints that need a zone toggle and rarely fire, Speed Brain that skips Worker routes, Rocket Loader and Cloudflare Fonts traps, and Web Analytics skipping EU visitors on Free.
- **Monitoring without guesswork.** RUM chosen by site size (Cloudflare Web Analytics, a DIY kit, RUMvision and others compared on data, EU storage, cookies, price and script weight), synthetic and uptime options with EU presence, Workers Observability for the endpoints, and the EU and Dutch privacy rules that actually apply to a beacon.
- **`assets/rum/`.** A working kit: a `web-vitals` 6 attribution beacon, a `/rum` Worker writing one Workers Analytics Engine data point per page view (no IP, no cookies, query strings stripped, build id), p75 queries for templates, LCP subparts, INP targets and regressions by build, and Node tests.
- **`scripts/perf_scan.py`.** A dependency-free scanner with 35 rules:
  - `site` reads the build with `_headers`: lazy or script-loaded hero images, missing priority, missing dimensions, `srcset` without `sizes`, blocking scripts, gzip-measured JavaScript and CSS budgets, heavy third parties, font loading, `client:only` islands, DOM size, `unload` handlers, caching of hashed files.
  - `live` reads the edge: time to first byte, compression, HTTP/3, cache headers, and with `--field` the CrUX p75 for the URL and origin.

## Install

```text
/plugin install site-performance@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s site-performance`.

## Example prompts

- "PageSpeed says LCP is 4 s on mobile. Fix it."
- "Is RUMvision worth it, or is something free good enough?"
- "The page jumps when the cookie banner and fonts load."
- "Add a performance budget to CI."
- "INP went poor after we added Tag Manager and a chat widget."

## Scanner

```bash
python3 skills/site-performance/scripts/perf_scan.py site path/to/repo
CRUX_API_KEY=… python3 skills/site-performance/scripts/perf_scan.py live https://example.org --field
```

Exit status 1 when a finding at or above `--fail-on` (default `fail`) exists. `test.sh` runs the `site` mode against `fixtures/careful` (nothing may fire), the unit tests (a generated careless site where every site rule must fire, and local servers for the live and CrUX rules), the RUM kit's Node tests, and checks every rule is documented in `checks.md`. Before release it was run against two real Workers sites; the false positives (stable brand file names taken for content hashes, a theme script in `<head>`, a local-only fallback `@font-face`) became exemptions.

## Sources

Each reference file links its sources:

- **Platforms:** web.dev and developer.chrome.com (metrics, thresholds, CrUX methodology and APIs, bfcache, prerender, soft navigations, Lighthouse scoring), the W3C specs via MDN compatibility data, Cloudflare developer docs and blog, Astro docs, the `web-vitals` README.
- **Data:** HTTP Archive Web Almanac 2025 (performance, page weight, third parties) and the technology report, CrUX release notes, the third-party-web dataset.
- **Experiments and audits:** Kohavi et al. on randomised slowdowns at Bing and Google, the HTTP Archive study of Lighthouse scores against CrUX, Google's single-site case studies labelled as such.
- **Law:** EDPB Guidelines 2/2023 on ePrivacy Art. 5(3), Telecommunicatiewet art. 11.7a, Autoriteit Persoonsgegevens guidance, GDPR Recital 30.
- **Market survey:** Cloudflare's `web-perf`, Addy Osmani's web-quality-skills, Vercel's `vercel-optimize` and other published performance skills, with their errors noted; RUM vendors' own documentation and pricing.
