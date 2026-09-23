#!/bin/sh
SOURCE_PATHS="${SOURCE_PATHS:-app tests}"
GREEN_MARKER="${GREEN_MARKER:-.claude/.tests-green}"
input=$(cat)
[ "$(printf '%s' "$input" | jq -r '.stop_hook_active')" = "true" ] && exit 0
git diff --quiet HEAD -- ${SOURCE_PATHS} && exit 0
newest=$(git diff --name-only HEAD -- ${SOURCE_PATHS} | xargs ls -t 2>/dev/null | head -1)
[ -f "${GREEN_MARKER}" ] && [ -n "$newest" ] && [ "${GREEN_MARKER}" -nt "$newest" ] && exit 0
jq -n '{hookSpecificOutput: {hookEventName: "Stop", additionalContext: "Source changed since the last green test run: run the narrowest affected tests before finishing, then touch the green marker."}}'
