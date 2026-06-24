import json
import re
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools" / "check_codex_one_person_next_supplement_sequence.py"
PLAN = Path("docs_bilingual/implementation_plans/codex_one_person_next_supplement_file_sequence_plan.md")
SHARED = Path("docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md")
CODEX = Path("docs_bilingual/product_lifecycle/codex_platform_inventory_map.md")
CODEX_ZH = Path("docs_bilingual/product_lifecycle/codex_platform_inventory_map.zh-CN.md")
OPC = Path("docs_bilingual/product_lifecycle/one_person_company_inventory_map.md")
SUMMARY = Path("docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md")
PROJECT_KIT = Path("docs_bilingual/project_kits/one_person_company_with_embedded_codex/README.md")
REGISTRY = Path("docs_bilingual/docs_registry.yaml")
MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD = Path("tools/run_openspec_guard.py")
GUARD_TEST = Path("test/run_openspec_guard_json.test.py")
SAFETY = Path("tools/safety_rule_script_backing_registry.json")
GENERATOR = Path("tools/generate_operations_package.py")


class CodexOnePersonNextSupplementSequenceTest(unittest.TestCase):
    maxDiff = None

    def run_python(self, args: list[str], root: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=root or REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def make_root(self) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"next-supplement-sequence-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        shutil.copytree(REPO_ROOT / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(REPO_ROOT / "docs_bilingual", root / "docs_bilingual")
        shutil.copytree(REPO_ROOT / "test", root / "test", ignore=shutil.ignore_patterns("__pycache__"))
        return root

    def run_checker(self, root: Path) -> dict:
        result = self.run_python([str(CHECKER), "--root", str(root), "--json"])
        self.assertNotEqual(result.stdout, "", result.stderr)
        return {"returncode": result.returncode, "payload": json.loads(result.stdout), "raw": result.stdout + result.stderr}

    def assert_checker_passes(self, root: Path) -> dict:
        checked = self.run_checker(root)
        self.assertEqual(checked["returncode"], 0, checked["raw"])
        self.assertTrue(checked["payload"]["ok"])
        self.assertEqual(checked["payload"]["counts"]["groups"], 5)
        self.assertGreaterEqual(checked["payload"]["counts"]["required_primary_files"], 27)
        return checked

    def assert_checker_fails_with(self, root: Path, expected: str) -> None:
        checked = self.run_checker(root)
        self.assertNotEqual(checked["returncode"], 0, checked["raw"])
        self.assertFalse(checked["payload"]["ok"])
        self.assertTrue(any(expected in error for error in checked["payload"]["errors"]), checked["payload"]["errors"])

    def replace_once(self, root: Path, rel: Path, old: str, new: str) -> None:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def test_current_repository_checker_passes(self) -> None:
        result = self.run_python([str(CHECKER), "--root", str(REPO_ROOT), "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["groups"], 5)

    def test_checker_accepts_copied_valid_stage_b_package(self) -> None:
        root = self.make_root()
        self.assert_checker_passes(root)

    def test_fails_when_stage_b_group_order_drifts(self) -> None:
        root = self.make_root()
        self.replace_once(root, PLAN, "Group 1: Shared Boundary And Tailoring Rules", "Group 9: Shared Boundary And Tailoring Rules")
        self.assert_checker_fails_with(root, "ordered group")

    def test_fails_when_required_group_file_is_missing(self) -> None:
        root = self.make_root()
        (root / SHARED).unlink()
        self.assert_checker_fails_with(root, "Required file is missing")

    def test_fails_when_bilingual_companion_is_missing(self) -> None:
        root = self.make_root()
        (root / CODEX_ZH).unlink()
        self.assert_checker_fails_with(root, "Required file is missing")

    def test_fails_when_translation_of_drifts(self) -> None:
        root = self.make_root()
        self.replace_once(root, CODEX_ZH, "translation_of: docs_bilingual/product_lifecycle/codex_platform_inventory_map.md", "translation_of: docs_bilingual/product_lifecycle/wrong.md")
        self.assert_checker_fails_with(root, "translation_of")

    def test_fails_when_registry_entry_is_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, REGISTRY, "docs_bilingual/product_lifecycle/codex_platform_inventory_map.md", "docs_bilingual/product_lifecycle/codex_platform_inventory_map_removed.md")
        self.assert_checker_fails_with(root, "docs_bilingual/docs_registry.yaml is missing")

    def test_fails_when_registry_has_duplicate_doc_id(self) -> None:
        root = self.make_root()
        registry = root / REGISTRY
        registry.write_text(registry.read_text(encoding="utf-8") + "\n  - doc_id: lifecycle_tailoring_rules\n    doc_class: product_lifecycle\n    status: draft\n    canonical_path: docs_bilingual/product_lifecycle/lifecycle_tailoring_rules_duplicate.md\n    zh_cn_path: docs_bilingual/product_lifecycle/lifecycle_tailoring_rules_duplicate.zh-CN.md\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "duplicate doc_id")

    def test_fails_when_codex_truth_boundary_language_is_missing(self) -> None:
        root = self.make_root()
        target = root / CODEX
        text = target.read_text(encoding="utf-8")
        self.assertIn("execution truth", text)
        target.write_text(text.replace("execution truth", "execution record").replace("Execution truth", "Execution record"), encoding="utf-8")
        self.assert_checker_fails_with(root, "execution truth")

    def test_fails_when_business_truth_boundary_language_is_missing(self) -> None:
        root = self.make_root()
        target = root / OPC
        text = target.read_text(encoding="utf-8")
        self.assertIn("business truth", text)
        target.write_text(text.replace("business truth", "business record").replace("Business truth", "Business record"), encoding="utf-8")
        self.assert_checker_fails_with(root, "business truth")

    def test_fails_when_tailoring_scope_language_is_missing(self) -> None:
        root = self.make_root()
        target = root / SHARED
        text = target.read_text(encoding="utf-8")
        self.assertIn("phase-local lightweight", text)
        mutated = re.sub(r"(?i)phase[- ]local lightweight", "phase local light", text)
        self.assertNotEqual(mutated, text)
        target.write_text(mutated, encoding="utf-8")
        self.assert_checker_fails_with(root, "phase-local lightweight")

    def test_fails_when_process_group_heading_is_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, PROJECT_KIT, "### Tools And Techniques", "### Techniques")
        self.assert_checker_fails_with(root, "process-group")

    def test_fails_when_summary_bridge_language_is_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, SUMMARY, "10-layer", "ten-layer")
        self.assert_checker_fails_with(root, "10-layer")

    def test_fails_when_generator_closeout_language_is_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, GENERATOR, "Codex owns execution truth", "Codex owns execution records")
        self.assert_checker_fails_with(root, "Codex owns execution truth")

    def test_fails_when_ci_manifest_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, MANIFEST, "check_codex_one_person_next_supplement_sequence.test.py", "check_codex_one_person_next_supplement_sequence.removed.py")
        self.assert_checker_fails_with(root, "ci_test_manifest")

    def test_fails_when_guard_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, GUARD, "check_codex_one_person_next_supplement_sequence", "check_codex_one_person_next_supplement_sequence_removed")
        self.assert_checker_fails_with(root, "run_openspec_guard")

    def test_fails_when_guard_json_test_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, GUARD_TEST, "check_codex_one_person_next_supplement_sequence", "check_codex_one_person_next_supplement_sequence_removed")
        self.assert_checker_fails_with(root, "run_openspec_guard_json")

    def test_fails_when_safety_registry_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, SAFETY, "tools/check_codex_one_person_next_supplement_sequence.py", "tools/check_codex_one_person_next_supplement_sequence_removed.py")
        self.assert_checker_fails_with(root, "safety_rule_script_backing_registry")


if __name__ == "__main__":
    unittest.main()
