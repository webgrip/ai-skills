---
name: search-visibility
description: Gets static sites on Cloudflare's edge found in Google and Bing and cited by ChatGPT, Claude, Perplexity and AI Overviews - crawler access and Cloudflare AI bot settings, one canonical URL per page under wrangler html_handling, robots.txt and sitemaps, titles, snippets, structured data and link previews, answer-first content, an evidence-graded verdict on GEO and llms.txt, and a build plus live-site scanner. Use when a site does not show up in Google or in AI answers; to improve the SEO or search visibility of a static, Astro, Hugo or Eleventy site; when checking robots.txt, a sitemap, canonical, hreflang, noindex, redirects or 404s; to make a site findable or citable by ChatGPT, Perplexity, Claude or AI Overviews (GEO, AEO, llms.txt); when deciding whether to block AI crawlers or training bots; when link previews, og:image or social cards are broken; or before launching a site. Not for paid search ads, page speed (site-performance), page design (expressive-design) or deployment (edge-hosting).
---

# Search visibility — found by engines, cited by assistants

Visibility is a chain: **crawlable → indexed → retrieved → shown or cited → clicked**. Most of the leverage is in the first two links, which are classic SEO; Google's own guide says optimising for its AI features "is still SEO". Static HTML on Cloudflare starts ahead (fast, no JavaScript needed) and loses it through a handful of edge and build traps. → [evidence.md](evidence.md)

Evidence labels used throughout: **Strong** (the platform's own docs, a controlled study, a large published sample, sworn testimony) · **Consistent** (independent sources agree) · **Contested** · **Anecdotal** (one site, one practitioner, vendor data with an unpublished method).

## Procedure

1. **Frame it.** Which site and hostnames, which audiences and languages, which questions people bring, which engines matter. Ask the owner's **AI training stance** (allow, or opt out while staying in search and answers) and record it; never change it silently.
2. **Access.** Run `python3 scripts/seo_scan.py live https://example.org --mirror staging.example.org --mirror example-org.example-account.workers.dev`. The live robots.txt is the truth: Cloudflare may prepend its own. In the zone's AI bot policies, Search and Agent stay Allow and Training is Allow or **Disallow AI Training**, never Block. → [cloudflare.md](cloudflare.md#ai-bot-policies), [ai-answers.md](ai-answers.md#crawler-roles)
3. **One URL per page.** Production URL set in the generator; one host; the trailing-slash form `html_handling` serves with 200; canonical, internal links, hreflang, og:url and sitemap all use it; unknown URLs answer a real 404 (`not_found_handling: "404-page"`); moves are 301/308 in `_redirects`; mirrors are never indexable. → [crawl-index.md](crawl-index.md#one-url-per-page), [cloudflare.md](cloudflare.md#mirror-hostnames)
4. **Scan the build.** `python3 scripts/seo_scan.py site path/to/repo` before every deploy, in CI with `--fail-on fail`. Fix every fail; read every warn. Rules → [checks.md](checks.md)
5. **Page signals.** Title, H1 and og:title aligned; a description and a first paragraph that answer "what is this, for whom"; `WebSite` JSON-LD for the site name and only the structured data Google still uses; a raster favicon; one 1200×630 preview image under 600 KB that exists; hreflang sets that point both ways. → [page-signals.md](page-signals.md)
6. **Content.** One page per real question; answer first under descriptive headings; sections that stand alone; concrete facts with sources; visible dates and authors; About and Contact; every page linked from another with descriptive anchor text; all of it in the initial HTML, under 2 MB. → [content.md](content.md)
7. **AI answers.** Allow the search and user agents; opt out of training by token if the owner chose to; no hidden text for AI, no GEO rewriting, no invented facts; llms.txt optional with no expected effect. → [ai-answers.md](ai-answers.md)
8. **Submit and measure.** Search Console and Bing Webmaster Tools via DNS TXT, sitemap submitted, IndexNow from the production deploy only. Watch Page indexing, the generative AI and Bing AI Performance reports, and cite rates from repeated assistant runs, reported with their sample. → [measurement.md](measurement.md)
9. **Report.** Findings ranked by consequence with the fix and the evidence label, what was verified live, what only the engines' reports can confirm, and the date. Never promise rankings or traffic.

## Gotchas

- **Cloudflare Training = Block removes the site from Google.** Since 2026-09-15, Block and Block on pages with ads also stop Googlebot, Bingbot and Applebot. Use Disallow AI Training. A spoofed user agent can't tell the two apart; the zone settings and the live robots.txt can.
- **SPA fallback on a content site**: `not_found_handling: "single-page-application"` (or a Pages site without `404.html`) answers 200 with the home page for every unknown URL.
- **Trailing slashes are 307s**, which Google does not treat as canonical signals. A canonical or sitemap URL in the other form points at a redirect.
- **A build without the production URL** writes `localhost` into every canonical, hreflang, og:url and sitemap entry.
- **workers.dev, pages.dev, Version and Preview URLs and staging are public copies** unless disabled, behind Access, or sending noindex.
- **robots.txt doesn't remove pages**; noindex does, and only if the page stays crawlable. A 5xx robots.txt stops Google crawling.
- **Googlebot reads only the first 2 MB** of uncompressed HTML (since 2026; older guides say 15 MB).
- **FAQPage and HowTo markup earn nothing in Google**; structured data is not a ranking or citation lever.
- **`Google-Extended` doesn't control AI Overviews** and never appears in a user agent; `noarchive` drops a page from Bing Copilot.
- **The "up to 40 %" GEO result did not replicate** on live engines; schema and llms.txt showed no citation effect. Don't sell them.
- **Text addressed to AI is prompt injection** under both engines' policies. So are invented statistics, reviews and authors.

## Example

[case-twente.md](case-twente.md): a bilingual Astro site on Workers, mostly right, with a missing preview image on every page, broken press downloads, an edge block on training crawlers that may also be blocking Googlebot, and a public staging copy.
