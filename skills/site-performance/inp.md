# INP: respond to every tap within 200 ms

On a static site INP is decided by how much JavaScript runs and when. Find the slow interaction and its phases first (RUM attribution with Long Animation Frames, or the DevTools Performance panel while you click through the page) before deciding whether first-party or third-party code is at fault; vendor claims that third parties are "the main cause" have no published method (Anecdotal). Strength labels as in [evidence.md](evidence.md).

Contents: ship less JavaScript · third parties · long tasks · rendering cost

## Ship less JavaScript

- **Astro islands**: a component with no `client:` directive ships no JavaScript. `client:load` hydrates immediately at high priority; `client:idle` waits for an idle period; `client:visible` waits until it scrolls into view ([directives](https://docs.astro.build/en/reference/directives-reference/), Strong). Default to no directive, then `client:visible`, then `client:idle`; `client:load` only for what must work in the first second.
- A per-page budget of about **100 KB of JavaScript (gzip)** fits a marketing or community site; the field median is far above it (632 KB per page). Scanner: `js-over-budget`; in CI, size-limit with `@size-limit/file` over `dist/_astro/*.js` ([measurement.md](measurement.md#budgets-in-ci)).
- Prefer platform features to libraries: `<details>`, `<dialog>`, the Popover API, CSS scroll snap and `:has()` replace whole widget libraries.

## Third parties

Measured main-thread cost per page (HTTP Archive lab data, March 2026, [third-party-web](https://github.com/patrickhulce/third-party-web), Consistent for the ranking, numbers indicative):

| Script | Main thread per page |
| --- | --- |
| YouTube embed | 6,297 ms |
| Vimeo | 4,099 ms |
| Intercom | 1,433 ms |
| HubSpot | 1,226 ms |
| Google Tag Manager | 1,066 ms |
| Consent managers (Osano, Usercentrics, OneTrust, Cookiebot) | 398–1,706 ms |
| Google Maps | 914 ms |
| Hotjar | 732 ms |
| Google Analytics | 108 ms |
| Cloudflare's injected scripts | 67 ms |

- **Facades** for video, maps and chat: a static image or button of the same size that loads the real embed on click (lite-youtube-embed and similar; the author's "224× faster" is Anecdotal, the mechanism is not).
- **Fewer tags, not later tags.** Loading Tag Manager on first scroll or click moves its cost onto the first interaction, which is exactly what INP measures, and hides it from Lighthouse. Remove what nobody reads.
- A cookieless analytics setup often removes the need for a consent manager, which is itself one of the heaviest scripts. Scanner: `heavy-third-party`.
- Partytown moves scripts to a web worker but throttles their DOM access and breaks `preventDefault`; a fit for a few analytics tags, not for UI widgets.

## Long tasks

- Any task over 50 ms is a long task. Split work and yield: `scheduler.yield()` (Chrome and Edge 129+, Firefox 142+, not Safari) continues before other queued tasks; fall back to `await new Promise((resolve) => setTimeout(resolve, 0))` ([long tasks](https://web.dev/articles/optimize-long-tasks), Strong).
- In event handlers, do the visible update first and defer the rest (analytics calls, storage, non-visible state) until after the next paint.
- Don't run heavy work inside `requestAnimationFrame`: it delays the very frame it was meant to speed up.

## Rendering cost

- Lighthouse warns above about 800 body nodes and errors above about 1,400; every style and layout pass, and so every interaction, scales with it ([DOM size](https://developer.chrome.com/docs/lighthouse/performance/dom-size)). Paginate long lists or use `content-visibility: auto` with `contain-intrinsic-size`. Scanner: `dom-size-large`.
- Animate `transform` and `opacity`, which skip layout ([cls.md](cls.md#animation)).
- Search widgets (Pagefind and similar) load their index on focus or first keystroke, not on page load.
