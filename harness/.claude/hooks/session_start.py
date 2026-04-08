#!/usr/bin/env python3
"""
SessionStart hook for Claude Code.
Displays active plans and in-progress tasks.

Input (stdin): JSON with session info
Output (stderr): Context summary (shown to Claude)

NOTE: SessionStart CANNOT block. This is informational only.
"""

import json
import os
import sys

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    output = []

    output.append(f"[session_start] Session: {session_id}")
    output.append(f"[session_start] Project: {PROJECT_DIR}")

    # Check for active plans
    plans_dir = os.path.join(PROJECT_DIR, "plans")
    if os.path.isdir(plans_dir):
        plans = sorted(
            [f for f in os.listdir(plans_dir) if f.endswith(".md")],
            reverse=True,
        )
        if plans:
            output.append(f"[session_start] Plans found ({len(plans)}): {', '.join(plans[:5])}")
            # Read latest plan header
            latest = os.path.join(plans_dir, plans[0])
            try:
                with open(latest, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("# Plan:"):
                            output.append(f"[session_start] Latest plan: {line}")
                            break
                        if line and not line.startswith("#"):
                            break
            except OSError:
                pass
        else:
            output.append("[session_start] No plans found in plans/")

    # Check for in-progress tasks
    harness_dir = os.path.join(PROJECT_DIR, ".harness")
    if os.path.isdir(harness_dir):
        tasks = [
            d
            for d in os.listdir(harness_dir)
            if d.startswith("task-") and os.path.isdir(os.path.join(harness_dir, d))
        ]
        if tasks:
            output.append(f"[session_start] Task dirs found: {', '.join(tasks)}")

    # Check for uncommitted changes
    import subprocess

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            output.append(f"[session_start] Uncommitted changes: {len(lines)} file(s)")
        else:
            output.append("[session_start] Working tree clean")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    print("\n".join(output), file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
