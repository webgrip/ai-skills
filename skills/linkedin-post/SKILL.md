---
name: linkedin-post
description: 'Writes and ships LinkedIn posts that actually reach people: the 2026 ranking mechanics (link penalty, comments over likes, dwell time, personal profile over company page), the plain-text formatting the editor will not destroy, accessible emphasis, and where to publish. Use when drafting or editing a LinkedIn post, announcement, launch, call for speakers or hiring post; when asked why a post got no reach; when choosing between a personal profile and a company page, or whether to repost; when a pasted post lost its blank lines or shows underlined links; and for the posting schedule. Dutch: LinkedIn-post schrijven, aankondiging, bereik, waarom krijgt mijn post geen reacties, op mijn profiel of op de bedrijfspagina.'
---

# LinkedIn posts that reach people

Three things decide whether a post works, in this order: **where you publish it**, **what you
ask for**, and **whether the editor destroys your formatting on paste**. The words matter less
than any of those.

Before writing a word, load the `humanize` skill and keep it loaded. A post that reads as
generated loses readers in its first lines, and time spent reading (dwell time) is a signal
LinkedIn's feed ranking explicitly models. Scan your draft before handing it over.

**How firm the numbers are.** LinkedIn publishes no weights. It confirms the direction of four
things below: dwell time counts, conversation counts for more than likes, hashtags are no reach
lever, and spammy comments get suppressed. Every figure beyond that comes from consultant and
tool-vendor datasets with unpublished methods, and the same report's figures move between
editions. Use them for direction and rough size, never as targets, and never state one as
settled fact.

## 1. Where

**The original goes on a personal profile. Always.**

Personal profiles reach several times more people than a company page with the same content;
vendor data puts it around 3 times the impressions and 5 times the engagement. A personal post
seeds to first-degree connections automatically, which produces the early engagement the feed
looks for. A page post reaches only a small share of its followers, so a young page with eighty
followers has almost nobody to start from.

**Never repost a page post to a profile.** An instant repost does little for the original and
nothing for the reposter, and even a repost with your own thoughts trails a fresh post. Write a
fresh post.

What the page is for: a followable address for next time, and a destination the site and event
listings can link to. Publish the same content there as its own post, reworded slightly, and
comment on it from the personal profile to get its test sample moving. Mention the page from the
personal post so people can follow it without spending your reach on a page post.

## 2. What you ask for

**Comments count for more than likes.** LinkedIn says so without giving a weight; the largest
disclosed dataset puts a comment at about twice a like. So the call to action should be
something to type, not something to click.

**Ask for one thing.** Stacking four asks reads as begging and splits the response. State the
rest; ask for one.

**Lower the cost of answering to one word.** "Who do you know who should be up there?" plus "I
will approach them myself" beats "submit your talk", because naming someone costs nothing and
tagging is a comment.

**Expect noise.** Many of the comments in the first minutes are AI-written, and LinkedIn says it
limits the reach of spammy ones. Answer the real ones with real sentences; short reciprocal
comments from the same handful of people count for less.

## 3. Links

One external link in the body costs reach: roughly 15 to 35 percent across the large datasets
(16 percent in van der Blom's July 2026 update, 26.5 percent in Ordinal's 900,000 posts), and in
Ordinal's data the cost falls mostly on company pages. LinkedIn denies a deliberate penalty as
long as the post stands alone without the link, which is the useful instruction either way.
**The "put the link in the first comment" workaround no longer escapes it**: comment links now
get hidden much of the time. Both placements cost you.

So decide on the goal, not the tactic. If the post exists to drive sign-ups or applications,
keep the link in the body and accept the cost; a call to action with no path is worse than the
haircut. If the post exists to start conversations, leave every URL out and let people ask.

**A bare domain counts as a link.** Writing `example.dev` three times gets you three underlined
links and three penalties. Name it once, and make that one an `@`-mention of the company page if
there is one — a mention is not a link.

## 4. Formatting the editor cannot destroy

