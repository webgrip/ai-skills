---
name: site-performance
description: Makes static sites on Cloudflare's edge fast for real users and proves it with field data - Core Web Vitals (LCP, INP, CLS) diagnosed by subpart and phase, ranked fixes for hero images, fonts, JavaScript, third parties and layout shift, edge caching, speculation rules and the back/forward cache, RUM and APM choices (RUMvision, Cloudflare Web Analytics, a free web-vitals beacon into Workers Analytics Engine, Workers Observability) with EU privacy, Lighthouse CI budgets, and a build plus live scanner. Use when a site is slow or feels slow; when LCP, INP or CLS fail in PageSpeed Insights, Lighthouse or Search Console; to improve a Lighthouse or PageSpeed score; when setting up real user monitoring, RUMvision, CrUX, synthetic checks or performance alerts; when adding a performance budget to CI; when a hero image, web font, cookie banner or third-party script slows a page; or to check whether a site is fast enough. Not for search rankings (search-visibility) or deployment (edge-hosting).
---

# Site performance — fast for real users, measured in the field

**Field data judges; lab data diagnoses.** Google ranks on real Chrome users at the 75th percentile, not on a Lighthouse score, and real users are the point anyway. About half of sites fail Core Web Vitals on mobile, mostly on LCP, and the usual cause is not image size but how late the browser learns about the LCP resource. Static output on Cloudflare starts fast; it loses speed to a handful of build and edge mistakes. → [evidence.md](evidence.md)

Evidence labels: **Strong** (the platform's docs or spec, a controlled experiment, a large published sample) · **Consistent** · **Contested** · **Anecdotal** (one site, a vendor case study, a slide). The famous "53 % leave after 3 seconds" and "100 ms costs 1 %" figures are Anecdotal; don't quote them.

## Procedure

1. **Read the field first.** Your RUM, then `CRUX_API_KEY=… python3 scripts/perf_scan.py live https://example.org --field` (URL and origin p75 on phones), CrUX Vis for trends, Search Console's Core Web Vitals report. Missing field data is unavailable, never passing. Segment by template × phone/desktop × browser engine. → [metrics.md](metrics.md#field-data)
2. **Decide whether there is a problem.** All three good at p75 on phones and nothing in the scans: say so and stop. Otherwise pick the worst metric on the most-visited template.
3. **Diagnose before fixing.** LCP by its four subparts, INP by its three phases and the Long Animation Frame script, CLS by its largest shift: from RUM attribution or a DevTools Performance trace throttled to match the field. → [metrics.md](metrics.md#diagnosing-each)
4. **Scan the build.** `python3 scripts/perf_scan.py site path/to/repo`. Rules → [checks.md](checks.md)
5. **Fix in impact order.**
   - LCP: hero in the HTML, never lazy, `fetchpriority="high"`, no redirect hops, `srcset` with `sizes`, then bytes → [lcp.md](lcp.md)
   - CLS: dimensions on all media, banners as overlays, metric-matched font fallbacks, transform-only animation → [cls.md](cls.md)
   - INP: ship less JavaScript (islands without directives, `client:visible`), cut third parties, yield in long tasks → [inp.md](inp.md)
   - Delivery: immutable caching for hashed files, no `no-store`, own speculation rules, no `unload` → [delivery.md](delivery.md)
6. **Prove each change.** One change at a time; lab median of 3–5 runs under the same conditions, or RUM grouped by build id. A neutral result is a revert. Log changes, including reverted ones. → [measurement.md](measurement.md#proving-a-change)
7. **Guard it in CI.** `perf_scan.py site --fail-on fail` plus Lighthouse CI on the **mobile** preset, asserting metrics and byte budgets on the median run, with a pinned `@lhci/cli`. → [measurement.md](measurement.md#budgets-in-ci)
8. **Monitor.** Pick RUM by site size: Cloudflare Web Analytics with EU visitors included, the DIY beacon kit in [assets/rum/](assets/rum/) for subparts, phases and build ids, or RUMvision for larger sites; uptime from two regions; Workers Observability for endpoints. Alert on p75 state changes with enough samples. → [monitoring.md](monitoring.md)
9. **Report.** An evidence table first (source, scope, form factor, window, sample, date), then findings ranked by measured impact with fix and verification, what wasn't measured, and when to look again. Never present a lab score as the user experience.

## Gotchas

- **Compressing the hero is rarely the fix.** On slow origins the image download is under 10 % of LCP; the delay before it starts is about four times the download.
- **Astro `<Image>` is lazy by default.** The hero needs `priority` (5.10+); output is WebP only unless `<Picture formats>`; no `layout` means no `srcset`.
- **Workers static assets revalidate hashed files on every repeat visit** (`max-age=0, must-revalidate`) unless `_headers` marks them immutable.
- **Lighthouse CI's default aggregation is the best run**, its desktop preset hides mobile problems, and `@lhci/cli` 0.15.1 bundles Lighthouse 12, whose audit names Lighthouse 13 removed.
- **Cloudflare Web Analytics on Free skips EU visitors** in its automatic setup; Speed Brain probably does nothing on an assets-only Worker; Early Hints need the zone toggle and `Link` headers; Rocket Loader and Cloudflare Fonts cost more than they give.
- **CLS is Chromium-only; CrUX excludes iOS.** Safari and Firefox report LCP and INP since 2025–26, timed slightly earlier than Chrome: segment RUM by engine.
- **`no-store` no longer blocks the back/forward cache in Chrome; `unload` stops running there from version 154.** Both still matter elsewhere.
- **Loading tag managers on first interaction moves their cost onto INP** and hides it from Lighthouse. Remove tags instead.
- **A cookieless beacon is still device access under EU ePrivacy**; in the Netherlands the quality-measurement exemption covers it, GDPR still applies to the IP in transit.
- **Speed is a small ranking factor and no known factor for AI citations.** Optimise for users; don't promise rankings.

## Example

[case-twente.md](case-twente.md): a fast Astro site on Workers with a desktop-only Lighthouse gate, a lazy first image on one page, and a web-vitals beacon that needs attribution, a build id and query-string stripping to be useful.
