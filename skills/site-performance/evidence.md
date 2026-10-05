# Evidence: what is known about speed

Strength labels: **Strong** (the platform's own documentation or spec, a controlled experiment, a large sample with a published method) · **Consistent** (independent sources agree) · **Contested** · **Anecdotal** (one site, a vendor case study or survey with an unpublished method, a slide). Vendor data is named as vendor data.

Contents: the state of the web · speed and people · speed and ranking · speed and AI answers · lab versus field · claim table

## The state of the web

- About half of sites fail: **48 % of origins pass Core Web Vitals on mobile, 56 % on desktop** (July 2025). LCP is the weak metric: 62 % of mobile pages have good LCP, against 77 % for INP and 81 % for CLS ([Web Almanac 2025](https://almanac.httparchive.org/en/2025/performance), Strong).
- 76 % of mobile pages have an image as their LCP element, and about **1 in 6 lazy-load it**, unchanged since 2024 (Strong). Pages that lazy-load the LCP image have a median p75 LCP of 3.5 s against 2.9 s without ([LCP lazy loading](https://web.dev/articles/lcp-lazy-loading), Strong).
- On origins with poor LCP the image download is **under 10 %** of LCP time; the wait before the download starts is about four times the download ([common LCP misconceptions](https://web.dev/blog/common-misconceptions-lcp), Strong). Discovery and priority beat compression.
- The median mobile home page weighs about 2.6 MB and grows about 8 % a year ([page weight](https://almanac.httparchive.org/en/2025/page-weight), Strong; the chapter's text and chart disagree slightly).
- Static generators do well in the field: in August 2026, 71 % of Astro and 78 % of Hugo mobile origins passed, against 35 % for Next.js and 49 % for WordPress (HTTP Archive technology report, Strong as a measurement; reading it as "the framework causes it" is Contested).

## Speed and people

The famous numbers trace back to Google marketing material or a single slide and publish no method. The causal evidence that exists is older and smaller:

- Randomised slowdown tests at search engines: Bing measured 100 ms costing 0.6 % of revenue; Google's 2009 test −0.2 % to −0.6 % of searches ([Kohavi et al.](https://exp-platform.com/Documents/2013%20controlledExperimentsAtScale.pdf), Strong). Etsy reported no effect from 200 ms in one test.
- Single-site A/B tests published by Google (Vodafone: +8 % sales with a 31 % better LCP; Rakuten: +33 % conversion) agree in direction ([Vodafone](https://web.dev/case-studies/vodafone), Anecdotal each).
- Response-time limits of 0.1 s, 1 s and 10 s are heuristics; the "400 ms Doherty threshold" does not appear in the 1982 paper, which says "sub-second" (Anecdotal).

**Use:** slower pages lose a little per 100 ms; measure your own outcome instead of quoting a multiplier.

## Speed and ranking

- "Core Web Vitals are used by our ranking systems", but a perfect score "just for SEO reasons may not be the best use of your time" ([page experience](https://developers.google.com/search/docs/appearance/page-experience), Strong). Google's own 2010 statement put speed's effect at "fewer than 1 % of search queries"; John Mueller called them "not giant factors" (Consistent). Relevance dominates; treat speed as a tie-breaker.
- Google ranks on field data (CrUX, real Chrome users at p75), not on Lighthouse or PageSpeed scores (Strong).
- TTFB "isn't a Core Web Vitals metric"; it matters through LCP and, for sites with tens of thousands of pages, crawl rate ([TTFB](https://web.dev/articles/ttfb), Strong).

## Speed and AI answers

No answer engine documents speed as a factor. The only data are vendor correlations that point in both directions (one found faster FCP with more ChatGPT citations and the opposite for INP; Anecdotal). What is documented: most AI crawlers don't run JavaScript, so content must be in the initial HTML (the `search-visibility` skill).

## Lab versus field

- In 2021, 43 % of pages scoring 90+ in Lighthouse failed Core Web Vitals in the field; the LCP correlation was r = 0.49 ([HTTP Archive](https://discuss.httparchive.org/t/lighthouse-scores-as-predictors-of-page-level-crux-data/2232), Strong for its date, before INP).
- Lighthouse can't measure INP (it uses Total Blocking Time), runs one throttled device on one network, and loads a cold cache; real users have warm caches, back/forward restores, prerendered navigations, slower and faster devices ([lab and field](https://web.dev/articles/lab-and-field-data-differences), Strong).
- **Lab diagnoses; field judges.**

## Claim table

| Claim | Verdict | Strength | What the skill says |
| --- | --- | --- | --- |
| 53 % of mobile visitors leave after 3 s | unknown | Anecdotal (Google, 2016, method never published; "visits", undefined "abandoned") | don't quote it |
| Every 100 ms cost Amazon 1 % of sales | a 2006 slide | Anecdotal; Bing/Google randomised tests Strong at 0.2–0.6 % per 100 ms | cite the experiments |
| 0.1 s faster = 8 % more conversions (Deloitte) | correlation | Anecdotal (Google-commissioned, observational regression) | not causal |
| Pinterest: −40 % wait, +15 % SEO traffic | one rewrite | Anecdotal | an example, speed not isolated |
| Passing CWV moves rankings | small | Strong that it is used; size Contested | tie-breaker |
| Better CWV raise conversions | direction yes | Consistent direction; uplifts Anecdotal | measure your own |
| A high Lighthouse score means good real-user experience | partly | Strong (r = 0.49 for LCP in 2021) | field data judges |
| About half of sites fail CWV on mobile | true | Strong | LCP fails most |
| Third parties are the main cause of poor INP | unknown | Anecdotal | attribute with Long Animation Frames before blaming |
| Speed affects AI citations | unknown | Anecdotal | no evidence |
| TTFB must be under 800 ms / ranks directly | false | Strong ("rough guide", not a CWV) | through LCP only |
| Compress the hero image first | mostly false | Strong | start the fetch earlier first |
| `no-store` kills the back/forward cache | false in Chrome since 2025 | Strong | still costs caching elsewhere |
| Safari and Firefox can't measure CWV | false since 2025/26 | Strong (LCP, INP baseline; CLS Chromium-only) | segment RUM by engine |
