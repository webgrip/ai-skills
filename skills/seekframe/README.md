# seekframe

Showreel-quality motion-graphics explainer videos made from code, one cut per audience, with the
[seekframe app](https://forgejo.webgrip.dev/webgrip/seekframe).

The skill teaches an agent to drive the app: find or build the `seekframe` binary, keep a project
as TOML (shared claims with status and proof, hooks, closes, one recipe or storyboard per
audience), check and time it, read a contact sheet before rendering, wait for the owner to
approve the words, render a draft first, generate ElevenLabs voice-over only after a dry run and
the owner's OK on the cost, and publish unlisted after a dry run. Projects of the old script
engine (`videos.mjs`, `parts.mjs`) move into the app with `seekframe import`.

Built while making a family of audience videos for a developer tool: leadership, clients,
developers, business roles, family and tongue-in-cheek pieces from one set of facts. The gotchas
are the failures that cost real render time and voice credits.

## Try it

```sh
seekframe new /tmp/acme
seekframe -C /tmp/acme check
seekframe -C /tmp/acme plan demo-reviewers
seekframe -C /tmp/acme sheet demo-reviewers
seekframe -C /tmp/acme render demo-reviewers --draft --subframes 2
```

Needs the `seekframe` binary (build it from the app repository with `mise run build`), Chromium
(a Playwright headless shell) and ffmpeg; `seekframe import` also needs Node.js 20+. `test.sh`
checks the skill's commands against the binary when one is on `PATH`, without network or credits.

Pairs with `youtube-upload-kit` (thumbnails, titles, upload) and `devtool-social` (where and how
to post).
