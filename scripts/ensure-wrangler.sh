#!/usr/bin/env bash
set -euo pipefail

MIN_WRANGLER="4.107.0"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "wrangler not found; installing wrangler@$MIN_WRANGLER globally..."
  npm install -g "wrangler@$MIN_WRANGLER"
  exit 0
fi

CURRENT=$(wrangler --version | head -n1 | tr -d 'v')
if [ "$(printf '%s\n' "$MIN_WRANGLER" "$CURRENT" | sort -V | head -n1)" != "$MIN_WRANGLER" ]; then
  echo "wrangler $CURRENT < $MIN_WRANGLER; upgrading..."
  npm install -g "wrangler@$MIN_WRANGLER"
else
  echo "wrangler $CURRENT OK"
fi
