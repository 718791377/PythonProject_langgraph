import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_openspec_code_archive_evidence.py"


class OpenSpecCodeArchiveEvidenceTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True)
        self.write(
            root,
            "README.md",
            "# Fixture\n",
        )
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, capture_output=True, text=True)
        return root

    def write(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def make_active_change(self, root: Path, name: str, yaml_extra: str, task_text: str) -> None:
        base = root / "openspec" / "changes" / name
        self.write(
            root,
            f"openspec/changes/{name}/.openspec.yaml",
            "schema: spec-driven\ncreated: 2026-05-03\n" + yaml_extra,
        )
        self.write(
            root,
            f"openspec/changes/{name}/tasks.md",
            f"## Tasks\n\n- [x] {task_text}\n",
        )
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", f"add {name}"], cwd=root, check=True, capture_output=True, text=True)

    def archive_change(self, root: Path, name: str) -> None:
        src = root / "openspec" / "changes" / name
        dst = root / "openspec" / "changes" / "archive" / f"2026-05-03-{name}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_code_class_archive_without_code_evidence_fails(self) -> None:
        root = self.make_repo("archive-code-no-evidence")
        self.make_active_change(
            root,
            "add-runtime-helper",
            "x_change_class: code\n",
            "Implement runtime helper script behavior.",
        )
        self.archive_change(root, "add-runtime-helper")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["counts"]["archive_dirs"], 1)
        self.assertEqual(payload["counts"]["code_required"], 1)
        self.assertIn("no code/test evidence", payload["errors"][0])

    def test_code_class_archive_with_code_evidence_passes(self) -> None:
        root = self.make_repo("archive-code-with-evidence")
        self.make_active_change(
            root,
            "add-runtime-helper",
            "x_change_class: code\nx_code_evidence_paths:\n  - tools/runtime_helper.py\n",
            "Implement runtime helper script behavior.",
        )
        self.write(root, "tools/runtime_helper.py", "def main():\n    return 0\n")
        self.archive_change(root, "add-runtime-helper")

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["archive_dirs"], 1)
        self.assertEqual(payload["counts"]["code_required"], 1)
        self.assertIn("tools/runtime_helper.py", payload["code_evidence_paths"])

    def test_code_class_archive_with_declared_existing_code_evidence_passes(self) -> None:
        root = self.make_repo("archive-code-declared-existing-evidence")
        self.make_active_change(
            root,
            "add-runtime-helper",
            "x_change_class: code\nx_code_evidence_paths:\n  - tools/runtime_helper.py\n",
            "Implement runtime helper script behavior.",
        )
        self.write(root, "tools/runtime_helper.py", "def main():\n    return 0\n")
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "implement runtime helper"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "switch", "-c", "archive-add-runtime-helper"], cwd=root, check=True, capture_output=True, text=True)
        self.archive_change(root, "add-runtime-helper")

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["archive_dirs"], 1)
        self.assertEqual(payload["counts"]["code_required"], 1)
        self.assertEqual(payload["counts"]["changed_code_evidence_paths"], 0)
        self.assertIn("tools/runtime_helper.py", payload["declared_existing_code_evidence_paths"])
        self.assertIn("tools/runtime_helper.py", payload["archives"][0]["existing_declared_code_evidence_paths"])

    def test_code_class_archive_with_missing_declared_code_evidence_fails(self) -> None:
        root = self.make_repo("archive-code-missing-declared-evidence")
        self.make_active_change(
            root,
            "add-runtime-helper",
            "x_change_class: code\nx_code_evidence_paths:\n  - tools/runtime_helper.py\n",
            "Implement runtime helper script behavior.",
        )
        subprocess.run(["git", "switch", "-c", "archive-add-runtime-helper"], cwd=root, check=True, capture_output=True, text=True)
        self.archive_change(root, "add-runtime-helper")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["counts"]["archive_dirs"], 1)
        self.assertEqual(payload["counts"]["code_required"], 1)
        self.assertIn("do not exist", payload["errors"][0])

    def test_docs_class_archive_without_code_evidence_passes(self) -> None:
        root = self.make_repo("archive-docs-no-evidence")
        self.make_active_change(
            root,
            "document-status",
            "x_change_class: docs\n",
            "Document status-only OpenSpec workflow.",
        )
        self.archive_change(root, "document-status")

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["archive_dirs"], 1)
        self.assertEqual(payload["counts"]["code_required"], 0)


if __name__ == "__main__":
    unittest.main()
