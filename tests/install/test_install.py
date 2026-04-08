#!/usr/bin/env python3
"""
End-to-end installation checks for stable-loop-harness.

Run:
  python -m unittest tests.install.test_install -v
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SCRIPT = REPO_ROOT / "install.sh"
TMP_ROOT = REPO_ROOT / ".tmp-smoke" / "install-e2e"
REQUIRED_FILES = [
    "AGENTS.md",
    ".claude/CLAUDE.md",
    ".claude/settings.json",
    ".claude/hooks/pretool_guard.py",
    ".claude/hooks/fix_scope_guard.py",
    ".claude/hooks/posttool_log.py",
    ".claude/hooks/session_start.py",
    ".claude/hooks/session_end.py",
    ".claude/hooks/feedback_capture.py",
    ".claude/commands/init.md",
    ".claude/commands/plan.md",
    ".claude/commands/work.md",
    ".claude/commands/fix.md",
    ".claude/commands/h-review.md",
    ".claude/commands/h-verify.md",
    ".claude/rules/anti-rationalization.md",
    ".claude/rules/confusion-management.md",
    ".claude/rules/scope-discipline.md",
    ".claude/rules/verification-protocol.md",
]


def bash_is_usable() -> bool:
    bash_path = shutil.which("bash")
    if not bash_path:
        return False

    try:
        result = subprocess.run(
            [bash_path, "-lc", "true"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            cwd=REPO_ROOT,
        )
    except OSError:
        return False

    return result.returncode == 0


def run_hook(project_dir: Path, hook_name: str, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    hook_path = project_dir / ".claude" / "hooks" / hook_name
    return subprocess.run(
        ["python", str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
        cwd=project_dir,
    )


@unittest.skipUnless(bash_is_usable(), "usable bash is required for install.sh E2E checks")
class InstallE2ETest(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        shutil.rmtree(TMP_ROOT, ignore_errors=True)
        TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.target_dir = TMP_ROOT / "target-project"
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(TMP_ROOT, ignore_errors=True)

    def run_install(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(INSTALL_SCRIPT), str(self.target_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            cwd=REPO_ROOT,
        )

    def test_install_copies_required_files_and_directories(self) -> None:
        result = self.run_install()
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Harness installed successfully", result.stdout)

        for relative_path in REQUIRED_FILES:
            installed = self.target_dir / relative_path
            self.assertTrue(installed.exists(), msg=f"Missing installed file: {relative_path}")

        self.assertTrue((self.target_dir / "plans").is_dir())
        self.assertTrue((self.target_dir / ".harness").is_dir())

    def test_installed_pretool_guard_blocks_multiedit_on_protected_path(self) -> None:
        install_result = self.run_install()
        self.assertEqual(install_result.returncode, 0, msg=install_result.stdout + install_result.stderr)

        hook_result = run_hook(
            self.target_dir,
            "pretool_guard.py",
            {
                "tool_name": "MultiEdit",
                "tool_input": {"file_path": ".github/workflows/ci.yml"},
            },
        )

        self.assertEqual(hook_result.returncode, 2, msg=hook_result.stderr)
        self.assertIn("protected path", hook_result.stderr)

    def test_installed_posttool_log_appends_entries(self) -> None:
        install_result = self.run_install()
        self.assertEqual(install_result.returncode, 0, msg=install_result.stdout + install_result.stderr)

        first = run_hook(
            self.target_dir,
            "posttool_log.py",
            {
                "tool_name": "Write",
                "tool_input": {"file_path": "src/app.ts"},
                "session_id": "install-e2e",
            },
        )
        second = run_hook(
            self.target_dir,
            "posttool_log.py",
            {
                "tool_name": "Bash",
                "tool_input": {"command": "npm test"},
                "session_id": "install-e2e",
            },
        )

        self.assertEqual(first.returncode, 0, msg=first.stderr)
        self.assertEqual(second.returncode, 0, msg=second.stderr)

        audit_log = self.target_dir / ".harness" / "audit.log"
        self.assertTrue(audit_log.exists())

        with audit_log.open(encoding="utf-8") as fh:
            entries = [json.loads(line) for line in fh if line.strip()]

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["tool"], "Write")
        self.assertEqual(entries[1]["tool"], "Bash")
