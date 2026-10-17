# Seekframe reference

Contents: [Project](#project) · [Commands](#commands) · [Scenes](#scenes) · [Brand](#brand) ·
[Sound](#sound) · [Voice](#voice) · [Publish](#publish) · [Move an old project](#move-an-old-project) ·
[Audiences](#audiences) · [Failure modes](#failure-modes)

The app's own docs (`docs/` in `webgrip/seekframe`) are the source of truth; `seekframe <command>
--help` lists every flag.

## Project

| File | Holds |
|---|---|
| `seekframe.toml` | `name`, `product`, `site`, optional `[pacing]` (`words_per_second` 2.45, `gap` 0.95, ...) and `[voice]` |
| `parts.toml` | `[claims.<id>]` `status` (live or planned), `proof`, `sc`, `p`, `h`, `say` per register; `[[hooks.<id>.lines]]`; `[[closes.<id>.lines]]` |
| `videos/<id>.toml` | `group` (output folder, required), `name`, `kicker`, `hud`, `note`, `format` (`16:9` or `9:16`), `music` (`drive`, `tech`, `calm`), `bpm`, `seed`, `voice` (delivery tag), then `lines` or a `recipe` (never both), `youtube` |
| `brand.css`, `scenes.js`, `fonts/`, `assets/` | the look; the scene page loads only these |
| `out/<group>/` | renders, sheets, stills, upload sheets; `older/` keeps every earlier version |
| `voice/` | line audio, `cache/`, `ledger.jsonl` |

A line: `vo` (spoken), `h` (headline, `*word*` takes the accent), `sc` (scene), `g` (consecutive
lines with the same `g` share one scene), `p` (scene parameters), `planned`, `beats`, `gap`, `min`,
`tr` (force a transition). A recipe: `register` (`dev`, `biz`, `family`, ...), `hook`, `claims`
in speaking order, `close`. A Short is one hook, one claim and the close; a long video a hook, two
or three claims and the close. `seekframe claims --write` writes `claims.md`: which video uses
which claim, so one correction fixes every video.

## Commands

| Step | Command |
|---|---|
| New project, or move an old one | `seekframe new <dir>`, `seekframe import <old> <new>` |
| Edit visually | `seekframe studio [--no-open]` |
| Check and time | `seekframe check`, `seekframe plan <id> [--json]` |
| Look | `seekframe sheet <id>`, `seekframe stills <id> 2.5,10` |
| Approve (owner) | `seekframe approve <id> --by "<name>"` |
| Render | `seekframe render <id> [--draft] [--subframes N] [--workers N] [--voice]`, `seekframe thumbs <id>` |
| Package | `seekframe upload-sheet <id> [--check-link]` |
| Voice | `seekframe voice` with `status`, `models`, `voices`, `preview`, `plan`, `gen`, `place`, `import` |
| Publish | `seekframe youtube login`, `youtube status`, `seekframe publish <id> --dry-run`, `metrics <id>`, `verdict <id>` |

A render writes music, frames with sub-frame motion blur, master, share copy, poster, subtitles
and a `.render.json` manifest; full renders add thumbnails and the upload sheet. `--draft` renders
without approved words, names files `<id>-draft*` and marks every frame DRAFT.

## Scenes

Built in: `statement` (`items`, big type), `slam` (`words`, one per beat), `steps` (`steps`),
`tiles` (`items: [{t, s, icon, planned}]`, `cols`, `hl`), `compare` (`lanes: [{label, speed,
end}]`, always an illustration), `endcard` (`name`, `a`, `b`, `url`). Transitions rotate through
wipe, rise, page, zoom and flap from `seed`; the endcard zooms; `tr` forces one.

A product's own scenes go in `scenes.js` as `defineScene(name, (root, p, ctx) => update(lt, info),
{noTitle, ground, note, sfx})`, with the kit's helpers (`at`, `h`, `sv`, `css`, `E`, `P`, `lerp`,
`ease`, `spring`, `scramble`, `richWords`) and `VERTICAL`, `SAFE`, `SW` for 9:16. Copy the closest
built-in scene, derive every coordinate from `lt`, keep text inside the Shorts safe area on 9:16,
and check with `stills` at the start, middle and end. The full contract is
`docs/reference/scene-page.md` in the app.

## Brand

`brand.css` overrides `--font-sans`, `--font-mono`, `--brand-dark`, `--brand-light`,
`--brand-accent`, `--brand-accent-on-dark`, `--brand-mute-dark`, `--brand-mute-light`. Web fonts
load with `@font-face` from `fonts/` (or `assets/`), so every render uses the same glyphs.
Third-party logos belong to their owners; show them only to state compatibility, unmodified, and
credit the trademarks in the description.

## Sound

The score is synthesized from the cut (`drive`, `tech`, `calm`): pads change every two bars,
drums stop for planned chapters, a riser lands on the endcard. Music ducks under the voice; the
mix is measured to -16 LUFS behind a look-ahead limiter, never set by peak.

## Voice

Two ways: a recorded take (`seekframe voice import <id> take.wav`, free, cut into lines at the
pauses) or ElevenLabs per line (credits).

1. `[voice]` in `seekframe.toml`: `voice`, `model` (`cheapest` picks the lowest credit multiplier
   that speaks the language), `language`, `settings`, `seed`, with `[voice.groups.<group>]` and
   `[voice.videos.<id>]` overrides. Settings are part of every cache key: keep them fixed.
2. `voice voices`, `voice preview <id>` (free) to pick; `voice status` for credits.
3. `voice plan` (free) shows tiers: 0 the shortest opening hook per voice (the first test), 1
   other hooks, 2 closing lines, 3 the rest. Generate tier 0 and let the owner listen first;
   voices that sound right in a preview often sound wrong on the real lines.
4. `voice gen --tier 0` is a dry run: quote lines x characters x model multiplier as credits, and
   wait for the owner's stated OK before `--go`. A go refuses above `--max-credits` (default 300)
   and above the credits left; a cached line is never paid twice.
5. `voice place` copies complete videos to `voice/<id>-NN.mp3`; `render <id> --voice --draft`
   writes `<id>-voice.mp4` beside the music-only cut, with word-timed subtitles.

| Fact | Consequence |
|---|---|
| Free plans use only ElevenLabs' own voices through the API | library voices answer 402; `gen` skips them on a free plan and says so |
| Free-plan audio is non-commercial and needs attribution | each line records its plan; on a paid plan `gen` makes free lines again and keeps the old copies |

Keep the API key in a secrets manager or the OS keyring, never in files or chat.

## Publish

`seekframe youtube login --client <file>` with the owner's own Google OAuth client (once a week
while it is in testing). `publish <id> --dry-run` shows exactly what would go up; without
`--dry-run` it uploads unlisted with captions and thumbnail and records it in `published.toml`.
Set `youtube.test` thresholds before the upload; `metrics` and `verdict` judge against them.
Never run a real upload, `--public`, or `metrics` with credentials without the owner's go.

## Move an old project

The old script engine kept videos in `videos.mjs` and parts in `parts.mjs`. `seekframe import
<old> <new>` evaluates them with Node.js and writes a new project; the old folder is not touched
and the target must be new or empty.

- It refuses and lists every field with no place in the app. `--extras-into-p` moves unknown line
  keys into the line's `p` (then change `scenes.js` to read `line.p.<key>`); `--flatten` turns
  recipe videos whose claims time single lines (`{vo, min, gap}`) into storyboards; `--only
  a,b` leaves the rest out. A `4:5` format has no place: change or leave out those videos.
- Voice files are copied (never moved): placed lines, takes, the ledger, and the old line cache
  re-keyed into `voice/cache/` so nothing is paid twice; the rest stays in `voice/imported/`.
- Renders (`out/`) stay where they are. Approvals never carry over.
- Then `check`, `plan <id>` for every video (timings match the old planner), `sheet <id>`, and
  ask the owner to approve the words again.

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
| `check` says unknown scene | the scene is not in the kit or `scenes.js` | add it to `scenes.js` with `defineScene`, or use a built-in |
| Text overflows or the font looks generic | the font is outside `fonts/`/`assets/`, or fitted before it loaded | move it, fit after `document.fonts.load` |
| An underline lands in the wrong place | measured under a page-turn transform | `offsetLeft` chain |
| Frames differ between workers, flicker | state outside `seek(t)` | make the scene a pure function of `t` |
| Full render refused | words not approved, or changed since | show the owner the words; `--draft` meanwhile |
| Voice cut drifts or lines split wrongly | a whole take cut at the wrong pauses | per-line generation, or re-record with clear pauses |
| Chromium or ffmpeg not found | the app names every place it searched | install the Playwright headless shell or set `SEEKFRAME_CHROME`/`SEEKFRAME_FFMPEG` |
