#!/usr/bin/env bash

set -euo pipefail

resolve_script_dir() {
    local source="${BASH_SOURCE[1]:-${BASH_SOURCE[0]}}"

    while [[ -L "$source" ]]; do
        local dir
        dir="$(cd "$(dirname "$source")" && pwd)"
        source="$(readlink "$source")"
        [[ "$source" != /* ]] && source="$dir/$source"
    done

    cd "$(dirname "$source")" && pwd
}

SCRIPT_DIR="$(resolve_script_dir)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

usage() {
    cat <<'EOF'
Usage: worktree-herd-setup [options] [branch-name] [herd-site]

Set up a git worktree with a dedicated Herd site, Vite port, and optionally
its own database. Project defaults come from worktree-herd.yml in the main
repo root (see the skill's reference.md); flags override config.

Arguments:
  branch-name   Git branch (required when run from the main repo)
  herd-site     Herd site name without the TLD (optional, auto-derived)

Options:
  --current       Configure Herd for the current worktree workspace
  --create        Create the branch if it does not exist yet
  --base <ref>    Base branch for --create (default: config base_branch,
                  then origin's default branch, then current HEAD)
  --db / --no-db  Force per-worktree database on/off (default: config
                  'database: per-worktree|shared', shared if unset)
  --no-install    Skip composer and node dependency installation
  --build / --no-build
                  Force asset build on/off (default: config build_assets)
  --no-secure     Link without HTTPS (APP_URL stays http://...)
  --open          Open the worktree in your editor (config 'editor:', default cursor)
  -h, --help      Show this help message
EOF
}

# --- rollback: undo everything this run created if setup fails -------------------

ROLLBACK_WORKTREE=""
ROLLBACK_SITE=""
ROLLBACK_DOMAIN=""
ROLLBACK_BRANCH=""
ROLLBACK_DB_ENV=""
ROLLBACK_DB_NAME=""
did_worktree=0
did_link=0
did_registry=0
did_db=0

rollback_on_failure() {
    local exit_code="$?"
    if [[ "$exit_code" -eq 0 ]]; then
        return 0
    fi

    whd_warn "Setup failed — rolling back what this run created."

    if [[ "$did_db" -eq 1 && -n "$ROLLBACK_DB_NAME" ]]; then
        whd_drop_database "$ROLLBACK_DB_ENV" "$ROLLBACK_DB_NAME" || true
    fi

    if [[ "$did_link" -eq 1 ]] && command -v herd >/dev/null 2>&1; then
        herd unsecure "$ROLLBACK_DOMAIN" --silent 2>/dev/null || true
        herd unlink "$ROLLBACK_SITE" 2>/dev/null || true
    fi

    if [[ "$did_registry" -eq 1 ]]; then
        whd_remove_registry_entry "$ROLLBACK_BRANCH" || true
    fi

    if [[ "$did_worktree" -eq 1 && -n "$ROLLBACK_WORKTREE" ]]; then
        git -C "$(whd_main_repo_root)" worktree remove --force "$ROLLBACK_WORKTREE" 2>/dev/null || true
    fi

    return "$exit_code"
}

# --- helpers ---------------------------------------------------------------------

resolve_base_ref() {
    local main_root="$1"
    local base="$2"

    if [[ -z "$base" ]]; then
        base="$(whd_config_value base_branch)"
    fi

    if [[ -z "$base" ]]; then
        # origin's default branch, e.g. refs/remotes/origin/main -> main
        base="$({ git -C "$main_root" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null || true; } | sed 's|.*/||')"
    fi

    if [[ -z "$base" ]]; then
        printf 'HEAD'
        return 0
    fi

    if git -C "$main_root" show-ref --verify --quiet "refs/remotes/origin/${base}"; then
        printf 'origin/%s' "$base"
    elif git -C "$main_root" show-ref --verify --quiet "refs/heads/${base}"; then
        printf '%s' "$base"
    else
        whd_error "Base branch '${base}' not found locally or on origin."
    fi
}

# Sets did_worktree/ROLLBACK_WORKTREE, so it must run in the main shell —
# never inside a command substitution (a subshell would lose the rollback state).
ensure_worktree() {
    local main_root="$1"
    local branch="$2"
    local create_branch="$3"
    local base="$4"
    local absolute_path="$5"
    local base_ref

    if whd_is_registered_worktree "$main_root" "$absolute_path"; then
        whd_log "Worktree already exists: $absolute_path"
        return 0
    fi

    if [[ -e "$absolute_path" ]]; then
        whd_error "Path exists but is not a registered worktree: $absolute_path"
    fi

    mkdir -p "$(dirname "$absolute_path")"

    git -C "$main_root" fetch origin --quiet 2>/dev/null \
        || whd_warn "git fetch failed (offline?); using local refs."

    if git -C "$main_root" show-ref --verify --quiet "refs/heads/$branch"; then
        whd_log "Creating worktree for existing branch: $branch"
        git -C "$main_root" worktree add "$absolute_path" "$branch" >&2
    elif git -C "$main_root" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        whd_log "Creating worktree tracking origin/$branch"
        git -C "$main_root" worktree add -b "$branch" "$absolute_path" "origin/$branch" >&2
    elif [[ "$create_branch" == "true" ]]; then
        base_ref="$(resolve_base_ref "$main_root" "$base")"
        whd_log "Creating new branch '$branch' from $base_ref"
        git -C "$main_root" worktree add -b "$branch" "$absolute_path" "$base_ref" >&2
    else
        whd_error "Branch '$branch' not found locally or on origin. Use --create to make a new branch."
    fi

    did_worktree=1
    ROLLBACK_WORKTREE="$absolute_path"
}

# Re-running setup for a branch must not trip the collision guard on its own site.
site_belongs_to_branch() {
    local site="$1"
    local branch="$2"
    local worktree_path="$3"

    [[ "$(whd_read_registry_value "$branch" herd_site)" == "$site" ]] && return 0
    [[ -d "$worktree_path" && "$(whd_marker_value "$worktree_path" herd_site)" == "$site" ]] && return 0
    return 1
}

resolve_site() {
    local main_root="$1"
    local branch="$2"
    local explicit_site="$3"
    local tld="$4"
    local worktree_path="$5"
    local site suffix slug colliding_site

    if [[ -n "$explicit_site" ]]; then
        site="$explicit_site"
        if ! site_belongs_to_branch "$site" "$branch" "$worktree_path"; then
            if whd_herd_has_link "$site" || whd_herd_has_secured "${site}.${tld}"; then
                whd_error "Herd site '${site}' already exists. Pick another name or clean up the existing site first."
            fi
        fi
        printf '%s' "$site"
        return 0
    fi

    site="$(whd_default_herd_site "$main_root" "$branch" "$tld")"

    if site_belongs_to_branch "$site" "$branch" "$worktree_path"; then
        printf '%s' "$site"
        return 0
    fi

    if whd_herd_has_link "$site" || whd_herd_has_secured "${site}.${tld}"; then
        suffix="$(whd_detect_herd_domain_suffix "$main_root" "$tld")"
        slug="$(whd_hashed_slug "$(whd_slugify_branch "$branch")" "$branch")"
        colliding_site="$site"
        site="$(whd_join_site "$slug" "$suffix")"
        whd_warn "Herd site '${colliding_site}' already exists; using '${site}' instead."

        if ! site_belongs_to_branch "$site" "$branch" "$worktree_path" \
            && { whd_herd_has_link "$site" || whd_herd_has_secured "${site}.${tld}"; }; then
            whd_error "Fallback site '${site}' also exists. Pass an explicit herd-site name."
        fi
    fi

    printf '%s' "$site"
}

configure_env() {
    local main_root="$1"
    local worktree_path="$2"
    local herd_site="$3"
    local domain="$4"
    local vite_port="$5"
    local secure="$6"
    local db_name="$7"
    local env_file="$worktree_path/.env"
    local main_env="$main_root/.env"
    local scheme="https"

    [[ "$secure" == "true" ]] || scheme="http"

    if [[ ! -f "$env_file" ]]; then
        if [[ -f "$main_env" ]]; then
            cp "$main_env" "$env_file"
        elif [[ -f "$worktree_path/.env.example" ]]; then
            cp "$worktree_path/.env.example" "$env_file"
        else
            whd_error "No .env or .env.example found to copy."
        fi
    fi

    whd_set_env_value "$env_file" "APP_URL" "${scheme}://${domain}"
    whd_set_env_value "$env_file" "VITE_PORT" "$vite_port"
    whd_set_env_value "$env_file" "SESSION_COOKIE" "$(printf '%s' "$herd_site" | tr '.-' '__')_session"

    whd_log "APP_URL set to ${scheme}://${domain}"
    whd_log "VITE_PORT set to $vite_port"

    if [[ -n "$db_name" ]]; then
        local driver
        driver="$(whd_db_driver "$env_file")"
        if [[ "$driver" == "sqlite" ]]; then
            mkdir -p "$worktree_path/database"
            touch "$worktree_path/database/database.sqlite"
            whd_set_env_value "$env_file" "DB_DATABASE" "$worktree_path/database/database.sqlite"
            whd_log "DB_DATABASE set to a per-worktree sqlite file"
        else
            whd_set_env_value "$env_file" "DB_DATABASE" "$db_name"
            whd_log "DB_DATABASE set to $db_name"
        fi
    fi
}

write_herd_yml() {
    local worktree_path="$1"
    local herd_site="$2"
    local php_version="$3"

    # A herd.yml tracked in the repo already ships with the worktree; overwriting
    # it would dirty the tree. herd link gets the site name explicitly anyway.
    if [[ -f "$worktree_path/herd.yml" ]]; then
        return 0
    fi

    cat >"$worktree_path/herd.yml" <<EOF
name: ${herd_site}
php: '${php_version}'
secured: true
aliases:
  - ${herd_site}
services: {  }
integrations:
  forge: {  }
EOF
}

link_herd_site() {
    local worktree_path="$1"
    local herd_site="$2"
    local php_version="$3"
    local secure="$4"
    local secure_flag=""

    [[ "$secure" == "true" ]] && secure_flag="--secure"

    whd_log "Linking Herd site: ${herd_site}"
    (
        cd "$worktree_path"
        # shellcheck disable=SC2086
        herd link $secure_flag --update-env --isolate="$php_version" "$herd_site"
    )
}

open_editor() {
    local worktree_path="$1"
    local editor

    editor="$(whd_config_value editor cursor)"

    case "$editor" in
        none) return 0 ;;
        cursor)
            if command -v cursor >/dev/null 2>&1; then
                cursor "$worktree_path"
            else
                open -a "Cursor" "$worktree_path" 2>/dev/null \
                    || whd_warn "Cursor not found; open $worktree_path manually."
            fi
            ;;
        code | vscode)
            if command -v code >/dev/null 2>&1; then
                code "$worktree_path"
            else
                open -a "Visual Studio Code" "$worktree_path" 2>/dev/null \
                    || whd_warn "VS Code not found; open $worktree_path manually."
            fi
            ;;
        *)
            "$editor" "$worktree_path" || whd_warn "Could not open editor '$editor'."
            ;;
    esac
}

