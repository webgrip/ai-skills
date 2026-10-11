#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
PIDS=()
trap 'kill "${PIDS[@]}" 2>/dev/null || true; rm -rf "$TMP"' EXIT

for f in engine/kit/*.js engine/render.mjs engine/gen.mjs; do node --check "$f"; done
python3 -m py_compile engine/eleven.py engine/vo.py engine/srt.py engine/music.py engine/audio_lib.py tests/mock_elevenlabs.py
bash -n engine/make.sh engine/voice.sh engine/setup.sh

cp -r example "$TMP/project"
node engine/gen.mjs "$TMP/project" > /dev/null
grep -q '^window.VIDEO = ' "$TMP/project/videos/demo-reviewers.js"
grep -q 'So who actually read it?' "$TMP/project/scripts.md"
printf 'export const VIDEOS = [{ id: "Bad Id", group: "x", lines: [] }];\n' > "$TMP/bad.mjs"
mkdir -p "$TMP/bad" && cp "$TMP/bad.mjs" "$TMP/bad/videos.mjs"
if node engine/gen.mjs "$TMP/bad" 2>/dev/null; then echo "gen.mjs accepted an invalid id" >&2; exit 1; fi

P="$TMP/project"
mkdir -p "$P/out/developers" "$P/voice"
printf '1\n00:00:00,700 --> 00:00:03,000\nAgents open pull requests.\n\n2\n00:00:03,100 --> 00:00:05,000\nWho read it?\n\n3\n00:00:05,100 --> 00:00:07,000\nAcme. You decide.\n' > "$P/out/developers/demo-reviewers.srt"
printf '{"groups":{"developers":"VOICE_EN"},"videos":{},"languages":{},"settings":{"stability":0.6},"seed":1,"output_format":"mp3_44100_128"}\n' > "$P/voice/voices.json"

PORT=$((20000 + RANDOM % 20000))
python3 tests/mock_elevenlabs.py "$PORT" "$TMP/calls.jsonl" paid & PIDS+=($!)
for _ in $(seq 50); do curl -fs -H 'xi-api-key: test-key' "http://127.0.0.1:$PORT/v1/models" > /dev/null 2>&1 && break; sleep 0.1; done
export ELEVENLABS_BASE_URL="http://127.0.0.1:$PORT" ELEVENLABS_API_KEY=test-key SEEKFRAME_PROJECT="$P"
EL="python3 engine/eleven.py"

$EL status | grep -q '9,000 left'
$EL gen --tier 0 --model cheapest | grep -q 'Dry run'
test ! -e "$TMP/calls.jsonl"
$EL gen --tier 0 --model cheapest | grep -q 'Agents open pull requests.'
if $EL gen --video demo-reviewers --model eleven_multilingual_v2 --max-credits 5 --go > /dev/null 2>&1; then echo "spent past --max-credits" >&2; exit 1; fi
test ! -e "$TMP/calls.jsonl"
$EL gen --video demo-reviewers --model eleven_flash_v2 --go > /dev/null
test "$(wc -l < "$TMP/calls.jsonl")" = 3
$EL gen --video demo-reviewers --model eleven_flash_v2 --go | grep -q 'already generated'
test "$(wc -l < "$TMP/calls.jsonl")" = 3
$EL place --model eleven_flash_v2 | grep -q 'Ready for a voice render: demo-reviewers'
test -s "$P/voice/demo-reviewers-03.mp3" && test -s "$P/voice/demo-reviewers-03.json"

printf '{"groups":{"developers":"VOICE_NL"},"videos":{},"languages":{"demo-reviewers":"nl"},"settings":{"stability":0.6},"seed":1,"output_format":"mp3_44100_128"}\n' > "$P/voice/voices.json"
$EL gen --tier 0 --model cheapest | grep -q 'eleven_flash_v2_5'
if $EL gen --tier 0 --model eleven_flash_v2 > /dev/null 2>&1; then echo "picked an English-only model for Dutch" >&2; exit 1; fi

kill "${PIDS[@]}"; PIDS=()
PORT=$((PORT + 1))
python3 tests/mock_elevenlabs.py "$PORT" "$TMP/calls-free.jsonl" free & PIDS+=($!)
for _ in $(seq 50); do curl -fs -H 'xi-api-key: test-key' "http://127.0.0.1:$PORT/v1/models" > /dev/null 2>&1 && break; sleep 0.1; done
export ELEVENLABS_BASE_URL="http://127.0.0.1:$PORT"
$EL gen --tier 0 --model cheapest | grep -q 'free plans can only use'
echo "seekframe: all checks passed"
