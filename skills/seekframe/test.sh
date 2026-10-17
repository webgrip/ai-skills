#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

fail() { echo "seekframe: $*" >&2; exit 1; }

COMMANDS="new import check plan claims approve upload-sheet sheet stills render thumbs studio voice youtube publish metrics verdict"
for f in SKILL.md reference.md; do
  if grep -nE '\$E/|engine/|gen\.mjs|make\.sh|voice\.sh|eleven\.py|render\.mjs' "$f"; then fail "$f still points at the old script engine"; fi
  for cmd in $(grep -oE '`seekframe [a-z][a-z-]*' "$f" | awk '{print $2}' | sort -u); do
    case " $COMMANDS " in *" $cmd "*) ;; *) fail "$f names an unknown command: seekframe $cmd" ;; esac
  done
done
grep -q -- '--dry-run' SKILL.md || fail "SKILL.md must keep publish dry-run first"
grep -q -- '--go' SKILL.md || fail "SKILL.md must name the voice spending gate"
grep -qi 'never approve on their behalf' SKILL.md || fail "SKILL.md must keep the words gate with the owner"
grep -q 'older/' SKILL.md || fail "SKILL.md must keep every rendered version"

if ! command -v seekframe > /dev/null; then
  echo "seekframe: static checks passed; no seekframe binary, app smoke skipped"
  exit 0
fi

help=$(seekframe --help)
for cmd in $COMMANDS; do
  [ "$cmd" = import ] && continue
  grep -qE "^  $cmd( |$)" <<< "$help" || fail "the binary has no '$cmd' command"
done

P="$TMP/project"
seekframe new "$P" > /dev/null
seekframe -C "$P" check > /dev/null
seekframe -C "$P" plan demo-reviewers | grep -q 'demo-reviewers:'

if grep -qE '^  import( |$)' <<< "$help" && command -v node > /dev/null; then
  O="$TMP/old"
  mkdir -p "$O"
  printf '%s\n' "export const VIDEOS = [{ id: 'demo', group: 'developers', product: 'Acme', lines: [" \
    "  { vo: 'Agents open pull requests faster than anyone can read them.', sc: 'statement', p: { items: ['Ten.', 'One.'] } }," \
    "  { vo: 'Acme. Agents work. You decide.', sc: 'endcard', label: 'x' }] }];" > "$O/videos.mjs"
  if seekframe import "$O" "$TMP/refused" > "$TMP/refused.log" 2>&1; then fail "import accepted a line key the app has no field for"; fi
  grep -q 'extras-into-p' "$TMP/refused.log" || fail "import did not explain the refusal"
  seekframe import "$O" "$TMP/new" --extras-into-p > /dev/null
  seekframe -C "$TMP/new" plan demo | grep -q 'demo:'
  test -f "$O/videos.mjs" || fail "import touched the old project"
fi
echo "seekframe: all checks passed"
