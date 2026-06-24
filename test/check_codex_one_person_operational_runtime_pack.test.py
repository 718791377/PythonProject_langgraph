import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools" / "check_codex_one_person_operational_runtime_pack.py"
SHARED = Path("docs_bilingual/project_kits/one_person_company_with_embedded_codex/shared-ledgers/decision-log.md")
SHARED_ZH = Path("docs_bilingual/project_kits/one_person_company_with_embedded_codex/shared-ledgers/decision-log.zh-CN.md")
CODEX = Path("docs_bilingual/project_kits/one_person_company_with_embedded_codex/codex-platform/agent-routing-policy.md")
BUSINESS = Path("docs_bilingual/project_kits/one_person_company_with_embedded_codex/business-operations/offer-pricing-finance-control.md")
MIXED = Path("docs_bilingual/project_kits/one_person_company_with_embedded_codex/mixed-governance/mixed-change-dual-gate-playbook.md")
REGISTRY = Path("docs_bilingual/docs_registry.yaml")
MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD = Path("tools/run_openspec_guard.py")
GUARD_TEST = Path("test/run_openspec_guard_json.test.py")
SAFETY = Path("tools/safety_rule_script_backing_registry.json")


class CodexOnePersonOperationalRuntimePackTest(unittest.TestCase):
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
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"operational-runtime-pack-{uuid.uuid4().hex[:8]}"
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
        self.assertEqual(checked["payload"]["counts"]["required_primary_files"], 26)
        self.assertEqual(checked["payload"]["counts"]["required_bilingual_files"], 52)
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
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def replace_all(self, root: Path, rel: Path, old: str, new: str) -> None:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def test_current_repository_checker_passes(self) -> None:
        result = self.run_python([str(CHECKER), "--root", str(REPO_ROOT), "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["groups"], 4)

    def test_checker_accepts_copied_valid_runtime_pack(self) -> None:
        root = self.make_root()
        self.assert_checker_passes(root)

    def test_fails_when_required_file_is_missing(self) -> None:
        root = self.make_root()
        (root / SHARED).unlink()
        self.assert_checker_fails_with(root, "Required file is missing")

    def test_fails_when_bilingual_companion_is_missing(self) -> None:
        root = self.make_root()
        (root / SHARED_ZH).unlink()
        self.assert_checker_fails_with(root, "Required file is missing")

    def test_fails_when_frontmatter_is_missing(self) -> None:
        root = self.make_root()
        target = root / SHARED
        target.write_text(target.read_text(encoding="utf-8").split("---", 2)[-1].lstrip(), encoding="utf-8")
        self.assert_checker_fails_with(root, "front matter")

    def test_fails_when_translation_of_drifts(self) -> None:
        root = self.make_root()
        self.replace_once(root, SHARED_ZH, str(SHARED).replace("\\", "/"), "docs_bilingual/project_kits/wrong.md")
        self.assert_checker_fails_with(root, "translation_of")

    def test_fails_when_shared_ledger_field_missing(self) -> None:
        root = self.make_root()
        self.replace_all(root, SHARED, "decision_right", "decisionRight")
        self.assert_checker_fails_with(root, "decision_right")

    def test_fails_when_codex_execution_truth_missing(self) -> None:
        root = self.make_root()
        text = (root / CODEX).read_text(encoding="utf-8")
        (root / CODEX).write_text(
            text.replace("execution truth", "execution record").replace("Execution Truth", "Execution Record"),
            encoding="utf-8",
        )
        self.assert_checker_fails_with(root, "execution truth")

    def test_fails_when_codex_claims_business_truth(self) -> None:
        root = self.make_root()
        with (root / CODEX).open("a", encoding="utf-8") as fh:
            fh.write("\nCodex owns business truth and Codex owns pricing.\n")
        self.assert_checker_fails_with(root, "prohibited authority claim")

    def test_fails_when_business_truth_missing(self) -> None:
        root = self.make_root()
        text = (root / BUSINESS).read_text(encoding="utf-8")
        (root / BUSINESS).write_text(
            text.replace("business truth", "business record").replace("Business Truth", "Business Record"),
            encoding="utf-8",
        )
        self.assert_checker_fails_with(root, "business truth")

    def test_fails_when_business_claims_execution_bypass(self) -> None:
        root = self.make_root()
        with (root / BUSINESS).open("a", encoding="utf-8") as fh:
            fh.write("\nBusiness may bypass Agent permissions and business owns execution truth.\n")
        self.assert_checker_fails_with(root, "prohibited authority claim")

    def test_fails_when_mixed_business_gate_missing(self) -> None:
        root = self.make_root()
        self.replace_all(root, MIXED, "business gate", "business approval")
        self.assert_checker_fails_with(root, "business gate")

    def test_fails_when_mixed_codex_gate_missing(self) -> None:
        root = self.make_root()
        self.replace_all(root, MIXED, "Codex execution gate", "Codex review gate")
        self.assert_checker_fails_with(root, "Codex execution gate")

    def test_fails_when_process_group_heading_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, SHARED, "## Tools And Techniques", "## Techniques")
        self.assert_checker_fails_with(root, "process-group")

    def test_fails_when_zh_process_group_heading_uses_english_fallback(self) -> None:
        root = self.make_root()
        self.replace_all(root, SHARED_ZH, "## 输入", "## Inputs")
        self.replace_all(root, SHARED_ZH, "## 工具与技术", "## Tools And Techniques")
        self.replace_all(root, SHARED_ZH, "## 输出", "## Outputs")
        self.assert_checker_fails_with(root, "输入 / 工具与技术 / 输出")

    def test_fails_when_registry_entry_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, REGISTRY, "shared_ledgers_decision_log", "shared_ledgers_decision_log_removed")
        self.assert_checker_fails_with(root, "docs_bilingual/docs_registry.yaml")

    def test_fails_when_registry_has_duplicate_doc_id(self) -> None:
        root = self.make_root()
        registry = root / REGISTRY
        registry.write_text(registry.read_text(encoding="utf-8") + "\n  - doc_id: shared_ledgers_decision_log\n    doc_class: operations_runtime_pack\n    status: active\n    canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/shared-ledgers/duplicate.md\n    zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/shared-ledgers/duplicate.zh-CN.md\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "duplicate doc_id")

    def test_fails_when_ci_manifest_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, MANIFEST, "check_codex_one_person_operational_runtime_pack.test.py", "check_codex_one_person_operational_runtime_pack.removed.py")
        self.assert_checker_fails_with(root, "ci_test_manifest")

    def test_fails_when_guard_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, GUARD, "check_codex_one_person_operational_runtime_pack", "check_codex_one_person_operational_runtime_pack_removed")
        self.assert_checker_fails_with(root, "run_openspec_guard")

    def test_fails_when_guard_json_test_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_all(root, GUARD_TEST, "check_codex_one_person_operational_runtime_pack", "check_codex_one_person_operational_runtime_pack_removed")
        self.assert_checker_fails_with(root, "run_openspec_guard_json")

    def test_fails_when_safety_registry_registration_missing(self) -> None:
        root = self.make_root()
        self.replace_once(root, SAFETY, "tools/check_codex_one_person_operational_runtime_pack.py", "tools/check_codex_one_person_operational_runtime_pack_removed.py")
        self.assert_checker_fails_with(root, "safety_rule_script_backing_registry")


if __name__ == "__main__":
    unittest.main()
