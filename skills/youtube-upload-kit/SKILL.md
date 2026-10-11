---
name: youtube-upload-kit
description: 'Packages a video for YouTube and YouTube Shorts so it gets clicked and watched: thumbnails rendered from the video''s own frames in the brand''s fonts and colours, three variants for Test & Compare, titles, descriptions, chapters, hashtags, end screens, the Short-to-long related-video link, captions, AI-voice and synthetic-content disclosure, unlisted drafts for feedback, and which Studio numbers to read afterwards. Use when uploading or publishing a video to YouTube, making a thumbnail or a Shorts cover, writing a YouTube title or description, setting up a thumbnail A/B test, choosing unlisted or private to collect feedback, filling in the upload form (audience, altered content, subtitles, tags, license, category, remixing), turning a finished render into an upload sheet, or asking why a video gets impressions but no clicks or views. Dutch: video uploaden naar YouTube, thumbnail maken, titel en beschrijving, A/B-test.'
---

# YouTube upload kit

Thumbnail and title make one promise; the first seconds keep it. Every rule here carries an
evidence label in [research.md](research.md); treat VENDOR and GAP items as starting points to test.

## Upload sheet

Hand the owner one sheet in the order Studio's upload dialog asks (Details with Show more, Video
elements, Checks, Visibility), every field filled, ready to paste. The upload dialog is in the
owner's own browser tab; do not open a second Studio tab on the same video while it is open.

`node <this skill's base directory>/scripts/sheet.mjs <id>.upload.json` writes `<id>-youtube.md`
and prints what breaks a rule: chapters under 10 s or fewer than three, a title over 100 characters
or without the product last, thumbnail words that repeat the title, a link that does not load,
thumbnails over 2 MB, an end screen outside 5 to 20 s, and a free-plan voice set to public. The
`seekframe` skill writes `<id>.upload.json` and runs this after every render; for any other video
write the JSON by hand (`node scripts/sheet.mjs` prints the format). Choose the title after the
thumbnails and run the sheet again until only notes are left.

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
   through the new words. Prefer a scene whose art is a diagram or interface over one that is mostly
   words. Place the art on the right; the words sit on a solid left.
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
- Open the link before putting it in; a domain that is still being set up costs the click.

## Upload form

| Field | Choice |
|---|---|
| Audience | Not made for kids; "made for kids" disables comments, end screens and Test & Compare |
| Paid promotion | Only for a paid relationship with a third party; your own product is not one |
| Altered or synthetic content | No for animation with a generic AI narrator; Yes when a real person appears to say or do something they did not |
| Tags | A few, for misspellings and the product name; they barely affect discovery |
| Automatic chapters | Off when the description carries chapters |
| License | Standard YouTube License; Creative Commons allows commercial reuse, which free-plan audio forbids |
| Shorts remixing | Don't allow video remixing while the audio is free-plan; audio-only remixing can only be blocked with Content Manager |
| Automatic dubbing | Off when a chosen voice is part of the video |
| Category | Science & Technology for a developer tool |
| Subtitles (Video elements) | Upload the word-timed `.srt`; set the video language; play a few seconds in Edit |
| End screen | Last 5 to 20 s: the related video or playlist plus subscribe; leave that space free in the edit, otherwise skip it |
| Cards, quiz | Cards only when a related video exists; no quiz on a promo |
| Visibility for feedback | **Unlisted**: link only, comments on, no Google account needed; sort comments by newest. Private only for sensitive drafts (no comments) |
| Short to long | Studio › Content › the Short › Related video |
| Test & Compare | The A/B Testing buttons next to the title and thumbnail, desktop Studio, up to three of each; not for Shorts or private videos; editing either stops the test |

## Test & Compare programme

Run a test on every long video; Shorts cannot use it. Evidence, sample sizes and the log format:
[testing.md](testing.md).

1. **Upload your best guess first**: an inconclusive test falls back to the first variant.
2. **Test promises, not pixels.** Single cues (colour, font, one word) move click-through by a few
   percent; telling 2 % from 2.2 % takes about 80,000 impressions per variant, 2 % from 3 % about
   3,800. A small channel can only see promise-level differences.
3. **One named hypothesis per test**, written down before upload (outcome vs mechanism, vague vs
   concrete, face vs product screen). Make the title concrete enough to understand and leave one
   question for the video to answer.
4. **Never edit the title or thumbnail mid-test**, and never compare one week's thumbnail with the
   next week's: the traffic mix changes.
5. **Log every arm** (impressions, click-through, watch time share, average view duration, the
   verdict) and pool results per hypothesis across videos; most single tests end inconclusive and
   that is expected.
6. Vendor "X % more clicks" figures and gut feeling are sources of hypotheses, not evidence; people
   pick the A/B winner barely better than chance.

## Afterwards

Wait for real impressions (days, not hours). Compare impressions click-through against the
channel's own median, not an internet benchmark. Read the retention curve: a cliff in the first
30 s means the thumbnail promised something else; a dip mid-video marks the part to cut next time.
For Shorts read "stayed to watch" against your own earlier Shorts. A Test & Compare result of
"performed the same" means ship the clearer variant.

Short-form planning, hooks and where to post: the `devtool-social` skill. The video itself: the
`seekframe` skill.
