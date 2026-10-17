---
name: seekframe
description: 'Makes showreel-quality motion-graphics explainer videos from code with the seekframe app: a TOML project of shared claims, hooks and closes composed into one cut per audience, a deterministic seek(t) scene page rendered frame by frame in headless Chromium with motion blur, a synthesized score, per-line ElevenLabs voice-over that re-times the scenes, subtitles, posters, 16:9 and 9:16 Shorts, and a YouTube upload sheet. Use when asked to make, script, storyboard, render, re-render or voice a product video, explainer, promo, showreel or motion-graphics animation; to make versions for different audiences (leadership, clients, developers, business roles, family, tongue-in-cheek); to add or swap a voice-over or generate it carefully with ElevenLabs; to move an old videos.mjs project into the app; or when a render hangs, renders only some videos, clips, drifts out of sync or a scene overlaps. Dutch: maak een video, explainer, motion graphics, voice-over toevoegen.'
---

# Motion videos with the seekframe app

seekframe is a Rust app: the `seekframe` command plus a studio in the browser. A **project** is a
folder of TOML files the owner keeps: `seekframe.toml` (product, pacing, `[voice]`), `parts.toml`
(claims with status and proof, hooks, closes), `videos/<id>.toml` (a storyboard of lines or a
recipe), `brand.css`, optional `scenes.js`, and `fonts/` or `assets/` for what those load.

## Get the binary

1. `command -v seekframe` and `seekframe --version`. Use it when found.
2. Otherwise build it from `webgrip/seekframe` (trunk `development`): `mise run setup`, then
   `mise run build`; the binary is `target/release/seekframe`. Put it on `PATH`.
3. Rendering needs Chromium (a Playwright headless shell in `~/.cache/ms-playwright`, `chromium`
   on `PATH`, or `SEEKFRAME_CHROME`) and ffmpeg (`PATH` or `SEEKFRAME_FFMPEG`). `seekframe import`
   also needs Node.js 20+. Run commands in the project or pass `-C <project>`.

## Decide first

| Ask | Do |
|---|---|
| New video or audience | Facts into `parts.toml`, a recipe or storyboard per audience, then the words gate below |
| An old project with `videos.mjs` | `seekframe import <old> <new>` ([reference.md](reference.md#move-an-old-project)) |
| "Too fast", "unclear" | Fewer words per line, one idea per scene, a longer `gap`; never squeeze more into a scene |
| A scene looks wrong | `seekframe stills <id> <t,...>` at three times inside it, fix, stills again |
| Vertical Short | `format = "9:16"` on the video; one hook, one claim, the close |
| Thumbnail, title, upload copy | `youtube.*` in the video, then `upload-sheet`; the `youtube-upload-kit` skill for the craft |

## Workflow

1. **Start**: `seekframe new <dir>` (an example project), or `seekframe studio` to edit visually
   (`127.0.0.1:7731`; never open the owner's browser unasked, give the URL).
2. **Write** parts and videos ([reference.md](reference.md#project)). One idea per line, 6 to 14
   words; the cut follows the words at 2.45 words a second.
3. **Truth on screen.** Every claim has `status` and `proof`; planned work is `status = "planned"`
   or `planned = true` (dashed frame); comparisons say "Illustration"; no invented numbers, spend
   or results. Check claims against the product's docs. A song or meme the owner names is a
   reference for tone, never words to mirror.
4. **Check** `seekframe check` (errors stop you), **plan** `seekframe plan <id>` (timings).
5. **Look**: `seekframe sheet <id>` (one frame late in every line) and read it for overlap,
   overflow, empty frames and font fallbacks before any render.
6. **Approve**: show the owner the exact words (`plan <id>`) and ask. Only the owner runs or
   OKs `seekframe approve <id> --by "<name>"`; never approve on their behalf. Any change to a
   spoken line, headline, scene or planned flag clears it.
7. **Render**: `seekframe render <id> --draft --subframes 2` first; the full render (approved
   words) after. Outputs land in `out/<group>/`; an earlier render moves to `older/`.
8. **Voice** ([reference.md](reference.md#voice)): `voice plan` (free), `voice gen` as a dry run,
   and `--go` only after the owner states OK to the credit cost you quote. Then `voice place`,
   `render <id> --voice --draft`.
9. **Publish**: `seekframe upload-sheet <id> --check-link`, `seekframe publish <id> --dry-run`.
   A real upload (unlisted) only on the owner's explicit go; later `metrics` and `verdict`.

## Gotchas

- **Never overwrite or delete a rendered video.** The app moves the previous set to
  `out/<group>/older/<timestamp>/`; never clear `older/` or rename over a render by hand.
- Voice files cost money: copy them, never move or delete them; `voice/cache/` keeps every paid line.
- Everything in `scenes.js` that moves is a pure function of `t`: no `Date.now`, no
  `requestAnimationFrame` state, no unseeded random. Parallel workers render different frames.
- Scenes take timing from `window.VIDEO.plan`; never recompute it from the words.
- Fonts: `@font-face` in `brand.css` pointing into `fonts/` or `assets/`; other paths are not
  staged and the sheet silently shows a fallback. Fit text after `document.fonts` has loaded.
- Measure positions under 3D transforms with the `offsetLeft` chain, not `getBoundingClientRect`.
- A full render of a 60 s video at 8 sub-frames takes minutes; test with `--draft --subframes 2`.
- Stop a stuck render by PID; `pkill -f seekframe` also kills the studio.
- Unknown keys in any TOML file are refused: read the error, do not guess field names.
