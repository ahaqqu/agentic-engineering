#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Ensure wrangler is new enough for compatibility_date in wrangler.toml.
./scripts/ensure-wrangler.sh

# Kill stale local dev servers from previous runs.
pkill -f "wrangler dev" 2>/dev/null || true
pkill -f "pywrangler dev" 2>/dev/null || true
pkill -f "workerd" 2>/dev/null || true
sleep 1

echo "=== ruff check ==="
uv run ruff check src/ features/
echo "=== ruff format check ==="
uv run ruff format --check src/ features/
echo "=== pyright ==="
uv run pyright
echo "=== pytest ==="
uv run pytest

echo "All checks passed"
