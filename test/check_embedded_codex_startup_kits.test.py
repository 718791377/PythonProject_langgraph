import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools" / "check_embedded_codex_startup_kits.py"
STARTUP = Path("docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md")
STARTUP_ZH = Path("docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.zh-CN.md")
MATRIX = Path("docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md")
LEDGER = Path("docs_bilingual/templates/shared_governance_ledgers/decision-log-entry-template.md")
TAILORING = Path("docs_bilingual/templates/tailoring_decision_record_template.md")
PROJECT_KIT = Path("docs_bilingual/project_kits/one_person_company_with_embedded_codex/remote-publication-gate.md")
REGISTRY = Path("docs_bilingual/docs_registry.yaml")
MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD = Path("tools/run_openspec_guard.py")
SAFETY = Path("tools/safety_rule_script_backing_registry.json")


class EmbeddedCodexStartupKitsTest(unittest.TestCase):
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
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"embedded-startup-kits-{uuid.uuid4().hex[:8]}"
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
        self.assertEqual(checked["payload"]["counts"]["startup_documents"], 12)
        return checked

    def assert_checker_fails_with(self, root: Path, expected: str) -> None:
        checked = self.run_checker(root)
        self.assertNotEqual(checked["returncode"], 0, checked["raw"])
        self.assertFalse(checked["payload"]["ok"])
        self.assertTrue(any(expected in error for error in checked["payload"]["errors"]), checked["payload"]["errors"])

    def test_current_repository_checker_passes(self) -> None:
        result = self.run_python([str(CHECKER), "--root", str(REPO_ROOT), "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["required_pairs"], 16)
        self.assertEqual(payload["counts"]["required_files"], 32)
        self.assertEqual(payload["counts"]["ledger_templates"], 6)
        self.assertEqual(payload["counts"]["project_kit_pages"], 7)

    def test_checker_accepts_copied_valid_stage_b_package(self) -> None:
        root = self.make_root()
        self.assert_checker_passes(root)

    def test_fails_when_required_stage_b_file_is_missing(self) -> None:
        root = self.make_root()
        (root / PROJECT_KIT).unlink()
        self.assert_checker_fails_with(root, "Required file is missing")

    def test_fails_when_bilingual_frontmatter_is_missing(self) -> None:
        root = self.make_root()
        target = root / STARTUP_ZH
        text = target.read_text(encoding="utf-8")
        target.write_text(text.split("---", 2)[-1].lstrip(), encoding="utf-8")
        self.assert_checker_fails_with(root, "front matter")

    def test_fails_when_english_primary_contains_non_ascii(self) -> None:
        root = self.make_root()
        target = root / STARTUP
        target.write_text(target.read_text(encoding="utf-8") + "\u4e71\u7801\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "non-ASCII")

    def test_fails_when_file_contains_replacement_character(self) -> None:
        root = self.make_root()
        target = root / STARTUP_ZH
        target.write_text(target.read_text(encoding="utf-8") + "\ufffd\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "replacement character")

    def test_fails_when_file_contains_mojibake_sentinel(self) -> None:
        root = self.make_root()
        target = root / STARTUP_ZH
        target.write_text(target.read_text(encoding="utf-8") + "\u4e71\u7801\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "mojibake")

    def test_fails_when_startup_order_is_not_exact(self) -> None:
        root = self.make_root()
        target = root / STARTUP
        text = target.read_text(encoding="utf-8")
        text = text.replace("1. `thesis.md`", "1. `architecture.md`", 1).replace("2. `architecture.md`", "2. `thesis.md`", 1)
        target.write_text(text, encoding="utf-8")
        self.assert_checker_fails_with(root, "12-document startup order")

    def test_fails_when_matrix_lacks_required_tokens(self) -> None:
        root = self.make_root()
        target = root / MATRIX
        target.write_text(target.read_text(encoding="utf-8").replace("truth_owner", "truthOwner"), encoding="utf-8")
        self.assert_checker_fails_with(root, "truth_owner")

    def test_fails_when_matrix_lacks_two_gate_language(self) -> None:
        root = self.make_root()
        target = root / MATRIX
        target.write_text(target.read_text(encoding="utf-8").replace("business gate", "business approval"), encoding="utf-8")
        self.assert_checker_fails_with(root, "business gate")

    def test_fails_when_shared_ledger_metadata_field_missing(self) -> None:
        root = self.make_root()
        target = root / LEDGER
        target.write_text(target.read_text(encoding="utf-8").replace("decision_right", "decisionRight"), encoding="utf-8")
        self.assert_checker_fails_with(root, "decision_right")

    def test_fails_when_tailoring_field_missing(self) -> None:
        root = self.make_root()
        target = root / TAILORING
        target.write_text(target.read_text(encoding="utf-8").replace("why_not_lighter", "whyNotLighter"), encoding="utf-8")
        self.assert_checker_fails_with(root, "why_not_lighter")

    def test_fails_when_process_group_heading_missing(self) -> None:
        root = self.make_root()
        target = root / PROJECT_KIT
        target.write_text(target.read_text(encoding="utf-8").replace("Tools And Techniques", "Techniques"), encoding="utf-8")
        self.assert_checker_fails_with(root, "Tools And Techniques")

    def test_fails_when_registry_entry_missing(self) -> None:
        root = self.make_root()
        registry = root / REGISTRY
        registry.write_text(registry.read_text(encoding="utf-8").replace("one_person_company_embedded_codex_startup_matrix", "one_person_company_embedded_codex_startup_matrix_removed"), encoding="utf-8")
        self.assert_checker_fails_with(root, "one_person_company_embedded_codex_startup_matrix")

    def test_fails_when_registry_has_duplicate_doc_id(self) -> None:
        root = self.make_root()
        registry = root / REGISTRY
        registry.write_text(registry.read_text(encoding="utf-8") + "\n  - doc_id: tailoring_decision_record_template\n    doc_class: template\n    status: active\n    canonical_path: docs_bilingual/templates/tailoring_decision_record_template.md\n    zh_cn_path: docs_bilingual/templates/tailoring_decision_record_template.zh-CN.md\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "duplicate doc_id")

    def test_fails_when_ci_manifest_registration_missing(self) -> None:
        root = self.make_root()
        manifest = root / MANIFEST
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["python_unittest"] = [name for name in data["python_unittest"] if name != "check_embedded_codex_startup_kits.test.py"]
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "does not register `check_embedded_codex_startup_kits.test.py`")

    def test_fails_when_guard_registration_missing(self) -> None:
        root = self.make_root()
        guard = root / GUARD
        guard.write_text(guard.read_text(encoding="utf-8").replace("check_embedded_codex_startup_kits", "check_other_startup_kits"), encoding="utf-8")
        self.assert_checker_fails_with(root, "check_embedded_codex_startup_kits")

    def test_fails_when_safety_registry_registration_missing(self) -> None:
        root = self.make_root()
        safety = root / SAFETY
        safety.write_text(safety.read_text(encoding="utf-8").replace("tools/check_embedded_codex_startup_kits.py", "tools/check_other.py"), encoding="utf-8")
        self.assert_checker_fails_with(root, "tools/check_embedded_codex_startup_kits.py")


if __name__ == "__main__":
    unittest.main()

