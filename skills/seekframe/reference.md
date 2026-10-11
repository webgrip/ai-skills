# Seekframe reference

Contents: [Pipeline](#pipeline) · [Scenes](#scenes) · [Brand](#brand) · [Sound](#sound) ·
[Voice](#voice) · [Audiences](#audiences) · [Failure modes](#failure-modes)

`$E` is the skill's `engine/` folder.

## Pipeline

| Step | Command | What happens |
|---|---|---|
| Plan | `kit/kit.js` `planVideo` | Line length = words ÷ 2.45 + gap (0.95 s), or the spoken length from `videos/<id>.timing.js`; snapped to the beat when `bpm` is set; same-`g` lines become one scene |
| Cue sheet | `render.mjs meta` | `window.CUES()`: duration, group, scenes, transitions, planned flags, on-screen sound events, lines |
| Music | `music.py cues.json music.wav` (runtime venv) | Score synthesized in numpy (`audio_lib.py`): styles `drive`, `tech`, `calm` |
| Frames | `render.mjs video` | Workers each open the page, call `seek(t)` per sub-frame and capture through CDP; ffmpeg `tmix` averages sub-frames into motion blur (half-frame shutter); FFV1 segments are concatenated |
| Encode | `make.sh` | x264 CRF 17 master, two-pass 8 Mb/s share copy, AAC, bt709 tags, poster 2.2 s before the end, SRT from the cue sheet |
| Voice | `voice.sh` | `vo.py prep` trims and levels each line and writes the timing → cue sheet → music → `vo.py mix` ducks the music under the voice → `-voice.mp4`, `-voice-share.mp4`, word-timed `-voice.srt` |

`render.mjs` uses Playwright from the runtime cache (`~/.cache/seekframe`, or `SEEKFRAME_RUNTIME`), or `PLAYWRIGHT_MJS`. When the Playwright CDN times out,
it falls back to the newest `chromium_headless_shell-*` in `~/.cache/ms-playwright` (or `REEL_CHROME`).

## Scenes

A scene is `defineScene(name, (root, p, ctx) => update(lt, info), {noTitle, ground, note, sfx})`.
`update` receives local time `lt` and `info` (`beat`, `beats`, `dur`); `sfx(scene)` returns sound
events `{t, k}` in local seconds. Scenes draw with CSS variables (`--ink`, `--mute`, `--acc`,
`--line`, `--card`), so one scene works on the `dark`, `paper` and `red` grounds.

| Scene | Parameters (`p`) | Use for |
|---|---|---|
| `statement` | `items` (lines of big type, `*accent*`), `align: 'center'`, `dim`, `every` | The hook, the thesis, a turn |
| `slam` | `words` (one per beat), `sub`, `size` | One punchline; red ground |
| `steps` | `steps`, `lit` (beat per step) | How it works, in order |
| `tiles` | `items: [{t, s, icon, planned}]`, `cols`, `hl` (indexes lit per beat) | What you get; planned items dashed |
| `compare` | `lanes: [{label, speed, end}]`, `note` | Before and after; always labelled an illustration |
| `endcard` | `name`, `a`, `b`, `url` | The closing line |

On `format: '9:16'` the core exposes `VERTICAL`, `SAFE` (`l r t b`) and `SW` (safe width); `tiles` takes `colsV` (default 1), `steps` runs top to bottom, `slam` stacks its words.

Icons for `tiles`: `doc check person shield clock bolt eye stack chat key`. Transitions rotate
through wipe, rise, page, zoom and flap from `seed`; set `tr` on a line to force one.

A product's own scenes go in `<project>/scenes.js` and use the same helpers (`at`, `h`, `sv`, `css`,
`E`, `P`, `lerp`, `ease`, `spring`, `scramble`, `richWords`). Copy the closest built-in scene, keep
every coordinate derived from `lt`, and check it with `stills` at the start, middle and end.

## Brand

`<project>/brand.css` overrides the `:root` tokens of `kit/kit.css`: `--font-sans`, `--font-mono`,
`--brand-dark`, `--brand-light`, `--brand-accent`, `--brand-accent-on-dark`, `--brand-mute-dark`,
`--brand-mute-light`. Load web fonts there with `@font-face` pointing at files in the project, so
every render uses the same glyphs. Third-party logos belong to their owners; show them only to state
compatibility, unmodified, and credit the trademarks in the description.

## Sound

- The score follows the cut: pads change every two bars, drums stop for planned chapters and for
  scenes with `energy: 'drop'`, a riser lands on the `endcard`.
- Sound events: `word slam flap blip check whoosh chime swell impact tagline drop tick click thunk
  stamp sweep typing msg error fail`.
- Music ducks 62 % under the voice with a 0.3 s release. The final mix is measured to −16 LUFS.

## Voice

`eleven.py` drives ElevenLabs one subtitle line at a time; run `eleven.py --help` for every command.

1. Render the music-only cut first; its `out/<group>/<id>.srt` is the line list.
2. `voice/voices.json`: one voice id per output group, per-video overrides, `languages` per video
   (default `en`), fixed voice settings (changing them changes every cache key).
3. Tiers: 0 the shortest opening hook per voice (the first test), 1 the other hooks, 2 the closing
   lines, 3 the rest. Let the owner listen after tier 0; voices that sounded right in a preview
   often sound wrong on the real lines.
4. `plan` is free. `gen` is a dry run until `--go`, refuses above `--max-credits` (default 300) and
   above the credits left. Lines are cached, so a line is never paid twice.
5. `place` copies complete videos to `voice/<id>-NN.mp3` with character timing; `voice.sh` renders.

Model and plan facts that change the plan:

| Fact | Consequence |
|---|---|
| Models differ in price (×0.5 or ×1 per character) and language | `--model cheapest` picks the cheapest model that speaks every selected line's language |
| Free plans use only ElevenLabs' own voices through the API; library voices answer 402 | `gen` skips library-voice lines on a free plan and says so |
| Free-plan audio is non-commercial and needs attribution | Each line records its plan; on a paid plan `gen` makes free lines again and keeps the old copies in `voice/lines/free-plan/` |

Keep the API key in a secrets manager and export it as `ELEVENLABS_API_KEY`, or cache it in the
OS keyring under `ELEVENLABS_KEYRING`. Scope it to text to speech and reading voices, models and
the subscription, with a credit limit.

## Audiences

- **Leadership**: questions before claims (how do we still matter in five years, what do we offer,
  what makes us different), built on the leader's own stated vision; keep that source private.
- **Clients**: one video per client type (fast founder, careful institution, agile team, enterprise
  product owner); their problem first, the product second.
- **Developers**: the path they lived (copy-paste, one agent, ten worktrees on a hot laptop, then
  the better place), review and comprehension as the real bottleneck; dry, a little wry.
- **Business roles**: each role's own question (finance: unplanned spend; compliance: approved tools
  and normal review; sales: what can we actually promise).
- **Family**: building blocks, no jargon.
- **Tongue-in-cheek**: confronting beats cute; a sentimental "letter from your laptop" reads as cringe.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| A batch renders only its first video | ffmpeg read the loop's stdin | `-nostdin`; feed batches from a queue file |
| The soundtrack step never finishes | A float loop over bars never reached its end | Step by integer index |
| Clipping above 0 dBFS | Waveshaper peaks | Look-ahead limiter before loudness normalisation |
| An underline lands in the wrong place | Measured under a page-turn transform | `offsetLeft` chain |
| Voice lines split in the wrong places | Cutting a whole take at its longest pauses | Per-line generation, or dynamic programming on each line's word share |
| Thumbnail or headline text overflows | Fitted before the web font loaded | Fit after `document.fonts.load` |
| Browser missing after an unrelated upgrade | Shared Playwright moved versions | The engine's own runtime cache, newest cached headless shell |
