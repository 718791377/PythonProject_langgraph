from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_fanout_write_ownership_evidence.py"

spec = importlib.util.spec_from_file_location("check_fanout_write_ownership_evidence", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

VALID_READ_FANOUT_EVIDENCE = """Run summary:
Native subagent fan-out used leader-side spawning with leader-owned fan-in.
agents.max_threads=4 and agents.max_depth=1.
Read-heavy, bounded, independent research fan-out was self-contained and materially advances the main task.
Raw Codex does not auto-spawn specialist roles; the main Codex CLI session spawned and absorbed results.
"""

VALID_WRITE_PARALLEL_EVIDENCE = """Worker brief:
Write-heavy parallel execution is allowed after plan freeze.
Each code-changing worker has file/module ownership and disjoint write sets.
No shared hotspot exists; otherwise hotspot serialization is leader-owned.
Leader-owned final integration and leader-owned merge plan remain in the main session.
Workers are not alone in the codebase, must not revert or overwrite other active owners, and must list changed paths.
"""

VALID_OVERRIDE_EVIDENCE = """Run summary:
Native subagent fan-out used leader-side spawning and leader-owned fan-in.
agents.max_threads=8 agents.max_depth=2 with explicit override approved by operator; override reason: emergency bounded read-heavy review.
Read-heavy, bounded, independent work materially advances the main task.
"""


class FanoutWriteOwnershipEvidenceCheckTest(unittest.TestCase):
    maxDiff = None

    def make_artifact_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_evidence(self, root: Path, content: str) -> Path:
        path = root / "evidence.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def run_cli(self, evidence_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--evidence", str(evidence_path), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_repository_surfaces_pass(self) -> None:
        payload = module.run_repository_check(REPO_ROOT)
        self.assertTrue(payload["ok"], payload["errors"])

    def test_missing_required_surface_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = module.run_repository_check(Path(temp_dir))
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Missing required fan-out/write-ownership policy surface" in e for e in payload["errors"]))

    def test_missing_registry_rule_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(snippets), encoding="utf-8")
            (root / "tools").mkdir(exist_ok=True)
            (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
            (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
                json.dumps({"schema_version": 1, "rules": []}), encoding="utf-8"
            )
            payload = module.run_repository_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any(module.REGISTRY_RULE_ID in e for e in payload["errors"]), payload["errors"])

    def test_valid_read_heavy_fanout_passes(self) -> None:
        root = self.make_artifact_root("fanout-read-valid")
        path = self.write_evidence(root, VALID_READ_FANOUT_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("fanout", payload["detected"])
        self.assertIn("read_heavy_fanout", payload["detected"])

    def test_valid_write_heavy_parallel_passes(self) -> None:
        root = self.make_artifact_root("fanout-write-valid")
        path = self.write_evidence(root, VALID_WRITE_PARALLEL_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("write_heavy_parallel", payload["detected"])

    def test_valid_override_passes(self) -> None:
        root = self.make_artifact_root("fanout-override-valid")
        path = self.write_evidence(root, VALID_OVERRIDE_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("fanout", payload["detected"])

    def test_cli_emits_json(self) -> None:
        root = self.make_artifact_root("fanout-cli")
        path = self.write_evidence(root, VALID_READ_FANOUT_EVIDENCE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["check_name"], module.CHECK_NAME)
        self.assertTrue(payload["ok"])

    def test_raw_codex_auto_spawn_claim_fails(self) -> None:
        root = self.make_artifact_root("raw-codex-auto")
        path = self.write_evidence(root, "Raw Codex auto-spawns specialist roles for every task.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("auto-spawns" in e for e in payload["errors"]), payload["errors"])

    def test_fanout_exceeding_threads_without_override_fails(self) -> None:
        root = self.make_artifact_root("too-many-threads")
        path = self.write_evidence(
            root,
            "Native subagent fan-out used leader-side spawning with leader-owned fan-in. "
            "agents.max_threads=7 agents.max_depth=1. "
            "Read-heavy, bounded, independent work materially advances the main task.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("agents.max_threads=6" in e for e in payload["errors"]), payload["errors"])

    def test_fanout_exceeding_depth_without_override_fails(self) -> None:
        root = self.make_artifact_root("too-deep")
        path = self.write_evidence(
            root,
            "Native subagent fan-out used leader-side spawning with leader-owned fan-in. "
            "agents.max_threads=6 agents.max_depth=2. "
            "Read-heavy, bounded, independent work materially advances the main task.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("agents.max_depth=1" in e for e in payload["errors"]), payload["errors"])

    def test_fanout_without_leader_side_spawning_fails(self) -> None:
        root = self.make_artifact_root("no-leader-side")
        path = self.write_evidence(
            root,
            "Native subagent fan-out used agents.max_threads=3 agents.max_depth=1. "
            "Read-heavy, bounded, independent work materially advances the main task.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("leader-side spawning" in e for e in payload["errors"]), payload["errors"])

    def test_write_heavy_without_ownership_fails(self) -> None:
        root = self.make_artifact_root("write-no-ownership")
        path = self.write_evidence(
            root,
            "Write-heavy parallel execution with code-changing workers. "
            "Workers are not alone in the codebase and must list changed paths.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("file/module ownership" in e for e in payload["errors"]), payload["errors"])
        self.assertTrue(any("disjoint write sets" in e for e in payload["errors"]), payload["errors"])

    def test_write_heavy_without_hotspot_or_integration_fails(self) -> None:
        root = self.make_artifact_root("write-no-hotspot")
        path = self.write_evidence(
            root,
            "Write-heavy parallel execution uses file/module ownership and disjoint write sets. "
            "Workers are not alone in the codebase, must not revert or overwrite, and list changed paths.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("hotspot serialization" in e for e in payload["errors"]), payload["errors"])
        self.assertTrue(any("leader-owned final integration" in e for e in payload["errors"]), payload["errors"])

    def test_overlapping_write_sets_without_serialization_fails(self) -> None:
        root = self.make_artifact_root("overlap-no-serialization")
        path = self.write_evidence(
            root,
            "Write-heavy parallel execution uses file/module ownership and overlapping write sets without serialization. "
            "Leader-owned final integration. Workers are not alone in the codebase, must not revert or overwrite, and list changed paths.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("Overlapping write sets" in e for e in payload["errors"]), payload["errors"])

    def test_blocking_critical_path_delegation_without_handoff_fails(self) -> None:
        root = self.make_artifact_root("blocking-delegation")
        path = self.write_evidence(
            root,
            "Delegated immediate blocking critical-path work to a worker while leader waited.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("critical-path" in e for e in payload["errors"]), payload["errors"])

    def test_no_fanout_marker_passes(self) -> None:
        root = self.make_artifact_root("no-fanout")
        path = self.write_evidence(root, "No fan-out occurred; single local execution slice.\n")

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("no_fanout", payload["detected"])


if __name__ == "__main__":
    unittest.main()
