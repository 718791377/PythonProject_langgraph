import json
import shutil
import subprocess
import sys
import unittest
import uuid
from importlib import util as importlib_util
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_spec_kit_authority_guard.py"


def load_guard_module():
    spec = importlib_util.spec_from_file_location("check_spec_kit_authority_guard_under_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    module = importlib_util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
        subprocess.run(["git", "commit", "-m", "fixture commit"], cwd=root, check=True, capture_output=True, text=True)

    def run_check(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *extra_args, "--json"],
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

    def test_ignores_linked_worktree_carrier_directory(self) -> None:
        root = self.make_root("spec-kit-worktrees-excluded")
        self.write(
            root,
            ".worktrees/old-branch/docs_bilingual/governance/usage.md",
            "Spec Kit is the primary governance authority for this repository.\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["findings"], 0)

    def test_prunes_excluded_directories_before_recursive_scan(self) -> None:
        root = self.make_root("spec-kit-prunes-excluded-before-scan")
        self.write(root, "docs/usage.md", "Spec Kit is a safe subordinate adapter reference.\n")
        self.write(
            root,
            ".worktrees/old-branch/docs_bilingual/governance/usage.md",
            "Spec Kit is the primary governance authority for this repository.\n",
        )
        guard = load_guard_module()

        with mock.patch.object(
            guard.Path,
            "rglob",
            side_effect=AssertionError("raw Path.rglob would descend into excluded worktrees"),
        ):
            scanned_files = guard.iter_scan_files(root, (".",))
            existing_paths = guard.iter_existing_paths(root, (".",))

        relative_files = {guard.relative_to_root(root, path) for path in scanned_files}
        self.assertEqual(relative_files, {"docs/usage.md"})
        self.assertTrue(all(not path.startswith(".worktrees/") for path in existing_paths))

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

    def test_blocks_generated_speckit_surfaces_without_active_plan(self) -> None:
        root = self.make_root("spec-kit-generated-surfaces")
        self.write(root, "specs/feature/spec.md", "# generated root specs fixture\n")
        self.write(root, ".codex/commands/speckit.plan.md", "# generated slash command fixture\n")
        self.write(root, ".codex/skills/speckit-plan/SKILL.md", "# generated skills-mode fixture\n")
        self.write(root, ".github/prompts/speckit.plan.prompt.md", "# generated prompt fixture\n")
        self.write(root, "speckit.toml", "generated = true\n")
        self.write(root, "speckit-plan.yaml", "generated: true\n")
        self.write(root, "extensions/speckit/extension.md", "# generated extension fixture\n")
        self.write(root, "presets/speckit/default.md", "# generated preset fixture\n")
        self.write(root, "workflow_outputs/speckit/result.json", '{"generated": true}\n')

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        kinds = {finding["kind"] for finding in payload["findings"]}
        self.assertIn("specs_directory_present_without_plan", kinds)
        self.assertIn("generated_speckit_surface_present_without_plan", kinds)
        self.assertIn("generated_speckit_extension_present_without_plan", kinds)
        self.assertIn("generated_speckit_preset_present_without_plan", kinds)
        self.assertIn("generated_speckit_workflow_output_present_without_plan", kinds)

    def test_blocks_unqualified_speckit_slash_and_skill_commands(self) -> None:
        root = self.make_root("spec-kit-command-surfaces")
        self.write(
            root,
            "docs_bilingual/governance/usage.md",
            "Run /speckit.plan and then $speckit-implement as the new workflow.\n",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        kinds = {finding["kind"] for finding in payload["findings"]}
        self.assertIn("unsafe_speckit_slash_command", kinds)
        self.assertIn("unsafe_speckit_skill_command", kinds)

    def test_accepts_valid_dry_run_runtime_receipt(self) -> None:
        root = self.make_root("spec-kit-receipt-valid")
        receipt = root / "receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "runtime": "spec_kit_subordinate_runtime",
                    "mode": "probe",
                    "dry_run_only": True,
                    "would_run_specify": False,
                    "source_url": "https://github.com/github/spec-kit",
                    "source_pin": "7106858c4e636098815fffa23f6c6b99eb0e156b",
                    "authority_decision": {
                        "decision": "subordinate",
                        "winning_authority": "Comet/OpenSpec/Superpowers",
                        "priority_order": "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit",
                    },
                    "surface_status": {
                        "specify_init": "blocked",
                        "specify_init_force": "blocked",
                        "specify_self_check": "blocked",
                        ".specify/": "absent",
                        "specs/": "absent",
                        "/speckit.*": "blocked",
                        "$speckit-*": "blocked",
                        "extensions": "absent",
                        "presets": "absent",
                        "workflow_outputs": "absent",
                    },
                    "redaction": {"status": "pass"},
                    "timeout": {"seconds": 10, "released": True},
                    "rollback_pointer": "not-needed-dry-run",
                    "local_main_first_validation": {"status": "not_required_for_probe"},
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        result = self.run_check(root, "--receipt", str(receipt))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["receipt_validation"]["ok"])
        self.assertEqual(payload["receipt_validation"]["counts"]["receipts"], 1)

    def test_rejects_receipt_missing_priority_order(self) -> None:
        root = self.make_root("spec-kit-receipt-priority-missing")
        receipt = root / "receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "runtime": "spec_kit_subordinate_runtime",
                    "mode": "probe",
                    "dry_run_only": True,
                    "would_run_specify": False,
                    "source_url": "https://github.com/github/spec-kit",
                    "source_pin": "7106858c4e636098815fffa23f6c6b99eb0e156b",
                    "authority_decision": {
                        "decision": "subordinate",
                        "winning_authority": "Comet/OpenSpec/Superpowers",
                    },
                    "surface_status": {
                        "specify_init": "blocked",
                        "specify_init_force": "blocked",
                        "specify_self_check": "blocked",
                        ".specify/": "absent",
                        "specs/": "absent",
                        "/speckit.*": "blocked",
                        "$speckit-*": "blocked",
                        "extensions": "absent",
                        "presets": "absent",
                        "workflow_outputs": "absent",
                    },
                    "redaction": {"status": "pass"},
                    "timeout": {"seconds": 10, "released": True},
                    "rollback_pointer": "not-needed-dry-run",
                    "local_main_first_validation": {"status": "not_required_for_probe"},
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        result = self.run_check(root, "--receipt", str(receipt))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["receipt_validation"]["ok"])
        self.assertIn(
            "receipt.json:receipt_authority_priority_order_mismatch:<missing>",
            payload["receipt_validation"]["errors"],
        )

    def test_rejects_receipt_missing_surface_status_key(self) -> None:
        root = self.make_root("spec-kit-receipt-invalid")
        receipt = root / "receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "dry_run_only": True,
                    "would_run_specify": False,
                    "source_url": "https://github.com/github/spec-kit",
                    "source_pin": "7106858c4e636098815fffa23f6c6b99eb0e156b",
                    "authority_decision": {
                        "decision": "subordinate",
                        "winning_authority": "Comet/OpenSpec/Superpowers",
                    },
                    "surface_status": {"specify_init": "blocked"},
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        result = self.run_check(root, "--receipt", str(receipt))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["receipt_validation"]["ok"])
        self.assertIn("receipt_missing_surface_status_key:.specify/", payload["receipt_validation"]["errors"])


if __name__ == "__main__":
    unittest.main()
