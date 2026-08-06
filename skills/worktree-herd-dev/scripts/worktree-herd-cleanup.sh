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
Usage: worktree-herd-cleanup [options] [branch-or-path]

Remove a worktree, its Herd link/cert, its database (if this tool created
one), and its registry entry. Teardown order: hook -> Herd -> database ->
git worktree. The Herd site name is read from the worktree's marker file
(.worktree-herd.json) or the registry -- never guessed.

Arguments:
  branch-or-path  Git branch, or a path to the worktree (optional in a
                  worktree workspace)

Options:
  --current     Clean up the current worktree workspace
  --dry-run     Print what would happen without doing anything
  --yes         Skip the confirmation prompt
  -f, --force   Remove even if the worktree has uncommitted changes
  --keep-herd   Do not touch Herd (no unsecure/unlink)
  --keep-db     Do not drop the per-worktree database
  -h, --help    Show this help message
EOF
}

confirm() {
    local prompt="$1"
    read -r -p "$prompt [y/N] " answer
    [[ "$answer" == "y" || "$answer" == "Y" ]]
}

main() {
    local use_current="false"
    local dry_run="false"
    local assume_yes="false"
    local force="false"
    local keep_herd="false"
    local keep_db="false"
    local target=""

    whd_require_command git
    whd_require_command node

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --current) use_current="true"; shift ;;
            --dry-run) dry_run="true"; shift ;;
            --yes) assume_yes="true"; shift ;;
            -f | --force) force="true"; shift ;;
            --keep-herd) keep_herd="true"; shift ;;
            --keep-db) keep_db="true"; shift ;;
            -h | --help)
                usage
                exit 0
                ;;
            -*)
                whd_error "Unknown option: $1"
                ;;
            *)
                if [[ -z "$target" ]]; then
                    target="$1"
                else
                    whd_error "Too many arguments. Use --help for usage."
                fi
                shift
                ;;
        esac
    done

    local main_root worktree_path branch=""
    main_root="$(whd_main_repo_root)"

    # --- resolve the target worktree ------------------------------------------

    if [[ "$use_current" == "true" || ( -z "$target" && "$(whd_is_main_worktree && echo main || echo wt)" == "wt" ) ]]; then
        if whd_is_main_worktree; then
            whd_error "You are in the main workspace. Pass a branch name or run from a worktree."
        fi
        use_current="true"
        branch="$(whd_resolve_branch_from_current)"
        worktree_path="$(whd_repo_root)"
    elif [[ -z "$target" ]]; then
        whd_error "Pass a branch name, a worktree path, or --current from a worktree workspace."
    elif [[ -d "$target" ]]; then
        worktree_path="$(cd "$target" && pwd)"
        branch="$(whd_marker_value "$worktree_path" branch)"
        if [[ -z "$branch" ]]; then
            branch="$(whd_registry_branch_for_path "$worktree_path")"
        fi
        if [[ -z "$branch" ]]; then
            branch="$(git -C "$worktree_path" branch --show-current 2>/dev/null || true)"
        fi
    else
        branch="$target"
        worktree_path="$(whd_read_registry_value "$branch" "path")"
        if [[ -z "$worktree_path" ]]; then
            worktree_path="$(whd_worktrees_root)/$branch"
        fi
    fi

    if [[ ! -d "$worktree_path" ]]; then
        whd_error "Worktree not found: $worktree_path"
    fi

    if [[ "$worktree_path" == "$main_root" ]]; then
        whd_error "Refusing to remove the main repo: $worktree_path"
    fi

    if ! whd_is_registered_worktree "$main_root" "$worktree_path"; then
        whd_error "Refusing to remove: not a registered git worktree of $main_root (see 'git worktree list')."
    fi

    # --- resolve Herd site and database: marker -> registry -> refuse ----------

    local site="" db_name="" tld domain=""
    tld="$(whd_herd_tld)"

    site="$(whd_marker_value "$worktree_path" herd_site)"
    if [[ -z "$site" && -n "$branch" ]]; then
        site="$(whd_read_registry_value "$branch" "herd_site")"
    fi

    if [[ -z "$site" && "$keep_herd" != "true" ]]; then
        whd_error "Cannot determine the Herd site (no marker, no registry entry). Refusing to guess; pass --keep-herd and unlink manually, or restore $WHD_MARKER_FILE."
    fi

    [[ -n "$site" ]] && domain="${site}.${tld}"

    db_name="$(whd_marker_value "$worktree_path" db_name)"
    if [[ -z "$db_name" && -n "$branch" ]]; then
        db_name="$(whd_read_registry_value "$branch" "db_name")"
    fi

    local hook
    hook="$(whd_hook_path pre_cleanup)"

    # --- dry run ----------------------------------------------------------------

    if [[ "$dry_run" == "true" ]]; then
        echo "Would remove worktree: $worktree_path (branch: ${branch:-unknown})"
        if [[ -x "$hook" ]]; then
            echo "Would run pre-cleanup hook: $hook"
        fi
        if [[ "$keep_herd" != "true" && -n "$site" ]]; then
            echo "Would run: herd unsecure $domain"
            echo "Would run: herd unlink $site"
            echo "Would prune Herd CA-bundle entries for $domain (plus orphans) and reset herd.json lastSite"
        fi
        if [[ "$keep_db" != "true" && -n "$db_name" ]]; then
            echo "Would drop database: $db_name"
        fi
        echo "Would run: git -C \"$main_root\" worktree remove \"$worktree_path\""
        if [[ -n "$branch" ]]; then
            echo "Would remove registry entry for: $branch"
        fi
        exit 0
    fi

    if [[ "$keep_herd" != "true" ]]; then
        whd_require_command herd
    fi

    # --- confirm + dirty-tree ladder ---------------------------------------------

    if [[ "$assume_yes" != "true" ]]; then
        cat <<EOF
