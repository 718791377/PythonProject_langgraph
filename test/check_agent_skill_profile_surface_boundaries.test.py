from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_agent_skill_profile_surface_boundaries.py"

spec = importlib.util.spec_from_file_location("check_agent_skill_profile_surface_boundaries", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class AgentSkillProfileSurfaceBoundaryTests(unittest.TestCase):
    def test_repository_surfaces_pass(self) -> None:
        payload = module.run_repository_check(ROOT)
        self.assertTrue(payload["ok"], payload["errors"])

    def test_missing_required_surface_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            payload = module.run_repository_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Missing required" in item for item in payload["errors"]), payload["errors"])

    def test_skill_invocation_as_expert_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir) / "report.md"
            evidence.write_text(
                "We loaded a plugin profile and used skill invocation as expert evidence; expert returned.",
                encoding="utf-8",
            )
            payload = module.run_evidence_check(evidence)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Skill/profile surfaces" in item or "cannot support" in item for item in payload["errors"]), payload["errors"])

    def test_skill_invocation_with_local_verification_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir) / "report.md"
            evidence.write_text(
                "Skill invocation loaded workflow instructions only. Evidence came from local verification and local test results.",
                encoding="utf-8",
            )
            payload = module.run_evidence_check(evidence)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("valid_evidence_source", payload["detected"])

    def test_plugin_profile_native_subagent_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir) / "report.md"
            evidence.write_text(
                "Plugin profiles are native subagents, so the profile helper is expert evidence.",
                encoding="utf-8",
            )
            payload = module.run_evidence_check(evidence)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("must not be described" in item for item in payload["errors"]), payload["errors"])

    def test_cli_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir) / "report.md"
            evidence.write_text("Skill invocation only; procedural instructions loaded without evidence claim.", encoding="utf-8")
            payload = module.run_evidence_check(evidence)
        self.assertEqual(payload["check_name"], "agent_skill_profile_surface_boundaries")
        self.assertTrue(payload["ok"], payload["errors"])


if __name__ == "__main__":
    unittest.main()
