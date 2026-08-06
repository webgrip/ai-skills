#!/usr/bin/env bash
# Shared helpers for worktree-herd-setup / worktree-herd-cleanup.

readonly WHD_BASE_VITE_PORT=5174
readonly WHD_DEFAULT_PHP_VERSION="8.4"
readonly WHD_CONFIG_FILE="worktree-herd.yml"
readonly WHD_MARKER_FILE=".worktree-herd.json"
readonly WHD_REGISTRY_BASENAME=".registry.json"

whd_log() {
    printf '→ %s\n' "$1" >&2
}

whd_warn() {
    printf '! %s\n' "$1" >&2
}

whd_error() {
    printf '✗ %s\n' "$1" >&2
    exit 1
}

whd_require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        whd_error "Required command not found: $1"
    fi
}

whd_repo_root() {
    git rev-parse --show-toplevel
}

whd_main_repo_root() {
    local git_dir
    git_dir="$(git rev-parse --git-common-dir)"

    if [[ "$git_dir" != /* ]]; then
        git_dir="$(cd "$(whd_repo_root)" && cd "$git_dir" && pwd)"
    fi

    dirname "$git_dir"
}

whd_is_main_worktree() {
    local git_dir worktree_git_dir
    git_dir="$(git rev-parse --git-common-dir)"
    worktree_git_dir="$(git rev-parse --git-dir)"

    [[ "$git_dir" == "$worktree_git_dir" ]]
}

whd_resolve_branch_from_current() {
    git -C "$(whd_repo_root)" branch --show-current
}

# --- project config (worktree-herd.yml, optional, flat key: value) ------------

whd_config_path() {
    printf '%s/%s' "$(whd_main_repo_root)" "$WHD_CONFIG_FILE"
}

whd_config_value() {
    local key="$1"
    local default="${2:-}"
    local file value=""

    file="$(whd_config_path)"

    if [[ -f "$file" ]]; then
        value="$({ grep -E "^${key}:" "$file" || true; } | head -1 \
            | sed -E "s/^${key}:[[:space:]]*//; s/[[:space:]]+#.*$//; s/[[:space:]]+$//" \
            | sed -E "s/^['\"]//; s/['\"]$//")"
    fi

    if [[ -n "$value" ]]; then
        printf '%s' "$value"
    else
        printf '%s' "$default"
    fi
}

whd_worktrees_root() {
    local main_root dir
    main_root="$(whd_main_repo_root)"
    dir="$(whd_config_value worktrees_dir)"

    if [[ -z "$dir" ]]; then
        printf '%s-worktrees' "$main_root"
    elif [[ "$dir" == /* ]]; then
        printf '%s' "$dir"
    else
        printf '%s/%s' "$main_root" "$dir"
    fi
}

whd_hook_path() {
    local kind="$1" # post_setup | pre_cleanup
    local main_root configured default_name
    main_root="$(whd_main_repo_root)"
    default_name="${kind//_/-}"

    configured="$(whd_config_value "${kind}_hook")"

    if [[ -z "$configured" ]]; then
        printf '%s/.worktree-herd/%s' "$main_root" "$default_name"
    elif [[ "$configured" == /* ]]; then
        printf '%s' "$configured"
    else
        printf '%s/%s' "$main_root" "$configured"
    fi
}

# Runs the hook if present. A hook that exists but is not executable is an
# error (silently skipping it would hide broken project automation).
whd_run_hook() {
    local hook="$1"
    local worktree_path="$2"

    if [[ -x "$hook" ]]; then
        whd_log "Running hook: $hook"
        (cd "$worktree_path" && "$hook")
    elif [[ -f "$hook" ]]; then
        whd_error "Hook exists but is not executable: $hook (chmod +x it)"
    fi
}

# --- naming --------------------------------------------------------------------

whd_slugify_branch() {
    local branch="$1"
    local slug

    slug="$(printf '%s' "$branch" \
        | sed -E 's/^CU-[^_]+_//; s/_[A-Za-z]+-Last(-v[0-9]+)?$//; s/_/-/g' \
        | tr '[:upper:]' '[:lower:]' \
        | sed -E 's/[^a-z0-9-]/-/g; s/-{2,}/-/g; s/^-//; s/-$//')"

    if [[ -z "$slug" ]]; then
        slug="$(printf '%s' "$branch" | tr '[:upper:]' '[:lower:]' \
            | sed -E 's/[^a-z0-9-]/-/g; s/-{2,}/-/g; s/^-//; s/-$//')"
    fi

    if [[ -z "$slug" ]]; then
        slug="wt"
    fi

    whd_dns_clamp "$slug"
}

# Clamp to a single DNS label (63 chars), no trailing hyphen.
whd_dns_clamp() {
    local label
    label="$(printf '%s' "$1" | cut -c1-63)"
    printf '%s' "${label%-}"
}

whd_hash6() {
    printf '%s' "$1" | shasum | cut -c1-6
}

# Slug with a 6-char hash suffix, still within one DNS label.
whd_hashed_slug() {
    local slug="$1"
    local seed="$2"
    local base
    base="$(printf '%s' "$slug" | cut -c1-56)"
    printf '%s-%s' "${base%-}" "$(whd_hash6 "$seed")"
}

whd_detect_herd_domain_suffix() {
    local main_root="$1"
    local tld="${2:-test}"
    local main_site=""

    if [[ -f "$main_root/herd.yml" ]]; then
        main_site="$({ grep -E '^name:' "$main_root/herd.yml" || true; } | head -1 | sed -E 's/^name:[[:space:]]*//')"
    fi

    if [[ -z "$main_site" && -f "$main_root/.env" ]]; then
        local app_url
        app_url="$(whd_get_env_value "$main_root/.env" APP_URL)"
        main_site="$(printf '%s' "$app_url" | sed -E "s|https?://||; s|\.${tld}\$||")"
    fi

    if [[ -z "$main_site" ]]; then
        whd_error "Cannot derive a Herd domain. Add a herd.yml or set APP_URL in .env."
    fi

    if [[ "$main_site" == *.* ]]; then
        printf '%s' "${main_site#*.}"
    else
        printf '%s' "$main_site"
    fi
}

# Join slug and suffix per the configured site_separator. '.' (default) yields
# subdomain-style sites; '-' yields a flat single-label site, required for apps
# that route their own subdomains: Herd resolves a host only by exact link name
# or by the LAST label before the TLD, so sub.slug.project.test would fall back
# to the main repo's 'project' site instead of the worktree.
whd_join_site() {
    local slug="$1"
    local suffix="$2"
    local sep max

    sep="$(whd_config_value site_separator .)"

    case "$sep" in
        .)
            printf '%s.%s' "$slug" "$suffix"
            ;;
        -)
            # The whole site is one DNS label; keep the suffix intact.
            max=$((63 - ${#suffix} - 1))
            slug="$(printf '%s' "$slug" | cut -c1-"$max")"
            printf '%s-%s' "${slug%-}" "$suffix"
            ;;
        *)
            whd_error "Invalid site_separator '${sep}' in ${WHD_CONFIG_FILE} (use '.' or '-')."
            ;;
    esac
}

whd_default_herd_site() {
    local main_root="$1"
    local branch="$2"
    local tld="${3:-test}"
    local suffix

    suffix="$(whd_detect_herd_domain_suffix "$main_root" "$tld")"
    whd_join_site "$(whd_slugify_branch "$branch")" "$suffix"
}

whd_detect_php_version() {
    local main_root="$1"
    local php_version=""

    if [[ -f "$main_root/herd.yml" ]]; then
        php_version="$({ grep -E '^php:' "$main_root/herd.yml" || true; } | head -1 | sed -E "s/^php:[[:space:]]*//; s/['\"]//g")"
    fi

    if [[ -z "$php_version" ]]; then
        php_version="$WHD_DEFAULT_PHP_VERSION"
    fi

    printf '%s' "$php_version"
}

# --- Herd introspection ---------------------------------------------------------

whd_herd_tld() {
    local tld=""
    if command -v herd >/dev/null 2>&1; then
        tld="$(herd tld 2>/dev/null | tr -d '[:space:]' || true)"
    fi
    printf '%s' "${tld:-test}"
}

whd_herd_table_sites() {
    awk -F'|' '
        $0 ~ /^\|/ {
            site=$2
            gsub(/^[ \t]+|[ \t]+$/, "", site)
            if (site != "" && site != "Site") print site
        }
    '
}

whd_herd_has_link() {
    local name="$1"
    command -v herd >/dev/null 2>&1 || return 1
    herd links 2>/dev/null | whd_herd_table_sites | grep -Fxq "$name"
}

whd_herd_has_secured() {
    local domain="$1"
    command -v herd >/dev/null 2>&1 || return 1
    herd secured 2>/dev/null | whd_herd_table_sites | grep -Fxq "$domain"
}

# --- Herd trace pruning ---------------------------------------------------------

whd_herd_config_root() {
    printf '%s/Library/Application Support/Herd/config' "$HOME"
}

# Herd appends each secured site's certificate to its PHP CA bundle
# (config/php/cacert.pem), but `herd unsecure` leaves that entry behind.
# Prune the block for the removed domain, plus any block whose certificate no
# longer exists in valet's Certificates directory (leftovers of older removals).
whd_prune_herd_cacert() {
    local domain="$1"
    local config_root cacert certs_dir removed
    config_root="$(whd_herd_config_root)"
    cacert="$config_root/php/cacert.pem"
    certs_dir="$config_root/valet/Certificates"
    [[ -f "$cacert" ]] || return 0

    removed="$(node -e '
        const fs = require("fs");
        const [cacertPath, certsDir, domain] = process.argv.slice(1);
        const content = fs.readFileSync(cacertPath, "utf8");
        const certsDirExists = fs.existsSync(certsDir);
        const block = /\nHerd ([^\n]+)\n=+\n-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----\n?/g;
        const removed = [];
        const cleaned = content.replace(block, (match, site) => {
            const orphaned = certsDirExists && !fs.existsSync(`${certsDir}/${site}.crt`);
            if (site === domain || orphaned) {
                removed.push(site);
                return "\n";
            }
            return match;
        });
        if (removed.length > 0) fs.writeFileSync(cacertPath, cleaned);
        process.stdout.write(removed.join(" "));
    ' "$cacert" "$certs_dir" "$domain")"

    if [[ -n "$removed" ]]; then
        whd_log "Pruned Herd CA-bundle entries: $removed"
    fi
}

# The Herd GUI remembers the last opened site (herd.json lastSite); after a
# cleanup it can point at the deleted worktree. Repoint it at the main repo.
whd_prune_herd_last_site() {
    local removed_path="$1"
    local replacement_path="$2"
    local herd_json
    herd_json="$(whd_herd_config_root)/herd.json"
    [[ -f "$herd_json" && -n "$removed_path" ]] || return 0

    node -e '
        const fs = require("fs");
        const [path, removed, replacement] = process.argv.slice(1);
        const data = JSON.parse(fs.readFileSync(path, "utf8"));
        if (typeof data.lastSite === "string" && (data.lastSite === removed || data.lastSite.startsWith(removed + "/"))) {
            data.lastSite = replacement;
            fs.writeFileSync(path, JSON.stringify(data, null, 4) + "\n");
        }
    ' "$herd_json" "$removed_path" "$replacement_path"
}

# --- registry (per worktrees root) + marker (per worktree) ----------------------

whd_registry_path() {
    printf '%s/%s' "$(whd_worktrees_root)" "$WHD_REGISTRY_BASENAME"
}

whd_read_registry_value() {
    local branch="$1"
    local field="$2"

    node -e "
        const fs = require('fs');
        const [path, branch, field] = process.argv.slice(1);
        if (!fs.existsSync(path)) process.exit(0);
        const data = JSON.parse(fs.readFileSync(path, 'utf8'));
        const entry = data[branch];
        if (entry && entry[field] !== undefined && entry[field] !== null) {
            process.stdout.write(String(entry[field]));
        }
    " "$(whd_registry_path)" "$branch" "$field"
}

whd_registry_branch_for_path() {
    local worktree_path="$1"

    node -e "
        const fs = require('fs');
        const [path, wt] = process.argv.slice(1);
        if (!fs.existsSync(path)) process.exit(0);
        const data = JSON.parse(fs.readFileSync(path, 'utf8'));
        for (const [branch, entry] of Object.entries(data)) {
            if (entry.path === wt) { process.stdout.write(branch); break; }
        }
    " "$(whd_registry_path)" "$worktree_path"
}

whd_write_registry_entry() {
    local branch="$1"
    local herd_site="$2"
    local vite_port="$3"
    local worktree_path="$4"
    local db_name="$5"

    node -e "
        const fs = require('fs');
        const [path, branch, site, port, wt, db] = process.argv.slice(1);
        const entry = { herd_site: site, vite_port: Number(port), path: wt };
        if (db) entry.db_name = db;
        let data = {};
        if (fs.existsSync(path)) {
            data = JSON.parse(fs.readFileSync(path, 'utf8'));
        }
        data[branch] = entry;
        fs.mkdirSync(require('path').dirname(path), { recursive: true });
        fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
    " "$(whd_registry_path)" "$branch" "$herd_site" "$vite_port" "$worktree_path" "$db_name"
}

whd_remove_registry_entry() {
    local branch="$1"

    node -e "
        const fs = require('fs');
        const [path, branch] = process.argv.slice(1);
        if (!fs.existsSync(path)) process.exit(0);
        const data = JSON.parse(fs.readFileSync(path, 'utf8'));
        delete data[branch];
        fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
    " "$(whd_registry_path)" "$branch"
}

whd_next_vite_port() {
    node -e "
        const fs = require('fs');
        const [registryPath, base] = process.argv.slice(1);
        const used = new Set([5173]);
        if (fs.existsSync(registryPath)) {
            const data = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
            for (const entry of Object.values(data)) {
                if (entry.vite_port) used.add(Number(entry.vite_port));
            }
        }
        let port = Number(base);
        while (used.has(port)) port += 1;
        process.stdout.write(String(port));
    " "$(whd_registry_path)" "$WHD_BASE_VITE_PORT"
}

whd_marker_path() {
    printf '%s/%s' "$1" "$WHD_MARKER_FILE"
}

whd_write_marker() {
    local worktree_path="$1"
    local branch="$2"
    local herd_site="$3"
    local vite_port="$4"
    local db_name="$5"
    local main_repo="$6"

    node -e "
        const fs = require('fs');
        const [path, branch, site, port, db, main] = process.argv.slice(1);
        const data = { herd_site: site, branch, vite_port: Number(port), db_name: db || null, main_repo: main };
        fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
    " "$(whd_marker_path "$worktree_path")" "$branch" "$herd_site" "$vite_port" "$db_name" "$main_repo"
}

whd_marker_value() {
    local worktree_path="$1"
    local field="$2"

    node -e "
        const fs = require('fs');
        const [path, field] = process.argv.slice(1);
        if (!fs.existsSync(path)) process.exit(0);
        try {
            const data = JSON.parse(fs.readFileSync(path, 'utf8'));
            if (data[field] !== undefined && data[field] !== null) {
                process.stdout.write(String(data[field]));
            }
        } catch (e) {}
    " "$(whd_marker_path "$worktree_path")" "$field"
}

# --- .env handling ---------------------------------------------------------------

whd_get_env_value() {
    local file="$1"
    local key="$2"

    [[ -f "$file" ]] || return 0
    # missing keys must yield empty, not a pipefail under the caller's set -e
    { grep -E "^${key}=" "$file" || true; } | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'"
}

# Atomic replace-or-append (temp file + rename); values may contain any character.
whd_set_env_value() {
    local file="$1"
    local key="$2"
    local value="$3"

    node -e "
        const fs = require('fs');
        const [file, key, value] = process.argv.slice(1);
        let text = '';
        try { text = fs.readFileSync(file, 'utf8'); } catch (e) {}
        const lines = text.split('\n');
        const prefix = key + '=';
        let found = false;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].startsWith(prefix)) { lines[i] = prefix + value; found = true; }
        }
        let out = lines.join('\n');
        if (!found) {
            if (out.length && !out.endsWith('\n')) out += '\n';
            out += prefix + value + '\n';
        }
        const tmp = file + '.tmp.' + process.pid;
        fs.writeFileSync(tmp, out);
        fs.renameSync(tmp, file);
    " "$file" "$key" "$value"
}

