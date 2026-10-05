# Measurement: field judges, lab diagnoses, CI guards

Contents: the order of evidence · proving a change · budgets in CI · lab tools · reporting

## The order of evidence

1. **Field data at p75 per form factor**: your RUM ([monitoring.md](monitoring.md)), then CrUX (`perf_scan.py live --field`, CrUX Vis, Search Console). This is what users get and what Google ranks on.
2. **Lab traces** reproduce and explain a field problem: DevTools Performance panel with the LCP subparts and insights, Lighthouse, WebPageTest.
3. **Static scans** (`perf_scan.py site`) find causes before they ship.

Rules that keep this honest (taken from the better published skills and Google's guidance):

- **Missing field data is unavailable, never passing.** Label CrUX numbers with their scope (URL or origin) and form factor.
- **Metrics before code**: decide what is slow from data, then read code. Findings from reading code alone are hypotheses until a trace or RUM confirms them.
- **Say so when it is already good.** A page with 1.2 s LCP and 0.02 CLS needs nothing; skip non-issues whose estimated gain is about zero. "No change recommended" is a valid outcome.
- **Segment before concluding**: page template × phone/desktop × browser engine. A site-wide p75 hides the one slow template.
- At least about 50 samples per segment before reading a p75; more before alerting.

## Proving a change

- One change at a time; measure before and after under the same conditions: lab median of at least 3 runs (5 for noisy pages), field p75 over a comparable window, or RUM grouped by build id.
- **A neutral result is a revert, not a keep**: complexity with no measured gain is a cost.
- Keep a short log beside the code (`docs/performance.md` or similar): change, metric before, after, sample, decision, including reverted attempts.
- Field data needs about four weeks to reflect a change fully (28-day window); RUM grouped by build shows it within days.

## Budgets in CI

Gate on bytes and lab metrics measured as medians within a noise band, never on a score.

| Budget | Value for a static marketing or community site | Tool |
| --- | --- | --- |
| JavaScript per page | ≤ 100 KB compressed | `perf_scan.py site` (`js-over-budget`), size-limit |
| CSS per page | ≤ 50 KB compressed | `perf_scan.py site` (`css-over-budget`) |
| Fonts | ≤ 3 WOFF2 files, ≤ 100 KB | Lighthouse `resource-summary:font:size` |
| Mobile hero image | ≤ ~150 KB | `perf_scan.py site --hero-budget-kb 150` |
| Total transfer | ≤ 1 MB | Lighthouse `resource-summary:total:size` |
| Third-party origins | ≤ 3 | `resource-summary:third-party:count` |
| Lab LCP, CLS, TBT | ≤ 2.5 s, ≤ 0.1, ≤ 200 ms (mobile) | Lighthouse CI, median run |

The values are judgment, anchored to Alex Russell's 2026 model (2 MiB critical path with 0.3 MiB JavaScript for a 3 s target on a mid-range phone, which he calls "extremely generous"; Anecdotal) and to field medians far above them.

**Lighthouse CI traps** ([configuration](https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/configuration.md)):

- `@lhci/cli` 0.15.1 bundles Lighthouse 12.6.1 while Lighthouse itself is at 13.x, which renamed or removed most performance audits in favour of "insights" (`unsized-images` and `layout-shifts` became `cls-culprits-insight`, `lcp-lazy-loaded` became `lcp-discovery-insight`). An assertion on an audit the report lacks fails with "not a known audit". Pin the version, and rewrite assertions when it moves.
- The default aggregation is `optimistic` (the best of the runs): set `aggregationMethod: "median-run"` or `pessimistic`.
- `resource-summary:<type>:size` budgets are in bytes; `budget.json` (in KB) was removed in Lighthouse 12.
- **The default preset is mobile, and that is the one that matters**: field data and ranking use phones. A `desktop` preset hides mobile problems; run desktop in addition, not instead.
- `collect.staticDistDir` serves the build without a server; never upload reports to the public temporary storage for a private site.

```json
{
  "ci": {
    "collect": { "staticDistDir": "./dist", "url": ["http://localhost/index.html", "http://localhost/events.html"], "numberOfRuns": 5 },
    "assert": {
      "assertions": {
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500, "aggregationMethod": "median-run" }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1, "aggregationMethod": "median-run" }],
        "total-blocking-time": ["warn", { "maxNumericValue": 200, "aggregationMethod": "median-run" }],
        "resource-summary:script:size": ["error", { "maxNumericValue": 102400 }],
        "resource-summary:third-party:count": ["warn", { "maxNumericValue": 3 }]
      }
    }
  }
}
```

- **size-limit** with `@size-limit/file` over `dist/_astro/*.js` reports Brotli sizes per bundle.
- `perf_scan.py site --fail-on fail` in the same job catches lazy heroes, missing dimensions and blocking scripts in seconds without a browser.

## Lab tools

| Tool | Use |
| --- | --- |
| Chrome DevTools Performance panel | live LCP, CLS, INP while you interact; field values beside them; LCP subparts; throttle to match the field |
| Lighthouse 13 / PageSpeed Insights | a quick lab run; PSI also shows CrUX, but its API will drop CrUX data, so read the CrUX API directly |
| WebPageTest (Catchpoint) | filmstrips, request waterfalls, real devices and locations; free tier limited |
| sitespeed.io | open-source scheduled runs in Docker with filmstrips, budgets and Graphite/Grafana history |
| Unlighthouse | Lighthouse across every page of the site; a monthly sweep (`npx unlighthouse --site https://example.org`) |
| Cloudflare Observatory | Lighthouse runs from Cloudflare locations; quotas on Pro and up |

## Reporting

Open every report with an evidence table: source (RUM, CrUX URL or origin, lab), form factor, window, sample size, date. Then findings ranked by measured impact, each with its metric, subpart or phase, fix, and how it will be verified; what was not measured; and the next measurement date. Never present a lab score as the user experience.
