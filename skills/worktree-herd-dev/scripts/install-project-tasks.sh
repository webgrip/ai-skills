#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
    printf 'Usage: worktree-herd-install-tasks <project-path>\n' >&2
    exit 1
fi

PROJECT_PATH="$(cd "$1" && pwd)"
TASKS_DIR="$PROJECT_PATH/.vscode"
TASKS_FILE="$TASKS_DIR/tasks.json"

mkdir -p "$TASKS_DIR"

cat >"$TASKS_FILE" <<'EOF'
{
  "version": "2.0.0",
  "inputs": [
    {
      "id": "worktreeBranch",
      "type": "promptString",
      "description": "Git branch name"
    },
    {
      "id": "worktreeHerdSite",
      "type": "promptString",
      "description": "Herd site (optional, e.g. my-feature.example)"
    }
  ],
  "tasks": [
    {
      "label": "Worktree: set up (Herd)",
      "type": "shell",
      "command": "worktree-herd-setup",
      "args": [
        "${input:worktreeBranch}",
        "${input:worktreeHerdSite}"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    },
    {
      "label": "Worktree: set up current workspace (Herd)",
      "type": "shell",
      "command": "worktree-herd-setup",
      "args": ["--current"],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    },
    {
      "label": "Worktree: clean up (Herd)",
      "type": "shell",
      "command": "worktree-herd-cleanup",
      "args": ["${input:worktreeBranch}"],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    },
    {
      "label": "Worktree: clean up current workspace (Herd)",
      "type": "shell",
      "command": "worktree-herd-cleanup",
      "args": ["--current"],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    }
  ]
}
EOF

printf '✓ Editor tasks installed at %s\n' "$TASKS_FILE"
printf '  Run via: Tasks: Run Task (VS Code / Cursor)\n'
