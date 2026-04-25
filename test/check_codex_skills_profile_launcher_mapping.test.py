import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_codex_skills_profile_launcher_mapping.py"


PROFILES = ["core", "browser", "web", "github", "full", "openspec", "orchestration"]

BASE_ENTRIES: dict[str, dict[str, Any]] = {
    "core": {
        "alias": "codex-ohmy-core",
        "lifecycle": "future_optional",
        "base_command": "codex-ohmy",
        "purpose": "Reduced default profile for non-web work.",
        "profile_set": ["core"],
        "plugin_policy": "no_vercel_required",
        "reduced_default": True,
        "default": True,
        "broad_plugin_discovery": False,
    },
    "browser": {
        "alias": "codex-ohmy-browser",
        "lifecycle": "future_optional",
        "base_command": "codex-ohmy",
        "purpose": "Browser automation profile.",
        "profile_set": ["core", "browser", "orchestration"],
        "plugin_policy": "preserve_vercel_bundle_until_fine_grained_filtering",
        "preserve_plugin_skills": [
            "agent-browser",
            "agent-browser-verify",
            "verification",
            "investigation-mode",
        ],
        "default": False,
        "broad_plugin_discovery": False,
    },
    "web": {
        "alias": "codex-ohmy-web",
        "lifecycle": "future_optional",
        "base_command": "codex-ohmy",
        "purpose": "Web and deployment profile.",
        "profile_set": ["core", "web"],
        "plugin_policy": "preserve_vercel_bundle_until_fine_grained_filtering",
        "default": False,
        "broad_plugin_discovery": False,
    },
    "github": {
        "alias": "codex-ohmy-github",
        "lifecycle": "future_optional",
        "base_command": "codex-ohmy",
        "purpose": "GitHub workflow profile.",
        "profile_set": ["core", "github"],
        "plugin_policy": "enable_github_plugin_when_github_workflow_is_active",
        "default": False,
        "broad_plugin_discovery": False,
    },
    "full": {
        "alias": "codex-ohmy-full",
        "lifecycle": "temporary_troubleshooting",
        "base_command": "codex-ohmy",
        "purpose": "Temporary broad discovery profile.",
        "profile_set": ["core", "browser", "web", "github", "openspec", "orchestration", "full"],
        "plugin_policy": "broad_discovery_only",
        "default": False,
        "broad_plugin_discovery": True,
    },
}


class CodexSkillsProfileLauncherMappingCheckTest(unittest.TestCase):
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

    def render_scalar(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, list):
            return "[" + ", ".join(str(item) for item in value) + "]"
        return str(value)

    def render_registry(
        self,
        *,
        overrides: dict[str, dict[str, Any]] | None = None,
        omit_aliases: set[str] | None = None,
    ) -> str:
        overrides = overrides or {}
        omit_aliases = omit_aliases or set()
        lines = ["version: 1", "profiles:"]
        for profile in PROFILES:
            lines.extend([f"  {profile}:", f"    description: {profile} profile."])
        lines.extend(
            [
                "launcher_mapping:",
                "  status: documented_only",
                "  config_mutation: forbidden",
                "  installed_wrapper_mutation: forbidden",
                "  base_command: codex-ohmy",
                "  default_profile: core",
                "  future_aliases_installed: false",
                "  aliases:",
            ]
        )
        for profile, base_entry in BASE_ENTRIES.items():
            if profile in omit_aliases:
                continue
            entry = {**base_entry, **overrides.get(profile, {})}
            lines.append(f"    {profile}:")
            for key, value in entry.items():
                lines.append(f"      {key}: {self.render_scalar(value)}")
        return "\n".join(lines) + "\n"

    def write_docs_registry(self, root: Path) -> None:
        self.write_file(
            root,
            "docs_bilingual/governance/codex_skills_profile_launcher_mapping.md",
            "---\ndoc_id: codex_skills_profile_launcher_mapping\nlang: en\n---\n# Mapping\n",
        )
        self.write_file(
            root,
            "docs_bilingual/governance/codex_skills_profile_launcher_mapping.zh-CN.md",
            "---\ndoc_id: codex_skills_profile_launcher_mapping\nlang: zh-CN\n---\n# 映射\n",
        )
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: codex_skills_profile_launcher_mapping\n"
            "    doc_class: governance\n"
            "    status: active\n"
            "    canonical_path: docs_bilingual/governance/codex_skills_profile_launcher_mapping.md\n"
            "    zh_cn_path: docs_bilingual/governance/codex_skills_profile_launcher_mapping.zh-CN.md\n",
        )

    def write_registry(self, root: Path, content: str) -> None:
        self.write_file(root, "docs_bilingual/governance/codex_skills_profiles.registry.yaml", content)

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_for_valid_minimal_registry_and_docs_registry(self) -> None:
        root = self.make_root("profile-launcher-pass")
        self.write_docs_registry(root)
        self.write_registry(root, self.render_registry())

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "codex_skills_profile_launcher_mapping")
        self.assertEqual(payload["counts"]["launcher_mappings"], 5)
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_fails_for_missing_required_alias(self) -> None:
        root = self.make_root("profile-launcher-missing")
        self.write_docs_registry(root)
        self.write_registry(root, self.render_registry(omit_aliases={"github"}))

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("launcher_mapping.aliases is missing required profile `github`" in error for error in payload["errors"])
        )

    def test_fails_when_browser_profile_does_not_preserve_required_plugin_skills(self) -> None:
        root = self.make_root("profile-launcher-browser")
        self.write_docs_registry(root)
        self.write_registry(
            root,
            self.render_registry(
                overrides={
                    "browser": {
                        "plugin_policy": "plugin_bundle_disabled",
                        "preserve_plugin_skills": ["agent-browser"],
                    }
                }
            ),
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("`browser` must preserve Vercel bundle behavior" in error for error in payload["errors"]))
        self.assertTrue(
            any("`browser` must preserve plugin skill `agent-browser-verify`" in error for error in payload["errors"])
        )

    def test_fails_when_core_requires_vercel_or_broad_plugin_discovery(self) -> None:
        root = self.make_root("profile-launcher-core")
        self.write_docs_registry(root)
        self.write_registry(
            root,
            self.render_registry(
                overrides={
                    "core": {
                        "plugin_policy": "require_vercel_bundle",
                        "broad_plugin_discovery": True,
                    }
                }
            ),
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("`core` must not require Vercel-specific plugin policy" in error for error in payload["errors"]))
        self.assertTrue(any("`core` must not use broad plugin discovery" in error for error in payload["errors"]))

    def test_fails_when_full_is_default_or_not_temporary(self) -> None:
        root = self.make_root("profile-launcher-full")
        self.write_docs_registry(root)
        self.write_registry(
            root,
            self.render_registry(
                overrides={
                    "full": {
                        "lifecycle": "future_optional",
                        "default": True,
                    }
                }
            ),
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("`full` must be temporary_troubleshooting" in error for error in payload["errors"]))
        self.assertTrue(any("`full` must not be default" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
