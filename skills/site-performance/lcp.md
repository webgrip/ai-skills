# LCP: get the largest thing painted sooner

Ranked by measured impact for static sites. Find the LCP element and its subparts first (DevTools Performance panel, or RUM attribution), then fix the largest subpart ([metrics.md](metrics.md#diagnosing-each)). Strength labels as in [evidence.md](evidence.md).

Contents: the LCP image · text LCP and fonts · render-blocking resources · TTFB · Astro · Hugo and Eleventy

## LCP image

In order of impact:

1. **Put the hero in the HTML as an `<img>`** (or `<picture>`), not a CSS `background-image`, a JS carousel or `data-src` for a lazy-load library. 35 % of LCP images weren't discoverable in the initial HTML in CrUX's sample; a CSS background needs a preload to be found early ([fetch priority](https://web.dev/articles/fetch-priority), Strong). Scanner: `lcp-image-js-loaded`.
2. **Never lazy-load it.** `loading="lazy"` makes the browser wait for layout before fetching; HTTP Archive median p75 LCP 3.5 s with lazy-loaded LCP images against 2.9 s without ([LCP lazy loading](https://web.dev/articles/lcp-lazy-loading), Strong). Lazy-load only below-the-fold images. Scanner: `lcp-image-lazy`.
3. **`fetchpriority="high"` on that one image** (Chrome 102+, Firefox 132+, Safari 17.2+). "If everything is prioritized then nothing is": one per page. Google Flights went from 2.6 s to 1.9 s (Anecdotal, Google's product). Scanner: `lcp-image-not-prioritized`.
4. **Avoid redirect hops** before the page or the image: each Cloudflare trailing-slash 307 is a full round trip in TTFB ([delivery.md](delivery.md#trailing-slashes-and-redirects)).
5. **Responsive images**: `srcset` with width descriptors **and** `sizes` that match the layout; without `sizes` the browser assumes 100vw, and at the median `sizes` is 43 % too large on desktop (Web Almanac, Strong). Scanner: `srcset-without-sizes`.
6. **Bytes**: AVIF or WebP at the displayed size. The field median is AVIF 1.4 and WebP 1.3 bits per pixel, so "always AVIF" is Contested: compare bytes per image, and ship AVIF with a WebP fallback in `<picture>`. A hero of 100–150 KB on mobile is a reasonable budget. Scanner: `lcp-image-heavy`, `lcp-image-legacy-format`. This comes after 1–5 because on slow origins the download is under 10 % of LCP.
7. **Preload** only what the HTML can't reveal (a CSS background hero, a font for a text LCP): `<link rel="preload" as="image" fetchpriority="high">`.

## Text LCP and fonts

When the LCP element is a heading or paragraph, LCP = TTFB + render delay; the render delay is usually a web font or render-blocking CSS.

- Self-host fonts (no Google Fonts: an extra origin on the critical path, and an EU privacy problem after the Munich ruling, LG München I 3 O 17493/20; Cloudflare Fonts falls back to Google Fonts when it can't rewrite a page). Scanner: `font-third-party`.
- WOFF2 only, subset to the scripts you use, one or two files preloaded with `crossorigin` (without it the font downloads twice). Scanner: `font-not-woff2`, `font-preload-no-crossorigin`, `font-preload-many`.
- `font-display: swap` with a metric-matched fallback, or `optional` (never swaps late, so no shift) ([font best practices](https://web.dev/articles/font-best-practices)). Scanner: `font-display-missing`. Fallback metrics: [cls.md](cls.md#web-fonts).

## Render-blocking resources

- Scripts in `<head>` get `defer` or `type="module"`; a tiny inline theme script that prevents a flash of the wrong colour scheme is the accepted exception. Scanner: `render-blocking-script`.
- **Critical CSS inlining is usually unnecessary**: "most sites should be able to achieve all of our recommended performance targets without implementing this technique", and inlining defeats caching ([critical CSS](https://web.dev/articles/extract-critical-css), Strong). The "14 KB first round trip" rule is Contested. Keep CSS per page and small instead. Scanner: `css-over-budget`, `css-import`.
- Astro inlines stylesheets under 4 KB by default (`build.inlineStylesheets: 'auto'`); per-page scoped CSS rarely needs more.

## TTFB

Static assets on Cloudflare normally answer from the edge in well under 0.8 s. When `perf_scan.py live` or RUM shows slow TTFB, look for: a redirect before the HTML (apex↔www, trailing slash, `/` → `/nl`), a Worker that runs in front of HTML (`run_worker_first: true`), a cold or distant origin behind a proxied record, or an Access login in the path. → [delivery.md](delivery.md)

## Astro

- `<Image>` and `<Picture>` default to `loading="lazy" decoding="async"`: the hero needs **`priority`** (Astro 5.10+), which sets `loading="eager"`, `decoding="sync"` and `fetchpriority="high"` ([astro:assets](https://docs.astro.build/en/reference/modules/astro-assets/)).
- Output is WebP unless you use `<Picture formats={['avif', 'webp']}>`; no `layout` means no `srcset` (`constrained`, `full-width` or `fixed` generate `srcset` and `sizes`).
- The Fonts API (stable since Astro 6) self-hosts fonts and generates metric-matched fallbacks; use `<Font preload />` for the one face the LCP text needs ([fonts](https://docs.astro.build/en/guides/fonts/)).
- Prefetch is off by default; `prefetch: true` with Speculation Rules is the Chromium path ([delivery.md](delivery.md#speculation-rules)).

## Hugo and Eleventy

- Hugo: image processing (`.Resize`, `.Process "webp"`) to generate sizes and formats, and render hooks to emit `width`, `height`, `srcset`, `sizes` and `fetchpriority` on the first content image.
- Eleventy: `@11ty/eleventy-img` generates formats and `<picture>` markup; pass `loading: "eager"` and `fetchpriority: "high"` for the hero, lazy for the rest.
