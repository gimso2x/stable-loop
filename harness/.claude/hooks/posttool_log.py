#!/usr/bin/env python3
"""
PostToolUse audit logger for Claude Code.
Logs Write/Edit/Bash tool usage to .harness/audit.log.

Input (stdin): JSON with tool_name, tool_input, session_id
Output: None (silent on success)
"""

import json
import os
import sys
from datetime import datetime, timezone

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
AUDIT_LOG = os.path.join(PROJECT_DIR, ".harness", "audit.log")


def log_entry(tool_name, tool_input, session_id):
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    pid = os.getpid()

    # Build concise entry
    entry = {
        "ts": timestamp,
        "pid": pid,
        "session": session_id,
        "tool": tool_name,
    }

    # Tool-specific details
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        entry["command"] = cmd[:200]  # truncate long commands
    elif tool_name in ("Write", "Edit"):
        entry["file"] = tool_input.get("file_path", "")
        if tool_name == "Edit":
            entry["old_size"] = len(tool_input.get("old_string", ""))
            entry["new_size"] = len(tool_input.get("new_string", ""))
    elif tool_name == "MultiEdit":
        entry["file"] = tool_input.get("file_path", "")
    elif tool_name == "Read":
        entry["file"] = tool_input.get("file_path", "")

    line = json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n"
    try:
        # Open the target log in append mode so prior entries are preserved.
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        # Log failure to stderr but don't break the hook chain
        print(f"[posttool_log] Write failed: {e}", file=sys.stderr)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "unknown")

    # Only log actionable tools (skip Read, Glob, Grep, etc. for noise reduction)
    if tool_name in ("Write", "Edit", "MultiEdit", "Bash", "Task"):
        log_entry(tool_name, tool_input, session_id)

    sys.exit(0)


if __name__ == "__main__":
    main()
