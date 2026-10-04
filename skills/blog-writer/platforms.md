# Platforms — constraints, norms, and adaptation recipes

Governing model: **POSSE** (Publish on your Own Site, Syndicate Elsewhere). One canonical post
at the home platform; every syndicated copy carries `rel=canonical` back to it; every
aggregator submission points at the canonical URL. Wait 2–10 days after the canonical goes
live before syndicating (2–3 for a well-crawled domain, 7–10 for a new one) so search engines
index the original as authoritative. Verbatim duplication without canonical tags measurably
bleeds organic traffic.

**Choosing the home**: an own-domain blog is SEO-optimal and survives platform churn; Substack
trades that for a subscriber/email relationship you own. Both are legitimate — pick per goal
(audience relationship vs. searchable archive) and note that the canonical can move to an own
domain later.

## Contents

1. [Hacker News](#hacker-news)
2. [LinkedIn](#linkedin)
3. [Substack](#substack)
4. [dev.to / Hashnode / Medium](#devto--hashnode--medium)
5. [Reddit](#reddit)
6. [Lobsters](#lobsters)
7. [Publish checklist template](#publish-checklist-template)

## Hacker News

**Rules** ([guidelines](https://news.ycombinator.com/newsguidelines.html)): original title,
no editorializing/clickbait/allcaps; strip the site name; drop gratuitous numbers. Mods retitle
violations. Submit the canonical URL (the original source, never a rehost or summary).
Self-promotion is tolerated "part of the time" — the account must be a curious participant,
not a distribution channel. **Never solicit votes anywhere**; ring detection kills the post
and the account. **AI-generated or AI-edited text is explicitly banned** (submissions and
comments; "AI-generated" is a flag reason) — the post must read, and be, human-authored.

**Show HN** ([rules](https://news.ycombinator.com/showhn.html)): only for something people can
try *now* (demo, repo, download). Title: `Show HN: Name – plain one-line description`, zero
marketing adjectives.

**Recipe**: submit canonical URL + de-hyped original title, Tue–Thu ~9:00–12:00 US Eastern.
Substance must arrive in the first screenful (HN bounces on preamble). Author shows up in the
comments and answers the hard questions — that's where the credibility (and half the value) is.

## LinkedIn

**Mechanics** (links, the fold, formatting, hashtags, timing, profile versus page) belong to the
`linkedin-post` skill: load it for this variant. Two facts shape the adaptation: only the first
~140 characters show on mobile before "see more", and a link costs reach in the body and gets
hidden in a comment.

**Recipe**: do not paste the post. Extract the single most surprising insight and write a
native post that stands alone without the click: strongest number or claim in line 1, a turn
in lines 3–6, short lines, one question people can answer in a word. Long-form alternatives
that keep readers on the platform: a native Article, or a document/PDF carousel for
list-shaped content.

## Substack

Email-first: the subscriber relationship is the asset; on-platform SEO is weak. As the
**canonical home**, the post is the post — write it whole. As a **syndication target**, reframe
as a personal note to subscribers ("what I built/learned this month"), lighter on raw code,
linking to the canonical for depth. Titles render as email subject lines — the payoff must be
in the first clause.

## dev.to / Hashnode / Medium

| Platform | Canonical mechanism | Tags | Audience |
|---|---|---|---|
| dev.to | `canonical_url` frontmatter (or editor's "republishing" field) | max 4, lowercase, established ones | best zero-follower developer reach |
| Hashnode | draft Settings → SEO → Original URL | 4–6 precise (framework + language + use-case) | developer-first; can double as own-domain home |
| Medium | Import tool / "originally published elsewhere" setting | up to 5 | general; broaden the framing |

dev.to frontmatter shape:

```yaml
---
title: "Post title"
published: true
description: "One-sentence description"
tags: kubernetes, homelab, gitops, devops
canonical_url: "https://home.example/original-post"
cover_image: "https://home.example/img/cover.png"
---
```

**Recipe**: dev.to gets the developer-depth cut (architecture, code, cover image); Hashnode the
tutorial-angled cut; Medium a broadened intro for a mixed audience. Same evidence, different
first screen — never the identical body.

## Reddit

The 9:1 norm survives per-subreddit even where the sitewide rule retired: ≤1 in 10
contributions is your own work; be "a redditor with a website, not a website with a Reddit
account". **Read each subreddit's rules and wiki before posting** — many ban self-promotion
outright. Disclose authorship ("I wrote this"), use the sub's flair, and post a first comment
with context/TL;DR that invites discussion. Don't blast multiple subreddits simultaneously.
Culture varies: r/selfhosted and r/kubernetes welcome substantial first-person write-ups;
r/programming has low self-promo tolerance; r/homelab prefers build/show posts.

## Lobsters

Invite-only; narrowly computing ("will this improve the reader's next program?"). Submitting
your own work requires the **"authored by" checkbox**, correct tags from the fixed taxonomy,
and total self-promo below ~25% of activity. Links must be to human-generated content. New
accounts (<70 days) can't use `show`/`announce`/`ask` tags.

## Publish checklist template

1. Canonical live at home platform; URL final; images render; code blocks tested.
2. Wait for indexing (2–10 days) — use the gap to prepare variants.
3. Syndicate: dev.to (canonical_url set) → Hashnode → Medium, each adapted.
4. Aggregators on a strong weekday morning (US ET): HN (original title), relevant subreddit
   (rules read, flair set, context comment ready), Lobsters (authored-by ticked).
5. LinkedIn native post same week (`linkedin-post` skill decides the link placement).
6. Author available for comments for 24–48 h after each aggregator submission.
7. One post per platform per piece — no reposting the same link to the same venue.
