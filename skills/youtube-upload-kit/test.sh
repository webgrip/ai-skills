#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
node --check scripts/sheet.mjs
node --check scripts/thumb.mjs

cat > "$TMP/good.upload.json" <<'JSON'
{"id": "demo", "file": "demo.mp4", "subtitles": "demo.srt", "duration": 46, "product": "Acme",
 "voice": {"provider": "ElevenLabs", "plan": "free"}, "thumbWords": ["Ten PRs.\n*One reviewer.*"],
 "youtube": {"title": "Know what an agent changed before you approve it | Acme", "above": ["Problem.", "What it shows."],
             "visibility": "public", "hashtags": ["DevTools"],
             "chapters": [{"t": 0, "title": "One"}, {"t": 15, "title": "Two"}, {"t": 30, "title": "Three"}]}}
JSON
node scripts/sheet.mjs "$TMP/good.upload.json" --offline > "$TMP/good.log"
grep -q 'free plan' "$TMP/good.log"
grep -q '^\*\*Unlisted\*\*' "$TMP/good-youtube.md"
grep -q '^00:15 Two$' "$TMP/good-youtube.md"
grep -q 'Voice: ElevenLabs (elevenlabs.io)' "$TMP/good-youtube.md"
grep -q 'Standard YouTube License' "$TMP/good-youtube.md"
if grep -q 'repeats the title' "$TMP/good.log"; then echo "flagged a thumbnail that adds to the title" >&2; exit 1; fi

cat > "$TMP/bad.upload.json" <<'JSON'
{"id": "bad", "file": "bad.mp4", "duration": 40, "product": "Acme", "thumbWords": ["Ten agents.\n*One laptop.*"],
 "thumbs": ["missing.jpg"], "youtube": {"title": "Get your coding agents off your laptop",
 "chapters": [{"t": 0, "title": "One"}, {"t": 6, "title": "Two"}, {"t": 25, "title": "Three"}], "endScreen": {"from": 38}}}
JSON
node scripts/sheet.mjs "$TMP/bad.upload.json" --offline > "$TMP/bad.log"
grep -q 'repeats the title (agent, laptop)' "$TMP/bad.log"
grep -q 'chapter "One" lasts 6.0 s' "$TMP/bad.log"
grep -q 'product name last' "$TMP/bad.log"
grep -q 'missing.jpg does not exist' "$TMP/bad.log"
grep -q 'end screen window is 2.0 s' "$TMP/bad.log"
grep -q 'no youtube.above' "$TMP/bad.log"
cat > "$TMP/short.upload.json" <<'JSON'
{"id": "s", "file": "s.mp4", "duration": 30, "format": "9:16", "product": "Acme",
 "youtube": {"title": "Who read the diff? | Acme", "titles": ["Other | Acme"], "above": ["a", "b"], "related": "https://youtu.be/x"}}
JSON
node scripts/sheet.mjs "$TMP/short.upload.json" --offline > "$TMP/short.log"
grep -q 'Shorts cannot use Test & Compare' "$TMP/short.log"
grep -q 'set the related video to https://youtu.be/x' "$TMP/short-youtube.md"
if grep -q 'chapters left out' "$TMP/short.log"; then echo "chapter note on a Short" >&2; exit 1; fi
echo "youtube-upload-kit: all checks passed"