# --- dependencies / project commands ----------------------------------------------

whd_run_composer() {
    local worktree_path="$1"
    shift

    if command -v herd >/dev/null 2>&1; then
        (cd "$worktree_path" && herd composer "$@")
    else
        (cd "$worktree_path" && composer "$@")
    fi
}

whd_run_artisan() {
    local worktree_path="$1"
    shift

    if command -v herd >/dev/null 2>&1; then
        (cd "$worktree_path" && herd php artisan "$@")
    else
        (cd "$worktree_path" && php artisan "$@")
    fi
}

whd_detect_node_pm() {
    local dir="$1"

    if [[ -f "$dir/pnpm-lock.yaml" ]]; then
        printf 'pnpm'
    elif [[ -f "$dir/yarn.lock" ]]; then
        printf 'yarn'
    elif [[ -f "$dir/package.json" ]]; then
        printf 'npm'
    else
        printf ''
    fi
}

whd_install_node_dependencies() {
    local worktree_path="$1"
    local pm

    if [[ ! -f "$worktree_path/package.json" ]]; then
        return 0
    fi

    pm="$(whd_detect_node_pm "$worktree_path")"

    case "$pm" in
        pnpm)
            whd_log "Installing node dependencies (pnpm)..."
            (cd "$worktree_path" && pnpm install --frozen-lockfile)
            ;;
        yarn)
            whd_log "Installing node dependencies (yarn)..."
            (cd "$worktree_path" && yarn install --frozen-lockfile)
            ;;
        npm)
            whd_log "Installing node dependencies (npm)..."
            (cd "$worktree_path" && npm ci)
            ;;
    esac
}

