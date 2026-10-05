# Delivery: what Cloudflare's edge adds or takes away

Static assets on Workers answer from the edge without a configured cache, so delivery is mostly right by default. The losses come from redirects, caching headers, and zone features that rewrite responses. Deployment itself is the `edge-hosting` skill. Cloudflare's own documentation is the source (Strong) unless marked; check the live headers, because zone settings and docs drift.

Contents: caching · compression and protocol · trailing slashes and redirects · Early Hints · speculation rules · back/forward cache · zone features · Server-Timing

## Caching

| Response | Default on Workers static assets | Set in `_headers` |
| --- | --- | --- |
| HTML | `public, max-age=0, must-revalidate` (revalidates with the ETag) | leave it, or a short `max-age`; never `no-store` |
| Content-hashed files (`/_astro/*`, Vite `assets/*`, Hugo fingerprints) | the same revalidation on every repeat visit | `Cache-Control: public, max-age=31536000, immutable` |
| Stable names (`/brand/logo.png`, `favicon.ico`) | revalidate | a day or a week, not `immutable` |

The default makes every repeat visit re-check every hashed file; no published skill mentioned it. Scanner: `assets-not-immutable`. `no-store` on HTML removes browser and edge caching and costs the back/forward cache outside Chrome (`html-no-store`).

Astro's prefetch falls back to `fetch()` in Safari and Firefox, which only helps when the prefetched page is cacheable.

## Compression and protocol

- Cloudflare compresses to visitors with Gzip, Brotli or Zstandard (Brotli and Zstandard above 50 bytes). Its compression page says both that Zstandard is enabled through Compression Rules and that Free-plan content is compressed with Zstandard by default (Contested within the doc); twente.dev answered `content-encoding: zstd` on 2026-10-04. Check live: `perf_scan.py live` (`html-uncompressed`, `asset-uncompressed`).
- `Cache-Control: no-transform` stops recompression (and Web Analytics injection).
- HTTP/3 is available on all plans (zone → Network); `perf_scan.py live` notes `http3-missing`.

## Trailing slashes and redirects

Every redirect before the HTML adds a round trip to TTFB, and so to LCP. Cloudflare answers non-canonical trailing-slash forms with a 307 under `assets.html_handling`; internal links, canonicals and the sitemap should use the form that answers 200 (the `search-visibility` scanner reports `internal-link-redirects`). Apex↔www and `/` → `/nl` redirects cost the same on entry pages.

## Early Hints

- **Workers static assets**: 103 Early Hints need the zone's Early Hints toggle **and** `Link` headers in `_headers`, for example `/*  Link: </_astro/base.Cz39HSr8.css>; rel=preload; as=style` ([Early Hints](https://developers.cloudflare.com/cache/advanced-configuration/early-hints/)).
- Cloudflare doesn't send a 103 once the final response is already available, so for static assets served from the edge the gain is small.
- **Pages** generates Early Hints from `<link rel=preload>` tags, but not for preloads carrying `crossorigin` or `fetchpriority`, which excludes font preloads and prioritised images.
- Published gains are vendor numbers (Anecdotal); do this last.

## Speculation rules

Prefetching or prerendering the next page makes it near-instant; prerendered navigations often report a 0 s LCP ([prerender](https://developer.chrome.com/docs/web-platform/prerender-pages)). Chromium only; Safari has prefetch behind a flag.

```html
<script type="speculationrules">
{ "prefetch": [{ "where": { "href_matches": "/*" }, "eagerness": "moderate" }] }
</script>
```

- `moderate` prefetches on hover or pointer-down; prerender only pages without side effects on load (no analytics double-counting, no state changes).
- **Cloudflare Speed Brain** (Free, on by default) adds conservative prefetch rules, but skips routes that invoke a Worker, content not in Cloudflare's cache, and pages.dev, so on an assets-only Worker it probably does nothing (inference from the docs). Ship your own rules ([Speed Brain](https://developers.cloudflare.com/speed/optimization/content/speed-brain/)).
- Astro: `prefetch: true` with `experimental.clientPrerender` uses Speculation Rules ([prefetch](https://docs.astro.build/en/guides/prefetch/)).

## Back/forward cache

One in ten desktop and one in five mobile navigations are back or forward; a restore from the back/forward cache is instant and counts in CrUX ([bfcache](https://web.dev/articles/bfcache)).

- No `unload` handlers: Chrome stops running them on all page loads from version 154, and where they still run they block the cache. Use `pagehide` or `visibilitychange`. Scanner: `unload-handler`.
- `Cache-Control: no-store` no longer blocks it in Chrome since 2025 (a cookie change evicts the page; 3-minute limit) ([no-store](https://developer.chrome.com/docs/web-platform/bfcache-ccns)); other browsers may still exclude such pages. In CrUX, removing `no-store` across one CMS moved 1.8 % of its origins to passing CLS.
- Close open connections (WebSocket, BroadcastChannel) on `pagehide`. Chrome DevTools → Application → Back/forward cache tests a page.

## Zone features

| Feature | Verdict for a static site |
| --- | --- |
| Rocket Loader | off: defers all JavaScript, Cloudflare claims only paint-metric gains, needs CSP changes, breaks some scripts |
| Polish | Pro plan and up; generate formats at build instead |
| Cloudflare Images transformations | free plan: 5,000 unique transformations a month, then error 9422; build-time images are simpler |
| Cloudflare Fonts | falls back to Google Fonts when it can't rewrite a page; self-host at build time instead |
| Web Analytics automatic injection | 10 KB beacon, about 67 ms main thread; fine, but on Free the automatic setup skips EU visitors ([monitoring.md](monitoring.md#cloudflare-web-analytics)) |
| Zaraz | moves third-party tags to the edge; still a third party in the page's budget |
| Speed Brain, Early Hints, HTTP/3 | above |

## Server-Timing

`Server-Timing: kv;dur=12, d1;dur=31` on responses a Worker builds lets RUM join server time to the user's experience (readable from `performance.getEntriesByType("navigation")[0].serverTiming`). An assets-only Worker runs no code for static responses, so there is nothing to time there; inside a Worker, clocks advance only across I/O, so `dur` measures awaited calls, not CPU. Never expose internal details you wouldn't publish.
