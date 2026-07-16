#!/usr/bin/env bash
# Smoke tests for the guard-secrets PreToolUse hook. CI runs every skills/*/test.sh.
# Feeds the hook synthetic tool_input events and asserts the exit-2 deny contract.
set -euo pipefail
cd "$(dirname "$0")"
HOOK=scripts/guard_secrets.py

# fire <expected-rc> <json>  — run the hook with a tool_input event
fire() {
  local want="$1" json="$2" rc=0
  printf '%s' "$json" | python3 "$HOOK" >/dev/null 2>&1 || rc=$?
  [ "$rc" = "$want" ] || { echo "FAIL: expected rc=$want got rc=$rc for: $json" >&2; exit 1; }
}

# denied (rc=2)
fire 2 '{"tool_input":{"file_path":"secrets.decrypted.yaml","content":"x"}}'
fire 2 '{"tool_input":{"file_path":"values.sops.yaml","content":"password: hunter2"}}'
fire 2 '{"tool_input":{"file_path":"app.sops.yml","new_string":"token: abc"}}'

# allowed (rc=0)
fire 0 '{"tool_input":{"file_path":"values.sops.yaml","content":"password: ENC[AES256,data:...]"}}'
fire 0 '{"tool_input":{"file_path":"README.md","content":"just docs"}}'
fire 0 '{"tool_input":{"file_path":"values.yaml","content":"replicas: 3"}}'
fire 0 '{"tool_input":{}}'
fire 0 'not json at all'

echo "guard-secrets: ok"
