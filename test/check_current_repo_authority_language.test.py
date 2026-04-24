import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_current_repo_authority_language.py"
RULES_PATH = REPO_ROOT / "tools" / "current_repo_authority_language_rules.json"


class CurrentRepoAuthorityLanguageCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--rules", str(RULES_PATH)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_check_json(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--rules", str(RULES_PATH), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_allows_migration_plan_and_history_context(self) -> None:
        root = self.make_root("authority-pass")
        self.write_file(
            root,
            "docs_bilingual/implementation_plans/codex_langgraph_repository_split_migration_plan.md",
            "Move work out of D:\\PythonProject_OpenClaw into D:\\PythonProject_langgraph.\n",
        )
        self.write_file(
            root,
            "docs_bilingual/governance/openspec_usage_convention.md",
            "## 14. Historical External OpenClaw References\nOpenClaw historical comparison.\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("passed", result.stdout)
        self.assertIn("migration_plan", result.stdout)
        self.assertIn("historical_external_reference", result.stdout)

        json_result = self.run_check_json(root)
        self.assertEqual(json_result.returncode, 0, json_result.stdout + "\n" + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "current_repo_authority_language")
        self.assertEqual(Path(payload["root"]), root)
        self.assertTrue(payload["generated_at"])
        self.assertIn("migration_plan", payload["allowed_context_matches"])
        self.assertIn("historical_external_reference", payload["allowed_context_matches"])
        self.assertGreaterEqual(payload["counts"]["checked_files"], 1)

    def test_fails_when_current_authority_surface_uses_old_repo_as_current_subject(self) -> None:
        root = self.make_root("authority-fail")
        self.write_file(
            root,
            "docs_bilingual/governance/example.md",
            "OpenClaw is the current repository authority for this line.\n",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[old_repo_brand]", result.stdout)
        self.assertIn("OpenClaw is the current repository authority", result.stdout)

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "current_repo_authority_language")
        self.assertIn("[old_repo_brand]", payload["violations"][0])
        self.assertEqual(payload["counts"]["violations"], 1)


if __name__ == "__main__":
    unittest.main()
