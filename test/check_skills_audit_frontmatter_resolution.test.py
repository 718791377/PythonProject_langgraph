import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_skills_audit_frontmatter_resolution.py"


class SkillsAuditFrontmatterResolutionCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> tuple[Path, Path]:
        base = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        repo = base / "repo"
        codex_home = base / "codex-home"
        repo.mkdir(parents=True, exist_ok=True)
        codex_home.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(base, ignore_errors=True))
        return repo, codex_home

    def write_skill(self, root: Path, relative_dir: str, *, name: str, description: str) -> Path:
        path = root / relative_dir / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nname: {name}\ndescription: {description}\n---\nBody\n", encoding="utf-8")
        return path

    def write_evidence_pair(self, repo: Path) -> None:
        evidence_dir = repo / "docs_bilingual" / "memory"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        content = "\n".join(
            [
                "# Evidence",
                "",
                "- Historical warning: `Skipped loading 286 skill(s) due to invalid SKILL.md files.`",
                "- Historical name marker: `invalid name: exceeds maximum length of 64 characters`.",
                "- Historical description marker: `invalid description: exceeds maximum length of 1024 characters`.",
            ]
        )
        (evidence_dir / "skills_usage_audit_reference_warning_resolution_2026-06-21.md").write_text(
            content,
            encoding="utf-8",
        )
        (evidence_dir / "skills_usage_audit_reference_warning_resolution_2026-06-21.zh-CN.md").write_text(
            content,
            encoding="utf-8",
        )

    def run_check(self, repo: Path, codex_home: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(repo),
                "--codex-home",
                str(codex_home),
                "--json",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_clean_current_frontmatter_closes_historical_warning(self) -> None:
        repo, codex_home = self.make_repo("frontmatter-clean")
        self.write_evidence_pair(repo)
        self.write_skill(codex_home / "skills", "valid", name="valid-skill", description="Valid current skill.")

        result = self.run_check(repo, codex_home)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["resolved"])
        self.assertTrue(payload["historical_issue"]["detected"])
        self.assertEqual(payload["current_frontmatter_compatibility"]["invalid_total"], 0)
        self.assertEqual(payload["interpretation"], "historical_warning_current_inventory_clean")
        self.assertFalse(payload["safety"]["mutates_config"])
        self.assertFalse(payload["safety"]["edits_plugin_cache"])
        self.assertFalse(payload["safety"]["raw_paths_retained"])
        self.assertFalse(payload["safety"]["raw_skill_bodies_retained"])

    def test_current_user_frontmatter_invalid_fails_closed(self) -> None:
        repo, codex_home = self.make_repo("frontmatter-invalid-user")
        self.write_evidence_pair(repo)
        self.write_skill(
            codex_home / "skills",
            "invalid",
            name="invalid-" + ("too-long-" * 8),
            description="D" * 1030,
        )

        result = self.run_check(repo, codex_home)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("current_frontmatter_blocking_invalid_total_not_zero", payload["errors"])
        self.assertIn("current_frontmatter_invalid_total_not_zero", payload["errors"])
        current = payload["current_frontmatter_compatibility"]
        self.assertGreater(current["invalid_total"], 0)
        self.assertGreater(current["blocking_invalid_total"], 0)
        self.assertEqual(current["plugin_cache_warning_total"], 0)

    def test_current_repo_frontmatter_invalid_fails_closed(self) -> None:
        repo, codex_home = self.make_repo("frontmatter-invalid-repo")
        self.write_evidence_pair(repo)
        self.write_skill(
            repo / ".codex" / "skills",
            "invalid",
            name="invalid-" + ("too-long-" * 8),
            description="D" * 1030,
        )

        result = self.run_check(repo, codex_home)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        current = payload["current_frontmatter_compatibility"]
        self.assertEqual(current["blocking_by_layer"].get("repo"), 1)
        self.assertIn("current_frontmatter_blocking_invalid_total_not_zero", payload["errors"])

    def test_current_plugin_cache_frontmatter_invalid_is_warning_only(self) -> None:
        repo, codex_home = self.make_repo("frontmatter-invalid-plugin")
        self.write_evidence_pair(repo)
        self.write_skill(
            codex_home / "plugins" / "cache" / "vendor" / "package" / "skills",
            "invalid",
            name="invalid-" + ("too-long-" * 8),
            description="D" * 1030,
        )

        result = self.run_check(repo, codex_home)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertTrue(payload["resolved"])
        self.assertNotIn("current_frontmatter_invalid_total_not_zero", payload["errors"])
        self.assertIn("plugin_cache_frontmatter_invalid_report_only_without_vendor_cache_authorization", payload["warnings"])
        current = payload["current_frontmatter_compatibility"]
        self.assertGreater(current["invalid_total"], 0)
        self.assertEqual(current["blocking_invalid_total"], 0)
        self.assertEqual(current["plugin_cache_warning_total"], 1)
        self.assertEqual(current["plugin_cache_policy"], "report_only_without_vendor_cache_authorization")
        self.assertFalse(current["edits_plugin_cache"])
        self.assertFalse(payload["safety"]["edits_plugin_cache"])
        self.assertFalse(payload["safety"]["plugin_cache_mutation_allowed"])

    def test_missing_historical_markers_fail_closed(self) -> None:
        repo, codex_home = self.make_repo("frontmatter-missing-markers")
        evidence_dir = repo / "docs_bilingual" / "memory"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "skills_usage_audit_reference_warning_resolution_2026-06-21.md").write_text(
            "# Evidence\n\nNo historical warning marker.\n",
            encoding="utf-8",
        )
        self.write_skill(codex_home / "skills", "valid", name="valid-skill", description="Valid current skill.")

        result = self.run_check(repo, codex_home)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["historical_issue"]["detected"])
        self.assertIn("historical_reference_warning_markers_missing", payload["errors"])


if __name__ == "__main__":
    unittest.main()
