import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_precommit_update_archive.py"


class PrecommitUpdateArchiveCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True)
        self.write(root, "README.md", "# Fixture\n")
        self.write(
            root,
            "tools/run_openspec_guard.py",
            "# guard fixture\n",
        )
        self.write(
            root,
            "tools/safety_rule_script_backing_registry.json",
            '{"schema_version": 1, "rules": []}\n',
        )
        self.write(
            root,
            "tools/ci/ci_test_manifest.json",
            '{"schema_version": 1, "python_unittest": [], "node_mjs": [], "powershell_ps1": []}\n',
        )
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "switch", "-c", "feature"], cwd=root, check=True, capture_output=True, text=True)
        return root

    def write(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def make_completed_change(self, root: Path, name: str) -> None:
        self.write(
            root,
            f"openspec/changes/{name}/.openspec.yaml",
            "schema: spec-driven\ncreated: 2026-05-17\nx_change_class: tooling\n",
        )
        self.write(
            root,
            f"openspec/changes/{name}/tasks.md",
            "## Tasks\n\n- [x] Implement checker.\n- [x] Add tests.\n",
        )

    def archive_change(self, root: Path, name: str) -> None:
        src = root / "openspec" / "changes" / name
        dst = root / "openspec" / "changes" / "archive" / f"2026-05-17-{name}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    def test_completed_active_change_without_archive_fails(self) -> None:
        root = self.make_repo("precommit-active-complete")
        self.make_completed_change(root, "add-local-guard")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("all tasks are checked", payload["errors"][0])
        self.assertEqual(payload["counts"]["active_change_reviews"], 1)

    def test_completed_active_change_with_archive_passes(self) -> None:
        root = self.make_repo("precommit-archive-complete")
        self.make_completed_change(root, "add-local-guard")
        self.archive_change(root, "add-local-guard")

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["active_change_reviews"], [])

    def test_completed_active_change_with_explicit_defer_marker_passes(self) -> None:
        root = self.make_repo("precommit-active-deferred")
        self.write(
            root,
            "openspec/changes/add-local-guard/.openspec.yaml",
            "\n".join(
                [
                    "schema: spec-driven",
                    "created: 2026-05-17",
                    "x_change_class: tooling",
                    "x_archive_deferred_reason: remote-ci-before-archive",
                    "x_archive_follow_up: archive-add-local-guard",
                    "",
                ]
            ),
        )
        self.write(
            root,
            "openspec/changes/add-local-guard/tasks.md",
            "## Tasks\n\n- [x] Implement checker.\n",
        )

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["active_change_reviews"][0]["deferred_archive_allowed"])

    def test_new_test_file_requires_manifest_update(self) -> None:
        root = self.make_repo("precommit-test-manifest")
        self.write(root, "test/new_policy.test.py", "import unittest\n")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("ci_test_manifest", payload["errors"][0])

        self.write(
            root,
            "tools/ci/ci_test_manifest.json",
            '{"schema_version": 1, "python_unittest": ["new_policy.test.py"], "node_mjs": [], "powershell_ps1": []}\n',
        )
        fixed = self.run_check(root)
        self.assertEqual(fixed.returncode, 0, fixed.stdout + fixed.stderr)

    def test_new_checker_requires_guard_or_registry_update(self) -> None:
        root = self.make_repo("precommit-checker-registration")
        self.write(root, "tools/check_new_policy.py", "# checker\n")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("new checker must be registered", payload["errors"][0])

        self.write(root, "tools/run_openspec_guard.py", "check_new_policy.py\n")
        fixed = self.run_check(root)
        self.assertEqual(fixed.returncode, 0, fixed.stdout + fixed.stderr)


if __name__ == "__main__":
    unittest.main()