whd_install_php_dependencies() {
    local worktree_path="$1"

    if [[ ! -f "$worktree_path/composer.json" ]]; then
        return 0
    fi

    whd_log "Installing composer dependencies..."
    whd_run_composer "$worktree_path" install --no-interaction
}

whd_has_npm_script() {
    local worktree_path="$1"
    local script="$2"

    [[ -f "$worktree_path/package.json" ]] || return 1
    node -e "
        const pkg = JSON.parse(require('fs').readFileSync(process.argv[1], 'utf8'));
        process.exit(pkg.scripts && pkg.scripts[process.argv[2]] ? 0 : 1);
    " "$worktree_path/package.json" "$script"
}

whd_build_assets() {
    local worktree_path="$1"
    local pm

    if ! whd_has_npm_script "$worktree_path" build; then
        whd_warn "No 'build' script in package.json; skipping asset build."
        return 0
    fi

    pm="$(whd_detect_node_pm "$worktree_path")"
    whd_log "Building assets ($pm run build)..."
    (cd "$worktree_path" && "$pm" run build)
}

# --- per-worktree database ----------------------------------------------------------

whd_db_driver() {
    whd_get_env_value "$1" DB_CONNECTION
}

# <main DB_DATABASE>_<slug with underscores>, clamped to 63 chars (postgres limit).
whd_db_name() {
    local main_env="$1"
    local slug="$2"
    local main_db name

    main_db="$(whd_get_env_value "$main_env" DB_DATABASE)"
    [[ -n "$main_db" ]] || return 0

    name="${main_db}_$(printf '%s' "$slug" | tr '-' '_' | tr '.' '_')"
    printf '%s' "$name" | cut -c1-63
}

