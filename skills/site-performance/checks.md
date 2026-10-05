# perf_scan.py

Stdlib Python 3.11+. Two modes:

```bash
python3 scripts/perf_scan.py site path/to/repo-or-dist [--js-budget-kb 100] [--css-budget-kb 50] [--hero-budget-kb 200] [--json] [--fail-on fail|warn|note|never]
python3 scripts/perf_scan.py live https://example.org [--field] [--form-factor phone|desktop] [--timeout 15] [--json] [--fail-on …]
```

`site` reads a repository with a wrangler config (its `assets.directory` is scanned) or a build directory. Byte budgets are gzip-measured, which is close to what the network carries. The "first large image" is the first `<img>` with `fetchpriority="high"`, else the first one declared at least 300 px wide or weighing 20 KB: a heuristic, since without a viewport the scanner can't know what is above the fold. Identical findings across pages fold into one line with `+N more`. `live` measures time to first byte as the median of three requests from wherever it runs (one vantage point, not a percentile), checks compression, HTTP/3 and cache headers, and with `--field` reads the 75th-percentile CrUX data for the URL and its origin from the CrUX API (set `CRUX_API_KEY`, a free key from the Google Cloud console with the Chrome UX Report API enabled; 150 queries a minute). Missing field data is reported as missing, never as passing. Exit 1 when a finding at or above `--fail-on` (default `fail`) exists.

## Site rules

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `build-missing` | fail | the wrangler config's assets directory doesn't exist | build first |
| `lcp-image-lazy` | warn (fail with `fetchpriority=high`) | the first large image is `loading="lazy"` | lazy-load only below the fold ([lcp.md](lcp.md#lcp-image)) |
| `lcp-image-not-prioritized` | note | the first large image has no `fetchpriority="high"` or image preload | add it to the one hero image |
| `lcp-image-heavy` | note | the first large image is over the hero budget (200 KB) | AVIF/WebP, `srcset`, the displayed size; fix discovery and priority first |
| `lcp-image-js-loaded` | warn | the first image has only `data-src`/`data-srcset` (a script loads it) | a real `src` with native `loading` |
| `lcp-image-legacy-format` | note | the first large image is JPEG/PNG over 50 KB with no AVIF/WebP alternative | `<picture>` with AVIF, or Astro `<Image>` |
| `image-heavy` | note | any other local image over 300 KB | resize, modern format, `srcset` |
| `srcset-without-sizes` | warn | a width-based `srcset` with no `sizes` | `sizes` matching the layout, or the browser assumes 100vw |
| `img-dimensions-missing` | warn | `<img>` without `width` and `height` (or `aspect-ratio`) | set the intrinsic size ([cls.md](cls.md)) |
| `embed-dimensions-missing` | warn | `<iframe>` or `<video>` without dimensions | `width`/`height` or `aspect-ratio` |
| `embed-not-lazy` | warn | a YouTube, Vimeo, Maps or social embed loads eagerly | `loading="lazy"` or a click-to-load facade |
| `render-blocking-script` | warn | `<script src>` in `<head>` without `defer`, `async` or `type="module"`, larger than 1.5 KB gzip | `defer` or `type="module"`; tiny theme scripts are exempt |
| `js-over-budget` | warn | the page's own JavaScript exceeds the budget (100 KB gzip) | fewer islands, later hydration, drop libraries ([inp.md](inp.md)) |
| `css-over-budget` | note | render-blocking CSS exceeds the budget (50 KB gzip) | split per page, drop unused rules |
| `css-import` | note | `@import` in CSS | bundle it or link it directly |
| `astro-client-only` | warn | an Astro island with `client:only` (no server HTML) | `client:visible` or `client:idle` with server rendering |
| `dom-size-large` | note | more than 1,500 elements on a page | paginate, virtualise, `content-visibility` |
| `heavy-third-party` | warn | Google Tag Manager, Analytics, Meta Pixel, Hotjar, Intercom, HubSpot, OneTrust, Cookiebot, YouTube API, Maps and similar | load on interaction, behind consent, or not at all |
| `font-third-party` | warn | fonts from Google Fonts, Typekit or Bunny | self-host (an extra origin, and an EU privacy problem) |
| `font-display-missing` | warn | a downloading `@font-face` without `font-display` | `swap` (or `optional`) with a metric-matched fallback |
| `font-not-woff2` | note | an `@font-face` with TTF, OTF or WOFF and no WOFF2 | WOFF2 only |
| `font-preload-no-crossorigin` | warn | a font preload without `crossorigin` | add it, or the font downloads twice |
| `font-preload-many` | note | more than two font preloads | preload one or two files |
| `unload-handler` | warn | an `unload` listener in inline or local JavaScript (Chrome stops running it from version 154; elsewhere it blocks the back/forward cache) | `pagehide` or `visibilitychange` |
| `html-no-store` | note | `_headers` sends `Cache-Control: no-store` on HTML paths (no caching; back/forward cache only in Chrome, under conditions) | `no-cache` or a short `max-age` |
| `assets-not-immutable` | note | a directory of content-hashed files has no year-long immutable caching in `_headers` | `/<dir>/*` → `Cache-Control: public, max-age=31536000, immutable` |

## Live rules

| Rule | Severity | Fires when |
| --- | --- | --- |
| `live-unreachable` | fail | the URL doesn't answer |
| `ttfb-slow` | warn | median time to first byte over three requests exceeds 800 ms |
| `html-uncompressed` | warn | HTML without Brotli, Zstandard or Gzip |
| `asset-uncompressed` | warn | a same-origin CSS or JS file without compression |
| `html-no-store` | note | HTML served with `Cache-Control: no-store` |
| `assets-not-immutable` | note | a hashed asset served without a year-long `max-age` |
| `http3-missing` | note | no `alt-svc: h3` |
| `field-metric-poor` | fail (TTFB: warn) | a p75 field metric (LCP, INP, CLS, TTFB) for the page or origin is poor |
| `field-metric-needs-improvement` | warn (TTFB: note) | a p75 field metric needs improvement |
| `field-data-missing` | note | CrUX has no data for the URL or the origin (too little Chrome traffic in 28 days) |
| `field-unavailable` | note | no `CRUX_API_KEY`, or the CrUX API failed |

Field data is 28 days of real Chrome users at the 75th percentile, so a fix shows in it weeks later; lab and live checks show it at once ([measurement.md](measurement.md)).
