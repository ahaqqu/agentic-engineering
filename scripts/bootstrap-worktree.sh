#!/usr/bin/env bash
set -euo pipefail

WT_DIR="${1:-}"
if [ -z "$WT_DIR" ]; then
  echo "Usage: $0 <worktree-directory>"
  exit 1
fi

MAIN_ROOT=$(git rev-parse --show-toplevel)

if [ -f "$MAIN_ROOT/.dev.vars" ]; then
  cp "$MAIN_ROOT/.dev.vars" "$WT_DIR/.dev.vars"
  echo "Copied .dev.vars from main worktree"
elif [ -f "$MAIN_ROOT/.dev.vars.example" ]; then
  cp "$MAIN_ROOT/.dev.vars.example" "$WT_DIR/.dev.vars"
  echo "Copied .dev.vars.example (no .dev.vars found in main worktree)"
else
  echo "No .dev.vars or .dev.vars.example found"
  exit 1
fi
