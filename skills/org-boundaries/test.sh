#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
skill_dir="$(pwd)"
scanner="$skill_dir/scripts/scan_boundary.py"

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_COMMON_DIR \
  GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL GIT_CONFIG_GLOBAL
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
export HOME="$work/home" GIT_CONFIG_NOSYSTEM=1 ORG_BOUNDARIES_DIR="$work/home/.config/org-boundaries"
export ORG_BOUNDARIES_SCANNER="$scanner"
mkdir -p "$ORG_BOUNDARIES_DIR"
git config --global user.name "Pat Example"
git config --global user.email "pat@acme.example"
git config --global init.defaultBranch main
git config --global advice.detachedHead false

printf '%s\n' '# markers of globex, the fictional employer' 'globex' '@globex\.example' \
  '\bsibling estate\b' '\bGBX-[0-9]+\b' '' 'allow:registry\.globex\.example/public/base' \
  > "$ORG_BOUNDARIES_DIR/globex.txt"
fake_value="$(printf '%s-%s%s' glpat Q7xRm2Kd9T zLw4Np8VbHc)"

fail() { echo "FAIL: $*" >&2; exit 1; }

scan() {
  local expected="$1"; shift
  local status=0
  python3 "$scanner" "$@" > "$work/out" 2> "$work/err" || status=$?
  [ "$status" -eq "$expected" ] || { cat "$work/out" "$work/err" >&2; fail "scan $* exited $status, expected $expected"; }
}

expect_line() {
  grep -q -E "$1" "$work/out" || { cat "$work/out" >&2; fail "no finding matching: $1"; }
}

refuse_line() {
  if grep -q -E "$1" "$work/out"; then cat "$work/out" >&2; fail "unexpected finding matching: $1"; fi
}

leaky="$work/leaky"
git init -q "$leaky"
printf 'plain readme\n' > "$leaky/README.md"
git -C "$leaky" add README.md
git -C "$leaky" commit -q -m "chore: start"
clean_point="$(git -C "$leaky" rev-parse HEAD)"
mkdir -p "$leaky/docs" "$leaky/deploy" "$leaky/config" "$leaky/assets"
printf 'Moved here from the Globex wiki.\n' > "$leaky/docs/globex-notes.md"
printf 'image: registry.globex.example/public/base:1.2\n' > "$leaky/deploy/values.yaml"
printf 'GLOBEX_VALUE=%s\n' "$fake_value" > "$leaky/config/env.txt"
printf 'PNG\0\0\0globex\0' > "$leaky/assets/logo.bin"
git -C "$leaky" add .
GIT_AUTHOR_EMAIL=pat@globex.example git -C "$leaky" commit -q -m "feat: parity with the sibling estate" -m "Refs GBX-12"
git -C "$leaky" tag -a v1.0 -m "release for GBX-12"
git -C "$leaky" branch globex-sync
git -C "$leaky" checkout -q -b side
mkdir -p "$leaky/notes"
printf 'kept in step with the sibling estate\n' > "$leaky/notes/side.md"
git -C "$leaky" add notes/side.md
git -C "$leaky" commit -q -m "docs: side note"
git -C "$leaky" checkout -q main
printf 'globex scratch\n' > "$leaky/globex-scratch.txt"

scan 1 --org globex "$leaky"
expect_line $'^content\tdocs/globex-notes.md:1\trule 1:2\t'
expect_line $'^content\tconfig/env.txt:1\t'
expect_line $'^content\tassets/logo.bin \\(binary\\)\t'
expect_line $'^path\tdocs/globex-notes.md\t'
expect_line $'^identity\tauthor of 1 commit, latest [0-9a-f]{10}\trule 1:3\tPat Example <pat@globex.example>'
expect_line $'^message\tcommit [0-9a-f]{10} line 1\trule 1:4\t'
expect_line $'^message\tcommit [0-9a-f]{10} line 3\trule 1:5\tRefs GBX-12'
expect_line $'^message\ttag v1.0 line 1\t'
expect_line $'^ref\trefs/heads/globex-sync\t'
refuse_line 'deploy/values.yaml'
refuse_line 'notes/side.md'
refuse_line 'scratch.txt'
refuse_line "$fake_value"
expect_line "glpa…\\[${#fake_value} chars masked\\]"
if grep -q -i globex "$work/err"; then fail "the summary names the organisation"; fi

scan 1 --org globex --all-refs --untracked "$leaky"
expect_line $'^content\trefs/heads/side:notes/side.md:1\t'
expect_line $'^content\tglobex-scratch.txt:1\t'
expect_line $'^path\tuntracked globex-scratch.txt\t'
[ "$(grep -c $'^content\tdocs/globex-notes.md' "$work/out")" -eq 1 ] || fail "--all-refs reported the checked-out blob twice"
refuse_line 'refs/heads/main:docs'

scan 1 --org globex --since-commit main "$leaky"
expect_line $'^content\t'
expect_line $'^ref\t'
expect_line $'^message\ttag v1.0 line 1\t'
refuse_line $'^identity\tauthor'
refuse_line $'^message\tcommit '

scan 1 --org globex --range "$clean_point..main" "$leaky"
expect_line $'^identity\tauthor'

git -C "$leaky" config org-boundaries.exclude globex
scan 1 "$leaky"
expect_line $'^ref\trefs/heads/globex-sync\t'

