#!/usr/bin/env python3
"""
PreToolUse guard hook for Claude Code.
Blocks destructive Bash commands and file mutations to protected paths.

Input (stdin): JSON with tool_name, tool_input
Output (stderr): Reason for block
Exit codes: 0=allow, 2=block
"""

import json
import os
import re
import sys

# Destructive Bash command patterns (glob-style)
BASH_DENY_PATTERNS = [
    r"rm\s+(-[rfRF]+\s+|--force\s+)?/",         # rm targeting root or any dir
    r"rm\s+(-[rfRF]+\s+|--force\s+)?\*",         # rm targeting wildcards
    r"rm\s+(-[rfRF]+\s+|--force\s+)?\S",         # rm -rf with any target (except single file)
    r"git\s+reset\s+--hard",
    r"git\s+clean",
    r"git\s+push\s+(-\w*\s+)*--force",
    r"git\s+push\s+(-\w*\s+)*-f\b",
    r"git\s+branch\s+(-[dD]\s+|--delete\s+)(?!.*--safe-delete)",  # branch -D without safe
    r"DROP\s+(TABLE|DATABASE|SCHEMA)",
    r"npm\s+publish",
    r"DROP\s+TABLE",
    r"chmod\s+(-R\s+)?777",
    r"curl\s+.*\|\s*(ba)?sh",                    # curl pipe to shell
]

# Allow list: rm of a single specific file (not -rf, not wildcard, not directory)
BASH_RM_ALLOW_PATTERN = r"rm\s+(?!-[rfRF])\S+$"  # rm without -r/-f flags

# Protected path patterns (for file mutation tools)
PROTECTED_PATH_PATTERNS = [
    r"\.env",
    r"\.github/",
    r"prisma/migrations/",
    r"package-lock\.json",
    r"yarn\.lock",
    r"pnpm-lock\.yaml",
    r"docker-compose",
    r"Claude\.md$",
    r"AGENTS\.md$",
]

# Project root
PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def matches_any(text, patterns):
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def is_protected_path(file_path):
    """Check if file_path matches any protected pattern."""
    if not file_path:
        return False
    # Normalize: make relative to project if absolute
    if os.path.isabs(file_path):
        try:
            rel = os.path.relpath(file_path, PROJECT_DIR)
        except ValueError:
            rel = file_path
    else:
        rel = file_path
    return matches_any(rel, PROTECTED_PATH_PATTERNS)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        # Malformed input — allow (don't break the session)
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # --- Bash tool: check for destructive commands ---
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        # First check if it's a safe single-file rm (no -r/-f flags)
        if re.match(BASH_RM_ALLOW_PATTERN, command.strip()):
            sys.exit(0)
        if matches_any(command, BASH_DENY_PATTERNS):
            print(
                f"[pretool_guard] BLOCKED: Dangerous command detected: {command[:200]}",
                file=sys.stderr,
            )
            sys.exit(2)

    # --- File mutation tools: check for protected paths ---
    elif tool_name in ("Write", "Edit", "MultiEdit"):
        file_path = tool_input.get("file_path", "")
        if is_protected_path(file_path):
            print(
                f"[pretool_guard] BLOCKED: {tool_name} on protected path: {file_path}",
                file=sys.stderr,
            )
            sys.exit(2)

    # Allow
    sys.exit(0)


if __name__ == "__main__":
    main()
