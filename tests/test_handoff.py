import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "skills" / "codex-research-workflow" / "scripts" / "workflow.py"
HANDOFF = WORKFLOW  # Compatibility name used by the historical regression tests.
HOOK = ROOT / "skills" / "codex-research-workflow" / "scripts" / "hook.py"
WORK_CONTRACT = (
    ROOT
    / "skills"
    / "codex-research-workflow"
    / "references"
    / "work-response-contract.md"
)
LEGACY_WORK_CONTRACT = (
    ROOT
    / "skills"
    / "maintain-codex-handoff"
    / "references"
    / "work-response-contract.md"
)


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
        output = self.run_command(sys.executable, str(WORKFLOW), "initialize", "--repo", str(self.repo))
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

    def read_state(self):
        text = (self.repo / "docs" / "CURRENT_STAGE.md").read_text(encoding="utf-8")
        payload = text.split("<!-- codex-handoff-state\n", 1)[1].split("\n-->", 1)[0]
        return json.loads(payload)

    def record_review(self, candidate, candidate_kind, verdict, report_name):
        report_path = self.repo / "docs" / report_name
        report_path.write_text(f"# Review\n\nCandidate: `{candidate}`\n", encoding="utf-8")
        review_path = self.repo / "review-input.json"
        review_path.write_text(
            json.dumps(
                {
                    "candidate_sha": candidate,
                    "candidate_kind": candidate_kind,
                    "verdict": verdict,
                    "review_report": f"docs/{report_name}",
                    "open_findings": (
                        []
                        if verdict == "ACCEPT"
                        else ["P1: blocking defect."]
                        if verdict == "REJECT"
                        else ["P2: bounded limitation."]
                        if verdict == "ACCEPT_WITH_P2"
                        else ["BLOCKED: required evidence is unavailable."]
                    ),
                    "current_gate": "review complete",
                    "next_gate": "next bounded gate",
                    "next_action": "Verify the review-state commit.",
                }
            ),
            encoding="utf-8",
        )
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
        )
        review_path.unlink()

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
            "Default to the shortest empirical loop",
            "Local, recoverable, no-cost work",
            "Use the simplest correct, testable implementation",
            "Stop when acceptance criteria pass",
            "Exploratory implementation, tests, smoke",
            "do not require independent review or review-state commits",
            "only for an explicit formal promotion",
            "accepted implementation candidate",
            "Browser Work responses must follow the public Work Response Contract",
            "A clean review-state verification may be followed by the next Goal",
            "Work verification of a formal review-state commit is mechanical closure",
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

        prompts = {}
        for surface in ("codex", "work"):
            prompts[surface] = self.run_command(
                sys.executable,
                str(HANDOFF),
                "resume-prompt",
                "--repo",
                str(self.repo),
                "--surface",
                surface,
            )
            for authority in ("AGENTS.md", "PROJECT_CORE.md", "CURRENT_STAGE.md"):
                self.assertIn(authority, prompts[surface])

        work_prompt = prompts["work"]
        self.assertIn("work-response-contract.md", work_prompt)
        self.assertIn("探索性实现、测试、smoke", work_prompt)
        self.assertIn("不需要独立审查或 review-state", work_prompt)
        self.assertIn("formal promotion", work_prompt)
        self.assertIn("机械验收通过后可立即签发下一 Goal", work_prompt)
        self.assertIn("真实数据运行", work_prompt)
        self.assertIn("达到验收目标即停止", work_prompt)
        self.assertIn("最多给出一个 Codex Goal", work_prompt)
        self.assertIn("无需逐次询问", work_prompt)

        codex_prompt = prompts["codex"]
        self.assertIn("默认执行探索流程", codex_prompt)
        self.assertIn("普通探索提交不需要审查或状态落库", codex_prompt)
        self.assertIn("才启动一次独立审查和 review-state", codex_prompt)
        self.assertIn("主动询问用户", codex_prompt)
        self.assertIn("机械验收不得生成新的审查报告", codex_prompt)
        self.assertIn("达到验收目标即停止", codex_prompt)

        payload = json.dumps({"hook_event_name": "SessionStart", "cwd": str(self.repo)})
        hook_output = self.run_command(sys.executable, str(HOOK), input_text=payload)
        parsed = json.loads(hook_output)
        context = parsed["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Use $codex-research-workflow", context)
        self.assertIn("direction=", context)
        self.assertIn("gate=", context)
        self.assertEqual(self.run_command("git", "-C", str(self.repo), "status", "--short"), "")

    def test_work_contract_is_format_not_mandatory_review_state_machine(self):
        contract = WORK_CONTRACT.read_text(encoding="utf-8")
        self.assertEqual(contract, LEGACY_WORK_CONTRACT.read_text(encoding="utf-8"))
        normalized = " ".join(contract.split())
        self.assertIn("Only the user may authorize changing", normalized)
        self.assertIn("Agents must not modify it autonomously", normalized)
        self.assertIn("It is not a mandatory review state machine", normalized)
        self.assertIn("at most one", normalized)
        self.assertIn("Use `无`", normalized)
        self.assertIn("do not require independent review, review-state recording", normalized)
        self.assertIn("only for explicit formal promotion", normalized)
        self.assertIn("Before freezing a publication evaluation", normalized)
        self.assertIn("Any `P0` or `P1` requires `REJECT`", normalized)
        self.assertIn("`REJECT` requires at least one such finding", normalized)
        self.assertIn("prefix every finding with `BLOCKED:`", normalized)
        self.assertIn("must not use blocking language", normalized)
        self.assertIn("same response may issue the next Goal", normalized)
        self.assertIn("stop when its acceptance criteria pass", normalized)
        self.assertIn("Pause for the user's decision", normalized)
        self.assertIn("one bounded, low-cost, reversible diagnostic", normalized)
        self.assertIn("without per-run approval", normalized)
        self.assertIn("Do not expand the threat model", normalized)
        self.assertNotIn("work-response-contract-v1", contract)

    def test_exploratory_commit_does_not_imply_pending_review(self):
        self.initialize_and_commit()
        implementation = self.repo / "method.py"
        implementation.write_text("VALUE = 1\n", encoding="utf-8")
        self.run_command("git", "-C", str(self.repo), "add", "method.py")
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "feat: exploratory method")

        audit = self.run_command(sys.executable, str(HANDOFF), "audit", "--repo", str(self.repo))
        self.assertNotIn("review closure may be pending", audit)
        audit_json = json.loads(
            self.run_command(sys.executable, str(HANDOFF), "audit", "--repo", str(self.repo), "--json")
        )
        self.assertNotIn("pending_after_state", audit_json)
        self.assertTrue(audit_json["head_newer_than_state"])

    def test_record_review_rejects_inconsistent_verdict_and_findings(self):
        self.initialize_and_commit()
        candidate_path = self.repo / "method.py"
        candidate_path.write_text("VALUE = 1\n", encoding="utf-8")
        self.run_command("git", "-C", str(self.repo), "add", "method.py")
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "feat: candidate")
        candidate = self.run_command("git", "-C", str(self.repo), "rev-parse", "HEAD")
        report = self.repo / "docs" / "REVIEW.md"
        report.write_text("# Review\n", encoding="utf-8")
        review_path = self.repo / "review-input.json"
        payload = {
            "candidate_sha": candidate,
            "candidate_kind": "implementation",
            "verdict": "ACCEPT",
            "review_report": "docs/REVIEW.md",
            "open_findings": ["P1: blocking defect."],
            "next_gate": "next",
            "next_action": "stop",
        }
        review_path.write_text(json.dumps(payload), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
            expected=2,
        )
        state = self.read_state()
        self.assertIsNone(state["accepted_code_commit"])
        self.assertEqual(state["review_verdict"], "NO_REVIEW")

        payload["verdict"] = "ACCEPT_WITH_P2"
        payload["open_findings"] = ["P2: blocking defect."]
        review_path.write_text(json.dumps(payload), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
            expected=2,
        )

        payload["open_findings"] = ["P2: promotion is blocked until fixed."]
        review_path.write_text(json.dumps(payload), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
            expected=2,
        )

        payload["open_findings"] = ["P2: must be fixed before promotion."]
        review_path.write_text(json.dumps(payload), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
            expected=2,
        )

        payload["open_findings"] = ["P2: non-blocking limitation."]
        review_path.write_text(json.dumps(payload), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
        )
        state = self.read_state()
        self.assertEqual(state["review_verdict"], "ACCEPT_WITH_P2")

        payload["verdict"] = "BLOCKED"
        payload["open_findings"] = []
        review_path.write_text(json.dumps(payload), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
            expected=2,
        )

    def test_audit_rejects_inconsistent_review_state(self):
        self.initialize_and_commit()
        state_path = self.repo / "docs" / "CURRENT_STAGE.md"
        text = state_path.read_text(encoding="utf-8")
        marker = "<!-- codex-handoff-state"
        start = text.index(marker) + len(marker)
        end = text.index("-->", start)
        state = json.loads(text[start:end].strip())
        state["review_verdict"] = "ACCEPT"
        state["open_findings"] = ["P1: blocking defect."]
        state_path.write_text(
            text[:start] + "\n" + json.dumps(state, indent=2) + "\n" + text[end:],
            encoding="utf-8",
        )
        output = self.run_command(
            sys.executable,
            str(HANDOFF),
            "audit",
            "--repo",
            str(self.repo),
            "--json",
            expected=1,
        )
        result = json.loads(output)
        self.assertIn("P0 or P1 findings require REJECT", result["errors"])

    def test_record_review_enforces_candidate_kind_and_accepted_code_semantics(self):
        self.initialize_and_commit()

        implementation = self.repo / "method.py"
        implementation.write_text("VALUE = 1\n", encoding="utf-8")
        self.run_command("git", "-C", str(self.repo), "add", "method.py")
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "feat: add method")
        implementation_sha = self.run_command("git", "-C", str(self.repo), "rev-parse", "HEAD")

        self.record_review(
            implementation_sha,
            "implementation",
            "ACCEPT",
            "IMPLEMENTATION_REVIEW.md",
        )
        implementation_state = self.read_state()
        self.assertEqual(implementation_state["last_reviewed_candidate"], implementation_sha)
        self.assertEqual(implementation_state["accepted_code_commit"], implementation_sha)
        self.run_command(
            "git",
            "-C",
            str(self.repo),
            "add",
            "docs/CURRENT_STAGE.md",
            "docs/IMPLEMENTATION_REVIEW.md",
        )
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "docs: record implementation review")

        protocol = self.repo / "docs" / "PROTOCOL.md"
        protocol.write_text("# Protocol\n", encoding="utf-8")
        self.run_command("git", "-C", str(self.repo), "add", "docs/PROTOCOL.md")
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "docs: add protocol")
        docs_sha = self.run_command("git", "-C", str(self.repo), "rev-parse", "HEAD")

        self.record_review(docs_sha, "docs_only", "ACCEPT_WITH_P2", "PROTOCOL_REVIEW.md")
        docs_state = self.read_state()
        self.assertEqual(docs_state["last_reviewed_candidate"], docs_sha)
        self.assertEqual(docs_state["accepted_code_commit"], implementation_sha)
        self.run_command(
            "git",
            "-C",
            str(self.repo),
            "add",
            "docs/CURRENT_STAGE.md",
            "docs/PROTOCOL_REVIEW.md",
        )
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "docs: record protocol review")

        implementation.write_text("VALUE = 2\n", encoding="utf-8")
        self.run_command("git", "-C", str(self.repo), "add", "method.py")
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "feat: revise method")
        rejected_sha = self.run_command("git", "-C", str(self.repo), "rev-parse", "HEAD")

        self.record_review(rejected_sha, "implementation", "REJECT", "REJECTED_REVIEW.md")
        rejected_state = self.read_state()
        self.assertEqual(rejected_state["last_reviewed_candidate"], rejected_sha)
        self.assertEqual(rejected_state["accepted_code_commit"], implementation_sha)

    def test_record_review_supports_legacy_inputs_and_rejects_kind_conflicts(self):
        self.initialize_and_commit()
        implementation = self.repo / "method.py"
        implementation.write_text("VALUE = 1\n", encoding="utf-8")
        self.run_command("git", "-C", str(self.repo), "add", "method.py")
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "feat: add method")
        candidate = self.run_command("git", "-C", str(self.repo), "rev-parse", "HEAD")
        report = self.repo / "docs" / "REVIEW.md"
        report.write_text("# Review\n", encoding="utf-8")

        review_path = self.repo / "review-input.json"
        base_review = {
            "candidate_sha": candidate,
            "verdict": "ACCEPT",
            "review_report": "docs/REVIEW.md",
            "open_findings": [],
            "next_gate": "next",
            "next_action": "verify",
        }
        review_path.write_text(json.dumps(base_review), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
        )
        legacy_state = self.read_state()
        self.assertEqual(legacy_state["accepted_code_commit"], candidate)

        base_review["verdict"] = "BLOCKED"
        base_review["open_findings"] = ["BLOCKED: required evidence is unavailable."]
        base_review["accepted_code_commit"] = candidate
        review_path.write_text(json.dumps(base_review), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
        )
        blocked_state = self.read_state()
        self.assertEqual(blocked_state["accepted_code_commit"], candidate)

        self.run_command(
            "git",
            "-C",
            str(self.repo),
            "add",
            "docs/CURRENT_STAGE.md",
            "docs/REVIEW.md",
        )
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "docs: record legacy review")
        protocol = self.repo / "docs" / "PROTOCOL.md"
        protocol.write_text("# Protocol\n", encoding="utf-8")
        self.run_command("git", "-C", str(self.repo), "add", "docs/PROTOCOL.md")
        self.run_command("git", "-C", str(self.repo), "commit", "-m", "docs: add protocol")
        docs_candidate = self.run_command("git", "-C", str(self.repo), "rev-parse", "HEAD")
        base_review["candidate_sha"] = docs_candidate
        base_review["verdict"] = "ACCEPT_WITH_P2"
        base_review["open_findings"] = ["P2: bounded limitation."]
        base_review["accepted_code_commit"] = candidate
        review_path.write_text(json.dumps(base_review), encoding="utf-8")
        self.run_command(
            sys.executable,
            str(HANDOFF),
            "record-review",
            "--repo",
            str(self.repo),
            "--input",
            str(review_path),
        )
        legacy_docs_state = self.read_state()
        self.assertEqual(legacy_docs_state["last_reviewed_candidate"], docs_candidate)
        self.assertEqual(legacy_docs_state["accepted_code_commit"], candidate)

        base_review["candidate_sha"] = docs_candidate
        base_review["verdict"] = "ACCEPT"
        base_review["open_findings"] = []
        base_review["candidate_kind"] = "implementation"
        base_review["accepted_code_commit"] = "0" * 40
        review_path.write_text(json.dumps(base_review), encoding="utf-8")
        conflict = subprocess.run(
            [
                sys.executable,
                str(HANDOFF),
                "record-review",
                "--repo",
                str(self.repo),
                "--input",
                str(review_path),
            ],
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=self.env,
        )
        self.assertEqual(conflict.returncode, 2)
        self.assertIn("conflicts with candidate_kind", conflict.stderr)

        base_review["candidate_kind"] = "invalid"
        base_review.pop("accepted_code_commit")
        review_path.write_text(json.dumps(base_review), encoding="utf-8")
        invalid = subprocess.run(
            [
                sys.executable,
                str(HANDOFF),
                "record-review",
                "--repo",
                str(self.repo),
                "--input",
                str(review_path),
            ],
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=self.env,
        )
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("candidate_kind must be", invalid.stderr)

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
