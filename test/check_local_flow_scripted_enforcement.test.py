import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_local_flow_scripted_enforcement.py"


class LocalFlowScriptedEnforcementCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_required_surfaces(self, root: Path) -> None:
        (root / "tools/ci").mkdir(parents=True, exist_ok=True)
        for script in [
            "check_local_flow_scripted_enforcement.py",
            "run_openspec_guard.py",
            "check_local_main_retire_lock.py",
        ]:
            (root / "tools" / script).write_text("# check_local_flow_scripted_enforcement\n", encoding="utf-8")
        (root / "tools/local_main_retire_lock.py").write_text(
            "local-main-retire\n"
            "owner_session_id\n"
            "nonce\n"
            "reclaim-stale\n",
            encoding="utf-8",
        )
        (root / "tools/check_local_main_retire_lock.py").write_text(
            "local-main-retire\n"
            "owner_session_id\n"
            "nonce\n"
            "reclaim-stale\n",
            encoding="utf-8",
        )
        (root / "tools/check_plan_exit_execution_governance.py").write_text(
            "requires_user_confirmation_before_implementation\n"
            "implementation_confirmed_by_user\n"
            "governance_package_commit\n"
            "governance_package_merged_to_local_main\n"
            "implementation_plan\n"
            "active registered implementation-plan\n"
            "confirmed Stage A receipt/claim\n",
            encoding="utf-8",
        )
        (root / "tools/complete_local_flow_to_remote_gate.py").write_text(
            "governance-confirmation\n"
            "--implementation-plan\n"
            "--preserve-carrier\n"
            "implementation_confirmed_by_user\n"
            "implementation_plan\n"
            "awaiting_implementation_confirmation\n"
            "Governance-confirmation stage must be docs-only\n"
            "--self-retire\n"
            "--acquire-retire-lock\n"
            "local_main_retire_lock.py\n"
            "self_retire_lock\n"
            "preflight_self_retire_rob_entry\n"
            "REQUIRED_SELF_RETIRE_GATES\n"
            "record_local_main_completion\n"
            "run_integrated_worktree_cleanup\n"
            "cleanup_integrated_worktree.py\n"
            "remote_publication_gate_closed\n",
            encoding="utf-8",
        )
        (root / "tools/install-codex-user-level-team-mode.ps1").write_text(
            "implementation authorization plus passing local gates is sufficient for automatic local `main` integration\n"
            "Automatic local `main` integration is not remote publication approval\n"
            "project safe-cleanup helper\n"
            "explicit preserve flag\n",
            encoding="utf-8",
        )
        (root / "tools/ci/local_mr_review.ps1").write_text("check_plan_exit_execution_governance.py\n", encoding="utf-8")
        (root / "tools/ci/ci_test_manifest.json").write_text(
            json.dumps(
                {
                    "python_unittest": [
                        "check_plan_exit_execution_governance.test.py",
                        "check_local_flow_scripted_enforcement.test.py",
                        "check_local_main_retire_lock.test.py",
                        "check_complete_local_flow_self_retire_preflight.test.py",
                    ]
                }
            ),
            encoding="utf-8",
        )
        (root / "完整提交流程.md").write_text(
            "# 完整本地提交流程\n"
            "默认本地动作不是停在 feature branch 等待\n"
            "合入后默认执行安全清理\n"
            "--preserve-carrier\n"
            "提交前必须检查 Git 状态和 worktree\n"
            "git merge --ff-only <feature-branch>\n"
            "远端发布门\n"
            "tools/check_plan_exit_execution_governance.py\n"
            "tools/complete_local_flow_to_remote_gate.py\n"
            "tools/cleanup_integrated_worktree.py\n"
            "local-main-retire.lock\n"
            "Work-Conserving eligible hotspot lease resource backpressure local-main retire\n",
            encoding="utf-8",
        )
        (root / "docs_bilingual/implementation_plans").mkdir(parents=True, exist_ok=True)
        for plan in [
            "multi_plan_parallel_session_orchestration_plan.md",
            "multi_plan_parallel_session_orchestration_plan.zh-CN.md",
            "complete_local_commit_flow_scheduler_reorder_buffer_plan.md",
            "complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md",
        ]:
            (root / "docs_bilingual/implementation_plans" / plan).write_text(
                "Work-Conserving eligible hotspot lease resource backpressure local-main retire\n",
                encoding="utf-8",
            )
        (root / "docs_bilingual/governance").mkdir(parents=True, exist_ok=True)
        (root / "docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md").write_text(
            "# Policy\n"
            "Post-Plan Local Governance Package\n"
            "complete local commit flow\n"
            "remote publication gate\n"
            "tools/check_plan_exit_execution_governance.py\n"
            "tools/complete_local_flow_to_remote_gate.py\n"
            "tools/local_main_retire_lock.py\n"
            "tools/ci/local_mr_review.ps1\n",
            encoding="utf-8",
        )
        (root / "docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md").write_text(
            "# 策略\n"
            "`/plan` 之后的本地治理包\n"
            "完整本地提交流程\n"
            "远端发布门\n"
            "tools/check_plan_exit_execution_governance.py\n"
            "tools/complete_local_flow_to_remote_gate.py\n"
            "tools/local_main_retire_lock.py\n"
            "tools/ci/local_mr_review.ps1\n",
            encoding="utf-8",
        )

    def run_check(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json", *extra],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_static_surfaces_pass_when_scripts_and_policy_terms_exist(self) -> None:
        root = self.make_root("local-flow-pass")
        self.write_required_surfaces(root)
        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])

    def test_static_surfaces_fail_when_helper_is_missing(self) -> None:
        root = self.make_root("local-flow-missing")
        self.write_required_surfaces(root)
        (root / "tools/complete_local_flow_to_remote_gate.py").unlink()
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("complete_local_flow_to_remote_gate.py" in error for error in payload["errors"]))

    def test_optional_parent_plan_is_not_a_global_local_flow_gate(self) -> None:
        root = self.make_root("local-flow-optional-parent")
        self.write_required_surfaces(root)
        parent = root / "docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md"
        parent.write_text(
            "Work-Conserving eligible hotspot lease resource backpressure local-main retire\n"
            "Default maximum parallel sessions per phase\n",
            encoding="utf-8",
        )
        parent_zh = root / "docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md"
        parent_zh.write_text(
            "Work-Conserving eligible hotspot lease resource backpressure local-main retire\n"
            "\u6700\u591a 3 \u4e2a session\n",
            encoding="utf-8",
        )
        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        joined = "\n".join(payload["info"])
        self.assertIn("not a global local-flow gate", joined)


if __name__ == "__main__":
    unittest.main()
