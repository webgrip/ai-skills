---
name: seekframe
description: 'Makes showreel-quality motion-graphics explainer videos from code: one script source per product, a deterministic seek(t) page rendered frame by frame in headless Chromium with motion blur, a score synthesized from the cut, per-line ElevenLabs voice-over that re-times the scenes, subtitles, posters and share copies, one cut per audience. Use when asked to make, script, storyboard, render, re-render or voice a product video, explainer, promo, showreel or motion-graphics animation; to make versions for different audiences (leadership, clients, developers, business roles, family, tongue-in-cheek); to add or swap a voice-over or generate it carefully with ElevenLabs; or when a render hangs, renders only some videos, clips, drifts out of sync or a scene overlaps. Dutch: maak een video, explainer, motion graphics, voice-over toevoegen.'
---

# Motion videos rendered from code

Engine: `E=<this skill's base directory>/engine`. A **project** is a folder you own:
`videos.mjs` (the script source), `brand.css` (colours and fonts), optional `scenes.js` (your own
scenes), and the generated `videos/`, `out/`, `voice/`, `.work/`. Start a project by copying
[example/](example/). Run `bash $E/setup.sh` once (Python venv with numpy and imageio-ffmpeg,
Playwright with its headless shell, all in `~/.cache/seekframe`; override with `SEEKFRAME_RUNTIME`).

## Decide first

| Ask | Do |
|---|---|
| New video or audience | Write the script (below) and get the owner's OK on the words before rendering anything |
| "Too fast", "unclear" | Fewer words per line, one idea per scene, a longer `gap`; never squeeze more into a scene |
| A scene looks wrong | `render.mjs stills` at three times inside it, fix, check stills again, then render |
| Add a voice | Per subtitle line with `eleven.py`, tiered and dry-run first ([reference.md](reference.md#voice)) |
| Thumbnail, title, upload | Fill the video's `youtube` block; every render writes the upload sheet (below). Rules: the `youtube-upload-kit` skill |
| Vertical Short | The kit renders 1920×1080 only; a 9:16 layout per scene is not built. Say so, then plan it as its own task |

## Script

Each video in `videos.mjs`: `{id, group, name, voice, music, bpm?, seed, product, site, kicker, hud,
note, lines: [{vo, h, sc, g, p, planned, beats}]}`. `vo` is spoken, `h` is the on-screen headline
(`*word*` takes the accent colour), `sc` the scene, consecutive lines with the same `g` share one
scene, `group` is the output folder. Scenes and their parameters: [reference.md](reference.md#scenes).

1. Open on what this reader fears or wants right now, then how it works, then proof, then one
   closing line. One idea per line, 6 to 14 words; the cut follows the words at 2.45 words a second.
2. **Truth on screen.** Set `planned: true` on lines about things not built yet (dashed frame,
   "planned, not built yet"); comparisons keep "Illustration · not a measurement"; recorded demos say
   they are recorded; no invented numbers. Check every claim against the product's docs.
3. A song, ad or meme the owner names is a reference for tone and structure. Write original lines;
   never mirror its words or its structure beat for beat.
4. Optional `youtube: {title, titles, above, link, chapters: [{line, title}], hashtags, tags,
   trademarks, endScreen, thumb: {frame, crop: [y, h], variants}}` packages the video for upload.
5. `node $E/gen.mjs <project>` writes `videos/<id>.js` and `scripts.md` (the voice script).

## Render

```sh
node $E/render.mjs sheet  <project> <id> sheet.png            # one frame per line: read it first
node $E/render.mjs stills <project> <id> out/ 4.0,12.5         # exact frames
bash $E/make.sh  <project> <id> [subframes=8] [workers=16]     # music, frames, master, share copy, poster, SRT
bash $E/voice.sh <project> <id> [subframes] [workers]          # after voice lines exist: <id>-voice.mp4 beside the music-only cut
```

After each render, `upload.mjs` writes `<id>[-voice].upload.json` beside the video, renders
thumbnails into `out/<group>/thumbs/<id>/` once (never over existing ones) and, when the
`youtube-upload-kit` skill is installed next to this one or `YOUTUBE_UPLOAD_KIT` points at it,
`<id>[-voice]-youtube.md`: the Studio form filled in, with what to fix first. Voice renders take the
plan from the voice files, so free-plan audio comes out unlisted with the credit line. Rerun on
its own: `node $E/upload.mjs <project> <id> .work/<id>/cues[-voice].json out/<group>/<id>[-voice].mp4 out/<group>/<id>[-voice].srt`.

Read the sheet for overlap, overflow, label collisions and empty frames before every full render.
A 60 s video at 8 sub-frames on 16 workers takes several minutes; test at 2 sub-frames.

## Gotchas

- **Never overwrite a rendered video.** `make.sh` and `voice.sh` refuse when the output exists; move
  the old file into an `older/` folder, never delete it.
- Everything that moves is a pure function of `t`: no `Date.now`, no `requestAnimationFrame` state,
  no unseeded random. Parallel workers render different frames of the same page.
- Fit text after `document.fonts` has loaded; text measured in the fallback font overflows later.
- Measure positions under 3D transforms with the `offsetLeft` chain, not `getBoundingClientRect`.
- ffmpeg inside a `while read` loop eats the loop's input: always `-nostdin`.
- Loops over musical time step by integer index; `t += step` on floats can fail to terminate.
- Loudness is measured (EBU R128, two passes to −16 LUFS) behind a look-ahead limiter, never set by peak.
- Stop a stuck batch by PID; `pkill -f <name>` also matches the shell running it.
