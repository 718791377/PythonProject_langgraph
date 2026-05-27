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
        subprocess.run(["git", "commit", "-m", "初始化：建立测试仓库"], cwd=root, check=True, capture_output=True, text=True)
        return root

    def commit_file(self, root: Path, relative: str, content: str, message: str) -> str:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", relative], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True, text=True)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()

    def rev_parse(self, root: Path, ref: str = "HEAD") -> str:
        return subprocess.run(["git", "rev-parse", ref], cwd=root, check=True, capture_output=True, text=True).stdout.strip()

    def run_check(self, root: Path, base: str = "main", head: str = "HEAD") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--base-ref", base, "--head-ref", head, "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def write_receipt(self, root: Path, commit: str, *, confirmed: bool = True, merged: bool = True) -> None:
        receipt = root / ".omx/worktree-task-receipt.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(
            json.dumps(
                {
                    "requires_user_confirmation_before_implementation": True,
                    "implementation_confirmed_by_user": confirmed,
                    "implementation_confirmation_recorded_at": "2026-05-28T08:00:00+08:00" if confirmed else None,
                    "governance_package_commit": commit,
                    "governance_package_merged_to_local_main": merged,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_passes_when_non_doc_range_starts_with_docs_bilingual_governance_commit(self) -> None:
        root = self.make_repo("plan-exit-pass")
        base = self.rev_parse(root)
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Governance\n", "治理：先提交本地治理包")
        self.commit_file(root, "tools/example.py", "print('ok')\n", "实现：更新脚本")

        result = self.run_check(root, base, "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["requires_governance_package"])
        self.assertTrue(payload["legacy_same_range_governance"])
        self.assertEqual(payload["counts"]["non_doc_paths"], 1)

    def test_fails_when_non_doc_range_starts_with_code_commit(self) -> None:
        root = self.make_repo("plan-exit-fail")
        base = self.rev_parse(root)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "实现：先改代码")
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Late\n", "治理：后补文档")

        result = self.run_check(root, base, "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("same-range docs_bilingual-first" in error for error in payload["errors"]))

    def test_docs_only_range_does_not_require_governance_package(self) -> None:
        root = self.make_repo("plan-exit-docs-only")
        base = self.rev_parse(root)
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Docs only\n", "文档：仅更新说明")

        result = self.run_check(root, base, "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["requires_governance_package"])

    def test_passes_with_confirmed_stage_a_receipt_when_code_range_has_no_docs_commit(self) -> None:
        root = self.make_repo("plan-exit-staged-pass")
        governance_commit = self.commit_file(root, "docs_bilingual/memory/sample.md", "# Governance\n", "治理：合入阶段A治理包")
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, text=True)
        self.commit_file(root, "tools/example.py", "print('ok')\n", "实现：执行阶段B脚本")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["legacy_same_range_governance"])
        self.assertEqual(payload["counts"]["valid_staged_confirmations"], 1)

    def test_fails_when_stage_a_receipt_is_not_confirmed(self) -> None:
        root = self.make_repo("plan-exit-staged-unconfirmed")
        governance_commit = self.commit_file(root, "docs_bilingual/memory/sample.md", "# Governance\n", "治理：合入阶段A治理包")
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, text=True)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "实现：缺少确认")
        self.write_receipt(root, governance_commit, confirmed=False, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("confirmed Stage A" in error for error in payload["errors"]))
        self.assertEqual(payload["counts"]["valid_staged_confirmations"], 0)

    def test_fails_when_governance_commit_is_not_merged_to_main(self) -> None:
        root = self.make_repo("plan-exit-staged-not-main")
        subprocess.run(["git", "checkout", "-b", "governance"], cwd=root, check=True, capture_output=True, text=True)
        governance_commit = self.commit_file(root, "docs_bilingual/memory/sample.md", "# Governance\n", "治理：未合入本地main")
        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, text=True)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "实现：治理包未合入")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any("must already be merged to local" in detail for record in payload["staged_confirmations"] for detail in record["errors"])
        )

    def test_fails_when_governance_commit_contains_code(self) -> None:
        root = self.make_repo("plan-exit-staged-mixed")
        (root / "docs_bilingual/memory").mkdir(parents=True, exist_ok=True)
        (root / "docs_bilingual/memory/sample.md").write_text("# Governance\n", encoding="utf-8")
        (root / "tools").mkdir(parents=True, exist_ok=True)
        (root / "tools/governance.py").write_text("print('mixed')\n", encoding="utf-8")
        subprocess.run(["git", "add", "docs_bilingual/memory/sample.md", "tools/governance.py"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "治理：错误混入代码"], cwd=root, check=True, capture_output=True, text=True)
        governance_commit = self.rev_parse(root)
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, text=True)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "实现：检查混合治理包")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("must be docs-only" in detail for record in payload["staged_confirmations"] for detail in record["errors"]))


if __name__ == "__main__":
    unittest.main()
