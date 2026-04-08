#!/usr/bin/env python3
"""
SessionEnd hook for Claude Code.
Displays summary: uncommitted files, modified paths.

Input (stdin): JSON with session info
Output (stderr): Summary (shown to Claude)

NOTE: SessionEnd CANNOT block. This is informational only.
"""

import json
import os
import sys
import subprocess

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    output = []

    output.append(f"[session_end] Session ended: {session_id}")

    # Uncommitted changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            if lines:
                modified = [l for l in lines if l.startswith((" M", "M ", "??", "A ", "D "))]
                output.append(f"[session_end] WARNING: {len(modified)} uncommitted file(s):")
                for line in modified[:10]:
                    output.append(f"[session_end]   {line}")
                if len(modified) > 10:
                    output.append(f"[session_end]   ... and {len(modified) - 10} more")
            else:
                output.append("[session_end] Working tree clean. Good.")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        output.append("[session_end] Could not check git status")

    # Audit log stats
    audit_log = os.path.join(PROJECT_DIR, ".harness", "audit.log")
    if os.path.exists(audit_log):
        try:
            with open(audit_log, "r") as f:
                line_count = sum(1 for _ in f)
            output.append(f"[session_end] Audit log: {line_count} entries")
        except OSError:
            pass

    print("\n".join(output), file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
