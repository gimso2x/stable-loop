#!/usr/bin/env python3
"""
UserPromptSubmit feedback capture hook for Claude Code.
Detects user feedback/correction patterns and injects context guidance.

Input (stdin): JSON with prompt (user message)
Output (stderr): Context injection for Claude

NOTE: This hook does NOT block. It adds context via stderr output.
"""

import json
import sys

# Patterns that indicate user feedback/correction
FEEDBACK_PATTERNS = [
    # Korean
    r"잘못",
    r"아닌",
    r"고쳐",
    r"아니야",
    r"그게\s+아니라",
    r"다시\s+해",
    r"취소",
    r"그만",
    r"멈춰",
    r"되돌려",
    r"커밋\s+취소",
    r"revert",
    # English
    r"\bwrong\b",
    r"\bincorrect\b",
    r"\bfix\s+that\b",
    r"\bundo\b",
    r"\brevert\b",
    r"\bcancel\b",
    r"\bstop\b",
    r"\bthat'?s\s+not\b",
    r"\bdon'?t\s+do\s+that\b",
    r"\bnot\s+what\s+i\b",
]


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = data.get("prompt", "")

    if not prompt:
        sys.exit(0)

    # Check for feedback patterns
    import re

    for pattern in FEEDBACK_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            print(
                "[feedback_capture] User feedback detected. "
                "STOP current action. Read the user's message carefully. "
                "Do NOT rationalize or explain — acknowledge and correct.",
                file=sys.stderr,
            )
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
