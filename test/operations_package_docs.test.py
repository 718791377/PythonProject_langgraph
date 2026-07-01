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
CODEX_DOC = Path("docs_bilingual/operations_packages/codex_cli_durable_team/vision.md")
CODEX_ZH = Path("docs_bilingual/operations_packages/codex_cli_durable_team/vision.zh-CN.md")
OPC_DOC = Path("docs_bilingual/operations_packages/one_person_company/offer.md")
CODEX_AGENT_GOVERNANCE = Path("docs_bilingual/operations_packages/codex_cli_durable_team/agent-governance.md")
CODEX_AGENT_TOOL_POLICY = Path("docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.md")
OPC_THESIS = Path("docs_bilingual/operations_packages/one_person_company/thesis.md")
OPC_COMPANY_THESIS = Path("docs_bilingual/operations_packages/one_person_company/company-thesis.md")
OPC_SUPPORT_PLAYBOOK = Path("docs_bilingual/operations_packages/one_person_company/support-playbook.md")
OPC_SUPPORT_POLICY = Path("docs_bilingual/operations_packages/one_person_company/support-policy.md")


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

    def run_checker(self, root: Path) -> dict:
        result = self.run_python([str(CHECKER), "--root", str(root), "--json"])
        self.assertNotEqual(result.stdout, "", result.stderr)
        return {"returncode": result.returncode, "payload": json.loads(result.stdout), "raw": result.stdout + result.stderr}

    def test_current_repository_checker_passes(self) -> None:
        result = self.run_python([str(CHECKER), "--root", str(REPO_ROOT), "--json"])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["codex_body_primaries"], 48)
        self.assertEqual(payload["counts"]["codex_body_files"], 96)
        self.assertEqual(payload["counts"]["one_person_company_body_primaries"], 60)
        self.assertEqual(payload["counts"]["one_person_company_body_files"], 120)
        self.assertEqual(payload["counts"]["required_pairs"], 108)
        self.assertEqual(payload["counts"]["required_files"], 216)
        self.assertEqual(payload["counts"]["tailoring_modes"], 5)
        self.assertTrue((REPO_ROOT / CODEX_AGENT_GOVERNANCE).exists())
        self.assertTrue((REPO_ROOT / OPC_THESIS).exists())
        self.assertTrue((REPO_ROOT / OPC_SUPPORT_PLAYBOOK).exists())
        self.assertFalse((REPO_ROOT / CODEX_AGENT_TOOL_POLICY).exists())
        self.assertFalse((REPO_ROOT / OPC_COMPANY_THESIS).exists())
        self.assertFalse((REPO_ROOT / OPC_SUPPORT_POLICY).exists())

    def test_generator_check_is_idempotent_for_current_repository(self) -> None:
        result = self.run_python([str(GENERATOR), "--root", str(REPO_ROOT), "--package", "all", "--check", "--json"])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["expected_pairs"], 108)
        self.assertEqual(payload["counts"]["expected_files"], 216)
        self.assertEqual(payload["counts"]["changed_or_missing"], 0)

    def test_generator_supports_individual_package_checks(self) -> None:
        codex = self.run_python([str(GENERATOR), "--root", str(REPO_ROOT), "--package", "codex", "--check", "--json"])
        one_person = self.run_python(
            [str(GENERATOR), "--root", str(REPO_ROOT), "--package", "one-person-company", "--check", "--json"]
        )

        self.assertEqual(codex.returncode, 0, codex.stdout + codex.stderr)
        self.assertEqual(one_person.returncode, 0, one_person.stdout + one_person.stderr)
        self.assertEqual(json.loads(codex.stdout)["counts"]["expected_pairs"], 48)
        self.assertEqual(json.loads(codex.stdout)["counts"]["expected_files"], 96)
        self.assertEqual(json.loads(one_person.stdout)["counts"]["expected_pairs"], 60)
        self.assertEqual(json.loads(one_person.stdout)["counts"]["expected_files"], 120)

    def test_package_specific_write_does_not_write_other_package(self) -> None:
        root = self.make_root()
        shutil.rmtree(root / "docs_bilingual" / "operations_packages", ignore_errors=True)

        codex = self.run_python([str(GENERATOR), "--root", str(root), "--package", "codex", "--json"])
        self.assertEqual(codex.returncode, 0, codex.stdout + codex.stderr)
        self.assertTrue((root / CODEX_DOC).exists())
        self.assertFalse((root / OPC_DOC).exists())

        one_person = self.run_python([str(GENERATOR), "--root", str(root), "--package", "one-person-company", "--json"])
        self.assertEqual(one_person.returncode, 0, one_person.stdout + one_person.stderr)
        self.assertTrue((root / OPC_DOC).exists())

    def test_checker_fails_when_required_body_document_is_missing(self) -> None:
        root = self.make_root()
        (root / CODEX_DOC).unlink()

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        self.assertFalse(checked["payload"]["ok"])
        self.assertTrue(any("Required generated body file is missing" in error for error in checked["payload"]["errors"]))

    def test_checker_fails_when_translation_of_drifts(self) -> None:
        root = self.make_root()
        target = root / CODEX_ZH
        text = target.read_text(encoding="utf-8")
        target.write_text(text.replace(str(CODEX_DOC).replace("\\", "/"), "docs_bilingual/operations_packages/wrong.md"), encoding="utf-8")

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        self.assertTrue(any("translation_of" in error for error in checked["payload"]["errors"]))

    def test_checker_fails_when_tailoring_or_ito_heading_drifts(self) -> None:
        root = self.make_root()
        target = root / CODEX_DOC
        text = target.read_text(encoding="utf-8")
        target.write_text(
            text.replace("## Inputs", "## Input Drift").replace("Hybrid architecture", "Hybrid drift"),
            encoding="utf-8",
        )

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        errors = checked["payload"]["errors"]
        self.assertTrue(any("I/T/O headings" in error for error in errors))
        self.assertTrue(any("not current with tools/generate_operations_package.py" in error for error in errors))

    def test_checker_fails_when_ito_section_is_empty(self) -> None:
        root = self.make_root()
        target = root / CODEX_DOC
        text = target.read_text(encoding="utf-8")
        start = text.index("## Inputs") + len("## Inputs")
        end = text.index("## Tools And Techniques")
        target.write_text(text[:start] + "\n\n" + text[end:], encoding="utf-8")

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        self.assertTrue(any("I/T/O section `## Inputs` is empty" in error for error in checked["payload"]["errors"]))

    def test_checker_fails_when_registry_entry_is_missing(self) -> None:
        root = self.make_root()
        registry = root / "docs_bilingual" / "docs_registry.yaml"
        lines = registry.read_text(encoding="utf-8").splitlines()
        target = "codex_cli_durable_team_vision"
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

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        self.assertTrue(any(f"docs_registry.yaml is missing generated doc_id `{target}`" in error for error in checked["payload"]["errors"]))

    def test_checker_fails_on_duplicate_registry_doc_id_or_path(self) -> None:
        root = self.make_root()
        registry = root / "docs_bilingual" / "docs_registry.yaml"
        text = registry.read_text(encoding="utf-8")
        duplicate = "\n  - doc_id: codex_cli_durable_team_vision\n    doc_class: operations_package\n    status: active\n    canonical_path: docs_bilingual/operations_packages/codex_cli_durable_team/vision.md\n    zh_cn_path: docs_bilingual/operations_packages/codex_cli_durable_team/vision.zh-CN.md\n"
        registry.write_text(text + duplicate, encoding="utf-8")

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        self.assertTrue(any("duplicate doc_id" in error or "duplicate path" in error for error in checked["payload"]["errors"]))

    def test_checker_fails_on_encoding_or_contamination(self) -> None:
        root = self.make_root()
        en = root / CODEX_DOC
        en.write_text(en.read_text(encoding="utf-8") + "\nNon ASCII: 中文\nsolo business\n", encoding="utf-8")
        zh = root / CODEX_ZH
        zh.write_text(zh.read_text(encoding="utf-8") + "\ufffd\n", encoding="utf-8")

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        errors = checked["payload"]["errors"]
        self.assertTrue(any("English primary contains non-ASCII" in error for error in errors))
        self.assertTrue(any("replacement character" in error for error in errors))
        self.assertTrue(any("one-person-company-only language" in error for error in errors))

    def test_checker_fails_on_zh_mojibake_sentinel(self) -> None:
        root = self.make_root()
        zh = root / CODEX_ZH
        text = zh.read_text(encoding="utf-8")
        zh.write_text(text.replace("## 目的", "## " + chr(0x9429) + "的", 1), encoding="utf-8")

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        errors = checked["payload"]["errors"]
        self.assertTrue(any("readable Chinese snippets" in error for error in errors))
        self.assertTrue(any("mojibake sentinel" in error for error in errors))

    def test_generator_removes_stale_legacy_files_and_registry_entries(self) -> None:
        root = self.make_root()
        stale_paths = [CODEX_AGENT_TOOL_POLICY, OPC_COMPANY_THESIS, OPC_SUPPORT_POLICY]
        for rel in stale_paths:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("stale legacy generated document\n", encoding="utf-8")
        registry = root / "docs_bilingual" / "docs_registry.yaml"
        registry.write_text(
            registry.read_text(encoding="utf-8")
            + "\n  - doc_id: codex_cli_durable_team_agent_tool_policy\n"
            + "    doc_class: operations_package\n"
            + "    status: active\n"
            + "    canonical_path: docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.md\n"
            + "    zh_cn_path: docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.zh-CN.md\n",
            encoding="utf-8",
        )

        before = self.run_python([str(GENERATOR), "--root", str(root), "--package", "all", "--check", "--json"])
        self.assertNotEqual(before.returncode, 0, before.stdout + before.stderr)
        write = self.run_python([str(GENERATOR), "--root", str(root), "--package", "all", "--json"])
        self.assertEqual(write.returncode, 0, write.stdout + write.stderr)

        for rel in stale_paths:
            self.assertFalse((root / rel).exists(), str(rel))
        registry_text = registry.read_text(encoding="utf-8")
        self.assertNotIn("agent-tool-policy", registry_text)
        self.assertNotIn("company-thesis", registry_text)
        self.assertNotIn("support-policy", registry_text)

    def test_checker_fails_on_stale_legacy_file_or_registry_entry(self) -> None:
        root = self.make_root()
        stale = root / CODEX_AGENT_TOOL_POLICY
        stale.write_text("stale legacy generated document\n", encoding="utf-8")
        registry = root / "docs_bilingual" / "docs_registry.yaml"
        registry.write_text(
            registry.read_text(encoding="utf-8")
            + "\n  - doc_id: one_person_company_company_thesis\n"
            + "    doc_class: operations_package\n"
            + "    status: active\n"
            + "    canonical_path: docs_bilingual/operations_packages/one_person_company/company-thesis.md\n"
            + "    zh_cn_path: docs_bilingual/operations_packages/one_person_company/company-thesis.zh-CN.md\n",
            encoding="utf-8",
        )

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        errors = checked["payload"]["errors"]
        self.assertTrue(any("Stale legacy generated operations-package file remains" in error for error in errors))
        self.assertTrue(any("stale legacy generated doc_id" in error for error in errors))
        self.assertTrue(any("stale legacy generated canonical_path" in error for error in errors))

    def test_checker_fails_when_generated_content_mentions_metrics_yaml(self) -> None:
        root = self.make_root()
        target = root / CODEX_DOC
        target.write_text(target.read_text(encoding="utf-8") + "\nsource list item `metrics.yaml`\n", encoding="utf-8")

        checked = self.run_checker(root)

        self.assertNotEqual(checked["returncode"], 0)
        self.assertTrue(any("metrics.yaml" in error for error in checked["payload"]["errors"]))

    def test_new_test_is_registered_in_ci_manifest(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertIn("operations_package_docs.test.py", manifest["python_unittest"])


if __name__ == "__main__":
    unittest.main()
