#!/bin/sh
PROTECTED_PATHS="${PROTECTED_PATHS:-public/build/|_ide_helper}"
command=$(jq -r '.tool_input.command // empty')
if printf '%s' "$command" | grep -Eq "(sed -i|>|tee|cp|mv|rm)[^|;&]*(${PROTECTED_PATHS})"; then
  echo "That path is generated. Change its source and rerun the generator instead." >&2
  exit 2
fi
exit 0
