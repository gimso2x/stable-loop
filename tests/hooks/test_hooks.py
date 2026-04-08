#!/usr/bin/env python3
"""
Tests for stable-loop hooks.
Uses JSON fixtures to test stdin parsing, pattern matching, and exit codes.
Run: python3 -m pytest tests/hooks/ -v
"""

import json
import os
import sys
import tempfile
import subprocess

# Add hooks dir to path
HOOKS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "harness", ".claude", "hooks")

def run_hook(hook_name, stdin_data):
    """Run a hook script with given stdin data. Returns (exit_code, stderr)."""
    hook_path = os.path.join(HOOKS_DIR, hook_name)
    result = subprocess.run(
        ["python3", hook_path],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.returncode, result.stderr


class TestPretoolGuard:
    """PreToolUse guard: blocks dangerous Bash, Write/Edit to protected paths."""

    # --- Bash deny patterns ---

    def test_bash_rm_rf_root(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"}
        })
        assert code == 2
        assert "BLOCKED" in stderr

    def test_bash_rm_rf_subdir(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf node_modules"}
        })
        assert code == 2

    def test_bash_rm_force(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "rm --force -r /tmp/something"}
        })
        assert code == 2

    def test_bash_git_reset_hard(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "git reset --hard HEAD~1"}
        })
        assert code == 2

    def test_bash_git_clean(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "git clean -fd"}
        })
        assert code == 2

    def test_bash_git_push_force(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "git push --force origin main"}
        })
        assert code == 2

    def test_bash_git_push_f(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "git push -f origin main"}
        })
        assert code == 2

    def test_bash_git_branch_D(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "git branch -D feature/test"}
        })
        assert code == 2

    def test_bash_drop_table(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "DROP TABLE users"}
        })
        assert code == 2

    def test_bash_npm_publish(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "npm publish"}
        })
        assert code == 2

    # --- Bash allow patterns ---

    def test_bash_npm_test(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "npm test"}
        })
        assert code == 0

    def test_bash_git_diff(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "git diff HEAD"}
        })
        assert code == 0

    def test_bash_ls(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la src/"}
        })
        assert code == 0

    def test_bash_rm_single_file(self):
        """rm of a single non-wildcard file is allowed."""
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "rm src/deprecated.js"}
        })
        assert code == 0

    # --- Write/Edit protected paths ---

    def test_write_env_file(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": ".env.local"}
        })
        assert code == 2
        assert "protected" in stderr

    def test_write_github(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": ".github/workflows/ci.yml"}
        })
        assert code == 2

    def test_write_lockfile(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": "package-lock.json"}
        })
        assert code == 2

    def test_edit_pragma_migrations(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Edit",
            "tool_input": {"file_path": "prisma/migrations/001_init.sql"}
        })
        assert code == 2

    # --- Write/Edit normal paths ---

    def test_write_src_file(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": "src/app.ts"}
        })
        assert code == 0

    def test_edit_test_file(self):
        code, stderr = run_hook("pretool_guard.py", {
            "tool_name": "Edit",
            "tool_input": {"file_path": "tests/app.test.ts"}
        })
        assert code == 0

    # --- Edge cases ---

    def test_empty_stdin(self):
        code, _ = run_hook("pretool_guard.py", {})
        assert code == 0

    def test_invalid_json(self):
        result = subprocess.run(
            ["python3", os.path.join(HOOKS_DIR, "pretool_guard.py")],
            input="not json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_unknown_tool(self):
        code, _ = run_hook("pretool_guard.py", {
            "tool_name": "Read",
            "tool_input": {"file_path": ".env"}
        })
        assert code == 0


class TestFixScopeGuard:
    """PostToolUse fix scope guard: counts file modifications."""

    def test_write_first_three_allowed(self):
        """First 3 files should produce no warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                for i in range(3):
                    code, stderr = run_hook("fix_scope_guard.py", {
                        "tool_name": "Write",
                        "tool_input": {"file_path": f"src/file{i}.ts"},
                        "session_id": "test-session",
                    })
                    assert code == 0
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def test_write_fourth_warns(self):
        """4th file should produce ALERT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                # Write 3 files — 3rd should warn at limit
                for i in range(3):
                    _, stderr = run_hook("fix_scope_guard.py", {
                        "tool_name": "Write",
                        "tool_input": {"file_path": f"src/file{i}.ts"},
                        "session_id": "test-warn2",
                    })
                # After 3 files, check last stderr had WARNING
                assert "WARNING" in stderr or "3/3" in stderr

                # 4th should ALERT (over limit)
                _, stderr4 = run_hook("fix_scope_guard.py", {
                    "tool_name": "Write",
                    "tool_input": {"file_path": "src/file4.ts"},
                    "session_id": "test-warn2",
                })
                assert "ALERT" in stderr4 or "exceeds" in stderr4
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def test_non_write_ignored(self):
        """Bash and other tools should be ignored."""
        code, stderr = run_hook("fix_scope_guard.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "npm test"},
            "session_id": "test-ignore",
        })
        assert code == 0
        assert stderr == ""

    def test_duplicate_file_not_double_counted(self):
        """Same file edited twice should count as 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                for _ in range(2):
                    code, stderr = run_hook("fix_scope_guard.py", {
                        "tool_name": "Edit",
                        "tool_input": {"file_path": "src/app.ts"},
                        "session_id": "test-dup",
                    })
                    assert code == 0
                    assert "ALERT" not in stderr
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)


class TestPosttoolLog:
    """PostToolUse audit logger."""

    def test_write_logs_to_audit_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                code, _ = run_hook("posttool_log.py", {
                    "tool_name": "Write",
                    "tool_input": {"file_path": "src/app.ts"},
                    "session_id": "test-log",
                })
                assert code == 0

                audit_log = os.path.join(tmpdir, ".harness", "audit.log")
                assert os.path.exists(audit_log)
                with open(audit_log) as f:
                    entry = json.loads(f.readline())
                    assert entry["tool"] == "Write"
                    assert entry["file"] == "src/app.ts"
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def test_bash_logs_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                run_hook("posttool_log.py", {
                    "tool_name": "Bash",
                    "tool_input": {"command": "npm test"},
                    "session_id": "test-bash-log",
                })
                audit_log = os.path.join(tmpdir, ".harness", "audit.log")
                with open(audit_log) as f:
                    entry = json.loads(f.readline())
                    assert entry["tool"] == "Bash"
                    assert entry["command"] == "npm test"
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def test_read_tool_not_logged(self):
        """Read tool should not be logged (noise reduction)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                run_hook("posttool_log.py", {
                    "tool_name": "Read",
                    "tool_input": {"file_path": "src/app.ts"},
                    "session_id": "test-read",
                })
                audit_log = os.path.join(tmpdir, ".harness", "audit.log")
                assert not os.path.exists(audit_log)
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)


