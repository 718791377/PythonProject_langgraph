import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "tools" / "generate_operations_package.py"
CHECKER = REPO_ROOT / "tools" / "check_operations_package_docs.py"
MANIFEST = REPO_ROOT / "tools" / "ci" / "ci_test_manifest.json"


class OperationsPackageDocsTest(unittest.TestCase):
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
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"operations-package-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        shutil.copytree(REPO_ROOT / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(REPO_ROOT / "docs_bilingual", root / "docs_bilingual")
        shutil.copytree(REPO_ROOT / "test", root / "test", ignore=shutil.ignore_patterns("__pycache__"))
        return root

    def test_current_repository_checker_passes(self) -> None:
        result = self.run_python([str(CHECKER), "--root", str(REPO_ROOT), "--json"])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["required_pairs"], 21)
        self.assertEqual(payload["counts"]["required_files"], 42)
        self.assertEqual(payload["counts"]["tailoring_modes"], 5)

    def test_generator_check_is_idempotent_for_current_repository(self) -> None:
        result = self.run_python([str(GENERATOR), "--root", str(REPO_ROOT), "--package", "all", "--check", "--json"])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["changed_or_missing"], 0)

    def test_generator_supports_individual_package_checks(self) -> None:
        codex = self.run_python([str(GENERATOR), "--root", str(REPO_ROOT), "--package", "codex", "--check", "--json"])
        one_person = self.run_python(
            [str(GENERATOR), "--root", str(REPO_ROOT), "--package", "one-person-company", "--check", "--json"]
        )

        self.assertEqual(codex.returncode, 0, codex.stdout + codex.stderr)
        self.assertEqual(one_person.returncode, 0, one_person.stdout + one_person.stderr)
        self.assertEqual(json.loads(codex.stdout)["counts"]["expected_files"], 22)
        self.assertEqual(json.loads(one_person.stdout)["counts"]["expected_files"], 20)

    def test_checker_fails_when_required_document_is_missing(self) -> None:
        root = self.make_root()
        target = root / "docs_bilingual" / "product_lifecycle" / "one_person_company_minimum_startup_documents.md"
        target.unlink()

        result = self.run_python([str(CHECKER), "--root", str(root), "--json"])

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Required generated file is missing" in error for error in payload["errors"]))

    def test_checker_fails_when_tailoring_or_ito_heading_drifts(self) -> None:
        root = self.make_root()
        target = root / "docs_bilingual" / "product_lifecycle" / "one_person_company_tailoring_decision_tree.md"
        text = target.read_text(encoding="utf-8")
        target.write_text(text.replace("## Inputs", "## Input Drift").replace("Hybrid architecture", "Hybrid drift"), encoding="utf-8")

        result = self.run_python([str(CHECKER), "--root", str(root), "--json"])

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("missing English I/T/O heading" in error for error in payload["errors"]))
        self.assertTrue(any("is not current with tools/generate_operations_package.py" in error for error in payload["errors"]))

    def test_checker_fails_when_registry_entry_is_missing(self) -> None:
        root = self.make_root()
        registry = root / "docs_bilingual" / "docs_registry.yaml"
        lines = registry.read_text(encoding="utf-8").splitlines()
        target = "codex_platform_core_documents_register"
        output: list[str] = []
        skip = False
        for line in lines:
            if line.strip() == f"- doc_id: {target}":
                skip = True
                continue
            if skip and line.startswith("  - doc_id: "):
                skip = False
            if not skip:
                output.append(line)
        registry.write_text("\n".join(output) + "\n", encoding="utf-8")

        result = self.run_python([str(CHECKER), "--root", str(root), "--json"])

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any(f"docs_registry.yaml is missing generated doc_id `{target}`" in error for error in payload["errors"]))

    def test_new_test_is_registered_in_ci_manifest(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertIn("operations_package_docs.test.py", manifest["python_unittest"])


if __name__ == "__main__":
    unittest.main()
