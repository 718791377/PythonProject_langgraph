import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_document_governance_rules.py"


class DocumentGovernanceRulesCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: bytes | str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
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

    def test_passes_for_paired_governance_docs_and_registry(self) -> None:
        root = self.make_root("governance-pass")
        self.write_file(
            root,
            "docs_bilingual/governance/sample_policy.md",
            "---\ndoc_id: sample_policy\nlang: en\ndoc_class: governance\nstatus: active\n---\n# Sample Policy\nASCII only.\n",
        )
        self.write_file(
            root,
            "docs_bilingual/governance/sample_policy.zh-CN.md",
            "---\ndoc_id: sample_policy\nlang: zh-CN\ndoc_class: governance\nstatus: active\n---\n# 示例策略\nUTF-8 中文。\n",
        )
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_policy\n"
            "    doc_class: governance\n"
            "    status: active\n"
            "    canonical_path: docs_bilingual/governance/sample_policy.md\n"
            "    zh_cn_path: docs_bilingual/governance/sample_policy.zh-CN.md\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Governance English primaries: 1", result.stdout)
        self.assertIn("Governance Chinese companions: 1", result.stdout)

        json_result = self.run_check_json(root)
        self.assertEqual(json_result.returncode, 0, json_result.stdout + "\n" + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "document_governance_rules")
        self.assertEqual(Path(payload["root"]), root)
        self.assertTrue(payload["generated_at"])
        self.assertIn("Governance English primaries: 1", payload["info"])
        self.assertEqual(payload["counts"]["governance_english_primaries"], 1)

    def test_fails_for_missing_pair_and_non_ascii_primary(self) -> None:
        root = self.make_root("governance-fail")
        self.write_file(
            root,
            "docs_bilingual/governance/sample_policy.md",
            "---\ndoc_id: sample_policy\nlang: en\ndoc_class: governance\nstatus: active\n---\n# Sample Policy\nNon ASCII: 中文\n",
        )
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_policy\n"
            "    doc_class: governance\n"
            "    status: active\n"
            "    canonical_path: docs_bilingual/governance/sample_policy.md\n"
            "    zh_cn_path: docs_bilingual/governance/sample_policy.zh-CN.md\n",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing Chinese governance companion", result.stdout)
        self.assertIn("contains non-ASCII text", result.stdout)

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "document_governance_rules")
        self.assertTrue(any("Missing Chinese governance companion" in error for error in payload["errors"]))
        self.assertGreaterEqual(payload["counts"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
