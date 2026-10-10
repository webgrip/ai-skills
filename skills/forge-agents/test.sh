#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TOOL="python3 scripts/forge_safety.py"
HOOKS=fixtures/webhooks
FIXTURE_KEY_PHRASE="forge-agents-fixture-signing-key"
GITHUB_DOCS_EXAMPLE_PHRASE="It's a Secret to Everybody"
SIGNED_AT=1614265330
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
failures=0

fail() { echo "FAIL: $*" >&2; failures=$((failures + 1)); }

expect_exit() {
  local expected=$1 label=$2
  shift 2
  local actual=0
  "$@" > /dev/null 2>&1 || actual=$?
  [ "$actual" -eq "$expected" ] || fail "$label: exit $actual, expected $expected"
}

$TOOL neutralise --json fixtures/neutralise/all-rules.md | python3 -c '
import json, sys
fired = set(json.load(sys.stdin)["fired"])
expected = {"quick-action", "mention", "closing-keyword"}
if fired != expected:
    sys.exit(f"all-rules fixture: missing {sorted(expected - fired)}, unexpected {sorted(fired - expected)}")
' || fail "neutralise all-rules fixture"

$TOOL neutralise fixtures/neutralise/all-rules.md | python3 -c '
import re, sys
text = sys.stdin.read()
outside_fences = text.split("```")[0]
if re.search(r"(?m)^\s*/[A-Za-z]", outside_fences):
    sys.exit("a quick-action line survived")
if re.search(r"(?<![\w.])@[A-Za-z]", outside_fences):
    sys.exit("a mention survived")
if re.search(r"(?i)\b(closes|fixes|resolved|implements)\s", outside_fences):
    sys.exit("a closing keyword survived")
if "/usr/bin/env true" not in text or "@bob fixes #9" not in text:
    sys.exit("code fence content was changed")
' || fail "neutralise output"

once=$($TOOL neutralise fixtures/neutralise/all-rules.md)
twice=$(printf '%s\n' "$once" | $TOOL neutralise)
[ "$once" = "$twice" ] || fail "neutralise is not idempotent"

$TOOL neutralise --json fixtures/neutralise/clean.md | python3 -c '
import json, sys
result = json.load(sys.stdin)
if result["fired"]:
    sys.exit("clean fixture fired " + ", ".join(sorted(result["fired"])))
if result["text"] != open("fixtures/neutralise/clean.md", encoding="utf-8").read():
    sys.exit("clean fixture text changed")
' || fail "neutralise clean fixture"

python3 - "$FIXTURE_KEY_PHRASE" "$SIGNED_AT" "$HOOKS/gitlab.body" "$WORK" <<'PY'
import base64, hashlib, hmac, json, sys
phrase, signed_at, body_path, work = sys.argv[1:5]
body = open(body_path, "rb").read()
message_id = "msg_fixture_0001"
digest = hmac.new(phrase.encode(), f"{message_id}.{signed_at}.".encode() + body, hashlib.sha256).digest()
signed = {
    "X-Gitlab-Event": "Issue Hook",
    "webhook-id": message_id,
    "webhook-timestamp": signed_at,
    "webhook-signature": "v1,AAAA v1," + base64.b64encode(digest).decode(),
}
json.dump(signed, open(f"{work}/gitlab-signed.headers.json", "w"))
PY

export WEBHOOK_SECRET="whsec_$(printf '%s' "$FIXTURE_KEY_PHRASE" | base64)"
SIGNED_HEADERS="$WORK/gitlab-signed.headers.json"
expect_exit 0 "gitlab signed" $TOOL verify --forge gitlab --headers "$SIGNED_HEADERS" --body $HOOKS/gitlab.body --now $SIGNED_AT
expect_exit 1 "gitlab tampered body" $TOOL verify --forge gitlab --headers "$SIGNED_HEADERS" --body $HOOKS/gitlab-tampered.body --now $SIGNED_AT
expect_exit 1 "gitlab stale timestamp" $TOOL verify --forge gitlab --headers "$SIGNED_HEADERS" --body $HOOKS/gitlab.body --now $((SIGNED_AT + 3600))
expect_exit 1 "gitlab token only" $TOOL verify --forge gitlab --headers $HOOKS/gitlab-token-only.headers.json --body $HOOKS/gitlab.body --now $SIGNED_AT
token_only_report=$($TOOL verify --forge gitlab --headers $HOOKS/gitlab-token-only.headers.json --body $HOOKS/gitlab.body --now $SIGNED_AT 2>/dev/null || true)
grep -q "X-Gitlab-Token is a plain shared secret" <<< "$token_only_report" || fail "gitlab token-only reason"
$TOOL verify --forge gitlab --headers "$SIGNED_HEADERS" --body $HOOKS/gitlab.body --now $SIGNED_AT \
  | grep -q '"delivery_id": "msg_fixture_0001"' || fail "gitlab delivery id"

export WEBHOOK_SECRET="$GITHUB_DOCS_EXAMPLE_PHRASE"
expect_exit 0 "github signed" $TOOL verify --forge github --headers $HOOKS/github-signed.headers.json --body $HOOKS/github.body
expect_exit 0 "forgejo signed" $TOOL verify --forge forgejo --headers $HOOKS/forgejo-signed.headers.json --body $HOOKS/github.body
expect_exit 1 "github tampered body" $TOOL verify --forge github --headers $HOOKS/github-signed.headers.json --body $HOOKS/gitlab.body

export WEBHOOK_SECRET="not-the-signing-phrase"
expect_exit 1 "github wrong secret" $TOOL verify --forge github --headers $HOOKS/github-signed.headers.json --body $HOOKS/github.body

unset WEBHOOK_SECRET
expect_exit 2 "secret unset" $TOOL verify --forge github --headers $HOOKS/github-signed.headers.json --body $HOOKS/github.body
export WEBHOOK_SECRET="any-value"
expect_exit 2 "headers file missing" $TOOL verify --forge github --headers $HOOKS/absent.json --body $HOOKS/github.body
unset WEBHOOK_SECRET

python3 - <<'PY' || failures=$((failures + 1))
import re, sys
rules = re.search(r"RULES = \(([^)]*)\)", open("scripts/forge_safety.py").read()).group(1)
names = re.findall(r'"([a-z-]+)"', rules)
skill = open("SKILL.md", encoding="utf-8").read()
undocumented = [name for name in names if f"`{name}`" not in skill]
if undocumented:
    sys.exit(f"FAIL: neutralise rules missing from SKILL.md: {undocumented}")
PY

if [ "$failures" -gt 0 ]; then
  echo "forge-agents: $failures check(s) failed" >&2
  exit 1
fi
echo "forge-agents: all checks passed"