cp "$ORG_BOUNDARIES_DIR/globex.txt" "$leaky/boundary.txt"
scan 2 --patterns "$leaky/boundary.txt" "$leaky"
grep -q "inside the repository" "$work/err" || fail "patterns inside the repo were not refused"
rm "$leaky/boundary.txt"
printf 'globex(\n' > "$work/broken.txt"
scan 2 --patterns "$work/broken.txt" "$leaky"
grep -q "rule 1:1" "$work/err" || fail "invalid regex was not reported with its rule"
printf '# only a comment\n\n' > "$work/empty.txt"
scan 2 --patterns "$work/empty.txt" "$leaky"
scan 2 --org missing "$leaky"
scan 2 --org "../escape" "$leaky"
scan 2 --patterns "$ORG_BOUNDARIES_DIR/globex.txt" "$work/not-a-repo"

unconfigured="$work/unconfigured"
git init -q "$unconfigured"
scan 2 "$unconfigured"

root="$work/root"
git init -q "$root"
git -C "$root" config org-boundaries.exclude globex
printf 'notes from the globex wiki\n' > "$root/notes.md"
git -C "$root" add notes.md
python3 "$scanner" --staged "$root" > "$work/out" 2>&1 && fail "a leak in the root commit passed --staged"
expect_line $'^content\tnotes.md:1\t'
scan 1 --org globex --max-bytes 4 "$leaky"
refuse_line $'^content\tdocs/'
grep -q "not scanned" "$work/err" || fail "files over --max-bytes were not listed"

install_hooks() {
  local hooks
  hooks="$(git -C "$1" rev-parse --git-path hooks)"
  case "$hooks" in /*) ;; *) hooks="$1/$hooks" ;; esac
  cp "$skill_dir/assets/hooks/pre-commit" "$skill_dir/assets/hooks/commit-msg" "$hooks/"
}

clean="$work/clean"
git init -q "$clean"
git -C "$clean" config org-boundaries.exclude globex
install_hooks "$clean"
printf 'deploy notes\n' > "$clean/README.md"
printf 'image: registry.globex.example/public/base:1.2\n' > "$clean/values.yaml"
git -C "$clean" add .
git -C "$clean" commit -q -m "feat: first notes" || fail "a clean first commit was blocked"
git -C "$clean" tag -a v0.1 -m "first release"
git -C "$clean" branch feature/retries
scan 0 "$clean"
scan 0 --all-refs --untracked "$clean"
scan 0 --range "HEAD" "$clean"

blocked() {
  local before after
  before="$(git -C "$clean" rev-parse HEAD)"
  if "$@" > "$work/hook" 2>&1; then cat "$work/hook" >&2; fail "hook let through: $*"; fi
  after="$(git -C "$clean" rev-parse HEAD)"
  [ "$before" = "$after" ] || fail "HEAD moved although the hook failed"
}

printf 'ported from the globex runbook\n' >> "$clean/README.md"
git -C "$clean" add README.md
blocked git -C "$clean" commit -q -m "docs: runbook"
grep -q $'^content\tREADME.md:2\t' "$work/hook" || fail "pre-commit did not name the added line"
git -C "$clean" reset -q --hard

printf 'retry with backoff\n' >> "$clean/README.md"
git -C "$clean" add README.md
blocked git -C "$clean" commit -q -m "docs: retries" -m "Refs GBX-7"
grep -q $'^message\tcommit message line 3\t' "$work/hook" || fail "commit-msg did not name the message line"
blocked env GIT_AUTHOR_EMAIL=pat@globex.example git -C "$clean" commit -q -m "docs: retries"
grep -q $'^identity\tnext commit author\t' "$work/hook" || fail "pre-commit did not check the identity"
git -C "$clean" checkout -q -b globex-port
blocked git -C "$clean" commit -q -m "docs: retries"
grep -q $'^ref\trefs/heads/globex-port\t' "$work/hook" || fail "pre-commit did not check the branch name"
git -C "$clean" checkout -q main
git -C "$clean" branch -q -D globex-port
git -C "$clean" commit -q -m "docs: retries" > "$work/hook" 2>&1 || { cat "$work/hook" >&2; fail "a clean commit was blocked"; }
[ ! -s "$work/hook" ] || { cat "$work/hook" >&2; fail "the hooks printed output on a clean commit"; }
scan 0 "$clean"

install_hooks "$leaky"
printf 'second line\n' >> "$leaky/docs/globex-notes.md"
git -C "$leaky" add docs/globex-notes.md
git -C "$leaky" commit -q -m "docs: extend notes" || fail "an existing leak in an untouched line blocked the commit"

printf 'globex\n' > "$clean/unguarded.txt"
git -C "$clean" config --unset-all org-boundaries.exclude
git -C "$clean" add unguarded.txt
git -C "$clean" commit -q -m "chore: unguarded" || fail "the hook blocked a repo without a configured boundary"

python3 - "$scanner" <<'PY'
import re
import sys
from pathlib import Path

options = set(re.findall(r'add_argument\(\s*"(--[a-z-]+)"', Path(sys.argv[1]).read_text()))
docs = Path("SKILL.md").read_text() + Path("references/surfaces.md").read_text()
undocumented = sorted(option for option in options if f"`{option}" not in docs and f" {option}" not in docs)
if undocumented:
    sys.exit(f"scan_boundary.py options missing from the docs: {undocumented}")
print(f"scan_boundary: {len(options)} options documented")
PY

echo "org-boundaries: all checks passed"
