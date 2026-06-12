from __future__ import annotations

import importlib.util
import shutil
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_orchestration_collaboration_evidenceguard.py"

spec = importlib.util.spec_from_file_location("check_orchestration_collaboration_evidenceguard", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class CollaborationEvidenceguardBilingualSurfaceTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_repository_surfaces(self, root: Path) -> None:
        shutil.copytree(REPO_ROOT / module.DEFAULT_FIXTURE_DIR, root / module.DEFAULT_FIXTURE_DIR)
        for rel in module.REQUIRED_SURFACE_SNIPPETS:
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8-sig"), encoding="utf-8")
        for rel in ("tools/run_openspec_guard.py", "tools/safety_rule_script_backing_registry.json"):
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8-sig"), encoding="utf-8")

    def test_extended_fixture_registration_is_required(self) -> None:
        root = self.make_root("collab-required-fixtures")
        self.copy_repository_surfaces(root)
        (root / module.DEFAULT_FIXTURE_DIR / "cold_start_read_order_valid.json").unlink()

        payload = module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("cold_start_read_order_valid.json" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_chinese_openspec_surface_requires_bilingual_parity_wording(self) -> None:
        root = self.make_root("collab-zh-bilingual-snippet")
        self.copy_repository_surfaces(root)
        zh_path = root / "openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md"
        zh_text = zh_path.read_text(encoding="utf-8-sig").replace("\u53cc\u8bed OpenSpec heading parity", "OpenSpec heading parity")
        zh_path.write_text(zh_text, encoding="utf-8")

        payload = module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("\u53cc\u8bed OpenSpec heading parity" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_updated_plan_conversation_rejects_markdown_checkboxes(self) -> None:
        issues = module.conversation_surface_issues(
            "updated_plan",
            "Updated Plan\n- [x] read startup files\n- [ ] run local gate",
        )

        self.assertTrue(any("Markdown checkbox" in issue for issue in issues), issues)

    def test_updated_plan_conversation_accepts_tree_status_panel(self) -> None:
        issues = module.conversation_surface_issues(
            "updated_plan",
            "Updated Plan\n\u2514 \u672c\u5730\u9a8c\u8bc1\u540e\u5408\u5165 main\n  \u2714 \u66f4\u65b0\u65b9\u6848\n  \u25a1 \u8fd0\u884c\u95e8\u7981",
        )

        self.assertEqual([], issues)

    def test_updated_plan_conversation_rejects_duplicate_or_nested_panels(self) -> None:
        duplicate = module.conversation_surface_issues(
            "updated_plan",
            "Updated Plan\n  \u2714 one\n\nUpdated Plan\n  \u25a1 duplicate",
        )
        nested = module.conversation_surface_issues(
            "updated_plan",
            "Updated Plan\n\u2514 Updated Plan\n  \u2714 nested",
        )

        self.assertTrue(any("exactly one" in issue for issue in duplicate), duplicate)
        self.assertTrue(any("exactly one" in issue for issue in nested), nested)

    def test_routing_trace_conversation_requires_full_key_value_fields(self) -> None:
        valid = module.conversation_surface_issues(
            "routing_trace",
            "Routing trace: phase=execute, capability_chain=subagent:auto > omx:on > langgraph:on, "
            "backend_default=langgraph, backend_ready=true, "
            "experts=blocked:platform_subagent_invocation_constraint, durable_workflow=not_needed, "
            "persistent_team=not_needed, main_session_escalation=not_needed, "
            "approval_timeout_risk=none, approval_receipt=none, "
            "why=threshold_not_met:single_execution_slice",
        )
        prose_only = module.conversation_surface_issues(
            "routing_trace",
            "Routing trace\nThis is only prose without diagnostic fields.",
        )
        missing_full_fields = module.conversation_surface_issues(
            "routing_trace",
            "Routing trace: phase=execute, experts=blocked:platform_subagent_invocation_constraint, "
            "why=threshold_not_met:single_execution_slice",
        )
        legacy = module.conversation_surface_issues(
            "routing_trace",
            "Routing trace: phase=execute, experts_now=main, durable_team=not_selected, "
            "why=threshold_not_met:single_execution_slice",
        )
        duplicate = module.conversation_surface_issues(
            "routing_trace",
            "Routing trace: phase=execute, capability_chain=subagent:auto > omx:on > langgraph:on, "
            "backend_default=langgraph, backend_ready=true, experts=none, durable_workflow=not_needed, "
            "persistent_team=not_needed, main_session_escalation=not_needed, approval_timeout_risk=none, "
            "approval_receipt=none, why=threshold_not_met:single_execution_slice\n"
            "Routing trace: phase=verify-accept, why=duplicate",
        )

        self.assertEqual([], valid)
        self.assertTrue(any("key=value" in issue for issue in prose_only), prose_only)
        self.assertTrue(any("capability_chain" in issue for issue in missing_full_fields), missing_full_fields)
        self.assertTrue(any("legacy short field" in issue for issue in legacy), legacy)
        self.assertTrue(any("exactly one" in issue for issue in duplicate), duplicate)


if __name__ == "__main__":
    unittest.main()
