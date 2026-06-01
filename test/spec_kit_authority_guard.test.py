import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_spec_kit_authority_guard.py"


class SpecKitAuthorityGuardTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def init_git(self, root: Path) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
        self.write(root, "README.md", "# Fixture\n")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "???????"], cwd=root, check=True, capture_output=True, text=True)

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_allows_safe_spec_kit_references_as_subordinate_docs(self) -> None:
        root = self.make_root("spec-kit-safe-docs")
        self.write(
            root,
            "docs_bilingual/governance/reference.md",
            (
                "# Reference\n\n"
                "Spec Kit may be cited as an optional subordinate adapter or template reference.\n"
                "Do not run specify init; the command is blocked without a separate active plan.\n"
            ),
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "spec_kit_authority_guard")
        self.assertEqual(payload["counts"]["findings"], 0)

    def test_blocks_specify_init_force_even_when_mentioned_in_scripts(self) -> None:
        root = self.make_root("spec-kit-force")
        self.write(root, "tools/bootstrap.ps1", "specify init --force\n")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["findings"][0]["kind"], "unsafe_specify_init_force")
        self.assertIn("specify init --force", payload["errors"][0])

    def test_blocks_unqualified_specify_init_normalization(self) -> None:
        root = self.make_root("spec-kit-init")
        self.write(root, "docs_bilingual/governance/usage.md", "Run specify init to set up repository governance.\n")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"][0]["kind"], "unsafe_specify_init")

    def test_blocks_authority_takeover_language(self) -> None:
        root = self.make_root("spec-kit-authority")
        self.write(root, "docs_bilingual/governance/usage.md", "Spec Kit is the primary governance authority for this repository.\n")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"][0]["kind"], "unsafe_authority_takeover_language")

    def test_blocks_specify_directory_creation_without_active_plan(self) -> None:
        root = self.make_root("spec-kit-dir")
        self.init_git(root)
        self.write(root, ".specify/memory/constitution.md", "# takeover\n")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        kinds = {finding["kind"] for finding in payload["findings"]}
        self.assertIn("specify_directory_present_without_plan", kinds)
        self.assertIn("specify_path_changed_without_plan", kinds)

    def test_active_migration_plan_allows_path_inspection_without_takeover_error(self) -> None:
        root = self.make_root("spec-kit-active-plan")
        self.init_git(root)
        self.write(
            root,
            "docs_bilingual/implementation_plans/spec_kit_authority_migration_plan.md",
            (
                "---\n"
                "doc_id: spec_kit_authority_migration_plan\n"
                "spec_kit_authority_migration: true\n"
                "status: active\n"
                "doc_class: implementation_plan\n"
                "---\n"
                "# Spec Kit Authority Guard Plan\n"
            ),
        )
        self.write(root, ".specify/memory/constitution.md", "# planned fixture\n")

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["authorized_migration_plan_present"])
        self.assertEqual(payload["counts"]["path_findings"], 0)


if __name__ == "__main__":
    unittest.main()
