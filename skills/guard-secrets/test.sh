#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
HOOK="$PWD/scripts/guard_secrets.py"
TWIN_SOURCE="$PWD/../../opencode/plugins/guard-secrets.js"
PY3="$(python3 -c 'import sys; print(sys.executable)')"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

make_gitleaks() {
  mkdir -p "$WORK/$1"
  printf '#!/bin/sh\n%s\n' "$2" > "$WORK/$1/gitleaks"
  chmod +x "$WORK/$1/gitleaks"
}

make_gitleaks finds-leak 'while [ $# -gt 0 ]; do [ "$1" = "--exit-code" ] && exit "$2"; shift; done; exit 1'
make_gitleaks scanner-error 'echo "mise ERROR No version is set for shim: gitleaks" >&2; exit 1'
make_gitleaks scan-clean 'exit 0'
mkdir -p "$WORK/no-gitleaks"

CLEAN="$WORK/scan-clean"
LEAK="$WORK/finds-leak"
BROKEN="$WORK/scanner-error"
MISSING="$WORK/no-gitleaks"

run_hook() { printf '%s' "$2" | PATH="$1" "$PY3" "$HOOK"; }

expect() {
  local want_rc="$1" want_stderr="$2" label="$3" rc=0 stderr
  shift 3
  stderr="$("$@" 2>&1 >/dev/null)" || rc=$?
  [ "$rc" = "$want_rc" ] || fail "$label: expected rc=$want_rc, got rc=$rc ($stderr)"
  case "$stderr" in *"$want_stderr"*) ;; *) fail "$label: stderr lacks '$want_stderr': $stderr" ;; esac
}

expect_silent() {
  local label="$1" rc=0 stderr
  shift
  stderr="$("$@" 2>&1 >/dev/null)" || rc=$?
  [ "$rc" = 0 ] && [ -z "$stderr" ] || fail "$label: expected a silent allow, got rc=$rc ($stderr)"
}

expect 2 "decrypted secret artifact" "decrypted artifact" run_hook "$CLEAN" '{"tool_input":{"file_path":"secrets.decrypted.yaml","content":"x"}}'
expect 2 "isn't encrypted" "plaintext sops write" run_hook "$CLEAN" '{"tool_input":{"file_path":"values.sops.yaml","content":"password: hunter2"}}'
expect 2 "isn't encrypted" "plaintext sops edit" run_hook "$CLEAN" '{"tool_input":{"file_path":"app.sops.yml","new_string":"token: abc"}}'
expect 2 "ExternalSecret" "leak found" run_hook "$LEAK" '{"tool_input":{"file_path":"values.yaml","content":"token: abc"}}'
expect 2 "flagged" "leak in a multi-edit" run_hook "$LEAK" '{"tool_input":{"file_path":"values.yaml","edits":[{"new_string":"token: abc"}]}}'

expect_silent "encrypted sops" run_hook "$CLEAN" '{"tool_input":{"file_path":"values.sops.yaml","content":"password: ENC[AES256,data:...]"}}'
expect_silent "clean scan" run_hook "$CLEAN" '{"tool_input":{"file_path":"values.yaml","content":"replicas: 3"}}'
expect_silent "no path" run_hook "$CLEAN" '{"tool_input":{}}'
expect_silent "not json" run_hook "$CLEAN" 'not json at all'
expect_silent "json list" run_hook "$CLEAN" '[1, 2]'

expect 0 "exited 1 without a finding" "scanner error" run_hook "$BROKEN" '{"tool_input":{"file_path":"README.md","content":"- **Owner:** Platform team"}}'
expect 0 "not on PATH" "scanner missing" run_hook "$MISSING" '{"tool_input":{"file_path":"values.yaml","content":"replicas: 3"}}'

echo "guard-secrets: hook ok"

if ! NODE="$(node -p 'process.execPath' 2>/dev/null)"; then
  echo "guard-secrets: no working node, opencode twin not exercised"
  exit 0
fi

TWIN="$WORK/twin"
mkdir -p "$TWIN/node_modules/@opencode-ai/plugin"
cp "$TWIN_SOURCE" "$TWIN/guard-secrets.js"
printf '{"type":"module"}\n' > "$TWIN/package.json"
printf '{"name":"@opencode-ai/plugin","type":"module","exports":{"./v2":"./v2.js"}}\n' > "$TWIN/node_modules/@opencode-ai/plugin/package.json"
printf 'export const Plugin = { define: (definition) => definition };\n' > "$TWIN/node_modules/@opencode-ai/plugin/v2.js"
cat > "$TWIN/run.mjs" <<'EOF'
import plugin from "./guard-secrets.js";
let hook;
await plugin.setup({ tool: { hook: (_event, handler) => { hook = handler; } } });
const [tool, path, content] = process.argv.slice(2);
try {
  await hook({ tool, input: { path, content } });
} catch (error) {
  console.error(error.message);
  process.exit(error.message.startsWith("BLOCKED:") ? 2 : 1);
}
EOF

run_twin() { PATH="$1" "$NODE" "$TWIN/run.mjs" "$2" "$3" "$4"; }

expect 2 "decrypted secret artifact" "twin decrypted artifact" run_twin "$CLEAN" write secrets.decrypted.yaml x
expect 2 "isn't encrypted" "twin plaintext sops" run_twin "$CLEAN" edit values.sops.yaml "password: hunter2"
expect 2 "ExternalSecret" "twin leak found" run_twin "$LEAK" write values.yaml "token: abc"
expect_silent "twin encrypted sops" run_twin "$CLEAN" write values.sops.yaml "password: ENC[AES256,data:...]"
expect_silent "twin clean scan" run_twin "$CLEAN" write values.yaml "replicas: 3"
expect_silent "twin other tool" run_twin "$LEAK" read values.yaml "token: abc"
expect 0 "exited 1 without a finding" "twin scanner error" run_twin "$BROKEN" write README.md "- **Owner:** Platform team"
expect 0 "not on PATH" "twin scanner missing" run_twin "$MISSING" write values.yaml "replicas: 3"

echo "guard-secrets: opencode twin ok"
