#!/usr/bin/env bash
# scripts/deploy.sh — end-to-end quality-gated deploy to Cloudflare Workers.
#
# Mirrors the CI pipeline (docs/TESTING_AND_QUALITY_SPEC.md):
#   preflight → install → lint → typecheck → BDD tests → D1 migrations → deploy → health check
#
# Usage:
#   ./scripts/deploy.sh                       # full gate + deploy
#   ./scripts/deploy.sh --skip-tests          # skip BDD suite (hotfix only; discouraged)
#   ./scripts/deploy.sh --dry-run             # run every gate, stop before deploy
#   ./scripts/deploy.sh --allow-dirty         # permit uncommitted changes
#   HEALTH_URL=https://app.example.com/health ./scripts/deploy.sh
#
# Requirements: git, node, pnpm (the only supported package manager), curl.
# CLOUDFLARE_API_TOKEN for non-interactive auth (otherwise wrangler's session is used).

set -euo pipefail

# ---------- pretty printing ----------------------------------------------------
step()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m ✓ %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31m ✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ---------- flags ---------------------------------------------------------------
SKIP_TESTS=false DRY_RUN=false ALLOW_DIRTY=false
for arg in "$@"; do
  case "$arg" in
    --skip-tests)  SKIP_TESTS=true ;;
    --dry-run)     DRY_RUN=true ;;
    --allow-dirty) ALLOW_DIRTY=true ;;
    *) fail "unknown flag: $arg" ;;
  esac
done

# ---------- locate project root -------------------------------------------------
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || fail "not inside a git repository"
cd "$ROOT"
[[ -f package.json ]]  || fail "package.json not found at repo root ($ROOT)"
[[ -f wrangler.toml || -f wrangler.jsonc || -f wrangler.json ]] || fail "wrangler config not found"

# ---------- package manager: pnpm only ------------------------------------------
command -v pnpm >/dev/null || fail "pnpm not installed (corepack enable && corepack prepare pnpm@latest --activate)"
[[ -f pnpm-lock.yaml ]] || fail "pnpm-lock.yaml missing — this template is pnpm-only; commit the lockfile"
RUN="pnpm run"; INSTALL="pnpm install --frozen-lockfile"; EXEC="pnpm exec"
ok "package manager: pnpm $(pnpm --version)"

# ---------- preflight ------------------------------------------------------------
step "Preflight"
if ! $ALLOW_DIRTY && [[ -n "$(git status --porcelain)" ]]; then
  fail "working tree is dirty — commit/stash or pass --allow-dirty"
fi
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[[ "$BRANCH" == "main" ]] || printf '\033[1;33m ! deploying from branch %s (not main)\033[0m\n' "$BRANCH"
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  $EXEC wrangler whoami >/dev/null 2>&1 || fail "no CLOUDFLARE_API_TOKEN and wrangler is not logged in (run: $EXEC wrangler login)"
  ok "wrangler session authenticated"
else
  ok "CLOUDFLARE_API_TOKEN present"
fi

# ---------- install --------------------------------------------------------------
step "Install (frozen lockfile)"
$INSTALL
ok "dependencies installed"

# ---------- quality gate ----------------------------------------------------------
step "Lint + format check (biome)"
$EXEC biome ci . || fail "biome gate failed — run '$RUN check' to autofix, then commit"
ok "biome clean"

step "Typecheck (tsc --noEmit)"
$RUN typecheck || fail "type errors — fix before deploying"
ok "types clean"

if $SKIP_TESTS; then
  printf '\033[1;33m ! BDD suite SKIPPED (--skip-tests). This bypasses the only test layer.\033[0m\n'
else
  step "BDD suite (cucumber-js + Playwright vs wrangler dev)"
  [[ -f .dev.vars ]] || fail ".dev.vars missing — tests need SESSION_SECRET (see docs/TESTING_AND_QUALITY_SPEC.md §4)"
  $RUN test || fail "BDD scenarios failed — deploy blocked"
  ok "all scenarios green"
fi

# ---------- deploy ----------------------------------------------------------------
if $DRY_RUN; then
  step "Dry run complete"
  ok "all gates passed; skipping migrations + deploy (--dry-run)"
  exit 0
fi

step "D1 migrations (remote)"
$EXEC wrangler d1 migrations apply DB --remote
ok "migrations applied"

step "Deploy (wrangler)"
DEPLOY_OUT="$($EXEC wrangler deploy 2>&1)" || { printf '%s\n' "$DEPLOY_OUT" >&2; fail "wrangler deploy failed"; }
printf '%s\n' "$DEPLOY_OUT"
ok "deployed"

# ---------- post-deploy health check ----------------------------------------------
# URL priority: $HEALTH_URL env → first workers.dev URL in wrangler output.
URL="${HEALTH_URL:-$(printf '%s' "$DEPLOY_OUT" | grep -oE 'https://[a-zA-Z0-9.-]+\.workers\.dev' | head -1 || true)}"
if [[ -n "$URL" ]]; then
  step "Health check: $URL"
  for i in 1 2 3 4 5; do
    CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "${URL%/}/health" || true)"
    [[ "$CODE" == "200" ]] && { ok "health check passed (200)"; break; }
    [[ $i -eq 5 ]] && fail "health check failed after 5 attempts (last status: $CODE)"
    sleep $((i * 2))
  done
else
  printf '\033[1;33m ! no HEALTH_URL set and none detected in deploy output — skipping health check\033[0m\n'
fi

step "Done"
ok "end-to-end deploy complete ($(git rev-parse --short HEAD) on $BRANCH)"
