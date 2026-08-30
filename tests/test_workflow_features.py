import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "skills" / "codex-research-workflow" / "scripts" / "workflow.py"
CLEANUP = ROOT / "skills" / "research-artifact-cleanup" / "scripts" / "cleanup.py"


class CommandTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex-research-workflow-")
        self.base = Path(self.temp.name)
        self.env = os.environ.copy()
        self.env["PYTHONUTF8"] = "1"

    def tearDown(self):
        self.temp.cleanup()

    def run_cmd(self, *args, expected=0):
        result = subprocess.run(
            args,
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            env=self.env,
        )
        self.assertEqual(result.returncode, expected, f"stdout={result.stdout}\nstderr={result.stderr}")
        return result

    def git(self, repo, *args):
        return self.run_cmd("git", "-C", str(repo), *args).stdout.strip()

    def configure(self, repo):
        self.git(repo, "config", "user.name", "Workflow Test")
        self.git(repo, "config", "user.email", "workflow@example.invalid")
        self.git(repo, "config", "commit.gpgsign", "false")

    def test_init_plans_then_commits_and_pushes_main(self):
        repo = self.base / "project"
        remote = self.base / "remote.git"
        repo.mkdir()
        (repo / "model.py").write_text("print('ok')\n", encoding="utf-8")
        self.run_cmd("git", "init", "--bare", str(remote))
        self.run_cmd("git", "init", "-b", "main", str(repo))
        self.configure(repo)
        self.git(repo, "remote", "add", "origin", str(remote))

        plan_result = self.run_cmd(sys.executable, str(WORKFLOW), "init", "--repo", str(repo))
        plan = json.loads(plan_result.stdout)
        self.assertEqual(plan["branch"], "main")
        self.assertFalse(plan["blocked_files"])

        applied = self.run_cmd(
            sys.executable,
            str(WORKFLOW),
            "init",
            "--repo",
            str(repo),
            "--apply",
            "--expected-plan-id",
            plan["plan_id"],
        )
        result = json.loads(applied.stdout)
        self.assertEqual(result["status"], "initialized")
        self.assertEqual(self.git(repo, "branch", "--show-current"), "main")
        self.assertEqual(self.git(repo, "rev-parse", "HEAD"), self.git(repo, "rev-parse", "origin/main"))
        self.assertTrue((repo / "docs" / "PROJECT_CORE.md").is_file())
        self.assertIn("experiments/runs/", (repo / ".gitignore").read_text(encoding="utf-8"))

    def test_migrate_and_prepare_artifacts_on_demand(self):
        repo = self.base / "legacy"
        repo.mkdir()
        self.run_cmd("git", "init", "-b", "main", str(repo))
        self.configure(repo)
        (repo / "README.md").write_text("legacy\n", encoding="utf-8")
        self.git(repo, "add", "README.md")
        self.git(repo, "commit", "-m", "initial")

        plan = json.loads(self.run_cmd(sys.executable, str(WORKFLOW), "migrate", "--repo", str(repo)).stdout)
        self.run_cmd(
            sys.executable,
            str(WORKFLOW),
            "migrate",
            "--repo",
            str(repo),
            "--apply",
            "--expected-plan-id",
            plan["plan_id"],
            "--no-push",
        )
        self.assertFalse((repo / "experiments").exists())

        run_result = json.loads(
            self.run_cmd(
                sys.executable,
                str(WORKFLOW),
                "prepare-experiment",
                "--repo",
                str(repo),
                "--experiment-id",
                "objective-ablation",
                "--entrypoint",
                "experiments/scripts/run_ablation.py",
                "--data-id",
                "dataset-v1",
            ).stdout
        )
        self.assertEqual(run_result["manifest"]["schema"], "research-experiment-run/v1")
        self.assertTrue((repo / run_result["path"] / "manifest.json").is_file())

        evidence = json.loads(
            self.run_cmd(
                sys.executable,
                str(WORKFLOW),
                "prepare-evidence",
                "--repo",
                str(repo),
                "--experiment-id",
                "objective-ablation",
                "--question",
                "Does the revised objective improve the decision metric?",
                "--with-metrics",
            ).stdout
        )
        self.git(repo, "add", evidence["path"])
        validated = json.loads(
            self.run_cmd(
                sys.executable,
                str(WORKFLOW),
                "validate-evidence",
                "--repo",
                str(repo),
                "--path",
                evidence["path"],
            ).stdout
        )
        self.assertEqual(validated["status"], "valid")

    def test_commands_reject_nested_or_inexact_project_roots(self):
        project = self.base / "project-root"
        repo = project / "nested-repo"
        child = repo / "src"
        child.mkdir(parents=True)
        self.run_cmd("git", "init", "-b", "main", str(repo))
        self.configure(repo)
        (repo / "README.md").write_text("nested\n", encoding="utf-8")
        self.git(repo, "add", "README.md")
        self.git(repo, "commit", "-m", "initial")

        nested = self.run_cmd(
            sys.executable,
            str(WORKFLOW),
            "audit",
            "--repo",
            str(project),
            expected=2,
        )
        self.assertIn("project root contains a nested Git repository", nested.stderr)

        inexact = self.run_cmd(
            sys.executable,
            str(WORKFLOW),
            "audit",
            "--repo",
            str(child),
            expected=2,
        )
        self.assertIn("exact project/Git root", inexact.stderr)

        decisions = self.base / "nested-decisions.json"
        decisions.write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "path": "nested-repo/README.md",
                            "classification": "unknown",
                            "action": "keep",
                            "reason": "must remain outside cleanup until roots are unified",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        cleanup = self.run_cmd(
            sys.executable,
            str(CLEANUP),
            "plan",
            "--repo",
            str(project),
            "--decisions",
            str(decisions),
            expected=2,
        )
        self.assertIn("one project root", cleanup.stderr)

    def test_cleanup_requires_plan_id_and_preserves_unknown(self):
        repo = self.base / "cleanup-project"
        repo.mkdir()
        self.run_cmd("git", "init", "-b", "main", str(repo))
        self.configure(repo)
        (repo / "AGENTS.md").write_text("# Rules\n\n- Experiment root: `experiments`\n", encoding="utf-8")
        (repo / "docs").mkdir()
        (repo / "docs" / "PROJECT_CORE.md").write_text("# Core\n", encoding="utf-8")
        (repo / ".gitignore").write_text(
            "experiments/runs/\n"
            "experiments/runs/old/r001\n"
            "experiments/.tmp/\n"
            "experiments/quarantine/\n",
            encoding="utf-8",
        )
        self.git(repo, "add", "AGENTS.md", "docs/PROJECT_CORE.md", ".gitignore")
        self.git(repo, "commit", "-m", "governance")
        junk = repo / "experiments" / "runs" / "old" / "r001"
        junk.mkdir(parents=True)
        (junk / "stdout.log").write_text("technical failure\n", encoding="utf-8")
        readonly = junk / "readonly.log"
        readonly.write_text("generated Git object\n", encoding="utf-8")
        os.chmod(readonly, stat.S_IREAD)

        decisions = self.base / "decisions.json"
        decisions.write_text(
            json.dumps(
                {
                    "important": True,
                    "items": [
                        {
                            "path": "experiments/runs/old/r001",
                            "classification": "delete_technical_failure",
                            "action": "delete",
                            "reason": "interpreter failed before the method ran",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        planned = json.loads(
            self.run_cmd(sys.executable, str(CLEANUP), "plan", "--repo", str(repo), "--decisions", str(decisions)).stdout
        )
        plan_path = repo / planned["plan"]
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["execution"]["failures"].append(
            {
                "phase": "delete",
                "at": "2026-01-01T00:00:00+00:00",
                "error": "simulated partial deletion at "
                + str((junk / "stdout.log").resolve()),
            }
        )
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        (junk / "stdout.log").unlink()
        self.run_cmd(
            sys.executable,
            str(CLEANUP),
            "apply",
            "--repo",
            str(repo),
            "--plan",
            planned["plan"],
            "--plan-id",
            "wrong",
            "--phase",
            "delete",
            expected=2,
        )
        self.assertTrue(junk.exists())
        for phase in ("relocate", "delete", "verify"):
            self.run_cmd(
                sys.executable,
                str(CLEANUP),
                "apply",
                "--repo",
                str(repo),
                "--plan",
                planned["plan"],
                "--plan-id",
                planned["plan_id"],
                "--phase",
                phase,
            )
        self.assertFalse(junk.exists())
        record_path = repo / "experiments" / "registry" / "cleanup" / f"{planned['plan_id']}.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assertEqual(record["schema"], "research-artifact-cleanup-record/v3")
        self.assertEqual(record["totals"]["delete_technical_failure"]["items"], 1)
        self.assertEqual(len(record["groups"]), 1)
        self.assertEqual(record["groups"][0]["items"], 1)
        self.assertEqual(record["groups"][0]["paths"], ["experiments/runs/old/r001"])
        self.assertNotIn("items", record)
        self.assertFalse((repo / planned["plan"]).exists())

    def test_cleanup_user_retired_requires_and_records_user_decision(self):
        repo = self.base / "cleanup-user-retired"
        repo.mkdir()
        self.run_cmd("git", "init", "-b", "main", str(repo))
        self.configure(repo)
        (repo / "AGENTS.md").write_text("# Rules\n\n- Experiment root: `experiments`\n", encoding="utf-8")
        (repo / "docs").mkdir()
        (repo / "docs" / "PROJECT_CORE.md").write_text("# Core\n", encoding="utf-8")
        (repo / ".gitignore").write_text("experiments/runs/\nexperiments/.tmp/\n", encoding="utf-8")
        self.git(repo, "add", "AGENTS.md", "docs/PROJECT_CORE.md", ".gitignore")
        self.git(repo, "commit", "-m", "governance")
        retired = repo / "experiments" / "runs" / "legacy-grid"
        retired.mkdir(parents=True)
        (retired / "result.json").write_text("{}\n", encoding="utf-8")

        decisions = self.base / "user-retired.json"
        item = {
            "path": "experiments/runs/legacy-grid",
            "classification": "delete_user_retired",
            "action": "delete",
            "reason": "compact golden evidence remains and exact stochastic replay is intentionally retired",
        }
        decisions.write_text(json.dumps({"important": True, "items": [item]}), encoding="utf-8")
        missing = self.run_cmd(
            sys.executable,
            str(CLEANUP),
            "plan",
            "--repo",
            str(repo),
            "--decisions",
            str(decisions),
            expected=2,
        )
        self.assertIn("requires user_decision", missing.stderr)

        item["user_decision"] = "Retain only golden, Results, and logs."
        decisions.write_text(json.dumps({"important": True, "items": [item]}), encoding="utf-8")
        planned = json.loads(
            self.run_cmd(sys.executable, str(CLEANUP), "plan", "--repo", str(repo), "--decisions", str(decisions)).stdout
        )
        self.assertEqual(json.loads((repo / planned["plan"]).read_text(encoding="utf-8"))["schema"], "research-artifact-cleanup-plan/v2")
        for phase in ("relocate", "delete", "verify"):
            self.run_cmd(
                sys.executable,
                str(CLEANUP),
                "apply",
                "--repo",
                str(repo),
                "--plan",
                planned["plan"],
                "--plan-id",
                planned["plan_id"],
                "--phase",
                phase,
            )
        record = json.loads(
            (repo / "experiments" / "registry" / "cleanup" / f"{planned['plan_id']}.json").read_text(encoding="utf-8")
        )
        self.assertEqual(record["schema"], "research-artifact-cleanup-record/v3")
        self.assertEqual(record["totals"]["delete_user_retired"]["items"], 1)
        self.assertEqual(record["groups"][0]["user_decision"], "Retain only golden, Results, and logs.")


if __name__ == "__main__":
    unittest.main()
