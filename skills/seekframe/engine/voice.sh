#!/bin/bash
set -euo pipefail
E="$(cd "$(dirname "$0")" && pwd)"
R="${SEEKFRAME_RUNTIME:-${XDG_CACHE_HOME:-$HOME/.cache}/seekframe}"
[ -x "$R/venv/bin/python" ] || { echo "run setup.sh first" >&2; exit 1; }
[ $# -ge 2 ] || { echo "voice.sh <project> <video-id> [subframes=8] [workers=16]: needs <project>/voice/<id>-NN.mp3 (eleven.py place) or one take <project>/voice/<id>.mp3" >&2; exit 2; }
P="$(cd "$1" && pwd)"; ID=$2; SUB=${3:-8}; WK=${4:-16}
VDIR="$P/voice"; W="$P/.work/$ID"; mkdir -p "$W"
TAKE=$(ls "$VDIR/$ID".mp3 "$VDIR/$ID".wav 2>/dev/null | head -1 || true); TAKE=${TAKE:-$VDIR/$ID.mp3}
read -r N WORDS < <(node "$E/lines.mjs" "$P/videos/$ID.js")
"$R/venv/bin/python" -I "$E/vo.py" prep "$TAKE" "$N" "$W/lines" "$P/videos/$ID.timing.js" "$WORDS"
trap 'mv -f "$P/videos/$ID.timing.js" "$W/timing-voice.js" 2>/dev/null || true' EXIT
node "$E/render.mjs" meta "$P" "$ID" "$W/cues-voice.json"
GRP=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['group'])" "$W/cues-voice.json")
DUR=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['dur'])" "$W/cues-voice.json")
DEST="$P/out/$GRP"; mkdir -p "$DEST"
[ -e "$DEST/$ID-voice.mp4" ] && { echo "$DEST/$ID-voice.mp4 exists; move it aside (keep every version) first" >&2; exit 1; }
"$R/venv/bin/python" -I "$E/music.py" "$W/cues-voice.json" "$W/music-voice.wav"
"$R/venv/bin/python" -I "$E/vo.py" mix "$W/cues-voice.json" "$W/lines" "$W/music-voice.wav" "$W/final-voice.wav"
node "$E/render.mjs" video "$P" "$ID" "$W/reel-voice.mkv" "$WK" "$SUB" 0 "$DUR"
FF="$R/ffmpeg"; VF="scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
COLOR=(-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv)
"$FF" -nostdin -loglevel error -y -i "$W/reel-voice.mkv" -i "$W/final-voice.wav" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 17 -profile:v high -vf "$VF" "${COLOR[@]}" -r 60 -g 120 -c:a aac -b:a 256k -movflags +faststart -shortest "$DEST/$ID-voice.mp4"
"$FF" -nostdin -loglevel error -y -i "$W/reel-voice.mkv" -map 0:v -c:v libx264 -preset slow -b:v 8M -maxrate 11M -bufsize 16M -profile:v high -vf "$VF" "${COLOR[@]}" -r 60 -g 120 -pass 1 -passlogfile "$W/x264v" -an -f mp4 /dev/null
"$FF" -nostdin -loglevel error -y -i "$W/reel-voice.mkv" -i "$W/final-voice.wav" -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 8M -maxrate 11M -bufsize 16M -profile:v high -vf "$VF" "${COLOR[@]}" -r 60 -g 120 -pass 2 -passlogfile "$W/x264v" -c:a aac -b:a 192k -movflags +faststart -shortest "$DEST/$ID-voice-share.mp4"
mv -f "$P/videos/$ID.timing.js" "$W/timing-voice.js"
if [ -f "$VDIR/$ID-01.json" ]; then
  "$R/venv/bin/python" -I "$E/eleven.py" --project "$P" srt "$ID" --cues "$W/cues-voice.json" --timing "$W/timing-voice.js" --out "$DEST/$ID-voice.srt"
else
  python3 "$E/srt.py" "$W/cues-voice.json" "$DEST/$ID-voice.srt"
fi
rm -f "$W"/x264v* "$W/reel-voice.mkv"
node "$E/upload.mjs" "$P" "$ID" "$W/cues-voice.json" "$DEST/$ID-voice.mp4" "$DEST/$ID-voice.srt" || echo "upload sheet failed; the video itself is fine" >&2
ls -la "$DEST/$ID-voice"*
