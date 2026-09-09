#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

curl -sL "https://www.gutenberg.org/cache/epub/3176/pg3176.txt" -o en-twain-innocents-abroad.txt
sed -i '' '1,/START OF THE PROJECT GUTENBERG/d' en-twain-innocents-abroad.txt 2>/dev/null || sed -i '1,/START OF THE PROJECT GUTENBERG/d' en-twain-innocents-abroad.txt
ls -la
