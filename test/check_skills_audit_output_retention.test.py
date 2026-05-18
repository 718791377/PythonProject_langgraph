import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_skills_audit_output_retention.py"


class SkillsAuditOutputRetentionCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
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

    def test_sanitized_markdown_summary_is_allowed(self) -> None:
        root = self.make_repo("skills-retention-clean")
        self.write_file(root, "docs/skills-usage-audit-30d-summary.md", "# sanitized summary\n")
        subprocess.run(["git", "add", "docs/skills-usage-audit-30d-summary.md"], cwd=root, check=True)

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["violations"], [])

    def test_tmp_json_output_is_blocked_even_when_forced_into_git(self) -> None:
        root = self.make_repo("skills-retention-tmp")
        self.write_file(root, ".gitignore", ".tmp/\n")
        self.write_file(root, ".tmp/skills-usage-audit-30d.json", '{"raw": true}\n')
        subprocess.run(["git", "add", ".gitignore"], cwd=root, check=True)
        subprocess.run(["git", "add", "-f", ".tmp/skills-usage-audit-30d.json"], cwd=root, check=True)

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        reasons = {violation["reason"] for violation in payload["violations"]}
        self.assertIn("tmp_audit_artifact_retained", reasons)
        self.assertIn("raw_audit_json_retained", reasons)

    def test_raw_skills_audit_json_outside_tmp_is_blocked(self) -> None:
        root = self.make_repo("skills-retention-json")
        self.write_file(root, "reports/skills-usage-baseline-2026-05-18.json", '{"raw": true}\n')
        subprocess.run(["git", "add", "reports/skills-usage-baseline-2026-05-18.json"], cwd=root, check=True)

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["violations"][0]["reason"], "raw_audit_json_retained")


if __name__ == "__main__":
    unittest.main()
