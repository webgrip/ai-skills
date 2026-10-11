# seekframe

Showreel-quality motion-graphics explainer videos made from code, one cut per audience.

A video is a list of spoken lines in `videos.mjs`. The engine turns it into a page whose every frame
is a pure function of time, renders that page in headless Chromium with sub-frame motion blur,
scores music from the cut, and encodes a master, a share copy, a poster and subtitles. Voice-over
comes from ElevenLabs one subtitle line at a time, dry-run first and capped, and re-times the scenes
to the real voice in a separate `-voice` cut.

Built while making a family of audience videos for a developer tool: leadership, clients,
developers, business roles, family and tongue-in-cheek pieces from one script source. The gotchas
in the skill are the failures that cost real render time.

## Try it

```sh
E=skills/seekframe/engine
bash $E/setup.sh
cp -r skills/seekframe/example /tmp/acme
node $E/gen.mjs /tmp/acme
node $E/render.mjs sheet /tmp/acme demo-reviewers /tmp/acme/sheet.png
bash $E/make.sh /tmp/acme demo-reviewers 2 8
```

Needs Node.js 20+, Python 3.10+ and network access for the first setup (numpy, imageio-ffmpeg,
Playwright). `test.sh` checks the engine and the voice tool against a local mock of the ElevenLabs
API, without a key or credits.

Pairs with `youtube-upload-kit` (thumbnails, titles, upload) and `devtool-social` (where and how
to post).