whd_psql() {
    local env_file="$1"
    shift
    local host port user password
    host="$(whd_get_env_value "$env_file" DB_HOST)"
    port="$(whd_get_env_value "$env_file" DB_PORT)"
    user="$(whd_get_env_value "$env_file" DB_USERNAME)"
    password="$(whd_get_env_value "$env_file" DB_PASSWORD)"

    PGPASSWORD="$password" PAGER=cat psql \
        -h "${host:-127.0.0.1}" -p "${port:-5432}" -U "${user:-root}" -d postgres "$@"
}

whd_mysql() {
    local env_file="$1"
    shift
    local host port user password
    host="$(whd_get_env_value "$env_file" DB_HOST)"
    port="$(whd_get_env_value "$env_file" DB_PORT)"
    user="$(whd_get_env_value "$env_file" DB_USERNAME)"
    password="$(whd_get_env_value "$env_file" DB_PASSWORD)"

    MYSQL_PWD="$password" mysql \
        -h "${host:-127.0.0.1}" -P "${port:-3306}" -u "${user:-root}" "$@"
}

whd_create_database() {
    local env_file="$1"
    local db="$2"
    local driver

    driver="$(whd_db_driver "$env_file")"

    case "$driver" in
        pgsql)
            whd_require_command psql
            if whd_psql "$env_file" -tAc "SELECT 1 FROM pg_database WHERE datname = '${db}'" | grep -q 1; then
                whd_log "PostgreSQL database already exists: $db"
            else
                whd_log "Creating PostgreSQL database: $db"
                whd_psql "$env_file" -c "CREATE DATABASE \"${db}\";"
            fi
            ;;
        mysql | mariadb)
            whd_require_command mysql
            whd_log "Creating MySQL database: $db"
            whd_mysql "$env_file" -e "CREATE DATABASE IF NOT EXISTS \`${db}\`;"
            ;;
        *)
            whd_error "Per-worktree databases are not supported for DB_CONNECTION='${driver}' (supported: pgsql, mysql, mariadb, sqlite)."
            ;;
    esac
}

