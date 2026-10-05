# seo_scan.py

Stdlib Python 3.11+. Two modes:

```bash
python3 scripts/seo_scan.py site path/to/repo-or-dist [--base-url https://example.org] [--json] [--fail-on fail|warn|note|never]
python3 scripts/seo_scan.py live https://example.org [--mirror host …] [--sample 20] [--timeout 15] [--json] [--fail-on …]
```

`site` reads a repository with a wrangler config (its `assets.directory` is scanned and `html_handling` decides which URL serves each file) or a build directory. The production host comes from `--base-url`, else the first route in the wrangler config, else the most common canonical host. Pages replaced by a `_redirects` rule or a meta refresh are skipped; identical findings across pages are folded into one line with `+N more`. `live` fetches robots.txt, the sitemaps it names, a sample of their URLs, the home page as a browser and as each crawler with a `probe_user_agent` in [scripts/crawlers.json](scripts/crawlers.json), and every `--mirror`. Exit 1 when a finding at or above `--fail-on` (default `fail`) exists.

Contents: build and robots · sitemaps · one URL per page · page signals · structured data · language versions · links · edge files · live

## Build and robots

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `build-missing` | fail | the wrangler config's assets directory doesn't exist | build first, then scan |
| `site-url-unset` | fail | most canonicals name localhost, workers.dev, pages.dev or example.* | set the generator's production URL and rebuild |
| `robots-blocks-everything` | fail | robots.txt disallows `/` for every crawler | allow `/`; keep blocks for named crawlers only |
| `robots-blocks-search` | fail | robots.txt disallows a `search` crawler (Googlebot, Bingbot, Applebot) | remove that group |
| `robots-blocks-ai-search` | warn | robots.txt disallows an `ai-search` or `ai-user` crawler | block training tokens only, if that is the intent |
| `robots-sitemap-missing` | note | robots.txt has no `Sitemap:` line | add the absolute sitemap URL |
| `robots-missing` | note | no robots.txt in the build | ship one; the live file may be Cloudflare's |
| `foreign-host-url` | fail | a canonical, og:url, og:image, hreflang, sitemap or robots Sitemap URL points at localhost, workers.dev, pages.dev or example.*, or a sitemap URL sits on another host | production URLs only |

## Sitemaps

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `sitemap-missing` | warn | no sitemap in the build, or one named in robots.txt is absent | add the generator's sitemap plugin |
| `sitemap-invalid` | fail | the sitemap doesn't parse as XML | fix the generator output |
| `sitemap-url-missing` | fail | a listed URL matches no file | regenerate; remove stale entries |
| `sitemap-url-noindex` | fail | a listed URL is noindex | drop it from the sitemap, or remove the noindex |
| `sitemap-url-redirects` | warn | a listed URL is answered with a redirect under `html_handling` | list the 200 form |
| `sitemap-url-not-canonical` | warn | a listed URL differs from that page's canonical | list the canonical |
| `sitemap-omits-page` | note | an indexable page is not listed | include it, or noindex it |
| `sitemap-lastmod-uniform` | note | five or more entries share one `lastmod` | real content dates (git or frontmatter), or none |

## One URL per page

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `noindex-home` | fail | the home page is noindex (meta or `_headers`) | remove it |
| `headers-noindex-all` | fail | `_headers` sends `X-Robots-Tag: noindex` on `/*` without a host | scope the rule to the mirror host |
| `canonical-missing` | warn | an indexable page has no canonical | absolute self-canonical |
| `canonical-multiple` | fail | more than one canonical | exactly one |
| `canonical-target-missing` | fail | the canonical matches no file | point at the page that exists |
| `canonical-redirects` | warn | the canonical is answered with a redirect under `html_handling` | the 200 form |
| `canonical-relative` | note | the canonical is relative | absolute production URL |
| `cross-host-canonical` | warn | the canonical or og:url names another real host | only for deliberate syndication |
| `og-url-mismatch` | warn | og:url differs from the canonical | og:url = canonical |
| `spa-fallback` | warn | `not_found_handling: "single-page-application"` on a multi-page site | `"404-page"` |
| `not-found-page-missing` | warn | no `404.html` and no SPA fallback | ship one, `not_found_handling: "404-page"` |
| `meta-refresh-redirect` | note | a page redirects with a meta refresh and no `_redirects` rule covers it | a `_redirects` 301 |

