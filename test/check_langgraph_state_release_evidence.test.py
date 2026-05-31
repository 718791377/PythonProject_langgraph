from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_durable_artifact_state_surfaces.py"
FIXTURE_DIR = REPO_ROOT / "test" / "fixtures" / "langgraph_state_release_evidence"

spec = importlib.util.spec_from_file_location("check_durable_artifact_state_surfaces", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class LangGraphStateReleaseEvidenceTest(unittest.TestCase):
    maxDiff = None

    def fixture(self, name: str) -> Path:
        path = FIXTURE_DIR / name
        self.assertTrue(path.exists(), f"missing fixture {path}")
        return path

    def run_cli(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--evidence", str(path), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_fixture(self, name: str) -> dict:
        return module.run_evidence_check(self.fixture(name))

    def test_fixture_set_covers_completed_running_released_and_handoff_states(self) -> None:
        names = {path.name for path in FIXTURE_DIR.glob("*.json")}
        self.assertIn("completed_valid.json", names)
        self.assertIn("running_completed_invalid.json", names)
        self.assertIn("released_valid.json", names)
        self.assertIn("handoff_valid.json", names)

    def test_completed_release_fixture_passes(self) -> None:
        payload = self.run_fixture("completed_valid.json")

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("langgraph_state_release", payload["detected"])

    def test_released_fixture_requires_release_fields_and_passes(self) -> None:
        payload = self.run_fixture("released_valid.json")

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("langgraph_state_release", payload["detected"])

    def test_handoff_fixture_requires_handoff_fields_and_passes(self) -> None:
        payload = self.run_fixture("handoff_valid.json")

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("langgraph_state_release", payload["detected"])

    def test_completed_running_state_fails_closed(self) -> None:
        payload = self.run_fixture("running_completed_invalid.json")

        self.assertFalse(payload["ok"])
        self.assertTrue(any("status=running" in error for error in payload["errors"]), payload["errors"])

    def test_handoff_missing_target_and_reason_fails(self) -> None:
        payload = self.run_fixture("handoff_missing_fields_invalid.json")

        self.assertFalse(payload["ok"])
        self.assertTrue(any("handoff_target" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("reason" in error for error in payload["errors"]), payload["errors"])

    def test_cli_rejects_completed_running_state(self) -> None:
        result = self.run_cli(self.fixture("running_completed_invalid.json"))

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("status=running" in error for error in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
