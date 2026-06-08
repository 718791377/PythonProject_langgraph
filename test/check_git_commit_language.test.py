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

    def run_git(self, root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        self.run_git(root, "init", "-b", "main")
        self.run_git(root, "config", "user.email", "test@example.invalid")
        self.run_git(root, "config", "user.name", "Test User")
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "初始提交")
        return root

    def run_check_json(self, root: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), *args, "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", **(env or {})},
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
        self.run_git(root, "checkout", "-b", "feature")
        (root / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "feat: add feature")
        result = self.run_check_json(root, "--base-ref", "main", "--head-ref", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["commits"], 1)

    def test_ci_before_sha_fallback_when_main_ref_missing(self) -> None:
        root = self.make_root("commit-lang-ci-before")
        base_sha = self.run_git(root, "rev-parse", "HEAD").stdout.strip()
        self.run_git(root, "checkout", "-b", "feature")
        self.run_git(root, "branch", "-D", "main")
        (root / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "测试：新增功能")

        result = self.run_check_json(root, "--base-ref", "main", "--head-ref", "HEAD", env={"CI_COMMIT_BEFORE_SHA": base_sha})

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["commits"], 1)

    def test_accepts_gitlab_generated_merge_commit_in_ci_range(self) -> None:
        root = self.make_root("commit-lang-gitlab-merge")
        base_sha = self.run_git(root, "rev-parse", "HEAD").stdout.strip()
        self.run_git(root, "checkout", "-b", "feature")
        (root / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "淇 GitLab main pipeline")
        self.run_git(root, "checkout", "main")
        self.run_git(
            root,
            "merge",
            "--no-ff",
            "feature",
            "-m",
            "Merge branch 'publish/local-main-20260602-638fc84' into 'main'",
        )
        merge_sha = self.run_git(root, "rev-parse", "HEAD").stdout.strip()
        self.run_git(root, "checkout", "--detach", merge_sha)
        self.run_git(root, "branch", "-D", "main")

        result = self.run_check_json(
            root,
            "--base-ref",
            "main",
            "--head-ref",
            "HEAD",
            env={"CI_COMMIT_BEFORE_SHA": base_sha},
        )

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["commits"], 2)

    def test_accepts_question_mark_corrupted_gitlab_merge_commit_in_ci_range(self) -> None:
        root = self.make_root("commit-lang-gitlab-merge-mojibake")
        base_sha = self.run_git(root, "rev-parse", "HEAD").stdout.strip()
        self.run_git(root, "checkout", "-b", "feature")
        (root / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "修复GitLab main pipeline")
        self.run_git(root, "checkout", "main")
        self.run_git(root, "merge", "--no-ff", "feature", "-m", "??R5???????")
        merge_sha = self.run_git(root, "rev-parse", "HEAD").stdout.strip()
        self.run_git(root, "checkout", "--detach", merge_sha)
        self.run_git(root, "branch", "-D", "main")

        result = self.run_check_json(
            root,
            "--base-ref",
            "main",
            "--head-ref",
            "HEAD",
            env={"CI_COMMIT_BEFORE_SHA": base_sha},
        )

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        merge_record = next(item for item in payload["commits"] if item.get("is_merge_commit"))
        self.assertEqual(merge_record.get("allowed_reason"), "gitlab_generated_merge_commit_subject_encoding_loss")

    def test_rejects_ascii_only_merge_commit_without_encoding_loss_pattern(self) -> None:
        root = self.make_root("commit-lang-plain-merge")
        base_sha = self.run_git(root, "rev-parse", "HEAD").stdout.strip()
        self.run_git(root, "checkout", "-b", "feature")
        (root / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "修复GitLab main pipeline")
        self.run_git(root, "checkout", "main")
        self.run_git(root, "merge", "--no-ff", "feature", "-m", "plain ascii merge")
        merge_sha = self.run_git(root, "rev-parse", "HEAD").stdout.strip()
        self.run_git(root, "checkout", "--detach", merge_sha)
        self.run_git(root, "branch", "-D", "main")

        result = self.run_check_json(
            root,
            "--base-ref",
            "main",
            "--head-ref",
            "HEAD",
            env={"CI_COMMIT_BEFORE_SHA": base_sha},
        )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("plain ascii merge" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
