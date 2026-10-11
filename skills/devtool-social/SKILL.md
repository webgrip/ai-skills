---
name: devtool-social
description: 'Plans and writes social content that reaches developers and technical buyers for a founder-led developer tool: which platform gets which job (YouTube Shorts, LinkedIn, Hacker News Show HN, Reddit), short vertical clips cut from longer audience videos, hooks for the first two seconds, a launch order for a set of videos, claims that survive developer scepticism, and what to measure instead of views. Use when asked to go viral, grow reach, plan social media, a content calendar or a launch, write a hook, caption or Short script, decide where to post a video, write a Show HN or Reddit post, repurpose a long video into clips, or ask why posts get no traction with developers. Dutch: viraal gaan, social media plan, contentkalender, bereik, korte video''s.'
---

# Reach developers without sounding like an ad

Developers punish hype and reward a named pain. Stack Overflow's 2025 survey: 46 % distrust AI
output, favourable views fell from 72 % to 60 %, and the top frustration is "almost right, but not
quite". Content that says that out loud earns attention; superlatives lose it. Evidence labels and
sources: [research.md](research.md).

## Pick the job, then the platform

| Job | Format | Where |
|---|---|---|
| Strangers discover you | 20 to 45 s vertical clip, one tension, captions burned in | YouTube Shorts, LinkedIn native video |
| A buyer understands it | The full audience video, 16:9 | YouTube (unlisted links in sales mail), LinkedIn |
| Developers trust it | The thing itself: repo, chart, live demo | Show HN; subreddits whose rules allow it |
| A conversation starts | Founder text post with one honest opinion | LinkedIn personal profile (the `linkedin-post` skill) |

Show HN only takes what people can run or try; a video or a landing page is not a Show HN. Post
from an account with real comment history and stay in the thread for the first hours.

## Cut a Short from a long video

1. One tension per Short, from the long video's strongest line (ten agents on one hot laptop;
   pull requests faster than anyone reads them; who actually read that diff?).
2. Seconds 0 to 2 carry the hook as on-screen words and voice together. No logo, no intro card.
3. Captions burned in, large, inside the central safe area; many viewers start muted.
4. End on the turn, then the product name; set the long video as the Short's related video.
5. Cut two or three openings of the same clip and compare "stayed to watch" against your own
   earlier Shorts. No trustworthy external benchmark exists.

## Launch a set of audience videos

1. Developer pieces first, with the humour pieces as Shorts: developers share what they recognise.
2. Then one client or business-role video per founder post on LinkedIn, each opening with that
   role's own question.
3. Leadership and vision pieces last, sent to people one by one rather than broadcast.
4. Answer every comment on day one. Questions from the roles you target are the success signal.

## Measure

Working means: stayed-to-watch and engaged views rising against your own baseline, comments from
the target roles, clicks through to the long video or the repo. Impressions alone mean nothing.

## Gotchas

- Label every demo as recorded, planned features as planned, comparisons as illustrations. One
  exaggeration a developer catches costs the whole channel.
- Free-plan AI voice audio is non-commercial: never use it in public marketing.
- Other companies' logos only to show compatibility, unmodified, with a trademark line in the caption.
- Asking friends to upvote on Hacker News or Reddit is vote manipulation and gets the post killed.
- X, TikTok, Instagram Reels, Bluesky, Mastodon, dev.to, posting times and cadence have no evidence
  behind them here; present any rule about them as a test to run, not as fact.

Copy that must not read as generated: the `humanize` skill. Thumbnails, titles and the upload form:
the `youtube-upload-kit` skill. The videos themselves: the `seekframe` skill.
