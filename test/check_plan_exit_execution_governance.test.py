import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_plan_exit_execution_governance.py"
GIT_TEXT_KWARGS = {"text": True, "encoding": "utf-8", "errors": "replace"}


class PlanExitExecutionGovernanceCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "初始化测试仓库"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        return root

    def commit_file(self, root: Path, relative: str, content: str, message: str) -> str:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", relative], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS).stdout.strip()

    def rev_parse(self, root: Path, ref: str = "HEAD") -> str:
        return subprocess.run(["git", "rev-parse", ref], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS).stdout.strip()

    def commit_plan_package(self, root: Path, *, doc_id: str = "example_plan", status: str = "active") -> str:
        canonical = f"docs_bilingual/implementation_plans/{doc_id}.md"
        zh_cn = f"docs_bilingual/implementation_plans/{doc_id}.zh-CN.md"
        (root / "docs_bilingual/implementation_plans").mkdir(parents=True, exist_ok=True)
        (root / canonical).write_text(
            "---\n"
            f"doc_id: {doc_id}\n"
            "lang: en\n"
            f"status: {status}\n"
            "doc_class: implementation_plan\n"
            f"zh_cn_path: {zh_cn}\n"
            "---\n"
            "# Example Plan\n",
            encoding="utf-8",
        )
        (root / zh_cn).write_text(
            "---\n"
            f"doc_id: {doc_id}\n"
            "lang: zh-CN\n"
            f"status: {status}\n"
            "doc_class: implementation_plan\n"
            f"translation_of: {canonical}\n"
            "---\n"
            "# 示例计划\n",
            encoding="utf-8",
        )
        (root / "docs_bilingual/docs_registry.yaml").write_text(
            "version: 1\n"
            "documents:\n"
            f"  - doc_id: {doc_id}\n"
            "    doc_class: implementation_plan\n"
            f"    status: {status}\n"
            f"    canonical_path: {canonical}\n"
            f"    zh_cn_path: {zh_cn}\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "docs_bilingual"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "新增示例实施计划"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        return self.rev_parse(root)

    def run_check(self, root: Path, base: str = "main", head: str = "HEAD") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--base-ref", base, "--head-ref", head, "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def write_receipt(
        self,
        root: Path,
        commit: str,
        *,
        confirmed: bool = True,
        merged: bool = True,
        include_plan: bool = True,
        plan: str = "docs_bilingual/implementation_plans/example_plan.md",
    ) -> None:
        receipt = root / ".omx/worktree-task-receipt.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "requires_user_confirmation_before_implementation": True,
            "implementation_confirmed_by_user": confirmed,
            "implementation_confirmation_recorded_at": "2026-05-28T08:00:00+08:00" if confirmed else None,
            "governance_package_commit": commit,
            "governance_package_merged_to_local_main": merged,
        }
        if include_plan:
            payload["implementation_plan"] = plan
        receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_completed_claim(
        self,
        root: Path,
        commit: str,
        *,
        confirmed: bool = True,
        merged: bool = True,
        include_plan: bool = True,
        plan: str = "docs_bilingual/implementation_plans/example_plan.md",
    ) -> None:
        claim = root / ".omx/session-claims/completed/completed-claim.json"
        claim.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "requires_user_confirmation_before_implementation": True,
            "implementation_confirmed_by_user": confirmed,
            "implementation_confirmation_recorded_at": "2026-05-28T08:00:00+08:00" if confirmed else None,
            "governance_package_commit": commit,
            "governance_package_merged_to_local_main": merged,
        }
        if include_plan:
            payload["implementation_plan"] = plan
        claim.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_remote_ci_forward_fix_receipt(self, root: Path, *, branch: str, paths: list[str]) -> None:
        receipt = root / ".omx/worktree-task-receipt.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(
            json.dumps(
                {
                    "task_type": "remote-ci-forward-fix",
                    "branch": branch,
                    "requires_code_implementation": True,
                    "requires_local_main_merge": True,
                    "paths": paths,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_fails_when_non_doc_range_only_has_same_range_docs_bilingual_governance_commit(self) -> None:
        root = self.make_repo("plan-exit-same-range")
        base = self.rev_parse(root)
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Governance\n", "新增治理说明")
        self.commit_file(root, "tools/example.py", "print('ok')\n", "添加实现代码")

        result = self.run_check(root, base, "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["requires_governance_package"])
        self.assertTrue(payload["legacy_same_range_governance"])
        self.assertTrue(any("same-range chat or docs-only governance is not sufficient" in error for error in payload["errors"]))
        self.assertEqual(payload["counts"]["non_doc_paths"], 1)

    def test_fails_when_non_doc_range_starts_with_code_commit(self) -> None:
        root = self.make_repo("plan-exit-fail")
        base = self.rev_parse(root)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "先提交代码")
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Late\n", "后补治理文档")

        result = self.run_check(root, base, "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("confirmed Stage A" in error or "same-range chat" in error for error in payload["errors"]))

    def test_docs_only_range_does_not_require_governance_package(self) -> None:
        root = self.make_repo("plan-exit-docs-only")
        base = self.rev_parse(root)
        self.commit_file(root, "docs_bilingual/memory/sample.md", "# Docs only\n", "更新文档")

        result = self.run_check(root, base, "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["requires_governance_package"])

    def test_passes_remote_ci_forward_fix_receipt_for_matching_branch_and_paths(self) -> None:
        root = self.make_repo("plan-exit-remote-ci-forward-fix")
        subprocess.run(["git", "checkout", "-b", "fix/remote-ci-forward"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/checker.py", "print('forward fix')\n", "修复远端 CI 门禁")
        self.write_remote_ci_forward_fix_receipt(root, branch="fix/remote-ci-forward", paths=["tools/checker.py"])

        result = self.run_check(root, "main", "fix/remote-ci-forward")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["requires_governance_package"])
        self.assertEqual(payload["counts"]["valid_remote_ci_forward_fix_records"], 1)
        self.assertTrue(any("remote CI forward-fix" in message for message in payload["info"]))

    def test_fails_remote_ci_forward_fix_receipt_when_paths_do_not_cover_range(self) -> None:
        root = self.make_repo("plan-exit-remote-ci-forward-fix-mismatch")
        subprocess.run(["git", "checkout", "-b", "fix/remote-ci-forward"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/checker.py", "print('forward fix')\n", "修复远端 CI 门禁")
        self.write_remote_ci_forward_fix_receipt(root, branch="fix/remote-ci-forward", paths=["tools/other.py"])

        result = self.run_check(root, "main", "fix/remote-ci-forward")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["valid_remote_ci_forward_fix_records"], 0)
        self.assertTrue(
            any(
                "remote CI forward-fix paths must cover every non-document changed path" in detail
                for record in payload["remote_ci_forward_fix_records"]
                for detail in record["errors"]
            )
        )

    def test_passes_with_confirmed_stage_a_receipt_when_code_range_has_no_docs_commit(self) -> None:
        root = self.make_repo("plan-exit-staged-pass")
        governance_commit = self.commit_plan_package(root)
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('ok')\n", "添加受控代码")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["legacy_same_range_governance"])
        self.assertEqual(payload["counts"]["valid_staged_confirmations"], 1)
        self.assertEqual(payload["staged_confirmations"][0]["implementation_plan"], "docs_bilingual/implementation_plans/example_plan.md")

    def test_passes_with_confirmed_final_stage_a_receipt_when_plan_is_frozen(self) -> None:
        root = self.make_repo("plan-exit-staged-final-pass")
        governance_commit = self.commit_plan_package(root, doc_id="frozen_plan", status="final")
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('ok')\n", "add frozen-plan authorized code")
        self.write_receipt(
            root,
            governance_commit,
            confirmed=True,
            merged=True,
            plan="docs_bilingual/implementation_plans/frozen_plan.md",
        )

        result = self.run_check(root, "main", "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["valid_staged_confirmations"], 1)
        self.assertEqual(
            payload["staged_confirmations"][0]["implementation_plan"],
            "docs_bilingual/implementation_plans/frozen_plan.md",
        )

    def test_passes_with_confirmed_completed_claim_for_publication_range(self) -> None:
        root = self.make_repo("plan-exit-completed-claim-pass")
        governance_commit = self.commit_plan_package(root)
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('ok')\n", "添加受控代码")
        self.write_completed_claim(root, governance_commit, confirmed=True, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["valid_staged_confirmations"], 1)
        self.assertEqual(payload["staged_confirmations"][0]["source_kind"], "completed_claim")
        self.assertEqual(
            payload["staged_confirmations"][0]["path"],
            ".omx/session-claims/completed/completed-claim.json",
        )

    def test_fails_when_stage_a_receipt_is_not_confirmed(self) -> None:
        root = self.make_repo("plan-exit-staged-unconfirmed")
        governance_commit = self.commit_plan_package(root)
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "添加未确认代码")
        self.write_receipt(root, governance_commit, confirmed=False, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("confirmed Stage A" in error for error in payload["errors"]))
        self.assertEqual(payload["counts"]["valid_staged_confirmations"], 0)

    def test_fails_when_governance_commit_is_not_merged_to_main(self) -> None:
        root = self.make_repo("plan-exit-staged-not-main")
        subprocess.run(["git", "checkout", "-b", "governance"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        governance_commit = self.commit_plan_package(root)
        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "添加未合入代码")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any("must already be merged to local" in detail for record in payload["staged_confirmations"] for detail in record["errors"])
        )

    def test_fails_when_governance_commit_contains_code(self) -> None:
        root = self.make_repo("plan-exit-staged-mixed")
        (root / "docs_bilingual/implementation_plans").mkdir(parents=True, exist_ok=True)
        (root / "docs_bilingual/implementation_plans/example_plan.md").write_text(
            "---\ndoc_id: example_plan\nstatus: active\ndoc_class: implementation_plan\n---\n# Plan\n",
            encoding="utf-8",
        )
        (root / "docs_bilingual/implementation_plans/example_plan.zh-CN.md").write_text("# 示例计划\n", encoding="utf-8")
        (root / "docs_bilingual/docs_registry.yaml").write_text(
            "version: 1\n"
            "documents:\n"
            "  - doc_id: example_plan\n"
            "    doc_class: implementation_plan\n"
            "    status: active\n"
            "    canonical_path: docs_bilingual/implementation_plans/example_plan.md\n"
            "    zh_cn_path: docs_bilingual/implementation_plans/example_plan.zh-CN.md\n",
            encoding="utf-8",
        )
        (root / "tools").mkdir(parents=True, exist_ok=True)
        (root / "tools/governance.py").write_text("print('mixed')\n", encoding="utf-8")
        subprocess.run(["git", "add", "docs_bilingual", "tools/governance.py"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "混合治理提交"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        governance_commit = self.rev_parse(root)
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "添加混合后代码")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("must be docs-only" in detail for record in payload["staged_confirmations"] for detail in record["errors"]))

    def test_fails_when_confirmed_receipt_omits_active_or_final_registered_plan_file(self) -> None:
        root = self.make_repo("plan-exit-missing-plan")
        governance_commit = self.commit_file(root, "docs_bilingual/memory/sample.md", "# Governance\n", "新增治理文档")
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "添加缺少计划代码")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True, include_plan=False)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any("implementation_plan must name" in detail for record in payload["staged_confirmations"] for detail in record["errors"])
        )

    def test_fails_when_confirmed_plan_file_is_not_registered_active_or_final(self) -> None:
        root = self.make_repo("plan-exit-unregistered-plan")
        plan = "docs_bilingual/implementation_plans/example_plan.md"
        governance_commit = self.commit_file(root, plan, "---\ndoc_id: example_plan\nstatus: active\ndoc_class: implementation_plan\n---\n# Plan\n", "新增未注册计划")
        subprocess.run(["git", "checkout", "-b", "feature/code"], cwd=root, check=True, capture_output=True, **GIT_TEXT_KWARGS)
        self.commit_file(root, "tools/example.py", "print('bad')\n", "添加未注册计划代码")
        self.write_receipt(root, governance_commit, confirmed=True, merged=True, plan=plan)

        result = self.run_check(root, "main", "HEAD")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any("must be registered" in detail for record in payload["staged_confirmations"] for detail in record["errors"])
        )


if __name__ == "__main__":
    unittest.main()
