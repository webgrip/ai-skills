# Case: twente.dev through the procedure

twente.dev is a bilingual (Dutch and English) community site: Astro static output on an assets-only Worker, `html_handling = "auto-trailing-slash"`, `not_found_handling = "404-page"`, a `_redirects` rule sending `/` to `/nl`, and a staging environment on `staging.twente.dev`. This is what the procedure found on 2026-10-04, using a fresh build of the main branch and the live site. It shows the kind of failure the scanner exists for: a site that looks finished and is mostly right, with a few defects nobody sees from a browser.

## What the scans found

`seo_scan.py site` on the build, `seo_scan.py live https://twente.dev --mirror staging.twente.dev` on the edge:

| Finding | Rule | Consequence | Fix |
| --- | --- | --- | --- |
| Every page's `og:image` is `/brand/social/banner-meetup-1200x675@2x.png`, which is not in the build; live it answers 404 | `og-image-missing`, `live-og-image-broken` | every share on LinkedIn, WhatsApp, Slack and Discord shows no image, on all 30 pages | ship the file or point `og:image` at an existing 1200×630 card under 600 KB |
| The press pages link three brand downloads that don't exist | `internal-link-broken` | journalists get a 404 | add the files or remove the links |
| GPTBot and ClaudeBot get 403 at the edge; robots.txt has no Cloudflare-managed training preference | `live-crawler-blocked` (warn) | fine if the zone uses **Disallow AI Training**; if it is **Block** or the legacy "Block AI bots", Googlebot, Bingbot and Applebot have been refused since 2026-09-15 too | open the zone's AI bot policies; set Training to Disallow AI Training and record it in infrastructure as code |
| `staging.twente.dev` serves the site with 200, no noindex, canonical to production | `live-mirror-canonical-only` | a hint keeps it out of results most of the time, not always | put Access in front of staging, or send `X-Robots-Tag: noindex` there |
| `/` → `/nl` is a 302, and `x-default` points at `/nl` | `root-redirect-temporary` | Google may keep showing `twente.dev/` for the Dutch home | 301 if `/nl` is the permanent home; keep the 302 only as a deliberate language chooser, with `x-default` on `/` |

## What it gets right

- One host, one trailing-slash form; canonicals, internal links and sitemap entries all use the 200 form, so no 307 is ever followed.
- Reciprocal hreflang (`nl-NL`, `en-GB`, `x-default`) on every page, translated slugs (`/nl/over`, `/en/about`), `lang` set.
- `WebSite` and `Organization` JSON-LD, `favicon.ico` beside the SVG, a sitemap named in robots.txt, a real 404 page.
- Complete Open Graph and Twitter tags in the server HTML; the only problem is the file the image tag names.
- An `llms.txt` generated from the same facts as the pages: harmless, though no engine is known to use it.

## What to take from it

1. **Scan the build and the edge, both.** The missing image showed in the build; whether crawlers get in only showed live.
2. **A complete tag set is not a working preview.** Check that the files the tags name exist.
3. **Cloudflare settings change meaning.** A training block that was safe in August became a search block on 2026-09-15. Settings belong in infrastructure as code, and the live probe belongs in the deploy job.
4. **Staging is public until proven otherwise.** Every non-production hostname gets Access or noindex.
