import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_user_level_mcp_skills_browser_cli_baseline.py"


class UserLevelMcpSkillsBrowserCliBaselineCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def write_minimal_repo(self, root: Path, *, omit: str | None = None) -> None:
        plan_dir = root / "docs_bilingual" / "implementation_plans"
        spec_dir = root / "openspec" / "specs" / "codex-user-level-mcp-skills-browser-cli-governance"
        tools_dir = root / "tools" / "ci"
        plan_dir.mkdir(parents=True, exist_ok=True)
        spec_dir.mkdir(parents=True, exist_ok=True)
        tools_dir.mkdir(parents=True, exist_ok=True)
        checklist = "\n".join(f"- [ ] item {i}" for i in range(34))
        rows = "\n".join("| a | b | c | d |" for _ in range(47))
        shared = f"""
status: draft
plan_readiness: execution-ready
implementation_state: baseline_policy_checker_complete
last_reviewed_at: 2026-05-23
skills2cli mcp2cli chrome-devtools-mcp CDP Bridge OpenCLI oh-my-pi CLI-Anything wecom-cli
active on-demand reference-only disabled
port registry codex-port pending_bind registry_revision 39000-39299 40000-40999 --port auto
authorization receipt schema action target scope expiry session operator confirmation
update receipt tool name installed version source URL install path wrapper path state path smoke test command updater command rollback pointer owner lane
secrets, cookies, tokens, raw browser data, message contents, full personal runtime paths, complete plugin description dumps
{rows}
{checklist}
"""
        zh = """
## 0. Current review verdict
## 4. Token and risk priority model
## 13. Readiness gate acceptance criteria
## 14. Sensitive authorization matrix
## 15. Installation and update evidence contract
## 16. OpenSpec implementation split
OpenSpec slice delivery matrix
Fine-grained implementation checklist
Slice completion rule
""" + shared
        en = """
## 0. Current review verdict
## 4. Token and risk priority model
## 13. Readiness gates and acceptance criteria
## 14. Sensitive authorization matrix
## 15. Installation and update evidence contract
## 16. OpenSpec implementation split
OpenSpec slice delivery matrix
Fine-grained implementation checklist
Slice completion rule
""" + shared
        if omit == "operator confirmation":
            zh = zh.replace("operator confirmation", "")
            en = en.replace("operator confirmation", "")
        if omit == "port":
            zh = zh.replace("pending_bind", "")
            en = en.replace("pending_bind", "")
        (plan_dir / "user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md").write_text(zh, encoding="utf-8")
        (plan_dir / "user_level_mcp_skills_browser_cli_governance_plan.md").write_text(en, encoding="utf-8")
        adapter_shared = """
## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local; remote publication remains closed.
Implementation evidence: tools/chrome_devtools_mcp_managed.py, tools/cdp_bridge_governance.py, tools/opencli_governance.py, tools/cli_anything_governance.py, and tools/wecom_cli_governance.py keep the adapter boundary repo-local.
Runtime boundary: no live browser start, GUI write, cookie read, raw browser data access, JavaScript execution, install, or user-level runtime mutation is performed.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Keep read-only tab inventory allowed without sensitive authorization.
- [x] Require authorization receipt for click, type, navigate, JavaScript execution, cookie read, and raw browser data access.
- [x] Require OpenCLI-style adapters to use `--port auto` and sanitized `codex-port` lease evidence.
- [x] Keep CLI-Anything generation-first and block hard-load skills until receipt plus smoke evidence exists.
- [x] Keep `wecom-cli` API/Webhook-first and require global lease, operator confirmation, timeout release, and dry-run evidence for WXWork GUI dispatch.
- [x] Report every adapter lane as `reference-only`, `planned`, `on-demand`, or `active-candidate` before integration.
- [x] Run focused validation for this child lane.
- [x] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
<!-- TASK_BACKLOG_END -->

## Adapter lane status

| Adapter lane | Status | Evidence |
| --- | --- | --- |
| chrome-devtools-mcp | on-demand | wrapper guard only |
| CDP Bridge | on-demand | read-only default, receipt-gated sensitive actions |
| OpenCLI | on-demand | `--port auto` and `codex-port` lease evidence |
| CLI-Anything | reference-only | generation-first, no hard-load skills |
| wecom-cli | on-demand | API/Webhook-first, global lease, operator confirmation, timeout release, dry-run evidence |

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01: user_level_browser_cli_adapter_boundary_plan implementation evidence recorded.
<!-- EVIDENCE_INDEX_END -->
"""
        if omit == "adapter-status":
            adapter_shared = adapter_shared.replace("Status: implemented-local", "Status: active")
        (plan_dir / "user_level_browser_cli_adapter_boundary_plan.zh-CN.md").write_text(adapter_shared, encoding="utf-8")
        (plan_dir / "user_level_browser_cli_adapter_boundary_plan.md").write_text(adapter_shared, encoding="utf-8")
        spec_text = "Token/risk priority authorization receipt update receipt evidence redaction port registry/lease codex-port allocator pending_bind registry_revision 39000-39299 40000-40999 OpenSpec slice fail closed"
        if omit == "spec":
            spec_text = "Token/risk priority only"
        (spec_dir / "spec.md").write_text(spec_text, encoding="utf-8")
        (root / "tools").mkdir(exist_ok=True)
        (root / "tools" / "wecom_cli_governance.py").write_text("# fixture helper\n", encoding="utf-8")
        (root / "tools" / "user_level_receipt_governance.py").write_text("# fixture receipt helper\n", encoding="utf-8")
        (root / "tools" / "safety_rule_script_backing_registry.json").write_text(json.dumps({
            "schema_version": 1,
            "rules": [{
                "id": "user-level-mcp-skills-browser-cli-baseline",
                "status": "implemented",
                "prompt_reminders": ["docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md"],
                "script_controls": ["tools/check_user_level_mcp_skills_browser_cli_baseline.py"],
                "guard_steps": ["check_user_level_mcp_skills_browser_cli_baseline"],
            }],
        }), encoding="utf-8")
        (root / "tools" / "run_openspec_guard.py").write_text("check_user_level_mcp_skills_browser_cli_baseline", encoding="utf-8")
        (tools_dir / "ci_test_manifest.json").write_text(json.dumps({
            "schema_version": 1,
            "python_unittest": [
                "check_user_level_mcp_skills_browser_cli_baseline.test.py",
                "wecom_cli_governance.test.py",
                "user_level_receipt_governance.test.py",
            ],
        }), encoding="utf-8")

    def test_repository_surfaces_pass(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_minimal_valid_surfaces_pass(self) -> None:
        root = self.make_root("baseline-pass")
        self.write_minimal_repo(root)
        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)

    def test_missing_authorization_receipt_field_fails(self) -> None:
        root = self.make_root("baseline-auth-fail")
        self.write_minimal_repo(root, omit="operator confirmation")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("operator confirmation" in error for error in payload["errors"]))

    def test_missing_port_governance_marker_fails(self) -> None:
        root = self.make_root("baseline-port-fail")
        self.write_minimal_repo(root, omit="port")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("port-governance" in error for error in payload["errors"]))

    def test_missing_spec_markers_fail(self) -> None:
        root = self.make_root("baseline-spec-fail")
        self.write_minimal_repo(root, omit="spec")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("spec candidate" in error for error in payload["errors"]))

    def test_adapter_child_plan_must_be_implemented_local(self) -> None:
        root = self.make_root("adapter-child-plan-fail")
        self.write_minimal_repo(root, omit="adapter-status")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("implemented-local" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
