# Measurement: knowing whether it worked

The scanner proves the site is technically sound. Only the engines' own reports show what they crawled, indexed and showed, and only repeated runs show what assistants cite. Report counts and ranges with their date and sample, never a single "visibility score".

Contents: Search Console · Bing Webmaster Tools · edge and analytics · AI answers · cadence

## Search Console

Domain property, verified by DNS TXT ([crawl-index.md](crawl-index.md#submitting)).

| Report | Look for |
| --- | --- |
| Page indexing | "Crawled – currently not indexed" (quality or duplication), "Duplicate, Google chose different canonical" (conflicting signals), soft 404, "Blocked by robots.txt", "Excluded by noindex" on pages you want |
| URL Inspection | the rendered HTML Googlebot saw, the canonical it chose, the live test after a fix |
| Sitemaps | submitted vs indexed counts per sitemap |
| Performance | queries and pages, impressions, clicks, position; filter out branded queries to see discovery |
| Generative AI performance (since 2026-06, all sites 2026-08-31) | impressions and pages in AI Overviews and AI Mode ([announcement](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)) |
| Core Web Vitals | field data; empty until a page has enough traffic |
| Rich results reports | errors in Event, Breadcrumb, Article markup |

## Bing Webmaster Tools

Import the Search Console property or verify by DNS. Search Performance, URL Inspection, Sitemaps, IndexNow insights, and **AI Performance** (public preview since 2026-02): citations, cited pages and the "grounding queries" behind them across Copilot and Bing's AI summaries ([announcement](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/)). Bing coverage reaches Copilot, DuckDuckGo and part of Ecosia and Qwant.

## Edge and analytics

- **Cloudflare AI Crawl Control**: which AI crawlers fetched what, robots.txt violations per crawler, AI referrals. Use it to confirm the training stance holds and search crawlers are getting through.
- **Cloudflare Web Analytics** (cookieless): page views, referrers including assistants (chatgpt.com, perplexity.ai, claude.ai, copilot.microsoft.com), and real-user Core Web Vitals. It knows nothing about queries, indexing or canonicals, and on the Free plan its automatic setup skips EU visitors unless set to include them. Speed and real-user monitoring belong to the `site-performance` skill.
- **Security Events**: blocks and challenges by bot category, the place to confirm a `live-crawler-blocked` finding.
- `seo_scan.py live` after every deploy; `seo_scan.py site` in CI before it.

## AI answers

Answers vary between runs, phrasings and weeks: only 18 % of AI Overview pages stayed the same over two months ([Kirsten et al.](https://arxiv.org/abs/2510.11560)), so one check proves nothing ([Schulte et al.](https://arxiv.org/abs/2604.07585), Strong).

1. Write 10–20 prompts real people would ask where the site should appear: the category question, the comparison, the local question, the brand question. Include the owner's language and English.
2. Run each prompt 3–5 times per assistant (ChatGPT search, Perplexity, Claude with search, Copilot, Google AI Mode), logged out or in a clean profile, same week.
3. Record per run: cited (yes/no), position, which page, which competitors and third-party sources appear.
4. Report rates with their sample: "cited in 7 of 25 runs (5 prompts × 5 runs, Perplexity, 2026-10-04)". Repeat monthly or after a significant change; compare rates, not single answers.
5. When a competitor or third-party page is cited instead, read it: that is the evidence of what the engine found relevant.

Don't buy "AI visibility scores" that hide their sample; don't attribute a change in one run to a content change.

## Cadence

| When | Do |
| --- | --- |
| Every deploy | `seo_scan.py site` in CI (fail on `fail`), `seo_scan.py live` after the edge serves the build, IndexNow ping from production |
| Launch, then two weeks later | URL Inspection on key pages; Page indexing; Bing AI Performance baseline; AI answer runs baseline |
| Monthly | Performance and generative AI reports, AI answer runs, AI Crawl Control |
| Yearly, or when an engine announces changes | re-check [scripts/crawlers.json](scripts/crawlers.json) and [scripts/rich-results.json](scripts/rich-results.json) against the linked sources and update their `checked` date |
