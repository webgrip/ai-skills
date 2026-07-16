#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

mkdir -p "$BIN_DIR"

link_script() {
    local source="$1"
    local name="$2"
    local target="$BIN_DIR/$name"

    chmod +x "$source"
    ln -sf "$source" "$target"
    printf '  ✓ %s -> %s\n' "$name" "$target"
}

cat <<'EOF'
Installing Worktree Herd Dev
EOF

link_script "$SCRIPT_DIR/worktree-herd-setup.sh" "worktree-herd-setup"
link_script "$SCRIPT_DIR/worktree-herd-cleanup.sh" "worktree-herd-cleanup"
link_script "$SCRIPT_DIR/install-project-tasks.sh" "worktree-herd-install-tasks"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    cat <<EOF

Note: $BIN_DIR is not on your PATH.
Add this to ~/.zshrc:

  export PATH="\$HOME/.local/bin:\$PATH"

EOF
fi

cat <<'EOF'

Done. Usage:

  worktree-herd-setup <branch> [herd-site]
  worktree-herd-setup --current
  worktree-herd-cleanup <branch>
  worktree-herd-cleanup --current

Install editor tasks into a project:

  worktree-herd-install-tasks /path/to/project

EOF