whd_show_pg_sessions() {
    local env_file="$1"
    local db="$2"

    echo "" >&2
    echo "Open sessions on database \"${db}\" (pg_stat_activity):" >&2
    whd_psql "$env_file" -v "db=${db}" -c "
SELECT pid, usename AS role, application_name,
       COALESCE(client_addr::text, '(local socket)') AS client,
       state, query_start,
       left(regexp_replace(COALESCE(query, ''), E'[[:space:]]+', ' ', 'g'), 120) AS query_preview
FROM pg_stat_activity
WHERE datname = :'db' AND pid <> pg_backend_pid()
ORDER BY query_start NULLS LAST;
" >&2 || echo "(Could not list sessions; check DB_HOST/DB_PORT/DB_USERNAME.)" >&2
}

whd_drop_database() {
    local env_file="$1"
    local db="$2"
    local driver

    driver="$(whd_db_driver "$env_file")"

    case "$driver" in
        pgsql)
            whd_require_command psql
            whd_log "Dropping PostgreSQL database: $db"
            if ! whd_psql "$env_file" -c "DROP DATABASE IF EXISTS \"${db}\";"; then
                whd_show_pg_sessions "$env_file" "$db"
                echo "" >&2
                echo "Disconnect the sessions above, then re-run. One-liner:" >&2
                echo "  psql ... -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${db}';\"" >&2
                exit 1
            fi
            ;;
        mysql | mariadb)
            whd_require_command mysql
            whd_log "Dropping MySQL database: $db"
            whd_mysql "$env_file" -e "DROP DATABASE IF EXISTS \`${db}\`;"
            ;;
        sqlite)
            : # database file lives inside the worktree and is removed with it
            ;;
        *)
            whd_warn "Unknown DB_CONNECTION '${driver}'; database '$db' was not dropped."
            ;;
    esac
}

# --- worktree state checks -----------------------------------------------------------

whd_is_registered_worktree() {
    local main_root="$1"
    local path="$2"
    git -C "$main_root" worktree list --porcelain \
        | awk -v p="$path" '$1 == "worktree" && substr($0, 10) == p { found = 1 } END { exit(found ? 0 : 1) }'
}

# Dirty check that ignores the artifacts this tool itself creates in a worktree
# (the marker and a generated herd.yml). Tracked modifications and any other
# untracked files still count as dirty.
whd_worktree_is_dirty() {
    local path="$1"
    git -C "$path" status --porcelain 2>/dev/null \
        | grep -vE "(\.worktree-herd\.json|herd\.yml)$" \
        | grep -q .
}
