import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_name_clarity_rules.py"


class NameClarityRulesCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_check_json(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json", *extra_args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_fails_for_new_bare_code_names_in_docs_and_openspec(self) -> None:
        root = self.make_root("name-clarity-fail")
        self.write_file(root, "docs_bilingual/guide.md", "# Guide\n\n- `tools/example.py`\n")
        self.write_file(root, "openspec/changes/example/tasks.md", "# Tasks\n\n1. `core`\n")

        result = self.run_check_json(root, "--no-baseline")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["check_name"], "name_clarity_rules")
        self.assertEqual(payload["counts"]["violations"], 2)
        self.assertTrue(any("docs_bilingual/guide.md" in error for error in payload["errors"]))
        self.assertTrue(any("openspec/changes/example/tasks.md" in error for error in payload["errors"]))

    def test_passes_when_names_have_purpose_explanations(self) -> None:
        root = self.make_root("name-clarity-pass")
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            "# Guide\n\n- `tools/example.py` - validates one repository invariant before CI accepts a change.\n",
        )
        self.write_file(
            root,
            "openspec/changes/example/tasks.md",
            "# Tasks\n\n1. `core` - the default profile for non-web repositories.\n",
        )

        result = self.run_check_json(root, "--no-baseline")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["violations"], 0)

    def test_baseline_allows_existing_debt_but_not_new_entries(self) -> None:
        root = self.make_root("name-clarity-baseline")
        self.write_file(
            root,
            "tools/name_clarity_baseline.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "check_name": "name_clarity_baseline",
                    "allowed_findings": {
                        "docs_bilingual/guide.md": ["- `tools/existing.py`"],
                    },
                }
            ),
        )
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            "# Guide\n\n- `tools/existing.py`\n- `tools/new.py`\n",
        )

        result = self.run_check_json(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["findings_total"], 2)
        self.assertEqual(payload["counts"]["baseline_allowed"], 1)
        self.assertEqual(payload["counts"]["violations"], 1)
        self.assertIn("tools/new.py", payload["errors"][0])


if __name__ == "__main__":
    unittest.main()
