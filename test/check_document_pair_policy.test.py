import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_document_pair_policy.py"


def from_codepoints(*codepoints: int) -> str:
    return "".join(chr(codepoint) for codepoint in codepoints)


class DocumentPairPolicyCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_check_json(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_for_changed_english_and_chinese_pair(self) -> None:
        root = self.make_root("doc-pair-pass")
        self.write_file(root, "docs/README.md", "# Readme\nASCII only.\n")
        self.write_file(root, "docs/README.zh-CN.md", "# 说明\n中文。\n")

        result = self.run_check_json(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["changed_target_markdown"], 2)

    def test_fails_for_missing_companion_and_non_ascii_primary(self) -> None:
        root = self.make_root("doc-pair-fail")
        self.write_file(root, "docs_bilingual/governance/sample.md", "# Sample\n中文 in primary.\n")

        result = self.run_check_json(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("missing bilingual companion" in error for error in payload["errors"]))
        self.assertTrue(any("contains non-ASCII" in error for error in payload["errors"]))

    def test_fails_when_startup_summary_primary_contains_literal_canary(self) -> None:
        root = self.make_root("doc-pair-startup-canary")
        start_marker = from_codepoints(25351, 25381, 23448)
        end_marker = from_codepoints(21941) + "~"
        self.write_file(
            root,
            "docs_bilingual/project_startup_summary.md",
            f"# Startup\nCanonical canary starts `{start_marker}` and ends `{end_marker}`.\n",
        )
        self.write_file(
            root,
            "docs_bilingual/project_startup_summary.zh-CN.md",
            f"# Startup ZH\nCanonical canary starts `{start_marker}` and ends `{end_marker}`.\n",
        )

        result = self.run_check_json(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("contains non-ASCII" in error for error in payload["errors"]))

    def test_fails_when_modified_file_omits_companion_update(self) -> None:
        root = self.make_root("doc-pair-companion")
        self.write_file(root, "openspec/specs/sample/spec.md", "# Sample\nASCII only.\n")
        self.write_file(root, "openspec/specs/sample/spec.zh-CN.md", "# 示例\n中文。\n")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=root, check=True, capture_output=True, text=True)
        self.write_file(root, "openspec/specs/sample/spec.md", "# Sample\nASCII changed.\n")

        result = self.run_check_json(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("without changing its bilingual companion" in error for error in payload["errors"]))

    def test_passes_for_deleted_english_and_chinese_pair(self) -> None:
        root = self.make_root("doc-pair-delete")
        self.write_file(root, "openspec/changes/sample/tasks.md", "# Tasks\n- [x] Done.\n")
        self.write_file(root, "openspec/changes/sample/tasks.zh-CN.md", "# 任务\n- [x] 完成。\n")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=root, check=True, capture_output=True, text=True)
        (root / "openspec/changes/sample/tasks.md").unlink()
        (root / "openspec/changes/sample/tasks.zh-CN.md").unlink()

        result = self.run_check_json(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["changed_target_markdown"], 2)

    def test_passes_for_staged_archive_rename_pair(self) -> None:
        root = self.make_root("doc-pair-archive-rename")
        self.write_file(root, "openspec/changes/sample/tasks.md", "# Tasks\n- [x] Done.\n")
        self.write_file(root, "openspec/changes/sample/tasks.zh-CN.md", "# 任务\n- [x] 完成。\n")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=root, check=True, capture_output=True, text=True)

        archive_parent = root / "openspec" / "changes" / "archive"
        archive_parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "mv", "openspec/changes/sample", "openspec/changes/archive/2026-06-08-sample"],
            cwd=root,
            check=True,
        )

        result = self.run_check_json(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn("openspec/changes/sample/tasks.md", payload["checked_files"])
        self.assertIn("openspec/changes/sample/tasks.zh-CN.md", payload["checked_files"])
        self.assertIn("openspec/changes/archive/2026-06-08-sample/tasks.md", payload["checked_files"])
        self.assertIn("openspec/changes/archive/2026-06-08-sample/tasks.zh-CN.md", payload["checked_files"])

    def test_fails_when_deleted_file_omits_companion_delete(self) -> None:
        root = self.make_root("doc-pair-delete-fail")
        self.write_file(root, "openspec/changes/sample/design.md", "# Design\nASCII only.\n")
        self.write_file(root, "openspec/changes/sample/design.zh-CN.md", "# 设计\n中文。\n")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=root, check=True, capture_output=True, text=True)
        (root / "openspec/changes/sample/design.md").unlink()

        result = self.run_check_json(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("was deleted without deleting its bilingual companion" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
