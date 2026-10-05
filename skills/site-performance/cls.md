# CLS: nothing moves unless the user moved it

Most layout shift on static sites comes from four sources, all fixable in the markup ([optimize CLS](https://web.dev/articles/optimize-cls), Strong unless marked). Remember CLS is measured only in Chromium; lab tools see only load-time shifts above the fold.

Contents: media · banners and late content · web fonts · animation · islands and lazy content

## Media

- `width` and `height` on every `<img>`, `<video>` and `<iframe>` (or `aspect-ratio` in CSS), with `height: auto` in the stylesheet so responsive images keep their ratio. 62 % of mobile pages still miss them on at least one image (Web Almanac). Astro's `<Image>` infers dimensions for local images; remote and Markdown images need them set. Scanner: `img-dimensions-missing`, `embed-dimensions-missing`.
- Embeds (YouTube, Maps, social posts) get a fixed-ratio container, or a click-to-load facade of the same size ([inp.md](inp.md#third-parties)).

## Banners and late content

- **Cookie notices and announcement bars**: "top-of-screen cookie notices are a very common source of layout shift"; render them as an overlay (sticky footer or modal) or server-render them into the HTML with their space reserved ([cookie notices](https://web.dev/articles/cookie-notice-best-practices)). A site that sets no tracking cookies may not need a consent banner at all ([monitoring.md](monitoring.md#privacy-in-the-eu)).
- Nothing inserted above existing content after load (newsletter bars, "new version" notices, consent prompts) unless space was reserved.

## Web fonts

- `font-display: optional` never swaps late, so it never shifts; `swap` shows text at once and shifts when the font arrives unless the fallback has the same metrics ([font best practices](https://web.dev/articles/font-best-practices)).
- **Metric-matched fallback**: an `@font-face` for a local font with `size-adjust`, `ascent-override`, `descent-override` and `line-gap-override` tuned to the web font, listed after it in `font-family`. Astro's Fonts API generates these automatically; Fontaine and Capsize do it elsewhere.

```css
@font-face { font-family: "Inter"; src: url(/fonts/inter-latin.woff2) format("woff2"); font-display: swap; }
@font-face { font-family: "Inter Fallback"; src: local("Arial"); size-adjust: 107%; ascent-override: 90%; }
body { font-family: "Inter", "Inter Fallback", system-ui, sans-serif; }
```

## Animation

Animate `transform` and `opacity` only. Pages that animate any layout-affecting property are 15 % less likely to have good CLS, and those animating `margin` or `border-width` have poor CLS at almost twice the rate ([top CWV](https://web.dev/articles/top-cwv), Strong sample, correlational).

## Islands and lazy content

- Astro `client:only` renders no server HTML, so the island's box appears only after its JavaScript runs ([directives](https://docs.astro.build/en/reference/directives-reference/)). Prefer server rendering with `client:visible` or `client:idle`, or reserve the space. Scanner: `astro-client-only`.
- `content-visibility: auto` without `contain-intrinsic-size` collapses offscreen sections to zero height and makes the scrollbar jump; pair it with `contain-intrinsic-size: auto <length>` ([content-visibility](https://web.dev/articles/content-visibility)).
- Back/forward cache restores have no layout shift at all; keep pages eligible ([delivery.md](delivery.md#backforward-cache)).
