import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_operator_usage_guide.py"
GUIDE_RELATIVES = [
    "docs_bilingual/guides/pyside6_gui_cross_project_usage.md",
    "docs_bilingual/guides/pyside6_gui_cross_project_usage.zh-CN.md",
]
REGISTRY_RELATIVE = "docs_bilingual/docs_registry.yaml"


class PySide6OperatorUsageGuideTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_contract_files(self, root: Path) -> None:
        for relative in GUIDE_RELATIVES + [REGISTRY_RELATIVE]:
            source = REPO_ROOT / relative
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_repository_guide_passes(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "pyside6_operator_usage_guide")
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_missing_registry_entry_fails(self) -> None:
        root = self.make_root("pyside6-operator-guide-missing-registry")
        self.copy_contract_files(root)
        registry = root / REGISTRY_RELATIVE
        registry.write_text(
            registry.read_text(encoding="utf-8").replace("doc_id: pyside6_gui_cross_project_usage", "doc_id: removed_pyside6_gui_cross_project_usage"),
            encoding="utf-8",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("docs_registry.yaml" in error for error in payload["errors"]))

    def test_missing_soft_load_boundary_fails(self) -> None:
        root = self.make_root("pyside6-operator-guide-missing-soft-load")
        self.copy_contract_files(root)
        guide = root / GUIDE_RELATIVES[0]
        guide.write_text(guide.read_text(encoding="utf-8").replace("soft-load", "task-scoped-load"), encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("soft-load" in error for error in payload["errors"]))

    def test_forbidden_global_install_guidance_fails(self) -> None:
        root = self.make_root("pyside6-operator-guide-global-install")
        self.copy_contract_files(root)
        guide = root / GUIDE_RELATIVES[0]
        with guide.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n```powershell\npip install --user PySide6\n```\n")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("global PySide6" in error or "user/global" in error for error in payload["errors"]))

    def test_chinese_boundary_phrases_are_required(self) -> None:
        root = self.make_root("pyside6-operator-guide-chinese-boundary")
        self.copy_contract_files(root)
        guide = root / GUIDE_RELATIVES[1]
        guide.write_text(guide.read_text(encoding="utf-8").replace("不会编辑 `config.toml`", "不会改动配置文件"), encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("no config mutation during soft-load" in error for error in payload["errors"]))



if __name__ == "__main__":
    unittest.main()
