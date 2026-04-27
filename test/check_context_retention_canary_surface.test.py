import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_context_retention_canary_surface.py"
START_CANARY = "".join(chr(codepoint) for codepoint in (25351, 25381, 23448))
END_CANARY = chr(21941) + "~"


class ContextRetentionCanarySurfaceCheckTest(unittest.TestCase):
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

    def write_startup_pair(self, root: Path, include_canary: bool = True) -> None:
        canary_sentence = f"Start `{START_CANARY}` and end `{END_CANARY}`.\n" if include_canary else ""
        self.write_file(
            root,
            "docs_bilingual/project_startup_summary.md",
            "# Startup\n\nContext-retention canary:\n\n" + canary_sentence,
        )
        self.write_file(
            root,
            "docs_bilingual/project_startup_summary.zh-CN.md",
            "# Startup ZH\n\nContext-retention canary:\n\n" + canary_sentence,
        )

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_when_canary_only_in_startup_pair(self) -> None:
        root = self.make_root("canary-pass")
        self.write_startup_pair(root)
        self.write_file(root, "AGENTS.md", "Refer to the startup summary for context-loss recovery.\n")

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_fails_when_startup_summary_missing_canary(self) -> None:
        root = self.make_root("canary-missing")
        self.write_startup_pair(root, include_canary=False)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("missing the startup-summary canary" in error for error in payload["errors"]))

    def test_fails_when_active_file_duplicates_canary(self) -> None:
        root = self.make_root("canary-duplicate")
        self.write_startup_pair(root)
        self.write_file(root, "AGENTS.md", f"Do not duplicate `{START_CANARY}` or `{END_CANARY}` here.\n")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("AGENTS.md" in error for error in payload["errors"]))

    def test_ignores_archived_openspec_history(self) -> None:
        root = self.make_root("canary-archive")
        self.write_startup_pair(root)
        self.write_file(
            root,
            "openspec/changes/archive/2026-04-01-old-change/proposal.md",
            f"Historical prompt `{START_CANARY}` and `{END_CANARY}`.\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)


if __name__ == "__main__":
    unittest.main()