**There is no bold.** The Unicode workaround substitutes mathematical alphanumeric characters.
JAWS spells them out one at a time ("mathematical bold small a"); NVDA, VoiceOver and Narrator
skip them, so a bolded "do not" silently drops out of the sentence. Do not use it. If someone
insists, tell them what it does to a screen reader first.

**The editor eats blank lines on paste.** Single newlines survive; consecutive ones collapse, and
a carefully spaced post arrives as a wall. Do not design around blank lines. Use a visible
separator line between sections instead — `· · ·` works and stays put — and keep every paragraph
to three lines or fewer.

**Emphasis that works and stays accessible:** an emoji plus a short ALL-CAPS label on its own
line, used two to four times. More than four turns a message into a form. Emoji also serve as the
only list markers available; do not add a dash or bullet in front of them.

**The fold.** Roughly the first 140 characters show on mobile, 210 on desktop, before "see more".
The first line carries the whole post. Do not move it.

**Hashtags:** one to three, at the end, for categorisation. LinkedIn has said since 2025 that
they are not a reach lever.

**Length:** about 800 to 1200 characters, where the datasets' sweet spots cluster. A launch or
announcement post may run to about 2000 because the people who care read it all and dwell time
rewards that. A routine post that long is just long.

## 5. When

Tuesday, Wednesday or Thursday, in working hours; Monday and Friday do worse. Studies disagree
on the hour (early morning in some, late morning to afternoon in others), so try both and keep
what your audience answers.

**Block the first hour.** The first hour or so decides most of how far the post travels, and you
need to be there answering comments in full sentences.

**One language per day.** For a Dutch-speaking audience, a Dutch post reaches a tighter,
higher-converting group than an English one in the same niche. Publish Dutch first and English
three or four days later; both on the same day means competing with yourself in one feed.

**Two to five posts a week.** Posting daily lowers average reach per post.

## Checklist before it goes out

- [ ] Scanned with `humanize`, no tells outside deliberate emoji
- [ ] Publishing on a personal profile, not as a repost
- [ ] One ask, and it can be answered in one word
- [ ] Link placement is a decision, not a habit; the domain appears once
- [ ] No Unicode pseudo-bold; emphasis is emoji plus a short caps label
- [ ] `· · ·` between sections, no paragraph over three lines
- [ ] First line intact and load-bearing
- [ ] One to three hashtags at the end
- [ ] Facts checked against the source of truth, not against an earlier draft

## Sources

**LinkedIn's own statements:** dwell time in
[feed ranking](https://www.linkedin.com/blog/engineering/feed/understanding-feed-dwell-time);
conversation over likes and spam-comment limits
([PR Daily](https://www.prdaily.com/what-works-and-doesnt-on-linkedin-according-to-guardians-of-the-feed/));
[hashtags](https://www.socialmediatoday.com/news/linkedin-algorithm-update-older-posts-ai-tools-hashtag-use/753512/);
[links](https://www.linkedin.com/feed/update/urn:li:activity:7370869955623542785/).

**Practitioner datasets** (methods unpublished): Richard van der Blom's Algorithm Insights, a paid
report over 1.3 million posts ([interview](https://podcast.creatorscience.com/richard-van-der-blom-2/),
[July 2026 link update](https://www.linkedin.com/pulse/67-link-penalty-just-changed-most-people-missed-richard-van-der-blom-9iese));
[Ordinal's link study](https://www.tryordinal.com/blog/linkedin-link-penalty-study);
[AuthoredUp](https://authoredup.com/blog/linkedin-algorithm);
[Sprout Social on timing](https://sproutsocial.com/insights/best-times-to-post-on-linkedin/).

**Screen readers:** [Adrian Roselli's recorded tests](https://adrianroselli.com/2025/03/dont-use-fake-bold-or-italic-in-social-media.html).

The platform changes yearly and the datasets disagree with each other. Re-check the link
penalty, the first-comment rule and the profile-versus-page ratio before leaning on them a year
from now.
