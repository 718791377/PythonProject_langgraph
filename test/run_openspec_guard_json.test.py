import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "run_openspec_guard.py"
COMET_POLICY_SCRIPT_PATH = REPO_ROOT / "tools" / "check_openspec_comet_superpowers_policy.py"

COMET_EN_POLICY = "docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md"
COMET_ZH_POLICY = "docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md"
COMET_SPEC = (
    "openspec/changes/upgrade-openspec-comet-superpowers/"
    "specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md"
)

GUARD_STEPS = [
    ("verify_official_openspec", "verify_official_openspec.py", "verify"),
    ("check_current_repo_authority_language", "check_current_repo_authority_language.py", "authority"),
    ("check_document_governance_rules", "check_document_governance_rules.py", "governance"),
    ("check_implementation_plan_rules", "check_implementation_plan_rules.py", "implementation_plan"),
    ("check_name_clarity_rules", "check_name_clarity_rules.py", "name_clarity_rules"),
    ("check_context_retention_canary_surface", "check_context_retention_canary_surface.py", "context_retention_canary_surface"),
    ("check_startup_instruction_mojibake", "check_startup_instruction_mojibake.py", "startup_instruction_mojibake"),
    ("check_safety_rule_script_backing", "check_safety_rule_script_backing.py", "safety_rule_script_backing"),
    ("check_precommit_update_archive", "check_precommit_update_archive.py", "precommit_update_archive"),
    ("check_skills_audit_output_retention", "check_skills_audit_output_retention.py", "skills_audit_output_retention"),
    ("check_openspec_code_archive_evidence", "check_openspec_code_archive_evidence.py", "openspec_code_archive_evidence"),
    ("check_openspec_comet_superpowers_policy", "check_openspec_comet_superpowers_policy.py", "openspec_comet_superpowers_policy"),
    ("check_mcp_router_scope_policy", "check_mcp_router_scope_policy.py", "mcp_router_scope_policy"),
    ("check_user_level_mcp_skills_browser_cli_baseline", "check_user_level_mcp_skills_browser_cli_baseline.py", "user_level_mcp_skills_browser_cli_baseline"),
    ("check_local_mirrored_ci_gate", "check_local_mirrored_ci_gate.py", "local_mirrored_ci_gate"),
    ("check_remote_publication_approval_policy", "check_remote_publication_approval_policy.py", "remote_publication_approval_policy"),
    ("check_role_routing_directive_evidence", "check_role_routing_directive_evidence.py", "role_routing_directive_evidence"),
    ("check_delegation_wait_discipline_evidence", "check_delegation_wait_discipline_evidence.py", "delegation_wait_discipline_evidence"),
    ("check_durable_artifact_state_surfaces", "check_durable_artifact_state_surfaces.py", "durable_artifact_state_surfaces"),
    ("check_leader_session_scope_evidence", "check_leader_session_scope_evidence.py", "leader_session_scope_evidence"),
    ("check_capability_switch_chain", "check_capability_switch_chain.py", "capability_switch_chain"),
    ("check_windows_cleanup_output_control", "check_windows_cleanup_output_control.py", "windows_cleanup_output_control"),
    ("check_plugin_modules_skill", "check_plugin_modules_skill.py", "plugin_modules_skill"),
    ("check_pyside6_shared_runtime_contract", "check_pyside6_shared_runtime_contract.py", "pyside6_shared_runtime_contract"),
    ("check_pyside6_gui_template_contract", "check_pyside6_gui_template_contract.py", "pyside6_gui_template_contract"),
    ("check_pyside6_gui_preview_helper_contract", "check_pyside6_gui_preview_helper_contract.py", "pyside6_gui_preview_helper_contract"),
    ("check_pyside6_gui_skill_contract", "check_pyside6_gui_skill_contract.py", "pyside6_gui_skill_contract"),
    ("check_pyside6_project_opt_in_contract", "check_pyside6_project_opt_in_contract.py", "pyside6_project_opt_in_contract"),
    ("check_pyside6_packaging_opt_in_contract", "check_pyside6_packaging_opt_in_contract.py", "pyside6_packaging_opt_in_contract"),
    ("check_pyside6_operator_usage_guide", "check_pyside6_operator_usage_guide.py", "pyside6_operator_usage_guide"),
    ("check_durable_routing_smoke_gate_template", "check_durable_routing_smoke_gate_template.py", "durable_routing_smoke_gate_template"),
    ("check_codex_native_rollback_release_gate_template", "check_codex_native_rollback_release_gate_template.py", "codex_native_rollback_release_gate_template"),
    ("check_worktree_session_hygiene", "check_worktree_session_hygiene.py", "worktree_session_hygiene"),
    ("check_worktree_task_receipt", "check_worktree_task_receipt.py", "worktree_task_receipt"),
    ("check_session_ownership_claims", "check_session_ownership_claims.py", "session_ownership_claims"),
    ("check_orchestration_activation_policy", "check_orchestration_activation_policy.py", "orchestration_activation_policy"),
    ("check_codex_skills_governance", "check_codex_skills_governance.py", "codex_skills_governance"),
    ("check_custom_agent_toml_schema", "check_custom_agent_toml_schema.py", "custom_agent_toml_schema"),
    ("check_agent_skill_profile_surface_boundaries", "check_agent_skill_profile_surface_boundaries.py", "agent_skill_profile_surface_boundaries"),
    ("check_effective_lane_fit_evidence", "check_effective_lane_fit_evidence.py", "effective_lane_fit_evidence"),
    ("check_fanout_write_ownership_evidence", "check_fanout_write_ownership_evidence.py", "fanout_write_ownership_evidence"),
]


class RunOpenSpecGuardJsonTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_guard_json(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--tool", "codex", "--skip-validate", "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=REPO_ROOT,
        )

    def make_json_script(self, ok: bool, payload: dict) -> str:
        payload_json = json.dumps(payload, ensure_ascii=False)
        code = [
            "import json",
            "import sys",
            f"payload = {payload_json!r}",
            "print(payload)",
            f"raise SystemExit({0 if ok else 1})",
        ]
        return "\n".join(code) + "\n"

    def write_guard_scripts(self, root: Path, failures: dict[str, dict] | None = None) -> None:
        failures = failures or {}
        for _step_name, script_name, check_name in GUARD_STEPS:
            failure = failures.get(script_name)
            ok = failure is None
            payload = {"ok": ok, "check_name": check_name}
            if failure:
                payload.update(failure)
            self.write_file(root, f"tools/{script_name}", self.make_json_script(ok, payload))

    def test_guard_json_passes_and_aggregates_steps(self) -> None:
        root = self.make_root("guard-json-pass")
        self.write_guard_scripts(root)

        result = self.run_guard_json(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "run_openspec_guard")
        self.assertEqual(Path(payload["root"]), root)
        self.assertTrue(payload["generated_at"])
        self.assertEqual(payload["tool"], "codex")
        self.assertEqual(len(payload["steps"]), len(GUARD_STEPS))
        self.assertEqual(payload["counts"]["steps_total"], len(GUARD_STEPS))
        self.assertEqual(payload["counts"]["steps_passed"], len(GUARD_STEPS))
        self.assertEqual([step["step"] for step in payload["steps"]], [step_name for step_name, _script, _check in GUARD_STEPS])
        self.assertEqual(payload["steps"][6]["step"], "check_startup_instruction_mojibake")
        self.assertEqual(payload["steps"][8]["step"], "check_precommit_update_archive")
        self.assertEqual(payload["steps"][9]["step"], "check_skills_audit_output_retention")
        self.assertIn("check_openspec_code_archive_evidence", [step["step"] for step in payload["steps"]])
        self.assertIn("check_openspec_comet_superpowers_policy", [step["step"] for step in payload["steps"]])

    def test_guard_json_reports_failed_step(self) -> None:
        root = self.make_root("guard-json-fail")
        self.write_guard_scripts(
            root,
            failures={
                "check_current_repo_authority_language.py": {
                    "errors": ["bad wording"],
                }
            },
        )

        result = self.run_guard_json(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "run_openspec_guard")
        self.assertEqual(payload["failed_step"], "check_current_repo_authority_language")
        self.assertEqual(payload["steps"][1]["data"]["check_name"], "authority")
        self.assertEqual(payload["counts"]["steps_failed"], 1)


