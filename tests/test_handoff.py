import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "skills" / "maintain-codex-handoff" / "scripts" / "handoff.py"
HOOK = ROOT / "skills" / "maintain-codex-handoff" / "scripts" / "hook.py"


class HandoffIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex-research-handoff-")
        self.repo = Path(self.temp.name)
        self.env = os.environ.copy()
        self.env["PYTHONUTF8"] = "1"
        self.run_command("git", "-C", str(self.repo), "init", "-b", "main")
        self.run_command("git", "-C", str(self.repo), "config", "user.name", "Handoff Test")
        self.run_command("git", "-C", str(self.repo), "config", "user.email", "handoff@example.invalid")
        self.run_command("git", "-C", str(self.repo), "config", "commit.gpgsign", "false")

    def tearDown(self):
        self.temp.cleanup()

    def run_command(self, *args, input_text=None, expected=0):
        result = subprocess.run(
            args,
            input=input_text,
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            env=self.env,
        )
        self.assertEqual(
            result.returncode,
            expected,
            msg=f"command failed: {args}\nstdout={result.stdout}\nstderr={result.stderr}",
        )
        return result.stdout.strip()

    def initialize_and_commit(self):
        output = self.run_command(sys.executable, str(HANDOFF), "initialize", "--repo", str(self.repo))
        self.run_command(
            "git",
            "-C",
            str(self.repo),
            "add",
            "AGENTS.md",
            "docs/PROJECT_CORE.md",
            "docs/CURRENT_STAGE.md",
        )
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "docs: initialize handoff")
        return output

    def test_initialize_audit_prompts_and_hook_are_consistent(self):
        first = self.run_command(sys.executable, str(HANDOFF), "initialize", "--repo", str(self.repo))
        core_path = self.repo / "docs" / "PROJECT_CORE.md"
        before = hashlib.sha256(core_path.read_bytes()).hexdigest()
        second = self.run_command(sys.executable, str(HANDOFF), "initialize", "--repo", str(self.repo))
        after = hashlib.sha256(core_path.read_bytes()).hexdigest()

        self.assertIn("created AGENTS.md", first)
        self.assertIn("created docs/PROJECT_CORE.md", first)
        self.assertIn("created docs/CURRENT_STAGE.md", first)
        self.assertIn("kept existing docs/PROJECT_CORE.md", second)
        self.assertEqual(before, after)

        agents_text = (self.repo / "AGENTS.md").read_text(encoding="utf-8")
        for required_rule in (
            "## Authority",
            "Execute one bounded Goal at a time.",
            "prefer the smallest sufficient implementation and experiment matrix",
            "Do not advance a Gate or scientific claim without explicit evidence.",
            "Require one qualified independent review",
            "Automatic context compaction alone is not a reason",
            "Do not amend, rebase, force-push, rewrite history",
        ):
            self.assertIn(required_rule, agents_text)

        self.run_command(
            "git",
            "-C",
            str(self.repo),
            "add",
            "AGENTS.md",
            "docs/PROJECT_CORE.md",
            "docs/CURRENT_STAGE.md",
        )
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "docs: initialize handoff")

        audit = self.run_command(sys.executable, str(HANDOFF), "audit", "--repo", str(self.repo))
        self.assertIn("PROJECT_CORE is an unaudited migration placeholder", audit)
        self.assertNotIn("ERROR:", audit)

        for surface in ("codex", "work"):
            prompt = self.run_command(
                sys.executable,
                str(HANDOFF),
                "resume-prompt",
                "--repo",
                str(self.repo),
                "--surface",
                surface,
            )
            for authority in ("AGENTS.md", "PROJECT_CORE.md", "CURRENT_STAGE.md"):
                self.assertIn(authority, prompt)

        payload = json.dumps({"hook_event_name": "SessionStart", "cwd": str(self.repo)})
        hook_output = self.run_command(sys.executable, str(HOOK), input_text=payload)
        parsed = json.loads(hook_output)
        context = parsed["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Strategy:", context)
        self.assertIn("Volatile state:", context)
        self.assertEqual(self.run_command("git", "-C", str(self.repo), "status", "--short"), "")

    def test_missing_core_is_migration_warning_until_declared_authoritative(self):
        self.initialize_and_commit()
        (self.repo / "docs" / "PROJECT_CORE.md").unlink()
        agents = self.repo / "AGENTS.md"
        agents.write_text("# Legacy Rules\n\nRead docs/CURRENT_STAGE.md.\n", encoding="utf-8")

        legacy = self.run_command(sys.executable, str(HANDOFF), "audit", "--repo", str(self.repo))
        self.assertIn("WARNING: missing docs/PROJECT_CORE.md", legacy)

        agents.write_text(
            "# Canonical Rules\n\nRead docs/PROJECT_CORE.md and docs/CURRENT_STAGE.md.\n",
            encoding="utf-8",
        )
        strict = self.run_command(
            sys.executable,
            str(HANDOFF),
            "audit",
            "--repo",
            str(self.repo),
            expected=1,
        )
        self.assertIn("ERROR: missing docs/PROJECT_CORE.md", strict)


if __name__ == "__main__":
    unittest.main()
