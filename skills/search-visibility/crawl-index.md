# Crawl and index: one reachable, canonical URL per page

The first two links of the chain. A page that is blocked, duplicated, redirected through or soft-404ed never reaches ranking or citation, however good it is. Google's documentation is the authority here (Strong throughout unless marked).

Contents: robots.txt and noindex · status codes · redirects · one URL per page · sitemaps · page weight and rendering · submitting

## robots.txt and noindex

| Goal | Use | Never |
| --- | --- | --- |
| Keep a page out of results | `<meta name="robots" content="noindex">` or `X-Robots-Tag: noindex`, and leave it crawlable | `Disallow` in robots.txt: it blocks crawling, so Google never sees the noindex and can still index the URL from links ([block indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing)) |
| Keep a whole mirror host out | Don't create it; else Access in front, or host-scoped `X-Robots-Tag: noindex` ([cloudflare.md](cloudflare.md#mirror-hostnames)) | robots.txt Disallow on the mirror |
| Save crawl on a small site | Nothing; crawl budget matters only for very large sites | Disallow rules for CSS, JS or images: Google renders with them |
| Limit snippets or AI Overviews use | `nosnippet`, `max-snippet`, `data-nosnippet` | `Google-Extended` (it does not touch Search or AI Overviews) |

- **Groups:** a crawler obeys only the most specific group that names it; rules under `User-agent: *` never reach a bot with its own group. Repeat shared rules in each group.
- **A 5xx on robots.txt** makes Google treat the site as disallowed and stop crawling (for up to 12 hours per incident); a 404 means "allow everything" ([robots.txt spec](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt)). A proxied hostname with no claimant answers 522: fix the route first (the `edge-hosting` skill owns that).
- **Changes take time:** Google caches robots.txt up to 24 h; OpenAI about 24 h; DuckDuckGo 72 h.
- **The live file is the truth.** Cloudflare can prepend managed rules to the repository's robots.txt ([cloudflare.md](cloudflare.md#robotstxt-cloudflare-writes)). Fetch it after every deploy.
- **`noarchive`**: Google ignores it, but Bing uses it to keep the page out of Copilot answers, and `nocache` limits Copilot to URL, title and snippet. Don't add either by habit.

## Status codes

- **Unknown URLs answer 404 or 410** with a page that helps people back. Google drops 4xx (except 429) from the index and treats 404 and 410 the same; 410 is not faster ([HTTP errors](https://developers.google.com/search/docs/crawling-indexing/http-network-errors)).
- **A 200 "not found" page is a soft 404**: wasted crawl, and the URL can be indexed as a thin duplicate. On Workers static assets that is `not_found_handling: "single-page-application"`; on Pages it is a missing `404.html` ([cloudflare.md](cloudflare.md#404-handling)).
- **5xx and 429** slow crawling down; persistent ones drop URLs.

## Redirects

| Code | Google's reading | Use for |
| --- | --- | --- |
| 301, 308, meta refresh 0 s | strong signal that the target is canonical | moved pages, host and protocol consolidation |
| 302, 303, 307, meta refresh > 0 s | followed, but "the indexing pipeline doesn't use the redirect as a signal that the redirect target should be canonical" | genuinely temporary moves, language choosers |

Source: [redirects](https://developers.google.com/search/docs/crawling-indexing/301-redirects). Keep permanent redirects at least a year; one hop, never a chain; at the edge in `_redirects` (which answers before any asset), with the code written out, because `_redirects` defaults to 302. Cloudflare's trailing-slash normalisation answers 307 and cannot be changed, so canonicals, links and sitemaps must never depend on it.

## One URL per page

Every page has exactly one URL that answers 200, and everything points at it.

1. **Production URL set in the generator**: Astro `site`, Hugo `baseURL`, Eleventy/Vite env. A build without it writes `localhost` into every canonical, hreflang, og:url and sitemap entry (`site-url-unset`).
2. **One host**: apex or `www`, one protocol; the other host 301s (the `edge-hosting` skill has the redirect rule).
3. **One trailing-slash form**, matching `assets.html_handling`. Under the default `auto-trailing-slash`, `about.html` serves `/about` and `about/index.html` serves `/about/`; every other form gets a 307.
4. **`<link rel="canonical">`** on every indexable page: absolute, production host, the exact 200 form, self-referencing on the page itself. It is a strong hint, not a directive; conflicting signals (two canonicals, canonical ≠ sitemap ≠ internal links) make Google choose for you. Clusters can take up to two weeks to settle.
5. **Internal links, hreflang, og:url and the sitemap use the same form.** Linking `/about/` when `/about` is served costs a 307 per click and splits signals.
6. **Mirrors** (`*.workers.dev`, `*.pages.dev`, Version and Preview URLs, staging) never serve indexable copies ([cloudflare.md](cloudflare.md#mirror-hostnames)).

## Sitemaps

- `loc` and an accurate `lastmod` only; Google and Bing ignore `priority` and `changefreq`, and Google ignores `lastmod` it finds inaccurate ([build a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)). Take `lastmod` from the content (frontmatter date or the file's last git commit), never the build time.
- List only canonical, indexable, 200 URLs on the production host. A noindex page in the sitemap is a contradiction; a redirecting URL wastes crawl.
- Name it in robots.txt with an absolute `Sitemap:` line and submit it in Search Console and Bing Webmaster Tools. Google's sitemap ping endpoint is gone.
- Most generators have a plugin (`@astrojs/sitemap`, Hugo built-in, `@quasibit/eleventy-plugin-sitemap`); check its output, not its config.

## Page weight and rendering

- **Googlebot reads the first 2 MB of uncompressed HTML** and drops the rest; other crawlers default to 15 MB ([Googlebot](https://developers.google.com/search/docs/crawling-indexing/googlebot)). Inlined SVG sprites, base64 images and serialised data blobs push pages over; keep the main content and JSON-LD early.
- **Content in the initial HTML.** Googlebot renders JavaScript in a second wave; most AI crawlers never do. Islands are fine; a page whose text arrives only from a script is empty to them (`thin-shell`).
- A noindex in the initial HTML can make Google skip rendering; JavaScript that removes it later is not seen.

## Submitting

- **Search Console**: a Domain property verified by DNS TXT (managed in the DNS-as-code repository, survives rebuilds; deleting an HTML verification file loses ownership). Submit the sitemap; use URL Inspection on key pages after launch.
- **Bing Webmaster Tools**: import from Search Console or verify by DNS; it feeds Bing, Copilot, DuckDuckGo and others ([ai-answers.md](ai-answers.md)).
- **IndexNow** for Bing, Yandex, Seznam, Naver, Yep and Amazon; Google does not take part. Host the key file in `public/`, and ping changed URLs from the production deploy job only, never from previews.
