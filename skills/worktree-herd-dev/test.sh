#!/usr/bin/env bash
# Smoke tests for the worktree-herd-dev plugin. CI runs every skills/*/test.sh.
# Exercises the pure lib.sh helpers only — no Herd, no network, no real worktrees.
set -euo pipefail
cd "$(dirname "$0")"
LIB="$(pwd)/scripts/lib.sh"
# pwd -P: git reports physical paths, so the fixture paths must be physical too
# (macOS mktemp returns /var/..., a symlink to /private/var/...)
TMP=$(cd "$(mktemp -d)" && pwd -P)
trap 'rm -rf "$TMP"' EXIT

# shellcheck source=scripts/lib.sh
source "$LIB"

fail() {
    echo "FAIL: $1" >&2
    exit 1
}

# --- slugify -------------------------------------------------------------------
[[ "$(whd_slugify_branch 'CU-86cagjaua_Afmetingen_Jos-Last-v2')" == "afmetingen" ]] \
    || fail "slugify should strip ClickUp prefix and author suffix"
[[ "$(whd_slugify_branch 'Feature_Foo_Bar')" == "feature-foo-bar" ]] \
    || fail "slugify should lowercase and hyphenate underscores"
[[ "$(whd_slugify_branch 'feature/my-branch')" == "feature-my-branch" ]] \
    || fail "slugify should sanitize slashes (invalid in hostnames)"

long_branch="$(printf 'a%.0s' $(seq 1 80))"
slug="$(whd_slugify_branch "$long_branch")"
[[ "${#slug}" -le 63 ]] || fail "slug must fit a DNS label (63 chars), got ${#slug}"

# --- dns clamp + hash suffix ------------------------------------------------------
clamped="$(whd_dns_clamp "$(printf 'a%.0s' $(seq 1 62))-x")"
[[ "${#clamped}" -le 63 && "$clamped" != *- ]] || fail "dns clamp must not leave a trailing hyphen"

[[ "$(whd_hash6 branchname)" == "$(whd_hash6 branchname)" ]] || fail "hash6 must be deterministic"
h="$(whd_hash6 branchname)"
[[ "${#h}" -eq 6 ]] || fail "hash6 must be 6 chars, got ${#h}"

hashed="$(whd_hashed_slug "afmetingen" "CU-123_branch")"
[[ "$hashed" == "$(whd_hashed_slug "afmetingen" "CU-123_branch")" ]] || fail "hashed slug must be deterministic"
[[ "${#hashed}" -le 63 ]] || fail "hashed slug must fit a DNS label"
[[ "$hashed" == afmetingen-* ]] || fail "hashed slug should keep the readable part"

# --- .env get/set (atomic, special characters) -------------------------------------
ENV="$TMP/.env"
cat >"$ENV" <<'EOF'
APP_NAME=Test
APP_URL=https://mijn.heebink.test
DB_CONNECTION=pgsql
DB_DATABASE=myapp
EOF

[[ "$(whd_get_env_value "$ENV" APP_URL)" == "https://mijn.heebink.test" ]] || fail "get_env_value"

whd_set_env_value "$ENV" APP_URL 'https://x.test/?a=1&b=2|c'
[[ "$(whd_get_env_value "$ENV" APP_URL)" == 'https://x.test/?a=1&b=2|c' ]] \
    || fail "set_env_value must survive |, & and ? in values"
[[ "$(grep -c '^APP_URL=' "$ENV")" -eq 1 ]] || fail "set_env_value must replace, not duplicate"

whd_set_env_value "$ENV" NEW_KEY "added"
[[ "$(whd_get_env_value "$ENV" NEW_KEY)" == "added" ]] || fail "set_env_value must append missing keys"

# --- db name derivation --------------------------------------------------------------
[[ "$(whd_db_name "$ENV" 'my-feature.heebink')" == "myapp_my_feature_heebink" ]] \
    || fail "db name should be <main db>_<slug with underscores>"
[[ -z "$(whd_db_name "$TMP/does-not-exist" slug)" ]] || fail "db name should be empty without a main .env"

# --- config file + worktrees root + registry (needs a git repo for the root lookup) ---
REPO="$TMP/myapp"
git init -q "$REPO"
cd "$REPO"

[[ "$(whd_worktrees_root)" == "$TMP/myapp-worktrees" ]] \
    || fail "default worktrees root should be the sibling <repo>-worktrees dir"

cat >worktree-herd.yml <<'EOF'
base_branch: development
worktrees_dir: .worktrees   # keep them inside the repo
database: per-worktree
editor: "cursor"
EOF