class TestFeedbackCapture:
    """UserPromptSubmit feedback detection."""

    def test_korean_feedback_detected(self):
        for msg in ["잘못됐어", "아닌데", "고쳐줘", "아니야 그게 아니라"]:
            code, stderr = run_hook("feedback_capture.py", {"prompt": msg})
            assert code == 0
            assert "feedback" in stderr.lower()

    def test_english_feedback_detected(self):
        for msg in ["that's wrong", "fix that please", "undo this", "not what I asked"]:
            code, stderr = run_hook("feedback_capture.py", {"prompt": msg})
            assert code == 0
            assert "feedback" in stderr.lower()

    def test_normal_prompt_not_flagged(self):
        code, stderr = run_hook("feedback_capture.py", {"prompt": "add a new feature for user auth"})
        assert code == 0
        assert stderr == ""

    def test_empty_prompt(self):
        code, _ = run_hook("feedback_capture.py", {"prompt": ""})
        assert code == 0


class TestSessionStart:
    """SessionStart: informational output only."""

    def test_runs_successfully(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                code, stderr = run_hook("session_start.py", {
                    "session_id": "test-session"
                })
                assert code == 0
                assert "session_start" in stderr
                assert "Project:" in stderr
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def test_detects_plans(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            plans_dir = os.path.join(tmpdir, "plans")
            os.makedirs(plans_dir)
            with open(os.path.join(plans_dir, "2026-04-08-test.md"), "w") as f:
                f.write("# Plan: test feature\n")
            try:
                code, stderr = run_hook("session_start.py", {
                    "session_id": "test-plans"
                })
                assert code == 0
                assert "Plans found" in stderr
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)


class TestSessionEnd:
    """SessionEnd: informational output only."""

    def test_runs_successfully(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
            try:
                code, stderr = run_hook("session_end.py", {
                    "session_id": "test-session"
                })
                assert code == 0
                assert "session_end" in stderr
            finally:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)
