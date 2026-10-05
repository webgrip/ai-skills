# Page signals: what each page tells engines, previews and assistants

The `<head>` and the first screen of every page. Google's documentation is the source (Strong) unless marked.

Contents: title · description and snippet · headings · structured data · site name and favicon · link previews · images · language versions

## Title

- Google builds the title link from `<title>`, the main heading, `og:title`, prominent text and anchor text pointing at the page ([title links](https://developers.google.com/search/docs/appearance/title-link)). Keep `<title>`, the H1 and `og:title` telling the same story so it keeps yours.
- Unique and specific per page; the distinguishing words first; the brand once, at the end, with one delimiter (`Sponsorship packages and prices — Example Meetup`).
- There is no length limit; titles are truncated to the device width in pixels. Character counts are a truncation heuristic, not a rule. Long, keyword-stuffed or boilerplate titles get rewritten more often (vendor data, Anecdotal).
- Language versions translate the title; identical titles across language alternates are fine when the words are the same.

## Description and snippet

- Snippets are "primarily created from the page content itself"; the meta description is used when it describes the page better than any passage ([snippets](https://developers.google.com/search/docs/appearance/snippet)). It is not a ranking factor.
- Write a unique description per page that answers "what is this and who is it for" in one or two sentences, with the specifics a searcher wants (date, place, price, what you get).
- **The first paragraph on the page does the same job**: it is the likely snippet, the passage an assistant lifts, and the card text a preview falls back to.
- Don't hide content in tabs or accordions that render empty without JavaScript: it can't be a snippet or a deep link.
- Control: `data-nosnippet` on an element, `max-snippet`, `nosnippet` (these also govern AI Overviews; Bing honours `data-nosnippet` for snippets and AI answers).

## Headings

- One visible H1 that names the page; headings that say what the section answers ("Sponsorship packages and prices", not "Overview"). Google does not care about heading order or the number of H1s; screen readers and passage retrieval do. Use semantic `<main>`, `<nav>`, `<article>`.

## Structured data

JSON-LD in the server HTML, describing only what is visible on the page, on the page it describes ([policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)). It earns rich-result eligibility and site identity; it is not a ranking factor and showed no causal citation lift in AI answers ([evidence.md](evidence.md#claim-table)). Validate with the [Rich Results Test](https://search.google.com/test/rich-results).

| Type | Earns | Use on a static site when |
| --- | --- | --- |
| `WebSite` (`name`, `alternateName`, `url`) on the home page of each host | the site name shown in results | always |
| `Organization` (`name`, `url`, `logo`, `sameAs`, contact) | logo and knowledge-panel facts | a company, community or foundation |
| `BreadcrumbList` | breadcrumbs (desktop only since 2025-01) | sites deeper than two levels |
| `Article` / `BlogPosting` (`headline`, `author` with `url`, `datePublished`, `dateModified`, `image`) | article features, author understanding | posts and news |
| `Event` (`name`, `startDate` with UTC offset, `location` as a `Place` with `PostalAddress`, `eventStatus`, `offers`, `image` 1920 px wide) | event experience | one URL per event, a physical location, open to the public ([event](https://developers.google.com/search/docs/appearance/structured-data/event)) |
| `Product`/`Offer`, `SoftwareApplication`, `VideoObject`, `ProfilePage`, `LocalBusiness`, `Dataset`, `JobPosting`, `Recipe` | their rich results | the page really is that thing |

**Retired** (the scanner lists them as `jsonld-retired-type`, from [scripts/rich-results.json](scripts/rich-results.json)): FAQPage (gone for every site since 2026-05-07), HowTo (2023), ClaimReview (phasing out), Special Announcement, Course Info, Estimated Salary, Learning Video and Vehicle Listing (2025), the sitelinks search box (`SearchAction`, 2024). Visible FAQ content is still useful to people and assistants; the markup earns nothing in Google.

Event times: Amsterdam is `+01:00` in winter and `+02:00` in summer; compute the offset per date, never hard-code it. A one-off event can't have a Google Business Profile; Event markup is the route.

## Site name and favicon

- The site name comes from `WebSite` JSON-LD on each host's home page, falling back to the title and other signals ([site names](https://developers.google.com/search/docs/appearance/site-names)).
- Favicon: square, larger than 48×48 (96 or 192 is safe), at a stable URL Googlebot-Image can crawl, linked from the home page with `rel="icon"`. Google's supported formats are BMP, GIF, ICO, PNG, JPEG, PPM and TIFF; **SVG is not listed** (2026-08) although SVG favicons are reported to work in practice (Contested) ([favicon](https://developers.google.com/search/docs/appearance/favicon-in-search)). Astro's starter ships only `favicon.svg`: add `favicon.ico` or a PNG.

## Link previews

Server-rendered tags in the `<head>`, early: none of these fetchers run JavaScript, WhatsApp reads only the first 300 KB, Apple 1 MB.

| Consumer | Reads | Image | Refresh |
| --- | --- | --- | --- |
| Facebook | `og:url`, `og:title`, `og:description`, `og:image`, `og:site_name` | ≥ 1200×630, 1.91:1, ≤ 8 MB | caches by image URL; Sharing Debugger |
| LinkedIn | `og:title`, `og:image`, `og:description`, `og:url` | ≥ 1200×627, ≤ 5 MB | Post Inspector refreshes new posts only |
| X | `twitter:card=summary_large_image`, falls back to `og:*` | 2:1, < 5 MB | — |
| Slack | oEmbed, then OG/Twitter, then meta | not specified | about 30 min; ignores robots.txt |
| WhatsApp | `og:title`, `og:description`, `og:url`, absolute `og:image` | < 600 KB, ≥ 300 px wide | — |
| iMessage | `og:title`, `og:image`, `og:site_name`; no JS, no meta refresh | ≥ 900 px wide | — |
| Discord, Mastodon, Bluesky | OpenGraph (Discord: `summary_large_image` for the large layout; Mastodon: `fediverse:creator`) | Bluesky ≤ 1 MB | Bluesky freezes the card into the post |

One image that satisfies all of them: **1200×630, ≤ 600 KB, JPEG or PNG, absolute `https://` URL**, with `og:image:width`, `og:image:height` and `og:image:alt`. `og:url` equals the canonical. `og:title` without the brand; the brand in `og:site_name`. To change a preview, change the image URL and re-scrape; existing LinkedIn and Bluesky posts never update. Platforms disagree about text in the image (Apple and Google advise against it, X shows only the image): keep it mostly graphical with at most a short, large headline (Contested). Never put a JavaScript challenge in front of HTML or image routes ([cloudflare.md](cloudflare.md#bot-protection)).

## Images

- `alt` that says what the image shows in context; `alt=""` for decoration. Descriptive file names, `width` and `height` attributes (layout stability), modern formats with a fallback, and the image near related text ([image SEO](https://developers.google.com/search/docs/appearance/google-images)).
- Images in CSS backgrounds are not indexed as images. `max-image-preview:large` allows large previews in Discover and results.

## Language versions

- A separate URL per language (`/nl/…`, `/en/…`), translated slugs, a language switcher with plain links ([localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions)).
- `hreflang` on every version listing **every** version including itself, plus `x-default` for visitors matching none; links must point both ways or Google ignores them. Each version is its own canonical.
- `lang` on `<html>`: Google ignores it for language detection (it reads the content), but WCAG 3.1.1 requires it and screen readers and assistants use it.
- **Never redirect by `Accept-Language` or IP.** Googlebot crawls mostly from the US without that header and would only ever see one version. A root that picks a language should be a page with links, or a redirect with `x-default` pointing at the root.