[[ "$(whd_config_value base_branch)" == "development" ]] || fail "config_value base_branch"
[[ "$(whd_config_value database shared)" == "per-worktree" ]] || fail "config_value database"
[[ "$(whd_config_value missing_key fallback)" == "fallback" ]] || fail "config_value default"
[[ "$(whd_config_value worktrees_dir)" == ".worktrees" ]] || fail "config_value must strip trailing comments"
[[ "$(whd_config_value editor)" == "cursor" ]] || fail "config_value must strip quotes"
[[ "$(whd_worktrees_root)" == "$REPO/.worktrees" ]] || fail "worktrees_dir config should override the default"

cat >herd.yml <<'EOF'
name: mijn.heebink
php: '8.3'
EOF
[[ "$(whd_detect_herd_domain_suffix "$REPO" test)" == "heebink" ]] || fail "domain suffix from herd.yml"
[[ "$(whd_default_herd_site "$REPO" 'CU-86cagjaua_Afmetingen_Jos-Last-v2' test)" == "afmetingen.heebink" ]] \
    || fail "default herd site should be <slug>.<suffix>"
[[ "$(whd_detect_php_version "$REPO")" == "8.3" ]] || fail "php version from herd.yml"

# --- site_separator: flat single-label sites for subdomain-routing apps -----------------
echo 'site_separator: "-"' >>worktree-herd.yml
[[ "$(whd_default_herd_site "$REPO" 'CU-86cagjaua_Afmetingen_Jos-Last-v2' test)" == "afmetingen-heebink" ]] \
    || fail "site_separator '-' should give a flat <slug>-<suffix> site"

flat="$(whd_join_site "$(printf 'a%.0s' $(seq 1 70))" heebink)"
[[ "${#flat}" -le 63 ]] || fail "flat site must fit a DNS label (63 chars), got ${#flat}"
[[ "$flat" == *-heebink ]] || fail "flat site clamping must keep the suffix intact"

grep -v '^site_separator:' worktree-herd.yml >worktree-herd.yml.tmp && mv worktree-herd.yml.tmp worktree-herd.yml
echo 'site_separator: "_"' >>worktree-herd.yml
if site="$( (whd_join_site foo heebink) 2>/dev/null )"; then
    fail "invalid site_separator must be rejected, got '$site'"
fi
grep -v '^site_separator:' worktree-herd.yml >worktree-herd.yml.tmp && mv worktree-herd.yml.tmp worktree-herd.yml

# registry roundtrip + vite port allocation
whd_write_registry_entry "feature/x" "x.heebink" 5174 "$REPO/.worktrees/feature/x" "myapp_x"
[[ "$(whd_read_registry_value 'feature/x' herd_site)" == "x.heebink" ]] || fail "registry read herd_site"
[[ "$(whd_read_registry_value 'feature/x' db_name)" == "myapp_x" ]] || fail "registry read db_name"
[[ "$(whd_next_vite_port)" == "5175" ]] || fail "next vite port should skip used ports"
whd_write_registry_entry "feature/y" "y.heebink" 5175 "$REPO/.worktrees/feature/y" ""
[[ "$(whd_next_vite_port)" == "5176" ]] || fail "next vite port should skip all used ports"
[[ "$(whd_registry_branch_for_path "$REPO/.worktrees/feature/x")" == "feature/x" ]] \
    || fail "registry lookup by path"
whd_remove_registry_entry "feature/x"
[[ -z "$(whd_read_registry_value 'feature/x' herd_site)" ]] || fail "registry entry should be removed"

# --- marker roundtrip -------------------------------------------------------------------
MARKER_DIR="$TMP/wt"
mkdir -p "$MARKER_DIR"
whd_write_marker "$MARKER_DIR" "feature/x" "x.heebink" 5174 "" "$REPO"
[[ "$(whd_marker_value "$MARKER_DIR" herd_site)" == "x.heebink" ]] || fail "marker read herd_site"
[[ "$(whd_marker_value "$MARKER_DIR" branch)" == "feature/x" ]] || fail "marker read branch"
[[ -z "$(whd_marker_value "$MARKER_DIR" db_name)" ]] || fail "empty db_name should read back empty"

# --- dirty check ignores the tool's own artifacts ------------------------------------------
WT="$TMP/wtrepo"
git init -q "$WT"
touch "$WT/.worktree-herd.json" "$WT/herd.yml"
if whd_worktree_is_dirty "$WT"; then
    fail "marker + generated herd.yml alone must not count as dirty"
fi
touch "$WT/user-file.txt"
whd_worktree_is_dirty "$WT" || fail "other untracked files must count as dirty"

# --- npm script detection ---------------------------------------------------------------------
echo '{"scripts": {"build": "vite build"}}' >"$MARKER_DIR/package.json"
whd_has_npm_script "$MARKER_DIR" build || fail "has_npm_script should find build"
whd_has_npm_script "$MARKER_DIR" nope && fail "has_npm_script must fail for missing scripts"

echo "worktree-herd-dev: ok"
