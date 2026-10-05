# Metrics: what is measured, where, and how to read it

Google's documentation and the specs are the source (Strong) unless marked.

Contents: the metrics · diagnosing each · browser support · field data · lab tools · navigations that change the numbers

## The metrics

| Metric | Good | Poor | Measures |
| --- | --- | --- | --- |
| **LCP** Largest Contentful Paint | ≤ 2.5 s | > 4.0 s | when the largest image, text block or video in the viewport rendered |
| **INP** Interaction to Next Paint | ≤ 200 ms | > 500 ms | the slowest-but-typical delay from a tap, click or key press to the next frame, over the whole visit |
| **CLS** Cumulative Layout Shift | ≤ 0.1 | > 0.25 | the largest burst of unexpected layout movement |
| TTFB Time to First Byte (supporting) | ≤ 0.8 s, "a rough guide" | > 1.8 s | navigation start to the first byte of HTML, redirects included |
| FCP First Contentful Paint (supporting) | ≤ 1.8 s | > 3.0 s | the first text or image painted |

- **The 75th percentile per form factor**: a page or origin passes when LCP, INP and CLS are all good at p75 of page loads, judged separately for phones and desktops ([vitals](https://web.dev/articles/vitals), [thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)). Report p75, never averages.
- INP replaced FID on 12 March 2024 ([announcement](https://web.dev/blog/inp-cwv-march-12)). FID and TTI are gone; advice that still names them is outdated.

## Diagnosing each

**LCP subparts** ([optimize LCP](https://web.dev/articles/optimize-lcp)):

| Subpart | From → to | Target share | Field median p75, poor-LCP origins |
| --- | --- | --- | --- |
| TTFB | navigation → first HTML byte | ~40 % | 2,270 ms |
| Resource load delay | first byte → LCP resource starts loading | < 10 % | 1,290 ms |
| Resource load duration | start → end of the LCP resource download | ~40 % | 350 ms |
| Element render delay | resource loaded → element painted | < 10 % | 360 ms |

The poor-LCP column ([common misconceptions](https://web.dev/blog/common-misconceptions-lcp), CrUX) is the point: the download is rarely the problem; the **delay before it starts** is. Text LCP has no resource, so LCP = TTFB + render delay.

**INP phases**: input delay (the main thread was busy when the input arrived), processing duration (event handlers), presentation delay (style, layout and paint of the next frame). The Long Animation Frames API names the scripts responsible ([LoAF](https://developer.chrome.com/docs/web-platform/long-animation-frames), Chromium only).

**CLS attribution**: the element that moved most and when; most shifts come from media without dimensions, late-inserted banners and web-font swaps ([CLS](https://web.dev/articles/cls)).

The `web-vitals` library (6.x) reports all of these; its `/attribution` build adds the subparts, phases, LoAF entries and target selectors ([web-vitals](https://github.com/GoogleChrome/web-vitals)).

## Browser support

| Metric | Chromium | Firefox | Safari (macOS and iOS) |
| --- | --- | --- | --- |
| LCP | yes | 122+ | 26.2+ (Dec 2025) |
| INP | yes | 144+ | 26.2+ |
| CLS | yes | no | no |
| Long Animation Frames | yes | no | no |
| Soft navigations | 151+ | no | no |

LCP and INP became Baseline in December 2025; Firefox and Safari time them to a slightly earlier point than Chrome ([web.dev](https://web.dev/blog/lcp-and-inp-are-now-baseline-newly-available)). **Segment RUM by browser engine**, and remember CLS figures are Chromium-only.

## Field data

**CrUX** is real Chrome users who opted in, on Android, desktop and ChromeOS; **Chrome on iOS is excluded and "this won't change"**. Rolling 28-day window, p75, origin and URL level, phone and desktop, with undisclosed traffic thresholds below which there is no data ([methodology](https://developer.chrome.com/docs/crux/methodology)).

| Source | Granularity | Use |
| --- | --- | --- |
| [CrUX API](https://developer.chrome.com/docs/crux/api) | latest 28 days, URL and origin | `perf_scan.py live --field` (free key, 150 queries a minute) |
| [CrUX History API](https://developer.chrome.com/docs/crux/history-api) | weekly 28-day windows, up to 40 weeks | trends; whether a fix landed |
| [CrUX Vis](https://cruxvis.withgoogle.com) | the History API as charts | sharing with people (replaced the CrUX Dashboard in November 2025) |
| [BigQuery](https://developer.chrome.com/docs/crux/bigquery) | monthly, origin only, by country | country breakdowns, competitors |
| PageSpeed Insights, Search Console | the same CrUX data with a lab run (PSI) or URL groups (Search Console) | quick look; Search Console groups similar URLs |

**Missing field data is unavailable, not passing.** Small sites often have none; that is what your own RUM is for ([monitoring.md](monitoring.md)). Because the window is 28 days, a fix shows fully about four weeks later.

## Lab tools

- **Lighthouse** (13.x since October 2025; audits became "insights"). Performance score weights: Total Blocking Time 30, LCP 25, CLS 25, FCP 10, Speed Index 10 ([scoring](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring)). It emulates a mid-range Android phone on slow 4G with a cold cache; it can't measure INP (TBT stands in) and sees only load-time CLS.
- **Chrome DevTools Performance panel**: live LCP, CLS and INP as you interact, with CrUX field values beside them and the LCP subparts and insights in the trace ([overview](https://developer.chrome.com/docs/devtools/performance/overview)).
- **WebPageTest** (Catchpoint), **sitespeed.io** (open source), **Unlighthouse** (Lighthouse across every page) for deeper or scheduled lab runs ([measurement.md](measurement.md)).
- A score is a lab summary, not a goal. Gate on the metrics and byte budgets, and judge by field data.

## Navigations that change the numbers

- **Back/forward cache** restores are near-instant and count as page views in CrUX; back/forward is about 1 in 10 navigations on desktop and 1 in 5 on mobile ([bfcache](https://web.dev/articles/bfcache)). Blockers: `unload` handlers (Chrome stops running them on all page loads from version 154), open connections; `Cache-Control: no-store` no longer blocks it in Chrome since 2025, with conditions ([no-store](https://developer.chrome.com/docs/web-platform/bfcache-ccns)).
- **Prerendered** navigations (Speculation Rules) are measured from activation and "will often result in a 0 second LCP" ([prerender](https://developer.chrome.com/docs/web-platform/prerender-pages)); Chromium only.
- **Soft navigations** (client-side route changes) are detected by default from Chrome 151 and reported by `web-vitals` 6 with `reportSoftNavs`; how CrUX will count them is undecided. A static multi-page site has none.
- Chrome 140–142 reported text LCP a few dozen ms too early; fixed in 143. Compare across browser versions with care.
