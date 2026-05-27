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

    def init_git_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True, text=True, cwd=root)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True, text=True, cwd=root)
        subprocess.run(
            ["git", "config", "user.email", "test@example.invalid"],
            check=True,
            capture_output=True,
            text=True,
            cwd=root,
        )

    def git_commit_all(self, root: Path, message: str) -> None:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True, text=True, cwd=root)
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True, text=True, cwd=root)

    def run_check_json(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json", *extra_args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_check_text(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), *extra_args],
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

    def test_text_output_reports_baseline_mode(self) -> None:
        root = self.make_root("name-clarity-text")
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            "# Guide\n\n- `tools/example.py` - validates one repository invariant before CI accepts a change.\n",
        )

        result = self.run_check_text(root, "--no-baseline")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Compatibility baseline: disabled", result.stdout)
        self.assertIn("Baseline allowed findings: 0", result.stdout)

    def test_fails_for_changed_unexplained_semantic_terms_in_git_forward_mode(self) -> None:
        root = self.make_root("semantic-forward-fail")
        self.init_git_repo(root)
        self.write_file(root, "docs_bilingual/guide.md", "# Guide\n\nExisting context.\n")
        self.git_commit_all(root, "initial")
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            (
                "# Guide\n\nExisting context.\n"
                "- [ ] `monitoring_status`: `clear`, `needs_decision`, or `blocked`.\n"
                "- [ ] Forward transition requires `monitoring_status=clear`.\n"
                "- [ ] Add `monitor-return-design`.\n"
            ),
        )

        result = self.run_check_json(root, "--no-baseline")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["semantic_violations"], 3)
        self.assertTrue(all("semantic_term_without_explanation" in error for error in payload["errors"]))

    def test_forward_mode_ignores_unchanged_historical_semantic_debt(self) -> None:
        root = self.make_root("semantic-forward-history")
        self.init_git_repo(root)
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            "# Guide\n\n- [ ] `monitoring_status`: `clear`, `needs_decision`, or `blocked`.\n",
        )
        self.git_commit_all(root, "historical debt")

        result = self.run_check_json(root, "--no-baseline")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["semantic_violations"], 0)

    def test_semantic_terms_pass_with_inline_explanation(self) -> None:
        root = self.make_root("semantic-inline-pass")
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            (
                "# Guide\n\n"
                "- `monitoring_status` - workflow field that records whether Monitoring is clear, needs operator decision, or blocks phase progress.\n"
                "- `monitor-return-design` - transition that moves work back to Design when planning evidence is incomplete.\n"
            ),
        )

        result = self.run_check_json(root, "--no-baseline", "--full-scan")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)

    def test_semantic_terms_pass_with_nearby_glossary(self) -> None:
        root = self.make_root("semantic-glossary-pass")
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            (
                "# Guide\n\n"
                "## Semantic notes\n\n"
                "| Term | Meaning |\n"
                "| --- | --- |\n"
                "| `monitor-return-design` | Transition that moves work back to Design when planning evidence is incomplete. |\n\n"
                "- [ ] In `comet-state.sh transition`, add `monitor-return-design`.\n"
            ),
        )

        result = self.run_check_json(root, "--no-baseline", "--full-scan")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)

    def test_paths_commands_urls_and_test_names_are_not_semantic_terms(self) -> None:
        root = self.make_root("semantic-ignore-pass")
        self.write_file(
            root,
            "docs_bilingual/guide.md",
            (
                "# Guide\n\n"
                "- `tools/check_name_clarity_rules.py` - checker script path, not a workflow state term.\n"
                "- `python tools/check_name_clarity_rules.py --root . --json` - command example, not a policy value.\n"
                "- `https://example.invalid/docs` - URL example, not a control decision.\n"
                "- `test/check_name_clarity_rules.test.py` - test file path, not a transition name.\n"
            ),
        )

        result = self.run_check_json(root, "--no-baseline", "--full-scan")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)


if __name__ == "__main__":
    unittest.main()
