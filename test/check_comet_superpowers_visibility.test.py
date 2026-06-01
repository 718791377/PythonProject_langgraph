from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_comet_superpowers_visibility.py"

spec = importlib.util.spec_from_file_location("check_comet_superpowers_visibility", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class CometSuperpowersVisibilityTests(unittest.TestCase):
    maxDiff = None

    def write_valid_surface(self, root: Path) -> None:
        for relative, terms in module.REQUIRED_TERMS.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(terms) + "\n", encoding="utf-8")

    def test_repository_surfaces_pass(self) -> None:
        payload = module.run_repository_check(REPO_ROOT)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn(".codex/skills/comet/SKILL.md", payload["checked_files"])
        self.assertIn("docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md", payload["checked_files"])

    def test_missing_required_surface_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            payload = module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("Missing required" in item for item in payload["errors"]), payload["errors"])

    def test_missing_how_layer_term_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_valid_surface(root)
            target = root / ".codex/skills/comet/SKILL.md"
            target.write_text(
                target.read_text(encoding="utf-8").replace("OpenSpec remains WHAT", ""),
                encoding="utf-8",
            )

            payload = module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("OpenSpec remains WHAT" in item for item in payload["errors"]), payload["errors"])

    def test_cli_emits_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_valid_surface(root)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=REPO_ROOT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["check_name"], "comet_superpowers_visibility")


if __name__ == "__main__":
    unittest.main()
