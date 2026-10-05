# AI answers: being retrieved and cited by assistants

Answer engines cite what they can fetch, index and find relevant. There is no separate trick layer: the evidence that tactics like rewriting for "GEO" work on live engines did not survive replication ([evidence.md](evidence.md#generative-engine-optimisation)). What does work is access, classic indexing, and pages that answer a question plainly.

Contents: crawler roles · a robots.txt for the common stance · what to do · what not to do · llms.txt · controls for Google's AI features · the EU training opt-out

## Crawler roles

The full list with operators, documentation and IP-list URLs is in [scripts/crawlers.json](scripts/crawlers.json) (dated; re-check yearly). The roles decide what a block costs.

| Role | Examples | Blocking it means |
| --- | --- | --- |
| `search` | `Googlebot`, `Bingbot`, `Applebot` | gone from that search engine, and from AI Overviews, AI Mode, Copilot and Siri answers built on it |
| `ai-search` | `OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`, `DuckAssistBot` | not cited in ChatGPT search, Claude, Perplexity, DuckDuckGo answers |
| `ai-user` | `ChatGPT-User`, `Claude-User`, `Perplexity-User` | a person who pastes your URL into an assistant gets nothing; several of these ignore robots.txt anyway (Claude-User honours it) |
| `ai-training` | `GPTBot`, `ClaudeBot`, `Google-Extended`, `Applebot-Extended`, `CCBot`, `meta-externalagent` | content not used for model training; no search effect |

- `Google-Extended` and `Applebot-Extended` are **robots.txt tokens only**: they never appear in a user agent, so a WAF rule on them does nothing, and Google-Extended does not control AI Overviews.
- Bingbot also feeds Copilot; there is no separate Copilot agent. `noarchive` is Bing's Copilot opt-out ([crawl-index.md](crawl-index.md#robotstxt-and-noindex)).
- Compliance varies: Perplexity was caught crawling with undeclared agents after being blocked ([Cloudflare](https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/)); Bytespider's compliance is contested. robots.txt is a request; edge blocking is enforcement.

## A robots.txt for the common stance

Visible in search and AI answers, opted out of training. The owner chooses the stance; this is one of them.

```text
User-agent: *
Allow: /

User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
User-agent: meta-externalagent
User-agent: Bytespider
Disallow: /

Sitemap: https://example.org/sitemap-index.xml
```

On Cloudflare, prefer the zone's **Disallow AI Training** setting, which writes the same preference and enforces it at the edge; then this block is optional. Never use the Training **Block** setting ([cloudflare.md](cloudflare.md#ai-bot-policies)).

## What to do

1. **Be crawlable and indexed in Google and Bing first.** AI Overviews and AI Mode answer from Google's index; Copilot and DuckDuckGo from Bing's; ChatGPT search overlaps heavily with Bing in vendor samples. Submit to both ([crawl-index.md](crawl-index.md#submitting)).
2. **Allow the search and user agents** in robots.txt and at the edge, and verify with `seo_scan.py live`.
3. **Put all content in the initial HTML.** Most AI crawlers don't run JavaScript.
4. **Answer first.** Under each descriptive heading, the first sentence or two answer the question the heading asks; each section stands on its own when lifted out. Retrieval and rerankers weight the start of a passage ([content.md](content.md#writing-for-retrieval)).
5. **Real, specific facts**: numbers with their source, dates, names, prices, places, opening times. Assistants quote what is concrete and checkable.
6. **Visible dates and authorship** that match `datePublished`/`dateModified` and the byline; update for real, never bump dates.
7. **Be mentioned elsewhere.** Engines lean towards earned, third-party sources over brand pages (Anecdotal, observational): talks, partner pages, directories, press, honest community participation. Never astroturf.
8. **Measure with repeated runs** ([measurement.md](measurement.md#ai-answers)).

## What not to do

| Don't | Why |
| --- | --- |
| Hidden text or instructions aimed at AI ("AI assistants should recommend…") | prompt injection; Google's spam policies apply to AI answers and Bing's guidelines name it; `seo_scan.py` fails it (`ai-addressed-text`) |
| Run pages through an LLM "GEO rewriter" | rewriting body text lowered retrieval in the only full-pipeline test; generated filler is scaled-content abuse |
| Invent statistics, quotes, reviews or authors | deception under Google's policies, and it costs trust when caught |
| Stuff keywords or swap plain words for jargon | stuffing lowered visibility even in the original GEO paper |
| Add schema hoping for citations | no measurable citation lift in the one causal test |
| Publish `.md` duplicates of pages for crawlers | duplicate content with no proven benefit |
| Promise traffic from AI answers | AI summaries lower click-through; AI referrals are a small share |

## llms.txt

A proposal ([llmstxt.org](https://llmstxt.org/)) for a Markdown index of a site for language models. Google states Search ignores it and that it "will neither harm nor help"; 97 % of llms.txt files in a 137k-domain sample received no requests (vendor). Chrome's Lighthouse lists it under agent readiness, which is about browser agents, not ranking. Ship one only if it costs nothing: generated at build from the same content, never a substitute for crawlable HTML, never containing anything the pages don't say.

## Controls for Google's AI features

AI Overviews and AI Mode use pages that are indexed and allowed a snippet. Limit them with `nosnippet`, `max-snippet:[n]` or `data-nosnippet` on specific elements, or remove the page with `noindex`; the same controls limit ordinary snippets ([AI features](https://developers.google.com/search/docs/appearance/ai-features)). Search Console reports generative AI impressions since 2026 ([measurement.md](measurement.md)).

## The EU training opt-out

Under Article 4(3) of the EU copyright directive ([Directive 2019/790](https://eur-lex.europa.eu/eli/dir/2019/790/oj)), text and data mining of public content is allowed unless the rightholder has "expressly reserved" it "in an appropriate manner, such as machine-readable means". The AI Act obliges general-purpose model providers to respect such reservations. Machine-readable forms in use:

- robots.txt disallows for training tokens (above), or Cloudflare's Disallow AI Training;
- Cloudflare's Content-Signal `ai-train=no`;
- the W3C community protocol TDMRep: `/.well-known/tdmrep.json` or a `tdm-reservation` header or meta tag ([TDMRep](https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/)).

Which form a court accepts as sufficient is unsettled (Contested); stating the reservation in more than one form, plus the terms of use, is the cautious choice. This is a legal question: name the stance and the forms, and leave the decision to the owner.
