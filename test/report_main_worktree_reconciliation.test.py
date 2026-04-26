import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "report_main_worktree_reconciliation.py"


class MainWorktreeReconciliationReportTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"main-reconcile-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self, root: Path, message: str) -> None:
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True, text=True)

    def test_classifies_backup_and_target_changes(self) -> None:
        root = self.make_repo()
        self.write_file(root, "same.txt", "base\n")
        self.write_file(root, "local.txt", "base\n")
        self.write_file(root, "target.txt", "base\n")
        self.write_file(root, "both-diff.txt", "base\n")
        self.write_file(root, "both-same.txt", "base\n")
        self.commit(root, "base")
        base_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

        subprocess.run(["git", "checkout", "-b", "backup"], cwd=root, check=True, capture_output=True, text=True)
        self.write_file(root, "local.txt", "local\n")
        self.write_file(root, "both-diff.txt", "local\n")
        self.write_file(root, "both-same.txt", "same\n")
        self.commit(root, "backup")

        subprocess.run(["git", "checkout", "-b", "target", base_commit], cwd=root, check=True, capture_output=True, text=True)
        self.write_file(root, "target.txt", "target\n")
        self.write_file(root, "both-diff.txt", "target\n")
        self.write_file(root, "both-same.txt", "same\n")
        self.commit(root, "target")

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--root",
                str(root),
                "--backup-ref",
                "backup",
                "--target-ref",
                "target",
                "--json",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        by_category = payload["summary"]["by_category"]
        self.assertEqual(by_category["local_only"], 1)
        self.assertEqual(by_category["target_only"], 1)
        self.assertEqual(by_category["both_changed_different"], 1)
        self.assertEqual(by_category["both_changed_same_content"], 1)

        categories = {item["path"]: item["category"] for item in payload["paths"]}
        self.assertEqual(categories["local.txt"], "local_only")
        self.assertEqual(categories["target.txt"], "target_only")
        self.assertEqual(categories["both-diff.txt"], "both_changed_different")
        self.assertEqual(categories["both-same.txt"], "both_changed_same_content")


if __name__ == "__main__":
    unittest.main()
