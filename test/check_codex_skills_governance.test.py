import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_codex_skills_governance.py"


class CodexSkillsGovernanceCheckTest(unittest.TestCase):
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

    def write_minimal_docs(self, root: Path, registry_profiles: str | None = None) -> None:
        self.write_file(
            root,
            "docs_bilingual/governance/codex_user_level_skills_governance_policy.md",
            "---\ndoc_id: codex_user_level_skills_governance_policy\nlang: en\ndoc_class: governance\nstatus: active\n---\n# Policy\n",
        )
        self.write_file(
            root,
            "docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md",
            "---\ndoc_id: codex_user_level_skills_governance_policy\nlang: zh-CN\ndoc_class: governance\nstatus: active\n---\n# ??\n",
        )
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: codex_user_level_skills_governance_policy\n"
            "    doc_class: governance\n"
            "    status: active\n"
            "    canonical_path: docs_bilingual/governance/codex_user_level_skills_governance_policy.md\n"
            "    zh_cn_path: docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md\n",
        )
        self.write_file(
            root,
            "docs_bilingual/governance/codex_skills_profiles.registry.yaml",
            registry_profiles
            or "version: 1\n"
            "settings:\n"
            "  description_limits:\n"
            "    user: 20\n"
            "    repo: 30\n"
            "profiles:\n"
            "  core:\n"
            "    description: Core.\n"
            "  browser:\n"
            "    description: Browser.\n"
            "projects:\n"
            "  D:\\sample:\n"
            "    profiles: [core, browser]\n",
        )

    def write_skill(self, root: Path, relative_path: str, name: str, description: str) -> None:
        self.write_file(root, relative_path, f"---\nname: {name}\ndescription: {description}\n---\n\nBody\n")

    def run_check(
        self,
        root: Path,
        user_skills_root: Path | None = None,
        include_plugins: bool = False,
        plugin_cache_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        user_root = user_skills_root or (root / "user-skills")
        command = [
            sys.executable,
            str(SCRIPT_PATH),
            "--root",
            str(root),
            "--json",
            "--user-skills-root",
            str(user_root),
        ]
        if include_plugins:
            command.extend(["--plugin-cache-root", str(plugin_cache_root or (root / "plugin-cache"))])
        else:
            command.append("--no-plugins")
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_for_minimal_policy_registry_and_unique_skills(self) -> None:
        root = self.make_root("skills-gov-pass")
        self.write_minimal_docs(root)
        self.write_skill(root, ".codex/skills/one/SKILL.md", "one", "Short repo")
        user_root = root / "user-skills"
        self.write_skill(user_root, "two/SKILL.md", "two", "Short user")

        result = self.run_check(root, user_root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "codex_skills_governance")
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_fails_for_same_layer_duplicate_and_long_description(self) -> None:
        root = self.make_root("skills-gov-fail")
        self.write_minimal_docs(root)
        self.write_skill(root, ".codex/skills/one/SKILL.md", "dup", "Short repo")
        self.write_skill(root, ".codex/skills/two/SKILL.md", "dup", "Short repo")
        user_root = root / "user-skills"
        self.write_skill(user_root, "long/SKILL.md", "long", "This user description is too long")

        result = self.run_check(root, user_root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Duplicate skill name `dup`" in error for error in payload["errors"]))
        self.assertTrue(any("description length" in error for error in payload["errors"]))

    def test_fails_for_unknown_project_profile(self) -> None:
        root = self.make_root("skills-gov-profile-fail")
        self.write_minimal_docs(
            root,
            "version: 1\n"
            "profiles:\n"
            "  core:\n"
            "    description: Core.\n"
            "projects:\n"
            "  D:\\sample:\n"
            "    profiles: [core, missing]\n",
        )
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("unknown profile `missing`" in error for error in payload["errors"]))

    def test_reports_known_same_layer_exception_as_deferred_cleanup(self) -> None:
        root = self.make_root("skills-gov-deferred")
        self.write_minimal_docs(
            root,
            "version: 1\n"
            "profiles:\n"
            "  core:\n"
            "    description: Core.\n"
            "projects:\n"
            "  D:\\sample:\n"
            "    profiles: [core]\n"
            "duplicate_skill_policy:\n"
            "  known_same_layer_exceptions:\n"
            "    - layer: repo\n"
            "      name_pattern: openspec-*\n"
            "      severity: warning\n"
            "      reason: Requires clean-clone OpenSpec evidence before cleanup.\n",
        )
        self.write_skill(root, ".codex/skills/openspec-demo/SKILL.md", "openspec-demo", "Short repo")
        self.write_skill(
            root,
            ".codex/skills/openspec-demo/openspec-demo/SKILL.md",
            "openspec-demo",
            "Short repo",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertEqual(payload["counts"]["deferred"], 1)
        self.assertTrue(any("openspec-demo" in item for item in payload["deferred"]))

    def test_reports_plugin_same_layer_duplicate_as_warning(self) -> None:
        root = self.make_root("skills-gov-plugin-duplicate")
        self.write_minimal_docs(root)
        plugin_root = root / "plugin-cache"
        self.write_skill(
            plugin_root,
            "openai-bundled/chrome/0.1.7/skills/chrome/SKILL.md",
            "Chrome",
            "Browser automation for Chrome.",
        )
        self.write_skill(
            plugin_root,
            "openai-bundled/chrome/0.1.7-copy/skills/chrome/SKILL.md",
            "Chrome",
            "Browser automation for Chrome.",
        )

        result = self.run_check(root, include_plugins=True, plugin_cache_root=plugin_root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertTrue(any("Plugin duplicate skill name `Chrome`" in item for item in payload["warnings"]))

    def test_fails_for_repo_or_user_codex_frontmatter_incompatibility(self) -> None:
        root = self.make_root("skills-gov-codex-incompat")
        self.write_minimal_docs(root)
        self.write_skill(root, ".codex/skills/too-long/SKILL.md", "x" * 65, "Short repo")
        user_root = root / "user-skills"
        self.write_file(user_root, "missing-desc/SKILL.md", "---\nname: missing-desc\n---\nBody\n")

        result = self.run_check(root, user_root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("name_too_long" in error for error in payload["errors"]))
        self.assertTrue(any("missing_description" in error for error in payload["errors"]))

    def test_plugin_codex_frontmatter_incompatibility_is_report_only(self) -> None:
        root = self.make_root("skills-gov-plugin-incompat")
        self.write_minimal_docs(root)
        plugin_root = root / "plugin-cache"
        self.write_skill(
            plugin_root,
            "openai-curated/twilio/hash/skills/twilio-enterprise-knowledge/SKILL.md",
            "twilio-enterprise-knowledge",
            "D" * 1030,
        )

        result = self.run_check(root, include_plugins=True, plugin_cache_root=plugin_root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertTrue(any("description_too_long" in warning for warning in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
