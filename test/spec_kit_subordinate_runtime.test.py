import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "tools" / "spec_kit_subordinate_runtime.py"
GUARD = REPO_ROOT / "tools" / "check_spec_kit_authority_guard.py"


class SpecKitSubordinateRuntimeTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def run_runtime(self, mode: str, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(RUNTIME), mode, "--root", str(root), *extra_args, "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def run_guard(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GUARD), "--root", str(root), *extra_args, "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_probe_emits_dry_run_receipt_without_mutating_spec_kit_surfaces(self) -> None:
        root = self.make_root("spec-kit-runtime-probe")

        result = self.run_runtime("probe", root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "probe")
        self.assertTrue(payload["dry_run_only"])
        self.assertFalse(payload["would_run_specify"])
        self.assertFalse(payload["runs_specify"])
        self.assertFalse(payload["installs_spec_kit"])
        self.assertEqual(payload["source_url"], "https://github.com/github/spec-kit")
        self.assertEqual(payload["source_pin"], "7106858c4e636098815fffa23f6c6b99eb0e156b")
        self.assertEqual(payload["authority_decision"]["decision"], "subordinate")
        self.assertEqual(
            payload["authority_decision"]["priority_order"],
            "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit",
        )
        self.assertFalse((root / ".specify").exists())
        self.assertFalse((root / "specs").exists())

    def test_init_dry_run_blocks_when_specify_directory_already_exists(self) -> None:
        root = self.make_root("spec-kit-runtime-init-blocked")
        (root / ".specify" / "memory").mkdir(parents=True)
        (root / ".specify" / "memory" / "constitution.md").write_text("# fixture\n", encoding="utf-8")

        result = self.run_runtime("init-dry-run", root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn(".specify_present", payload["blockers"])
        self.assertTrue(payload["dry_run_only"])
        self.assertFalse(payload["would_run_specify"])

    def test_probe_receipt_is_accepted_by_authority_guard(self) -> None:
        root = self.make_root("spec-kit-runtime-receipt")
        receipt = root / "receipt.json"

        runtime = self.run_runtime("probe", root, "--receipt-out", str(receipt))
        self.assertEqual(runtime.returncode, 0, runtime.stdout + runtime.stderr)
        self.assertTrue(receipt.exists())

        guard = self.run_guard(root, "--receipt", str(receipt))
        self.assertEqual(guard.returncode, 0, guard.stdout + guard.stderr)
        payload = json.loads(guard.stdout)
        self.assertTrue(payload["receipt_validation"]["ok"])

    def test_live_apply_mode_is_rejected_by_argparse_choices(self) -> None:
        root = self.make_root("spec-kit-runtime-live-rejected")

        result = self.run_runtime("apply", root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)
        self.assertFalse((root / ".specify").exists())
        self.assertFalse((root / "specs").exists())


if __name__ == "__main__":
    unittest.main()