## Page signals

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `title-missing` | fail | no `<title>` on an indexable page | unique, specific title |
| `title-duplicate` | warn | pages that aren't language versions of each other share a title | one per page |
| `description-missing` | warn | no meta description | one or two sentences on what the page offers |
| `description-thin` | note | description under 50 characters | say who it's for and what they get |
| `description-duplicate` | note | pages share a description | one per page |
| `lang-missing` | warn | `<html>` without `lang` | the page's language |
| `viewport-missing` | warn | no viewport meta | `width=device-width, initial-scale=1` |
| `og-incomplete` | warn | og:title, og:type, og:image or og:url missing | the full set ([page-signals.md](page-signals.md#link-previews)) |
| `og-image-relative` | fail | og:image is not an absolute URL | absolute `https://` |
| `og-image-missing` | fail | og:image is on the production host but matches no file in the build | ship the image or fix the path |
| `twitter-card-missing` | note | og:image set but no `twitter:card` | `summary_large_image` |
| `noarchive-set` | warn | robots meta has `noarchive` or `nocache` | remove unless the page must stay out of Copilot |
| `thin-shell` | warn | under 200 characters of text without JavaScript on a page with scripts | render the content into the HTML |
| `img-alt-missing` | warn | `<img>` without `alt` | describe it, or `alt=""` when decorative |
| `h1-missing` | note | no `<h1>` | the visible page name |
| `html-over-limit` | fail | HTML file over 2 MiB | move inlined sprites, base64 and data out |
| `ai-addressed-text` | fail | text addressed to AI systems or prompt-injection phrasing | delete it |
| `placeholder-text` | warn | lorem ipsum in a built page | real copy |
| `favicon-unsupported` | note | home page links no ICO or raster favicon and the build has no `favicon.ico` | `favicon.ico` or a PNG ≥ 48×48 |
| `site-name-missing` | note | no `WebSite` JSON-LD with a name on the home page | add it |

## Structured data

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `jsonld-invalid` | fail | a JSON-LD block doesn't parse | valid JSON (no trailing commas, no comments) |
| `jsonld-untyped` | warn | a top-level node has no `@type` | type it or remove it |
| `jsonld-retired-type` | note | a type in [scripts/rich-results.json](scripts/rich-results.json) | drop the markup; keep visible content if useful |

## Language versions

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `hreflang-invalid` | fail | a code is not language(-script)(-region) or `x-default` | `nl`, `en-GB`, `x-default` |
| `hreflang-no-self` | warn | the set doesn't list the page itself | every version lists every version |
| `hreflang-not-reciprocal` | warn | a listed version doesn't link back | make the sets identical |
| `hreflang-no-x-default` | note | no `x-default` | the version for everyone else |

## Links

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `internal-link-broken` | fail | an internal `<a href>` matches no file | fix the link or restore the page |
| `anchor-missing` | warn | a `#fragment` has no matching `id` | fix the id or the link |
| `internal-link-redirects` | note | an internal link hits a redirect under `html_handling` | link the 200 form |
| `internal-nofollow` | warn | `rel=nofollow` on an internal link | remove it |
| `orphan-page` | warn | an indexable page no other page links to | link it from a related page |
| `link-text-generic` | note | anchor text like "click here", "read more", "lees meer" | name the destination |

## Edge files

| Rule | Severity | Fires when | Fix |
| --- | --- | --- | --- |
| `redirect-temporary` | warn | a `_redirects` rule is 302, 303 or 307 (302 is the default) | 301 or 308 for moves |
| `root-redirect-temporary` | note | `/` redirects temporarily | 301 if the target is the permanent home; keep for a language chooser |
| `redirect-chain` | warn | a `_redirects` target is itself redirected | point at the final URL |

## Live

| Rule | Severity | Fires when |
| --- | --- | --- |
| `live-unreachable` | fail | the home page doesn't answer |
| `live-noindex` | fail | the live home page is noindex (header or meta) |
| `live-robots-error` | fail | robots.txt answers 5xx: Google stops crawling |
| `live-robots-managed` | note | Cloudflare-managed content is prepended to robots.txt |
| `live-content-signals` | note | robots.txt carries Content-Signal lines (listed) |
| `live-crawler-blocked` | fail / warn / note | a crawler's user agent gets 401/403/429/503 where a browser doesn't: fail for `search`, warn for `ai-search` and `ai-user`, and for `ai-training` warn on Cloudflare when robots.txt shows no managed training preference (possible Training = Block, which also stops Googlebot), else note |
| `live-sitemap-unreachable` | warn | a sitemap named in robots.txt doesn't answer or parse |
| `live-sitemap-url-error` | fail | a sampled sitemap URL answers 4xx/5xx |
| `live-sitemap-url-redirects` | warn | a sampled sitemap URL redirects |
| `live-sitemap-url-noindex` | fail | a sampled sitemap URL is noindex |
| `live-og-image-broken` | fail | the home page's og:image doesn't answer 200 |
| `live-og-image-heavy` | note | the home page's og:image is over 600 KB (WhatsApp's limit) |
| `live-mirror-indexable` | warn | a `--mirror` serves 200 without noindex or a canonical to production |
| `live-mirror-canonical-only` | note | a `--mirror` serves 200 without noindex, relying on a canonical to production |

Robots findings from the live file use the same rules as `site` (`robots-blocks-search`, `robots-blocks-ai-search`, …). A spoofed user agent can be refused as a fake bot; confirm a `live-crawler-blocked` finding in Cloudflare Security Events before acting.
