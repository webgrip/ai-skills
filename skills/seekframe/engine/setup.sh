#!/bin/bash
set -euo pipefail
R="${SEEKFRAME_RUNTIME:-${XDG_CACHE_HOME:-$HOME/.cache}/seekframe}"
command -v node >/dev/null || { echo "needs Node.js 20 or newer" >&2; exit 1; }
command -v python3 >/dev/null || { echo "needs Python 3.10 or newer" >&2; exit 1; }
mkdir -p "$R"
[ -x "$R/venv/bin/python" ] || python3 -m venv "$R/venv"
"$R/venv/bin/python" -m pip install -q --disable-pip-version-check numpy imageio-ffmpeg
ln -sf "$("$R/venv/bin/python" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')" "$R/ffmpeg"
[ -f "$R/package.json" ] || echo '{"private":true,"type":"module"}' > "$R/package.json"
[ -d "$R/node_modules/playwright" ] || npm i -s --prefix "$R" --no-audit --no-fund playwright@1.63.0
node "$R/node_modules/playwright/cli.js" install chromium-headless-shell \
  || echo "headless shell download failed; render.mjs falls back to the newest one in ~/.cache/ms-playwright, or set REEL_CHROME" >&2
"$R/ffmpeg" -hide_banner -version | head -1
