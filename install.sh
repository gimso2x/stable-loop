#!/usr/bin/env bash
set -euo pipefail

# stable-loop-harness: Install Claude Code harness into an existing project
# Usage: ./install.sh [target_dir]
#   target_dir: Project root to install into (default: current directory)

TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

# Source paths (relative to this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HARNESS_DIR="$SCRIPT_DIR/harness"

if [ ! -f "$HARNESS_DIR/AGENTS.md" ]; then
  # Maybe install.sh is inside harness/ itself
  HARNESS_DIR="$SCRIPT_DIR"
  if [ ! -f "$HARNESS_DIR/AGENTS.md" ]; then
    echo "ERROR: Cannot find harness source (expected AGENTS.md)."
    exit 1
  fi
fi

echo "Installing stable-loop harness into: $TARGET_DIR"

# 1. Create directory structure
mkdir -p "$TARGET_DIR/.claude/hooks"
mkdir -p "$TARGET_DIR/.claude/commands"
mkdir -p "$TARGET_DIR/.claude/rules"
mkdir -p "$TARGET_DIR/plans"
mkdir -p "$TARGET_DIR/.harness"

# 2. Copy core files
cp "$HARNESS_DIR/AGENTS.md" "$TARGET_DIR/AGENTS.md"
cp "$HARNESS_DIR/.claude/settings.json" "$TARGET_DIR/.claude/settings.json"

# 3. Copy hooks
for hook in pretool_guard.py fix_scope_guard.py posttool_log.py session_start.py session_end.py feedback_capture.py; do
  if [ -f "$HARNESS_DIR/.claude/hooks/$hook" ]; then
    cp "$HARNESS_DIR/.claude/hooks/$hook" "$TARGET_DIR/.claude/hooks/$hook"
  fi
done

# 4. Copy commands
for cmd in init.md plan.md fix.md work.md h-review.md h-verify.md; do
  if [ -f "$HARNESS_DIR/.claude/commands/$cmd" ]; then
    cp "$HARNESS_DIR/.claude/commands/$cmd" "$TARGET_DIR/.claude/commands/$cmd"
  fi
done

# 5. Copy rules
for rule in scope-discipline.md anti-rationalization.md verification-protocol.md confusion-management.md; do
  if [ -f "$HARNESS_DIR/.claude/rules/$rule" ]; then
    cp "$HARNESS_DIR/.claude/rules/$rule" "$TARGET_DIR/.claude/rules/$rule"
  fi
done

# 6. Verify Python3 available
if ! command -v python3 &>/dev/null; then
  echo "WARNING: python3 not found. Hooks require Python 3.11+."
fi

# 7. Verify hooks work
echo ""
echo "Verifying hooks..."
ERRORS=0
for hook in pretool_guard.py fix_scope_guard.py posttool_log.py session_start.py session_end.py feedback_capture.py; do
  if python3 "$TARGET_DIR/.claude/hooks/$hook" </dev/null 2>/dev/null; then
    echo "  ✓ $hook"
  else
    echo "  ✗ $hook (exit code: $?)"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "✅ Harness installed successfully!"
  echo ""
  echo "Commands available:"
  echo "  /init     — Project setup & context gathering"
  echo "  /plan     — Write implementation plan"
  echo "  /work     — Execute plan (TDD)"
  echo "  /fix      — Quick fix (≤3 files)"
  echo "  /h-review — Review changes vs plan"
  echo "  /h-verify — Format → lint → typecheck → test"
  echo ""
  echo "Start with: /init"
else
  echo "⚠️  $ERRORS hook(s) failed verification. Check Python 3.11+ is installed."
  exit 1
fi
