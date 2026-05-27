import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_plan_exit_execution_governance.py"


class PlanExitExecutionGovernanceCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "初始化仓库"], cwd=root, check=True, capture_output=True, text=True)
        return root

    def commit_file(self, root: Path, relative: str, content: str, message: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", relative], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True, text=True)

    def run_check(self, root: Path, base: str = "main", head: str = "HEAD") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--base-ref", base, "--head-ref", head, "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_when_non_doc_range_starts_with_docs_bilingual_governance_commit(self) -> None:
        root = self.make_repo("plan-exit-pass")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Governance\n", "治理：先提交本地治理包")
        self.commit_file(root, "tools/example.py", "print('ok')\n", "实现：更新脚本")

        result = self.run_check(root, base, "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["requires_governance_package"])
        self.assertEqual(payload["counts"]["non_doc_paths"], 1)

    def test_fails_when_non_doc_range_starts_with_code_commit(self) -> None:
        root = self.make_repo("plan-exit-fail")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
        self.commit_file(root, "tools/example.py", "print('bad')\n", "实现：先改代码")
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Late\n", "治理：后补文档")

        result = self.run_check(root, base, "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("first commit" in error for error in payload["errors"]))

    def test_docs_only_range_does_not_require_governance_package(self) -> None:
        root = self.make_repo("plan-exit-docs-only")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Docs only\n", "文档：仅更新说明")

        result = self.run_check(root, base, "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["requires_governance_package"])


if __name__ == "__main__":
    unittest.main()
