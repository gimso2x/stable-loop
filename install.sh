#!/usr/bin/env bash
set -euo pipefail

# stable-loop harness installer
# Usage: ./install.sh <target-project-dir>

TARGET="${1:-.}"
HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)/harness"

if [ ! -d "$HARNESS_DIR/.claude" ]; then
  echo "Error: harness template not found at $HARNESS_DIR"
  exit 1
fi

if [ ! -d "$TARGET" ]; then
  echo "Error: target directory does not exist: $TARGET"
  exit 1
fi

echo "Installing harness into: $TARGET"

# 1. Copy .claude/ directory
echo "  → .claude/ (CLAUDE.md + commands + settings)"
cp -r "$HARNESS_DIR/.claude" "$TARGET/.claude"

# 2. Copy AGENTS.md to root
echo "  → AGENTS.md"
cp "$HARNESS_DIR/AGENTS.md" "$TARGET/AGENTS.md"

# 3. Create directories
mkdir -p "$TARGET/plans"
mkdir -p "$TARGET/.harness"
echo "  → plans/"
echo "  → .harness/"

# 4. Add .harness/ to .gitignore if .gitignore exists
GITIGNORE="$TARGET/.gitignore"
if [ -f "$GITIGNORE" ]; then
  if ! grep -q "^\.harness/" "$GITIGNORE"; then
    echo "" >> "$GITIGNORE"
    echo "# stable-loop harness artifacts" >> "$GITIGNORE"
    echo ".harness/" >> "$GITIGNORE"
    echo "  → updated .gitignore"
  fi
else
  echo -e "\n# stable-loop harness artifacts\n.harness/" > "$GITIGNORE"
  echo "  → created .gitignore"
fi

# 5. Detect project type
echo ""
echo "Project detection:"
if [ -f "$TARGET/package.json" ]; then
  echo "  ✓ package.json found"
  # Check for Next.js
  if [ -f "$TARGET/next.config.js" ] || [ -f "$TARGET/next.config.mjs" ] || [ -f "$TARGET/next.config.ts" ]; then
    echo "  ✓ Next.js detected"
  fi
  # Check for TypeScript
  if [ -f "$TARGET/tsconfig.json" ]; then
    echo "  ✓ TypeScript detected"
  fi
else
  echo "  ⚠ No package.json found (greenfield project)"
fi

echo ""
echo "Installation complete."
echo ""
echo "Available commands in Claude Code:"
echo "  /plan <requirement>   Create implementation plan"
echo "  /work [plan-path]     Execute latest plan"
echo "  /review               Self-review changes"
echo "  /verify               Run verification suite"
echo ""
echo "Start by running: /plan <your requirement>"