setup_worktree() {
    local main_root="$1"
    local branch="$2"
    local explicit_site="$3"
    local create_branch="$4"
    local base="$5"
    local db_mode="$6"
    local no_install="$7"
    local build_mode="$8"
    local secure="$9"
    local open_after="${10}"
    local current_mode="${11}"

    local tld domain site worktree_path vite_port php_version db_name="" env_file
    local dev_command="composer run dev"

    tld="$(whd_herd_tld)"
    php_version="$(whd_detect_php_version "$main_root")"

    if [[ "$current_mode" == "true" ]]; then
        worktree_path="$(whd_repo_root)"
    else
        worktree_path="$(whd_worktrees_root)/$branch"
    fi

    site="$(resolve_site "$main_root" "$branch" "$explicit_site" "$tld" "$worktree_path")"
    domain="${site}.${tld}"

    ROLLBACK_SITE="$site"
    ROLLBACK_DOMAIN="$domain"
    ROLLBACK_BRANCH="$branch"
    trap rollback_on_failure EXIT

    if [[ "$current_mode" != "true" ]]; then
        ensure_worktree "$main_root" "$branch" "$create_branch" "$base" "$worktree_path"
    fi

    env_file="$worktree_path/.env"

    vite_port="$(whd_read_registry_value "$branch" "vite_port")"
    if [[ -z "$vite_port" ]]; then
        vite_port="$(whd_next_vite_port)"
    fi

    if [[ "$db_mode" == "per-worktree" ]]; then
        db_name="$(whd_db_name "$main_root/.env" "$(whd_slugify_branch "$branch")")"
        local main_driver
        main_driver="$(whd_db_driver "$main_root/.env")"
        if [[ "$main_driver" != "sqlite" && -z "$db_name" ]]; then
            whd_error "database: per-worktree needs DB_DATABASE in the main repo's .env."
        fi
        [[ "$main_driver" == "sqlite" ]] && db_name="sqlite"
    fi

    configure_env "$main_root" "$worktree_path" "$site" "$domain" "$vite_port" "$secure" "$db_name"

    # sqlite has no server-side database to create or drop later
    [[ "$db_name" == "sqlite" ]] && db_name=""

    if [[ -z "$(whd_read_registry_value "$branch" herd_site)" ]]; then
        did_registry=1
    fi
    whd_write_registry_entry "$branch" "$site" "$vite_port" "$worktree_path" "$db_name"
    whd_write_marker "$worktree_path" "$branch" "$site" "$vite_port" "$db_name" "$main_root"

    write_herd_yml "$worktree_path" "$site" "$php_version"
    link_herd_site "$worktree_path" "$site" "$php_version" "$secure"
    did_link=1

    if [[ "$no_install" != "true" ]]; then
        whd_install_php_dependencies "$worktree_path"
        whd_install_node_dependencies "$worktree_path"
    fi

    if [[ -f "$worktree_path/artisan" ]]; then
        whd_run_artisan "$worktree_path" storage:link 2>/dev/null || true
    fi

    if [[ -n "$db_name" ]]; then
        ROLLBACK_DB_ENV="$env_file"
        ROLLBACK_DB_NAME="$db_name"
        whd_create_database "$env_file" "$db_name"
        did_db=1
        whd_log "Running migrations..."
        whd_run_artisan "$worktree_path" migrate --force
    fi

    if [[ "$build_mode" == "true" ]]; then
        whd_build_assets "$worktree_path"
    fi

    export WHD_WORKTREE_PATH="$worktree_path"
    export WHD_BRANCH="$branch"
    export WHD_HERD_SITE="$site"
    export WHD_HERD_DOMAIN="$domain"
    export WHD_VITE_PORT="$vite_port"
    export WHD_DB_NAME="$db_name"
    export WHD_MAIN_REPO="$main_root"
    whd_run_hook "$(whd_hook_path post_setup)" "$worktree_path"

    trap - EXIT

    if [[ ! -f "$worktree_path/composer.json" ]]; then
        dev_command="pnpm run dev"
    fi

    local scheme="https"
    [[ "$secure" == "true" ]] || scheme="http"

    cat <<EOF

✓ Worktree ready

  Branch:     $branch
  Path:       $worktree_path
  Browser:    ${scheme}://${domain}
  Vite port:  $vite_port
EOF
    if [[ -n "$db_name" ]]; then
        printf '  Database:   %s\n' "$db_name"
    fi
    cat <<EOF

Start the dev server in this worktree:
  cd "$worktree_path" && $dev_command

EOF

    if [[ "$open_after" == "true" ]]; then
        open_editor "$worktree_path"
    fi
}

