from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_orchestration_activation_policy.py"

spec = importlib.util.spec_from_file_location("check_orchestration_activation_policy", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class OrchestrationActivationPolicyCheckerTests(unittest.TestCase):
    def test_repository_surfaces_pass(self) -> None:
        payload = module.run_check(ROOT)
        self.assertTrue(payload["ok"], payload["errors"])

    def test_missing_required_surface_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Missing required orchestration activation surface" in item for item in payload["errors"]))

    def test_forbidden_missing_reminder_wording_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(snippets), encoding="utf-8")
            (root / "tools").mkdir(exist_ok=True)
            (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
            (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "rules": [
                            {
                                "id": module.REGISTRY_RULE_ID,
                                "prompt_reminders": [
                                    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md"
                                ],
                                "script_controls": ["tools/check_orchestration_activation_policy.py"],
                                "guard_steps": [module.GUARD_STEP],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            agents = root / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8") + "\nuser did not ask for parallelism\n", encoding="utf-8")
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("forbidden missing-reminder" in item for item in payload["errors"]))

    def test_missing_durable_team_threshold_trace_wording_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                filtered = [
                    snippet
                    for snippet in snippets
                    if snippet
                    not in {
                        "threshold_not_met:no_frozen_plan",
                        "threshold_not_met:single_execution_slice",
                    }
                ]
                path.write_text("\n".join(filtered), encoding="utf-8")
            (root / "tools").mkdir(exist_ok=True)
            (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
            (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "rules": [
                            {
                                "id": module.REGISTRY_RULE_ID,
                                "prompt_reminders": [
                                    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md"
                                ],
                                "script_controls": ["tools/check_orchestration_activation_policy.py"],
                                "guard_steps": [module.GUARD_STEP],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("threshold_not_met:no_frozen_plan" in item for item in payload["errors"]),
            payload["errors"],
        )
        self.assertTrue(
            any("threshold_not_met:single_execution_slice" in item for item in payload["errors"]),
            payload["errors"],
        )

    def test_missing_hard_routing_directive_adoption_wording_fails(self) -> None:
        directive_snippets = {
            "hard routing directives",
            "Hard routing directives SHALL require adoption or named blockers",
            "Explicit directive is adopted",
            "Explicit directive is blocked",
            "explanation-only mode",
            "blocked:backend_not_ready",
            "blocked:preflight_failed",
            "blocked:helper_missing",
            "blocked:write_ownership_conflict",
            "optional preference",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                filtered = [snippet for snippet in snippets if snippet not in directive_snippets]
                path.write_text("\n".join(filtered), encoding="utf-8")
            (root / "tools").mkdir(exist_ok=True)
            (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
            (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "rules": [
                            {
                                "id": module.REGISTRY_RULE_ID,
                                "prompt_reminders": [
                                    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md"
                                ],
                                "script_controls": ["tools/check_orchestration_activation_policy.py"],
                                "guard_steps": [module.GUARD_STEP],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("explanation-only mode" in item for item in payload["errors"]), payload["errors"])
        self.assertTrue(any("blocked:backend_not_ready" in item for item in payload["errors"]), payload["errors"])
        self.assertTrue(any("optional preference" in item for item in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
