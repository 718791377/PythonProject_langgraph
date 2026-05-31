from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCEGUARD_PATH = REPO_ROOT / "tools" / "check_orchestration_collaboration_evidenceguard.py"
ROLE_CHECK_PATH = REPO_ROOT / "tools" / "check_role_routing_directive_evidence.py"
FIXTURE_DIR = REPO_ROOT / "test" / "fixtures" / "orchestration_prompt_independent_collaboration_parity"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


evidenceguard = load_module("check_orchestration_collaboration_evidenceguard", EVIDENCEGUARD_PATH)
role_check = load_module("check_role_routing_directive_evidence", ROLE_CHECK_PATH)


class PromptIndependentActivationParityTest(unittest.TestCase):
    maxDiff = None

    def test_repository_fixtures_include_expected_failure_without_failing_suite(self) -> None:
        payload = evidenceguard.run_fixture_check(REPO_ROOT)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("missing_reminder_excuse_invalid.json", payload["checked_cases"])

    def test_missing_reminder_fixture_fails_when_not_marked_expected_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_fixture_dir = Path(temp_dir) / "fixtures"
            shutil.copytree(FIXTURE_DIR, temp_fixture_dir)
            invalid_path = temp_fixture_dir / "missing_reminder_excuse_invalid.json"
            payload = json.loads(invalid_path.read_text(encoding="utf-8"))
            payload.pop("expected_failure", None)
            invalid_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = evidenceguard.run_fixture_check(REPO_ROOT, temp_fixture_dir)

        self.assertFalse(result["ok"])
        self.assertTrue(any("missing user reminders" in error for error in result["errors"]), result["errors"])

    def test_qualified_governance_update_routes_match_with_and_without_collaboration_words(self) -> None:
        without_phrase = json.loads(
            (FIXTURE_DIR / "qualified_governance_update_without_collaboration_phrase.json").read_text(encoding="utf-8")
        )
        with_phrase = json.loads(
            (FIXTURE_DIR / "qualified_governance_update_with_collaboration_phrase.json").read_text(encoding="utf-8")
        )

        comparable_fields = {
            "phase",
            "capability_chain",
            "backend_default",
            "backend_ready",
            "experts",
            "durable_workflow",
            "persistent_team",
            "main_session_escalation",
            "approval_timeout_risk",
            "approval_receipt",
            "why",
        }
        self.assertFalse(without_phrase["collaboration_phrase_present"])
        self.assertTrue(with_phrase["collaboration_phrase_present"])
        self.assertEqual(
            {field: without_phrase["expected"][field] for field in comparable_fields},
            {field: with_phrase["expected"][field] for field in comparable_fields},
        )

    def test_role_evidence_rejects_missing_user_collaboration_reminder_excuse(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_path = Path(temp_dir) / "evidence.txt"
            evidence_path.write_text(
                "Routing trace: durable_workflow=not_needed because the user did not request parallelism or subagents.\n",
                encoding="utf-8",
            )

            payload = role_check.run_evidence_check(evidence_path)

        self.assertFalse(payload["ok"])
        self.assertIn("missing_reminder_excuse", payload["detected"])
        self.assertTrue(any("missing user collaboration reminders" in error for error in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
