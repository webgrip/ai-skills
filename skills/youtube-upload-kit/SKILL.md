---
name: youtube-upload-kit
description: 'Packages a video for YouTube and YouTube Shorts so it gets clicked and watched: thumbnails rendered from the video''s own frames in the brand''s fonts and colours, three variants for Test & Compare, titles, descriptions, chapters, hashtags, end screens, the Short-to-long related-video link, captions, AI-voice and synthetic-content disclosure, unlisted drafts for feedback, and which Studio numbers to read afterwards. Use when uploading or publishing a video to YouTube, making a thumbnail or a Shorts cover, writing a YouTube title or description, setting up a thumbnail A/B test, choosing unlisted or private to collect feedback, filling in the upload form (audience, altered content, subtitles), or asking why a video gets impressions but no clicks or views. Dutch: video uploaden naar YouTube, thumbnail maken, titel en beschrijving, A/B-test.'
---

# YouTube upload kit

Thumbnail and title make one promise; the first seconds keep it. Every rule here carries an
evidence label in [research.md](research.md); treat VENDOR and GAP items as starting points to test.

## Thumbnail

Tool: `node <this skill's base directory>/scripts/thumb.mjs <config.json> <out.jpg>` (template
`scripts/thumb.html`; the first run prints the one-time Playwright install).

```json
{"brand": "brand.css", "product": "Acme", "kicker": "For reviewers",
 "bg": "still-art.png", "bgZoom": 1.05, "bgPos": "690px 55%",
 "variants": [{"words": "Ten PRs.\n*One reviewer.*", "badge": "who read it?"}, {"words": "Who read\n*the diff?*"}]}
```

1. **Background**: a frame from the video, cropped below that scene's own headline
   (`ffmpeg -i still.png -vf crop=1920:760:0:270 still-art.png`), so the old headline never shows
   through the new words. Place the art on the right; the words sit on a solid left.
2. **Words**: two to five, on two short lines, one accent phrase. They add to the title and never
   repeat it.
3. One focal point; nothing important in the bottom-right corner (the duration badge).
4. Check it small: `ffmpeg -i thumb-a.jpg -vf scale=168:94 small.png` and read it.
5. Long video: 1280×720 rendered at 2×, JPG, under 2 MB. Short cover: `"ratio": "9:16"`; keep text
   inside the central area, clear of the bottom 400 px and the right 200 px.
6. **Variants** differ in promise, not in colour. Three real alternatives or none.

## Title and description

- Title: the concrete outcome in the first 60 characters, product name last. Clear beats clever
  for technical buyers; a click the video does not repay loses Test & Compare, which ranks by watch
  time share, not clicks.
- Description, in this order: two lines above the fold (the problem, what the video shows), the
  link, chapters (`00:00` first, at least three, each at least 10 s), two or three hashtags, then
  credits, trademark notices and disclosures.
- AI voice made on a free ElevenLabs plan is non-commercial: keep that video unlisted, credit
  "Voice: ElevenLabs (elevenlabs.io)" in the title or description, and replace the audio with a
  paid-plan generation before publishing publicly.
- Third-party logos on screen: add "<Brand> is a trademark of its owner." for each.

## Upload form

| Field | Choice |
|---|---|
| Visibility for feedback | **Unlisted**: link only, comments on, no Google account needed. Private only for sensitive drafts (no comments) |
| Audience | Not made for kids; "made for kids" disables comments, end screens and Test & Compare |
| Altered or synthetic content | No for animation with a generic AI narrator; Yes when a real person appears to say or do something they did not |
| Subtitles | Upload the word-timed `.srt`; set the video language |
| End screen | Last 5 to 20 s: the related video or playlist plus subscribe; leave that space free in the edit |
| Short to long | Studio › Content › the Short › Related video |
| Test & Compare | Desktop Studio, up to three thumbnails and/or titles; not for Shorts or private videos; editing either stops the test |

## Afterwards

Wait for real impressions (days, not hours). Compare impressions click-through against the
channel's own median, not an internet benchmark. Read the retention curve: a cliff in the first
30 s means the thumbnail promised something else; a dip mid-video marks the part to cut next time.
For Shorts read "stayed to watch" against your own earlier Shorts. A Test & Compare result of
"performed the same" means ship the clearer variant.

Short-form planning, hooks and where to post: the `devtool-social` skill. The video itself: the
`seekframe` skill.
