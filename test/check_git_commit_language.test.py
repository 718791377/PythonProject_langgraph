import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_git_commit_language.py"


class GitCommitLanguageCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "初始提交"], cwd=root, check=True, capture_output=True, text=True)
        return root

    def run_check_json(self, root: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), *args, "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
            env={**os.environ, **(env or {})},
        )

    def test_accepts_chinese_subject_with_ascii_prefix(self) -> None:
        root = self.make_root("commit-lang-pass")
        result = self.run_check_json(root, "--message", "docs: 更新治理规则")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_rejects_ascii_only_subject(self) -> None:
        root = self.make_root("commit-lang-fail")
        result = self.run_check_json(root, "--message", "docs: update governance rules")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("must contain Chinese" in error for error in payload["errors"]))

    def test_checks_commit_range(self) -> None:
        root = self.make_root("commit-lang-range")
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=root, check=True, capture_output=True, text=True)
        (root / "feature.txt").write_text("feature\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "feat: add feature"], cwd=root, check=True, capture_output=True, text=True)
        result = self.run_check_json(root, "--base-ref", "main", "--head-ref", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["commits"], 1)

    def test_ci_before_sha_fallback_when_main_ref_missing(self) -> None:
        root = self.make_root("commit-lang-ci-before")
        base_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "branch", "-D", "main"], cwd=root, check=True, capture_output=True, text=True)
        (root / "feature.txt").write_text("feature\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "测试：新增功能"], cwd=root, check=True, capture_output=True, text=True)

        result = self.run_check_json(root, "--base-ref", "main", "--head-ref", "HEAD", env={"CI_COMMIT_BEFORE_SHA": base_sha})

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["commits"], 1)


if __name__ == "__main__":
    unittest.main()
