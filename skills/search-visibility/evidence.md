# Evidence: what is known about being found and cited

Strength labels: **Strong** (the platform's own documentation of its system, a controlled study, a large sample with a published method, or sworn testimony) · **Consistent** (several independent sources agree) · **Contested** (sources disagree, or the platform denies) · **Anecdotal** (one site, one practitioner, or a vendor dataset with an unpublished method). Vendor data is named as vendor data wherever it appears.

Contents: the pipeline · how the engines retrieve · generative engine optimisation · what answer engines cite · traffic · claim table

## The pipeline

Visibility is a chain: **crawlable → indexed → retrieved → shown or cited → clicked**. Each link has its own failure, and most of the leverage sits in the first two, which are classic SEO. Google's own guide for its AI features says so outright: "AEO/GEO is still SEO", no special files, markup or chunking ([AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), Strong).

## How the engines retrieve

| Engine | Index it answers from | Crawler that must be allowed | Strength |
| --- | --- | --- | --- |
| Google Search, AI Overviews, AI Mode | Google's index plus query fan-out; a page must be indexed and allowed a snippet | `Googlebot`; `Google-Extended` does not control AI Overviews | Strong ([AI features](https://developers.google.com/search/docs/appearance/ai-features)) |
| Bing, Copilot, DuckDuckGo | Bing's index; DuckDuckGo "largely" sources from Bing; Ecosia and Qwant partly from their own EU index since 2025 | `bingbot` (no separate Copilot agent) | Strong / Consistent |
| ChatGPT search | OpenAI's own crawl plus partners; overlap with Bing is high in one vendor sample | `OAI-SearchBot` (and `ChatGPT-User` for live fetches) | Strong ([OpenAI bots](https://developers.openai.com/api/docs/bots)); Bing reliance Contested |
| Claude | Anthropic's search crawler and live fetches; the search provider is Brave by consistent reporting, not by Anthropic's docs | `Claude-SearchBot`, `Claude-User` | Strong / Consistent |
| Perplexity | Its own index | `PerplexityBot` (and `Perplexity-User`, which generally ignores robots.txt) | Strong ([Perplexity bots](https://docs.perplexity.ai/guides/bots)) |

AI crawlers other than Googlebot and Applebot did not execute JavaScript in the largest published measurement (GPTBot: 569M requests, no JS executed; [Vercel/MERJ, Dec 2024](https://vercel.com/blog/the-rise-of-the-ai-crawler), Strong for its date). Static HTML is the advantage of this stack; keep it.

## Generative engine optimisation

- **The paper:** Aggarwal et al., GEO, KDD 2024 ([arXiv 2311.09735](https://arxiv.org/abs/2311.09735)). An LLM rewrote one of the top five Google sources per query and the authors measured that source's word share in a GPT-3.5 answer. Quotations raised share about 41 %, statistics 31 %, fluency 28 %, citing sources 27 %; keyword stuffing lowered it. The "up to 40 %" is a relative gain in share for a page that was already retrieved, in a simulated engine, in 2023. The paper's own examples add invented sources and statistics.
- **It did not replicate.** C-SEO Bench (NeurIPS 2025, [arXiv 2506.11097](https://arxiv.org/abs/2506.11097)): 3 of 54 method-domain cases significant, none for question answering; "statistics" lowered citation rank in 19 of 24 settings; moving a document to the top of the context beat every rewrite, and gains shrank as more sites adopted the methods. SAGEO Arena (KDD 2026, [arXiv 2602.12187](https://arxiv.org/abs/2602.12187)), the first full-pipeline test: rewriting body text lowered retrieval at every stage; putting the answer early raised reranker scores. Strong.
- **Relevance beats style.** Models weigh relevance and largely ignore references and neutral tone ([Wan et al., ACL 2024](https://arxiv.org/abs/2402.11782), Strong). Embedding models weight the start of a text most ([Coelho et al., ACL 2024](https://arxiv.org/abs/2404.04163), Strong), which supports answer-first writing ([content.md](content.md#writing-for-retrieval)).
- **Manipulation works and is an attack.** Hidden instructions in a page shifted live recommendations on Bing and Perplexity ([Nestaas et al.](https://arxiv.org/abs/2406.18382); [Pfrommer et al., EMNLP 2024](https://arxiv.org/abs/2406.03589)). Bing's 2026 guidelines and Google's spam policies name it. Strong.

**Use:** sources, statistics and quotations are good writing for people; they are not a proven lever for citation. Being retrieved matters more than being rewritten.

## What answer engines cite

- AI Overviews and page-one results share only about 18 % of sources ([Grossman et al., SIGIR 2026](https://arxiv.org/abs/2604.27790)); 53 % of AI Overview domains sit outside the organic top 10 ([Kirsten et al., ACL 2026 Findings](https://arxiv.org/abs/2510.11560)). Strong.
- Answers are unstable: 18 % of AI Overview pages stayed the same between runs two months apart, against 45 % for organic results (Kirsten et al.). Measure with repeated runs ([Schulte et al.](https://arxiv.org/abs/2604.07585)). Strong.
- Engines favour earned, third-party sources over brand-owned pages ([Chen et al.](https://arxiv.org/abs/2509.08919), Anecdotal: observational preprint). Neural retrievers rank LLM-written text above human text ([Dai et al., KDD 2024](https://arxiv.org/abs/2310.20501), Strong in the lab).
- Vendor citation shares swing widely: Ahrefs found 38 % of AI Overview citations in the top 10, down from 76 % ([vendor](https://ahrefs.com/blog/ai-overview-citations-top-10/)); Profound's "46.7 % Reddit" is a share of Perplexity's top-10 domains, 6.6 % of all its citations ([vendor](https://www.tryprofound.com/blog/ai-platform-citation-patterns)). Direction Consistent, shares Anecdotal.

## Traffic

- With an AI summary on the page, people clicked an organic result on 8 % of visits against 15 % without one, and a link inside the summary on 1 % ([Pew Research Center, 2025](https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/), Strong).
- Vendor estimates of the click loss run from −34.5 % to −61 % ([Ahrefs](https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/), [Seer](https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-september-2025-update)); a causal estimate fell to about 5 % across revisions. Google says total clicks are stable and "higher quality" without publishing data ([Google](https://blog.google/products/search/ai-search-driving-more-queries-higher-quality-clicks/), Contested). **Give a range, never one number, and never promise traffic.**
- AI assistants send a small share of referrals (about 0.3 % of traffic in one vendor study, [SE Ranking](https://seranking.com/blog/ai-traffic-research-study/), Anecdotal).

## Claim table

| Claim | Verdict | Strength | What the skill says |
| --- | --- | --- | --- |
| GEO tactics raise AI visibility up to 40 % | lab only | Strong in the lab; Contested live | Good writing, not a lever; retrieval first |
| Structured data raises rankings or AI citations | false | Strong (Google); vendor causal test: AI Overviews −4.6 %, ChatGPT +2.2 % (n.s.) ([Ahrefs](https://ahrefs.com/blog/schema-ai-citations/)) | Use it for rich-result eligibility and site identity only |
| llms.txt improves visibility | false | Strong (Google ignores it); 97 % of files got zero requests ([Ahrefs, vendor](https://ahrefs.com/blog/llmstxt-study/)) | Optional, generated at build, no effect expected |
| Core Web Vitals are a major factor | used, minor | Strong ([page experience](https://developers.google.com/search/docs/appearance/page-experience)) | Reach "good" for people; a tie-breaker for ranking |
| E-E-A-T is a ranking factor | false | Strong | Show real authorship and sources; there is no score |
| AI Overviews cut clicks | true in direction | Consistent; size Contested | A range, 8 % vs 15 % clicks in Pew |
| Google uses clicks; a site-level quality score exists | true; weights unknown | Strong (NavBoost trained on 13 months of clicks, [US v. Google, ECF 1033 ¶96](https://storage.courtlistener.com/recap/gov.uscourts.dcd.223205/gov.uscourts.dcd.223205.1033.0_2.pdf)) | Real, unweighted; no manipulation |
| Longer content ranks better | false | Strong | Length follows intent |
| Keyword density, LSI keywords | false | Strong / Consistent | Use the words people search, naturally |
| Meta descriptions affect ranking | false | Strong | Write them for the snippet |
| HTTPS boost | true, tiny | Strong | A floor, not a lever |
| AI-written content is penalised | false; scaled low-value content is | Strong ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies)) | Fact-check, add value, never mass-produce |
| Backlinks matter; "domain authority" reflects Google | partly; false | Strong (PageRank feeds a quality score); DA is a vendor metric | A few real links help; ignore DA |
| Bumping dates helps | false, and deceptive | Strong | Honest dateModified on real updates only |
| Ranking top 10 means being cited in AI Overviews | weakening | Contested (17–76 % depending on study and month) | Necessary-ish, not sufficient |
| Reddit dominates LLM citations | false as "dominates" | Consistent order, Anecdotal shares | The long tail dominates; no astroturfing |
| AI crawlers skip JavaScript | true except Googlebot, Applebot | Strong (Dec 2024) | Content in the initial HTML |
| IndexNow speeds indexing | Bing and others; not Google | Strong ([participants](https://www.indexnow.org/searchengines.json)) | Turn it on for Bing-fed engines |
| priority / changefreq in sitemaps matter | ignored | Strong | loc and an accurate lastmod only |
| FAQ markup earns rich results | false since 2026-05-07 | Strong ([updates](https://developers.google.com/search/updates)) | No FAQPage for Google |
| Page speed alone moves rankings | mostly false | Strong that the effect is limited | Speed for people |
| Googlebot reads 15 MB of HTML | false since 2026 | Strong: 2 MB uncompressed ([Googlebot](https://developers.google.com/search/docs/crawling-indexing/googlebot)) | Keep HTML well under 2 MB |