class CheckOpenSpecCometSuperpowersPolicyTest(unittest.TestCase):
    maxDiff = None

    def make_root(self) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"comet-policy-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_valid_surface(self, root: Path) -> None:
        self.write_file(
            root,
            COMET_EN_POLICY,
            "\n".join(
                [
                    "Comet-controlled OpenSpec + Superpowers",
                    "OpenSpec is the WHAT layer",
                    "Superpowers is the HOW layer",
                    "Comet is the control layer",
                    "Open -> Design -> Build -> Verify -> Archive",
                    ".openspec.yaml",
                    ".comet.yaml",
                    "comet init",
                    "explicit operator approval",
                    "Skills remain workflow instruction surfaces",
                    "not native subagent evidence",
                ]
            ),
        )
        self.write_file(
            root,
            COMET_ZH_POLICY,
            "\n".join(
                [
                    "Comet 控制",
                    "OpenSpec",
                    "Superpowers",
                    "WHAT",
                    "HOW",
                    "Comet 管 WHEN & NEXT",
                    "Open -> Design -> Build -> Verify -> Archive",
                    ".openspec.yaml",
                    ".comet.yaml",
                    "显式操作员批准",
                    "不是 native subagent 证据",
                ]
            ),
        )
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            """version: 1
documents:
  - doc_id: openspec_comet_superpowers_workflow_policy
    doc_class: governance
    status: active
    canonical_path: docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md
    zh_cn_path: docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md
""",
        )
        self.write_file(
            root,
            COMET_SPEC,
            "\n".join(
                [
                    "Comet-controlled workflow SHALL preserve layer boundaries",
                    "five-phase pipeline",
                    "decoupled state",
                    "guard phase transitions",
                    "archive evidence",
                    "explicit and repository-local",
                    "checker-backed",
                ]
            ),
        )

    def run_comet_policy_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(COMET_POLICY_SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=REPO_ROOT,
        )

    def test_comet_policy_surface_passes(self) -> None:
        root = self.make_root()
        self.write_valid_surface(root)

        result = self.run_comet_policy_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "openspec_comet_superpowers_policy")
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertIn(COMET_EN_POLICY, payload["checked_files"])

    def test_comet_policy_missing_required_term_fails(self) -> None:
        root = self.make_root()
        self.write_valid_surface(root)
        en_path = root / COMET_EN_POLICY
        en_path.write_text(
            en_path.read_text(encoding="utf-8").replace("Comet is the control layer", ""),
            encoding="utf-8",
        )

        result = self.run_comet_policy_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("Comet is the control layer", payload["missing_terms"]["english_policy"])
        self.assertTrue(any("English policy is missing required term" in error for error in payload["errors"]))

    def test_comet_policy_missing_registry_entry_fails(self) -> None:
        root = self.make_root()
        self.write_valid_surface(root)
        self.write_file(root, "docs_bilingual/docs_registry.yaml", "version: 1\ndocuments: []\n")

        result = self.run_comet_policy_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("docs registry is missing" in error for error in payload["errors"]))

    def test_comet_policy_chinese_mojibake_placeholder_fails(self) -> None:
        root = self.make_root()
        self.write_valid_surface(root)
        zh_path = root / COMET_ZH_POLICY
        zh_path.write_text(
            zh_path.read_text(encoding="utf-8").replace("Comet 控制", "Comet ??"),
            encoding="utf-8",
        )

        result = self.run_comet_policy_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("mojibake" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
