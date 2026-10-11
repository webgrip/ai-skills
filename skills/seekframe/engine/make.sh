#!/bin/bash
set -euo pipefail
E="$(cd "$(dirname "$0")" && pwd)"
R="${SEEKFRAME_RUNTIME:-${XDG_CACHE_HOME:-$HOME/.cache}/seekframe}"
[ -x "$R/venv/bin/python" ] || { echo "run setup.sh first" >&2; exit 1; }
[ $# -ge 2 ] || { echo "make.sh <project> <video-id> [subframes=8] [workers=16]" >&2; exit 2; }
P="$(cd "$1" && pwd)"; ID=$2; SUB=${3:-8}; WK=${4:-16}
W="$P/.work/$ID"; mkdir -p "$W"
node "$E/render.mjs" meta "$P" "$ID" "$W/cues.json"
GRP=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['group'])" "$W/cues.json")
DUR=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['dur'])" "$W/cues.json")
DEST="$P/out/$GRP"; mkdir -p "$DEST"
for f in "$DEST/$ID.mp4" "$DEST/$ID-share.mp4"; do
  [ -e "$f" ] && { echo "$f exists; move it aside (keep every version) before rendering again" >&2; exit 1; }
done
"$R/venv/bin/python" -I "$E/music.py" "$W/cues.json" "$W/music.wav"
node "$E/render.mjs" video "$P" "$ID" "$W/reel.mkv" "$WK" "$SUB" 0 "$DUR"
FF="$R/ffmpeg"; VF="scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
COLOR=(-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv)
"$FF" -nostdin -loglevel error -y -i "$W/reel.mkv" -i "$W/music.wav" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 17 -profile:v high -vf "$VF" "${COLOR[@]}" -r 60 -g 120 -c:a aac -b:a 256k -movflags +faststart -shortest "$DEST/$ID.mp4"
"$FF" -nostdin -loglevel error -y -i "$W/reel.mkv" -map 0:v -c:v libx264 -preset slow -b:v 8M -maxrate 11M -bufsize 16M -profile:v high -vf "$VF" "${COLOR[@]}" -r 60 -g 120 -pass 1 -passlogfile "$W/x264" -an -f mp4 /dev/null
"$FF" -nostdin -loglevel error -y -i "$W/reel.mkv" -i "$W/music.wav" -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 8M -maxrate 11M -bufsize 16M -profile:v high -vf "$VF" "${COLOR[@]}" -r 60 -g 120 -pass 2 -passlogfile "$W/x264" -c:a aac -b:a 192k -movflags +faststart -shortest "$DEST/$ID-share.mp4"
"$FF" -nostdin -loglevel error -y -sseof -2.2 -i "$W/reel.mkv" -frames:v 1 "$DEST/$ID-poster.png"
python3 "$E/srt.py" "$W/cues.json" "$DEST/$ID.srt"
rm -f "$W"/x264* "$W/reel.mkv"
ls -la "$DEST/$ID"*