main() {
    local use_current="false"
    local create_branch="false"
    local branch=""
    local herd_site=""
    local base=""
    local db_flag=""
    local no_install="false"
    local build_flag=""
    local secure="true"
    local open_after="false"

    whd_require_command git
    whd_require_command herd
    whd_require_command node

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --current) use_current="true"; shift ;;
            --create) create_branch="true"; shift ;;
            --base)
                [[ $# -ge 2 ]] || whd_error "--base needs a branch name"
                base="$2"
                shift 2
                ;;
            --db) db_flag="per-worktree"; shift ;;
            --no-db) db_flag="shared"; shift ;;
            --no-install) no_install="true"; shift ;;
            --build) build_flag="true"; shift ;;
            --no-build) build_flag="false"; shift ;;
            --no-secure) secure="false"; shift ;;
            --open) open_after="true"; shift ;;
            -h | --help)
                usage
                exit 0
                ;;
            -*)
                whd_error "Unknown option: $1"
                ;;
            *)
                if [[ -z "$branch" ]]; then
                    branch="$1"
                elif [[ -z "$herd_site" ]]; then
                    herd_site="$1"
                else
                    whd_error "Too many arguments. Use --help for usage."
                fi
                shift
                ;;
        esac
    done

    local main_root db_mode build_mode
    main_root="$(whd_main_repo_root)"

    db_mode="${db_flag:-$(whd_config_value database shared)}"
    build_mode="${build_flag:-$(whd_config_value build_assets false)}"
    [[ "$build_mode" == "true" ]] || build_mode="false"

    if [[ "$db_mode" != "per-worktree" && "$db_mode" != "shared" ]]; then
        whd_error "Invalid database mode '${db_mode}' (use 'per-worktree' or 'shared')."
    fi

    if [[ "$use_current" == "true" ]]; then
        if whd_is_main_worktree; then
            whd_error "You are in the main workspace. Pass a branch name or open a worktree workspace first."
        fi
        branch="$(whd_resolve_branch_from_current)"
        setup_worktree "$main_root" "$branch" "$herd_site" "false" "$base" "$db_mode" \
            "$no_install" "$build_mode" "$secure" "$open_after" "true"
        exit 0
    fi

    if [[ -z "$branch" ]]; then
        if whd_is_main_worktree; then
            usage
            exit 1
        fi
        # Run from inside a worktree without arguments: configure this workspace.
        branch="$(whd_resolve_branch_from_current)"
        setup_worktree "$main_root" "$branch" "$herd_site" "false" "$base" "$db_mode" \
            "$no_install" "$build_mode" "$secure" "$open_after" "true"
        exit 0
    fi

    setup_worktree "$main_root" "$branch" "$herd_site" "$create_branch" "$base" "$db_mode" \
        "$no_install" "$build_mode" "$secure" "$open_after" "false"
}

main "$@"
