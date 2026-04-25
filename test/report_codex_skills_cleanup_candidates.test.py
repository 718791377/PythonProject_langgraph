import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "report_codex_skills_cleanup_candidates.py"


class CodexSkillsCleanupReportTest(unittest.TestCase):
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

    def write_registry(self, root: Path) -> None:
        self.write_file(
            root,
            "docs_bilingual/governance/codex_skills_profiles.registry.yaml",
            "version: 1\n"
            "settings:\n"
            "  description_limits:\n"
            "    user: 20\n"
            "    repo: 30\n"
            "  description_enforcement:\n"
            "    user: warning\n"
            "    repo: error\n"
            "duplicate_skill_policy:\n"
            "  preferred_sources:\n"
            "    gh-fix-ci: plugin\n"
            "  known_same_layer_exceptions:\n"
            "    - layer: repo\n"
            "      name_pattern: openspec-*\n"
            "      severity: warning\n"
            "      reason: Requires clean-clone OpenSpec evidence before cleanup.\n",
        )

    def write_skill(self, root: Path, relative_path: str, name: str, description: str) -> None:
        self.write_file(root, relative_path, f"---\nname: {name}\ndescription: {description}\n---\n\nBody\n")

    def run_report(
        self,
        root: Path,
        user_skills_root: Path | None = None,
        plugin_cache_root: Path | None = None,
        output: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--root",
            str(root),
            "--json",
            "--user-skills-root",
            str(user_skills_root or (root / "user-skills")),
            "--plugin-cache-root",
            str(plugin_cache_root or (root / "plugin-cache")),
        ]
        if output:
            cmd.extend(["--output", output])
        return subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_reports_openspec_nested_duplicate_as_deferred(self) -> None:
        root = self.make_root("cleanup-openspec")
        self.write_registry(root)
        self.write_skill(root, ".codex/skills/openspec-demo/SKILL.md", "openspec-demo", "Short repo")
        self.write_skill(
            root,
            ".codex/skills/openspec-demo/openspec-demo/SKILL.md",
            "openspec-demo",
            "Short repo",
        )

        result = self.run_report(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        matches = [
            item
            for item in payload["candidates"]
            if item["candidate_type"] == "openspec_nested_duplicate" and item["name"] == "openspec-demo"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["disposition"], "deferred_requires_clean_clone_evidence")
        self.assertFalse(matches[0]["cleanup_action_performed"])
        self.assertEqual(payload["summary"]["cleanup_actions_performed"], 0)

    def test_reports_user_plugin_duplicate_with_preferred_source(self) -> None:
        root = self.make_root("cleanup-gh")
        self.write_registry(root)
        user_root = root / "user-skills"
        plugin_root = root / "plugin-cache"
        self.write_skill(user_root, "gh-fix-ci/SKILL.md", "gh-fix-ci", "Short user")
        self.write_skill(
            plugin_root,
            "openai-curated/github/example/skills/gh-fix-ci/SKILL.md",
            "gh-fix-ci",
            "Short plugin",
        )

        result = self.run_report(root, user_root, plugin_root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        matches = [
            item
            for item in payload["candidates"]
            if item["candidate_type"] == "cross_layer_user_plugin_duplicate" and item["name"] == "gh-fix-ci"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["preferred_source"], "plugin")
        self.assertEqual(matches[0]["disposition"], "preferred_source_recorded_no_action")

    def test_output_file_is_written_without_mutating_skills(self) -> None:
        root = self.make_root("cleanup-output")
        self.write_registry(root)
        user_root = root / "user-skills"
        skill_path = user_root / "long/SKILL.md"
        self.write_skill(user_root, "long/SKILL.md", "long", "This user description is too long")
        before = skill_path.read_text(encoding="utf-8")

        result = self.run_report(root, user_root, output="docs_bilingual/governance/report.json")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        after = skill_path.read_text(encoding="utf-8")
        self.assertEqual(before, after)
        report_path = root / "docs_bilingual/governance/report.json"
        self.assertTrue(report_path.exists())
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["summary"]["cleanup_actions_performed"], 0)
        self.assertTrue(
            any(item["candidate_type"] == "user_long_description" for item in payload["candidates"])
        )


if __name__ == "__main__":
    unittest.main()
