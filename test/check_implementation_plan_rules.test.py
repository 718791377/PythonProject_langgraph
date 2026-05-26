import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_implementation_plan_rules.py"


class ImplementationPlanRulesCheckTest(unittest.TestCase):
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
            [sys.executable, str(SCRIPT_PATH), "--root", str(root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_check_json(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_for_active_english_primary_and_chinese_companion(self) -> None:
        root = self.make_root("impl-plan-pass")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", "# Sample\n")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", "# 示例\n")
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_plan\n"
            "    doc_class: implementation_plan\n"
            "    status: active\n"
            "    canonical_path: docs_bilingual/implementation_plans/sample_plan.md\n"
            "    zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Implementation plan rules check passed.", result.stdout)

        json_result = self.run_check_json(root)
        self.assertEqual(json_result.returncode, 0, json_result.stdout + "\n" + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "implementation_plan_rules")
        self.assertEqual(Path(payload["root"]), root)
        self.assertTrue(payload["generated_at"])
        self.assertEqual(payload["implementation_plan_entries"], 1)
        self.assertEqual(payload["counts"]["implementation_plan_entries"], 1)

    def test_warns_for_draft_chinese_canonical_without_failing(self) -> None:
        root = self.make_root("impl-plan-warn")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", "# 示例\n")
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_plan\n"
            "    doc_class: implementation_plan\n"
            "    status: draft\n"
            "    canonical_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n"
            "    zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Warnings:", result.stdout)
        self.assertIn("still uses a Chinese file as canonical_path", result.stdout)

        json_result = self.run_check_json(root)
        self.assertEqual(json_result.returncode, 0, json_result.stdout + "\n" + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "implementation_plan_rules")
        self.assertTrue(any("still uses a Chinese file as canonical_path" in warning for warning in payload["warnings"]))
        self.assertEqual(payload["counts"]["warnings"], 2)


    def test_fails_for_mojibake_or_replacement_markers_in_plan_pair(self) -> None:
        root = self.make_root("impl-plan-mojibake")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", "# Sample\nASCII only.\n")
        self.write_file(
            root,
            "docs_bilingual/implementation_plans/sample_plan.zh-CN.md",
            "# ??\n?????`field` ?????\nReplacement: \ufffd\n",
        )
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_plan\n"
            "    doc_class: implementation_plan\n"
            "    status: active\n"
            "    canonical_path: docs_bilingual/implementation_plans/sample_plan.md\n"
            "    zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contains mojibake or replacement-character marker", result.stdout)

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("contains mojibake or replacement-character marker" in error for error in payload["errors"])
        )
        self.assertGreaterEqual(payload["counts"]["errors"], 1)

    def test_fails_when_comet_build_references_draft_plan(self) -> None:
        root = self.make_root("impl-plan-comet-draft")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", "# Sample\n")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", "# 示例\n")
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_plan\n"
            "    doc_class: implementation_plan\n"
            "    status: draft\n"
            "    canonical_path: docs_bilingual/implementation_plans/sample_plan.md\n"
            "    zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n",
        )
        self.write_file(
            root,
            "openspec/changes/sample-change/.comet.yaml",
            "workflow: full\n"
            "phase: build\n"
            "plan: docs_bilingual/implementation_plans/sample_plan.md\n",
        )

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("status must be active before implementation" in error for error in payload["errors"])
        )


if __name__ == "__main__":
    unittest.main()
