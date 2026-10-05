# search-visibility

Gets static sites on Cloudflare's edge found in Google and Bing and cited by ChatGPT, Claude, Perplexity and Google's AI Overviews. It is the search sibling of `edge-hosting` (deployment), `expressive-design` (distinctive pages) and `product-ux` (product interfaces).

What it does that the popular SEO and GEO skills don't:

- **Grades its own evidence.** Every claim is labelled Strong, Consistent, Contested or Anecdotal, and vendor data is named as vendor data. The folklore is corrected against Google's documentation, sworn testimony from US v. Google and replication studies: word counts, keyword density, title lengths, E-E-A-T as a score, FAQ markup, and the GEO paper's "up to 40 %", which did not replicate on live engines.
- **Cloudflare's edge, not a generic host.** The AI bot policies, including the 2026-09-15 change that makes Training = Block also block Googlebot, Bingbot and Applebot; managed robots.txt and Bot Preference Sync prepending rules you didn't write; Markdown for Agents sending `ai-train=yes`; `html_handling` 307s against canonicals; SPA fallback soft 404s; public workers.dev, pages.dev, preview and staging copies.
- **AI answers by crawler role.** Search, user-fetch and training crawlers separated, with a dated data file of 24 crawlers from their operators' own docs, a robots.txt for the common "in search, out of training" stance, the EU text-and-data-mining opt-out, and a measurement protocol of repeated assistant runs instead of a visibility score.
- **`scripts/seo_scan.py`.** A dependency-free scanner with 78 rules in two modes:
  - `site` reads the build with the wrangler config: canonicals, sitemaps and links that hit a trailing-slash redirect or a missing file, a build without the production URL, noindex on the home page or across `_headers`, hreflang that doesn't point both ways, missing preview images, pages over Googlebot's 2 MB limit, text addressed to AI, retired schema types.
  - `live` reads the edge: robots.txt as served (Cloudflare content, Content-Signal lines, a 5xx), crawlers refused at the edge by role, sitemap URLs that redirect or fail, the preview image, and mirror hostnames that can be indexed.

## Install

```text
/plugin install search-visibility@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s search-visibility`.

## Example prompts

- "Our Astro site on Workers doesn't show up in Google. Why?"
- "How do we get cited when people ask ChatGPT or Perplexity about this?"
- "Stop AI companies training on our site but keep us in Google."
- "The LinkedIn preview of our homepage has no image."
- "We launch next week; do an SEO check first."

## Scanner

```bash
python3 skills/search-visibility/scripts/seo_scan.py site path/to/repo
python3 skills/search-visibility/scripts/seo_scan.py live https://example.org --mirror staging.example.org
```

Exit status 1 when a finding at or above `--fail-on` (default `fail`) exists. `test.sh` runs the `site` mode against `fixtures/careful` (nothing may fire) and the four `fixtures/careless` sites (every expected rule must fire), runs the `live` mode against local HTTP servers that misbehave on purpose, and checks that every rule is documented in `checks.md` and both data files carry a `checked` date. Before release it was run against two real Workers sites; the false positives it found (redirected stub pages, language alternates as duplicate titles, a dev build repeated 48 times) became exemptions and aggregation.

## Sources

Each reference file links its sources:

- **Platforms:** Google Search Central documentation and changelog, Bing Webmaster blog and guidelines, Cloudflare developer documentation and blog, the crawler pages of OpenAI, Anthropic, Perplexity, Apple, Amazon, Meta, Mistral, DuckDuckGo and Common Crawl, ogp.me and each link-preview consumer's docs.
- **Research:** Aggarwal et al. (GEO, KDD 2024) and the replications C-SEO Bench (NeurIPS 2025) and SAGEO Arena (KDD 2026); Wan et al. and Coelho et al. (ACL 2024); Kirsten et al. (ACL 2026 Findings) and Grossman et al. (SIGIR 2026) on what AI Overviews cite; Nestaas et al. and Pfrommer et al. on prompt injection; Pew Research Center on clicks with AI summaries; the Vercel/MERJ crawler study.
- **Law:** the US v. Google liability and remedies opinions; Article 4 of EU Directive 2019/790 and the W3C TDMRep protocol.
- **Market survey:** the most-installed published SEO and GEO skills (coreyhaines31 marketingskills, addyosmani web-quality-skills, resciencelab, agricidaniel claude-seo, sanity agent-toolkit, Anthropic knowledge-work-plugins, aaron-he-zhu, Joost de Valk's static-seo) and the audit rule sets of Lighthouse, Search Console, Bing Webmaster Tools and Screaming Frog.
