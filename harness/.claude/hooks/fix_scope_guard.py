#!/usr/bin/env python3
"""
PostToolUse scope guard for /fix command.
Counts Write/Edit operations; warns when >3 files modified.

Input (stdin): JSON with tool_name, tool_input, session_id
Output (stderr): Warning when over limit

NOTE: PostToolUse CANNOT block. This is informational only.
Enforcement relies on prompt discipline (see CLAUDE.md escalation rules).
"""

import json
import os
import sys
import tempfile

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
FIX_STATE_DIR = os.path.join(PROJECT_DIR, ".harness", ".fix-state")
FIX_FILE_LIMIT = 3


def get_state_path(session_id="default"):
    os.makedirs(FIX_STATE_DIR, exist_ok=True)
    return os.path.join(FIX_STATE_DIR, f"{session_id}.json")


def load_state(session_id="default"):
    path = get_state_path(session_id)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"files": [], "count": 0}


def save_state(state, session_id="default"):
    path = get_state_path(session_id)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "default")

    # Only track Write and Edit tools
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    state = load_state(session_id)

    # Track unique files
    if file_path not in state["files"]:
        state["files"].append(file_path)
        state["count"] = len(state["files"])
        save_state(state, session_id)

    # Warn when approaching or exceeding limit
    if state["count"] == FIX_FILE_LIMIT:
        print(
            f"[fix_scope_guard] WARNING: {FIX_FILE_LIMIT}/{FIX_FILE_LIMIT} files modified in this /fix session. "
            f"Next file modification will exceed the limit. Consider redirecting to /plan.",
            file=sys.stderr,
        )
    elif state["count"] > FIX_FILE_LIMIT:
        print(
            f"[fix_scope_guard] ALERT: {state['count']}/{FIX_FILE_LIMIT} files modified! "
            f"This exceeds the /fix limit. STOP and redirect to /plan. "
            f"Files: {', '.join(state['files'])}",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