This removes:

  Branch:    ${branch:-unknown}
  Path:      $worktree_path
EOF
        [[ "$keep_herd" != "true" && -n "$site" ]] && printf '  Herd:      %s\n' "$domain"
        [[ "$keep_db" != "true" && -n "$db_name" ]] && printf '  Database:  %s\n' "$db_name"
        echo ""
        if ! confirm "Continue?"; then
            whd_log "Aborted."
            exit 0
        fi
    fi

    if whd_worktree_is_dirty "$worktree_path"; then
        if [[ "$force" == "true" ]]; then
            :
        elif [[ "$assume_yes" == "true" ]]; then
            whd_error "Worktree has uncommitted or untracked files; refusing with --yes alone. Re-run with --force, or clean the worktree first."
        elif confirm "Worktree has local changes that will be DELETED. Force-remove?"; then
            force="true"
        else
            whd_error "Aborted. Commit/stash the changes or pass --force."
        fi
    fi

    # A process holding files under the worktree (dev server, editor, queue
    # worker) would leave a half-removed state. Unavoidable in --current mode,
    # where your own shell/editor is inside the worktree.
    if [[ "$use_current" != "true" ]] && command -v lsof >/dev/null 2>&1; then
        if lsof +D "$worktree_path" >/dev/null 2>&1; then
            whd_error "Worktree is in use (open files under $worktree_path). Stop dev servers and close editors/terminals there, then retry."
        fi
    fi

    cd "$main_root"

    # --- teardown: hook -> Herd -> database -> worktree -> registry ---------------

    export WHD_WORKTREE_PATH="$worktree_path"
    export WHD_BRANCH="$branch"
    export WHD_HERD_SITE="$site"
    export WHD_HERD_DOMAIN="$domain"
    export WHD_DB_NAME="$db_name"
    export WHD_MAIN_REPO="$main_root"
    whd_run_hook "$hook" "$worktree_path"

    if [[ "$keep_herd" != "true" && -n "$site" ]]; then
        if whd_herd_has_secured "$domain"; then
            whd_log "Removing Herd cert: $domain"
            herd unsecure "$domain" --silent
        fi

        if whd_herd_has_link "$site"; then
            whd_log "Unlinking Herd site: $site"
            herd unlink "$site"
        fi

        if whd_herd_has_secured "$domain" || whd_herd_has_link "$site"; then
            whd_error "Herd still lists ${site}; fix Herd first (the worktree was NOT removed, so nginx/TLS config stays valid)."
        fi

        whd_prune_herd_cacert "$domain"
        whd_prune_herd_last_site "$worktree_path" "$main_root"
    fi

    if [[ "$keep_db" != "true" && -n "$db_name" ]]; then
        whd_drop_database "$worktree_path/.env" "$db_name"
    fi

    # Remove our own artifacts so a clean tree passes git's own dirty check;
    # anything else still triggers it unless the ladder set --force.
    rm -f "$(whd_marker_path "$worktree_path")"
    if [[ -f "$worktree_path/herd.yml" ]] \
        && ! git -C "$worktree_path" ls-files --error-unmatch herd.yml >/dev/null 2>&1; then
        rm -f "$worktree_path/herd.yml"
    fi

    whd_log "Removing git worktree: $worktree_path"
    if [[ "$force" == "true" ]]; then
        git -C "$main_root" worktree remove --force "$worktree_path"
    else
        git -C "$main_root" worktree remove "$worktree_path"
    fi
    git -C "$main_root" worktree prune

    if [[ -n "$branch" ]]; then
        whd_remove_registry_entry "$branch"
    fi

    cat <<EOF

✓ Worktree cleaned up

  Branch:  ${branch:-unknown}
  Path:    $worktree_path removed
EOF
    [[ "$keep_herd" != "true" && -n "$site" ]] && printf '  Herd:    %s removed\n' "$domain"
    [[ "$keep_db" != "true" && -n "$db_name" ]] && printf '  Database: %s dropped\n' "$db_name"
    echo ""

    if [[ "$use_current" == "true" ]]; then
        whd_warn "Your shell's directory no longer exists — cd somewhere else."
    fi
}

main "$@"
