import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "run_openspec_guard.py"


class RunOpenSpecGuardJsonTest(unittest.TestCase):
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

    def run_guard_json(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--tool", "codex", "--skip-validate", "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def make_json_script(self, ok: bool, payload: dict) -> str:
        payload_json = json.dumps(payload, ensure_ascii=False)
        code = [
            "import json",
            "import sys",
            f"payload = {payload_json!r}",
            "print(payload)",
            f"raise SystemExit({0 if ok else 1})",
        ]
        return "\n".join(code) + "\n"

    def test_guard_json_passes_and_aggregates_steps(self) -> None:
        root = self.make_root("guard-json-pass")
        self.write_file(root, "tools/verify_official_openspec.py", self.make_json_script(True, {"ok": True, "check_name": "verify"}))
        self.write_file(root, "tools/check_current_repo_authority_language.py", self.make_json_script(True, {"ok": True, "check_name": "authority"}))
        self.write_file(root, "tools/check_document_governance_rules.py", self.make_json_script(True, {"ok": True, "check_name": "governance"}))
        self.write_file(root, "tools/check_implementation_plan_rules.py", self.make_json_script(True, {"ok": True, "check_name": "implementation_plan"}))
        self.write_file(root, "tools/check_name_clarity_rules.py", self.make_json_script(True, {"ok": True, "check_name": "name_clarity_rules"}))
        self.write_file(root, "tools/check_context_retention_canary_surface.py", self.make_json_script(True, {"ok": True, "check_name": "context_retention_canary_surface"}))
        self.write_file(root, "tools/check_codex_skills_governance.py", self.make_json_script(True, {"ok": True, "check_name": "codex_skills_governance"}))

        result = self.run_guard_json(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "run_openspec_guard")
        self.assertEqual(Path(payload["root"]), root)
        self.assertTrue(payload["generated_at"])
        self.assertEqual(payload["tool"], "codex")
        self.assertEqual(len(payload["steps"]), 7)
        self.assertEqual(payload["counts"]["steps_total"], 7)
        self.assertEqual(payload["counts"]["steps_passed"], 7)
        self.assertEqual(payload["steps"][0]["step"], "verify_official_openspec")
        self.assertEqual(payload["steps"][1]["step"], "check_current_repo_authority_language")
        self.assertEqual(payload["steps"][4]["step"], "check_name_clarity_rules")
        self.assertEqual(payload["steps"][5]["step"], "check_context_retention_canary_surface")
        self.assertEqual(payload["steps"][6]["step"], "check_codex_skills_governance")

    def test_guard_json_reports_failed_step(self) -> None:
        root = self.make_root("guard-json-fail")
        self.write_file(root, "tools/verify_official_openspec.py", self.make_json_script(True, {"ok": True, "check_name": "verify"}))
        self.write_file(root, "tools/check_current_repo_authority_language.py", self.make_json_script(False, {"ok": False, "check_name": "authority", "errors": ["bad wording"]}))
        self.write_file(root, "tools/check_document_governance_rules.py", self.make_json_script(True, {"ok": True, "check_name": "governance"}))
        self.write_file(root, "tools/check_implementation_plan_rules.py", self.make_json_script(True, {"ok": True, "check_name": "implementation_plan"}))
        self.write_file(root, "tools/check_name_clarity_rules.py", self.make_json_script(True, {"ok": True, "check_name": "name_clarity_rules"}))
        self.write_file(root, "tools/check_context_retention_canary_surface.py", self.make_json_script(True, {"ok": True, "check_name": "context_retention_canary_surface"}))
        self.write_file(root, "tools/check_codex_skills_governance.py", self.make_json_script(True, {"ok": True, "check_name": "codex_skills_governance"}))

        result = self.run_guard_json(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "run_openspec_guard")
        self.assertEqual(payload["failed_step"], "check_current_repo_authority_language")
        self.assertEqual(payload["steps"][1]["data"]["check_name"], "authority")
        self.assertEqual(payload["counts"]["steps_failed"], 1)


if __name__ == "__main__":
    unittest.main()
