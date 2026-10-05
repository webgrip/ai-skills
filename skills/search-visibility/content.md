# Content: pages worth showing and quoting

Engines and assistants pick pages that answer the query and that they can trust. Neither can be faked for long. Visual design and copy voice belong to the `expressive-design` and `product-ux` skills, and AI-sounding prose to `humanize`; this file covers what makes content findable, quotable and credible.

Contents: what to write · writing for retrieval · trust and authorship · structure and internal links · freshness · events and local · folklore

## What to write

- **One page per real question or task** someone brings: what the thing is, who it is for, what it costs, when and where, how to start, how it compares. Pages for queries nobody types are wasted; one thin page per keyword variant is spam.
- **Use the words your audience searches with**, in headings and body, naturally. Check them in Search Console queries, site search logs and the questions people ask in person.
- **Concrete over general**: numbers with their source, names, dates, prices, places, examples, photos of the real thing. Original information (your data, your experience, your event) is what neither a competitor nor an assistant can produce, and what Google's 2026 rater guidance calls effort and originality ([helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), Strong).
- **Generated text** is allowed when it adds value and a person checked it; many pages generated to rank are scaled-content abuse "no matter how it's created" ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies), Strong).

## Writing for retrieval

Search and assistants retrieve passages, not just pages.

- **Answer first.** The first sentence under each heading answers the question the heading asks; detail follows. Google ranks passages ([ranking systems](https://developers.google.com/search/docs/appearance/ranking-systems-guide), Strong); embedding models weight the beginning of a text most ([Coelho et al., ACL 2024](https://arxiv.org/abs/2404.04163), Strong); answer-early pages ranked higher in the only full-pipeline GEO test ([SAGEO](https://arxiv.org/abs/2602.12187), Strong).
- **Sections that stand alone**: name the subject instead of "it" or "as mentioned above", so a lifted passage still makes sense. No need to cut text into tiny chunks: Google says it doesn't require that.
- **Descriptive headings** phrased the way the question is asked.
- **Tables for comparisons and facts** (prices, schedules, specifications), lists for steps; real HTML, not images of text.
- **Definitions** in one sentence when you introduce a term.

## Trust and authorship

Trust is what Google's raters weigh most; E-E-A-T is a rater concept, not a ranking factor or score (Strong).

- An **About** page (who runs this, why, since when) and a **Contact** page, linked from every page.
- **Visible bylines** linking to an author page with the person's role and experience; `Article` markup with `author.url`. Never invent people, reviews, logos or numbers: fabricated creator profiles are deception under Google's guidelines and destroy trust when found.
- `Organization` JSON-LD with `sameAs` links to the real profiles (LinkedIn, GitHub, Mastodon, Meetup).
- Cite sources for claims you didn't originate; link out when it helps the reader.

## Structure and internal links

- **Every page you care about is linked from at least one other page** with a plain `<a href>` ([links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable), Strong); the sitemap supplements links, it doesn't replace them (`orphan-page`).
- **Descriptive anchor text** naming the destination, never "click here" or "read more" (`link-text-generic`); it tells engines and screen readers what the target is.
- **Readable, hyphenated slugs** in the page's own language (`/nl/sponsoren`, `/en/sponsors`); keywords in URLs barely matter beyond readability.
- Important pages a click or two from the home page (one Googler's statement, Anecdotal); breadcrumbs on deep sites.
- Navigation, footer and related-links blocks in the server HTML, not injected by script.

## Freshness

- Update when something changed; show the date visibly and keep `dateModified` honest. Bumping dates without substantive change does not help ("No, it won't") and is deceptive (Strong). Freshness matters for queries that deserve it (events, news, prices), not for evergreen pages.
- Past events stay online with their outcome (slides, recordings, photos): they keep earning links and show a track record. Past events keep `EventScheduled` with their past dates; set `EventCancelled` or `EventPostponed` when that is what happened.

## Events and local

- One URL per event with `Event` markup, a physical `Place` with an address, and offset-correct times ([page-signals.md](page-signals.md#structured-data)). Keep `eventStatus` current.
- List the event where people look: Meetup, the venue's agenda, regional calendars, partner sites. Those pages are often what assistants cite.
- A permanent business location gets a Google Business Profile and `LocalBusiness` markup; a one-off event cannot.

## Folklore

What the evidence and Google say (Strong unless marked):

| Claim | Reality |
| --- | --- |
| Target word counts; longer ranks better | "(No, we don't.)" Length follows the question |
| Keyword density, LSI keywords | No density metric; stuffing is spam; "no such thing as LSI keywords" (Consistent) |
| Meta keywords tag | Unused; omit it |
| Exact-match domains | Discounted; pick a brandable domain |
| "SEO score" tools, Lighthouse SEO 100 | Third-party tools have no access to ranking data; a checklist, not a predictor |
| Title ≤ 60 characters, description ≤ 160 | No limit; pixel truncation heuristic only |
| One H1, heading order | Irrelevant to Search; keep the hierarchy for accessibility |
| Duplicate content penalty | None; canonicalise anyway so signals consolidate |
| Subdomain vs subfolder | Google says no difference; practitioners disagree (Contested) |
| Fewer slashes means more important | Click depth matters, URL depth doesn't (Anecdotal) |
| CTR doesn't matter / CTR manipulation works | Google uses aggregated interaction data; manipulation is spam and unsupported |
| Chunking content for AI, llms.txt for Google | Not needed; Google ignores both |
