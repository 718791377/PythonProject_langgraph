from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_capability_switch_chain.py"

spec = importlib.util.spec_from_file_location("check_capability_switch_chain", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


VALID_STATE = {
    "schema_version": 3,
    "subagent_routing": "auto",
    "oh_my_codex": "on",
    "langgraph": "on",
    "durable_orchestration_backend": "langgraph",
}

VALID_BACKEND = {
    "backend": "langgraph",
    "status": "running",
    "phase": "define-target",
}


class CapabilitySwitchChainCheckerTests(unittest.TestCase):
    def run_with(self, state: dict | None, backend: dict | None = VALID_BACKEND, *, require_state: bool = True) -> dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            root.mkdir()
            state_path = Path(temp_dir) / "state.json"
            backend_path = root / ".omx" / "state" / "langgraph" / "backend.json"
            if state is not None:
                state_path.write_text(json.dumps(state), encoding="utf-8")
            if backend is not None:
                backend_path.parent.mkdir(parents=True)
                backend_path.write_text(json.dumps(backend), encoding="utf-8")
            return module.run_check(root, state_path, backend_path, require_state=require_state)

    def test_valid_langgraph_default_chain_passes(self) -> None:
        payload = self.run_with(VALID_STATE)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["state"]["effective_backend_default"], "langgraph")

    def test_subagent_off_disables_higher_layers(self) -> None:
        state = dict(VALID_STATE, subagent_routing="off", oh_my_codex="on", langgraph="on")
        payload = self.run_with(state)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("subagent_routing=off requires oh_my_codex=off" in item for item in payload["errors"]), payload["errors"])
        self.assertTrue(any("subagent_routing=off requires langgraph=off" in item for item in payload["errors"]), payload["errors"])

    def test_oh_my_codex_off_disables_langgraph(self) -> None:
        state = dict(VALID_STATE, oh_my_codex="off", langgraph="on")
        payload = self.run_with(state)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("oh_my_codex=off requires langgraph=off" in item for item in payload["errors"]), payload["errors"])

    def test_langgraph_backend_requires_langgraph_on(self) -> None:
        state = dict(VALID_STATE, langgraph="off", durable_orchestration_backend="langgraph")
        payload = self.run_with(state)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("durable_orchestration_backend=langgraph requires langgraph=on" in item for item in payload["errors"]), payload["errors"])

    def test_invalid_switch_value_fails(self) -> None:
        state = dict(VALID_STATE, subagent_routing="maybe")
        payload = self.run_with(state)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Invalid `subagent_routing`" in item for item in payload["errors"]), payload["errors"])

    def test_missing_state_warns_without_require_state(self) -> None:
        payload = self.run_with(None, require_state=False)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertGreaterEqual(payload["counts"]["warnings"], 1)

    def test_missing_state_fails_when_required(self) -> None:
        payload = self.run_with(None, require_state=True)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("capability state" in item for item in payload["errors"]), payload["errors"])

    def test_unready_langgraph_backend_fails_when_selected(self) -> None:
        backend = dict(VALID_BACKEND, status="unavailable")
        payload = self.run_with(VALID_STATE, backend)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("backend status is not ready" in item for item in payload["errors"]), payload["errors"])

    def test_readiness_projection_accepts_distinct_states(self) -> None:
        readiness = {
            "selected_backend": "langgraph",
            "readiness_fields": ["installed", "enabled", "selected", "ready"],
            "native_omx": {
                "installed": True,
                "enabled": True,
                "selected": False,
                "ready": False,
            },
            "langgraph": {
                "installed": True,
                "enabled": True,
                "selected": True,
                "ready": True,
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            root.mkdir()
            state_path = Path(temp_dir) / "state.json"
            backend_path = root / ".omx" / "state" / "langgraph" / "backend.json"
            readiness_path = Path(temp_dir) / "readiness.json"
            state_path.write_text(json.dumps(VALID_STATE), encoding="utf-8")
            backend_path.parent.mkdir(parents=True)
            backend_path.write_text(json.dumps(VALID_BACKEND), encoding="utf-8")
            readiness_path.write_text(json.dumps(readiness), encoding="utf-8")

            payload = module.run_check(root, state_path, backend_path, readiness_path, require_readiness=True)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["counts"]["capability_readiness_loaded"], 1)
        self.assertEqual(
            payload["capability_readiness"]["readiness_fields"],
            ["installed", "enabled", "selected", "ready"],
        )

    def test_readiness_projection_installed_only_is_not_ready(self) -> None:
        readiness = {
            "selected_backend": "native_omx",
            "readiness_fields": ["installed", "enabled", "selected", "ready"],
            "native_omx": {
                "installed": True,
                "enabled": False,
                "selected": True,
                "ready": False,
            },
            "langgraph": {
                "installed": False,
                "enabled": False,
                "selected": False,
                "ready": False,
            },
        }
        payload = module.validate_capability_readiness_projection(
            readiness,
            errors := [],
            [],
            label="test readiness",
        )
        self.assertFalse(errors, errors)
        self.assertFalse(payload["backends"]["native_omx"]["ready"])

    def test_readiness_projection_enabled_not_selected_is_not_ready(self) -> None:
        readiness = {
            "selected_backend": "langgraph",
            "readiness_fields": ["installed", "enabled", "selected", "ready"],
            "native_omx": {
                "installed": True,
                "enabled": True,
                "selected": False,
                "ready": False,
            },
            "langgraph": {
                "installed": True,
                "enabled": True,
                "selected": True,
                "ready": True,
            },
        }
        payload = module.validate_capability_readiness_projection(
            readiness,
            errors := [],
            [],
            label="test readiness",
        )
        self.assertFalse(errors, errors)
        self.assertFalse(payload["backends"]["native_omx"]["ready"])

    def test_readiness_projection_selected_not_ready_fails_if_ready_collapses_states(self) -> None:
        readiness = {
            "selected_backend": "langgraph",
            "readiness_fields": ["installed", "enabled", "selected", "ready"],
            "native_omx": {
                "installed": True,
                "enabled": True,
                "selected": False,
                "ready": False,
            },
            "langgraph": {
                "installed": False,
                "enabled": True,
                "selected": True,
                "ready": True,
            },
        }
        errors: list[str] = []
        module.validate_capability_readiness_projection(readiness, errors, [], label="test readiness")
        self.assertTrue(any("ready must equal installed && enabled && selected" in item for item in errors), errors)

    def test_readiness_projection_requires_all_distinct_fields(self) -> None:
        readiness = {
            "selected_backend": "langgraph",
            "readiness_fields": ["installed", "selected", "ready"],
            "native_omx": {
                "installed": True,
                "enabled": True,
                "selected": False,
                "ready": False,
            },
            "langgraph": {
                "installed": True,
                "enabled": True,
                "selected": True,
                "ready": True,
            },
        }
        errors: list[str] = []
        module.validate_capability_readiness_projection(readiness, errors, [], label="test readiness")
        self.assertTrue(any("readiness_fields missing required distinct state field `enabled`" in item for item in errors), errors)

    def test_readiness_projection_receipt_accepts_r4_smoke_metadata(self) -> None:
        receipt = {
            "receipt_kind": "durable_capability_readiness_projection",
            "promotion_marker": "smoke-tested",
            "generated_at": "2026-06-05T00:00:00Z",
            "capability_readiness": {
                "selected_backend": "langgraph",
                "readiness_fields": ["installed", "enabled", "selected", "ready"],
                "native_omx": {"installed": True, "enabled": True, "selected": False, "ready": False},
                "langgraph": {"installed": True, "enabled": True, "selected": True, "ready": True},
            },
            "blockers": [],
            "source_receipts": {"status_helper": "codex-durable-state-status.ps1"},
            "selector_evidence": {"selector_authority": ".omx/state/selectors/active.json", "active_selector_status": "missing"},
            "version_evidence": {"native_omx": {"install_state": "installed"}, "langgraph": {"install_state": "installed"}},
            "durable_workflow_adopted": False,
            "persistent_team_launched": False,
            "smoke": {"marker": "smoke-tested", "launched_backend": False, "launched_persistent_team": False},
        }
        payload = module.validate_capability_readiness_projection(receipt, errors := [], [], label="test receipt")
        self.assertFalse(errors, errors)
        self.assertEqual(payload["receipt"]["promotion_marker"], "smoke-tested")

    def test_readiness_projection_receipt_rejects_adoption_claim(self) -> None:
        receipt = {
            "receipt_kind": "durable_capability_readiness_projection",
            "promotion_marker": "smoke-tested",
            "generated_at": "2026-06-05T00:00:00Z",
            "capability_readiness": {
                "selected_backend": "native_omx",
                "readiness_fields": ["installed", "enabled", "selected", "ready"],
                "native_omx": {"installed": True, "enabled": True, "selected": True, "ready": True},
                "langgraph": {"installed": False, "enabled": False, "selected": False, "ready": False},
            },
            "blockers": [],
            "source_receipts": {},
            "selector_evidence": {"selector_authority": ".omx/state/selectors/active.json", "active_selector_status": "missing"},
            "version_evidence": {"native_omx": {"install_state": "installed"}, "langgraph": {"install_state": "not_installed"}},
            "durable_workflow_adopted": True,
            "persistent_team_launched": False,
            "smoke": {"marker": "smoke-tested", "launched_backend": False, "launched_persistent_team": False},
        }
        errors: list[str] = []
        module.validate_capability_readiness_projection(receipt, errors, [], label="test receipt")
        self.assertTrue(any("durable_workflow_adopted must be false" in item for item in errors), errors)

    def test_current_user_state_passes_when_available(self) -> None:
        state_path = module.default_state_file()
        if not state_path.exists():
            self.skipTest(f"user-level capability state is not present: {state_path}")
        payload = module.run_check(ROOT, state_path, module.default_backend_file(ROOT))
        self.assertTrue(payload["ok"], payload["errors"])


if __name__ == "__main__":
    unittest.main()
