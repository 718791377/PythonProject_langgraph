import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_shared_runtime_contract.py"


class PySide6SharedRuntimeContractTest(unittest.TestCase):
    maxDiff = None

    def run_check(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args, "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_repository_contract_passes(self) -> None:
        result = self.run_check("--root", str(REPO_ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "pyside6_shared_runtime_contract")
        self.assertEqual(payload["counts"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
