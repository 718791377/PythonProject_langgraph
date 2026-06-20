import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "repair_codex_skill_frontmatter.py"


class RepairCodexSkillFrontmatterTest(unittest.TestCase):
    maxDiff = None

    def make_home(self, name: str) -> Path:
        base = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        home = base / "codex-home"
        home.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(base, ignore_errors=True))
        return home

    def write_skill(self, root: Path, relative_path: str, *, name: str, description: str, bom: bool = False) -> Path:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        text = f"---\nname: {name}\ndescription: {description}\n---\nBody must stay unchanged.\n"
        if bom:
            text = "\ufeff" + text
        path.write_text(text, encoding="utf-8")
        return path

    def run_json(self, *args: str, check: bool = True) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc
        if check and proc.returncode != 0:
            self.fail(json.dumps(payload, ensure_ascii=False, indent=2) + "\n" + proc.stderr)
        return proc.returncode, payload

    def test_audit_and_plan_are_read_only_and_include_plugins_by_default(self) -> None:
        home = self.make_home("audit-plan")
        self.write_skill(home / "skills", "very-long-user/SKILL.md", name="user-" + "long-" * 20, description="Short.")
        self.write_skill(home / "plugins" / "cache", "twilio/hash/skills/twilio-enterprise-knowledge/SKILL.md", name="twilio-enterprise-knowledge", description="D" * 1030)

        code, audit = self.run_json("audit", "--codex-home", str(home))
        self.assertEqual(code, 0)
        self.assertTrue(audit["ok"])
        self.assertEqual(audit["summary"]["invalid_total"], 2)
        self.assertEqual(audit["summary"]["by_error"], {"description_too_long": 1, "name_too_long": 1})
        self.assertFalse(audit["mutates_user_level_state"])

        code, plan = self.run_json("plan", "--codex-home", str(home))
        self.assertEqual(code, 0)
        self.assertEqual(plan["planned_action_count"], 2)
        self.assertFalse(plan["apply_performed"])
        self.assertFalse(plan["mutates_user_level_state"])
        self.assertTrue(any(item["plugin_cache_edit"] for item in plan["actions"]))

    def test_apply_requires_confirmation_then_writes_backup_manifest_and_preserves_body(self) -> None:
        home = self.make_home("apply")
        user_skill = self.write_skill(
            home / "skills",
            "too-long/SKILL.md",
            name="this-user-skill-name-is-far-too-long-for-codex-frontmatter-loader",
            description="Short.",
            bom=True,
        )
        plugin_skill = self.write_skill(
            home / "plugins" / "cache",
            "twilio/hash/skills/twilio-enterprise-knowledge/SKILL.md",
            name="twilio-enterprise-knowledge",
            description="D" * 1030,
        )

        code, blocked = self.run_json("apply", "--codex-home", str(home), check=False)
        self.assertEqual(code, 3)
        self.assertIn("operator_confirmation_required", blocked["blockers"])

        code, applied = self.run_json("apply", "--codex-home", str(home), "--operator-confirmation")
        self.assertEqual(code, 0)
        self.assertTrue(applied["ok"])
        self.assertTrue(applied["apply_performed"])
        self.assertEqual(applied["touched_count"], 2)
        self.assertTrue(Path(applied["rollback_manifest_path"]).exists())
        self.assertTrue(Path(applied["receipt_path"]).exists())
        self.assertEqual(applied["post_summary"]["invalid_total"], 0)

        user_text = user_skill.read_text(encoding="utf-8")
        plugin_text = plugin_skill.read_text(encoding="utf-8")
        self.assertFalse(user_text.startswith("\ufeff"))
        self.assertIn("Body must stay unchanged.", user_text)
        self.assertIn("Body must stay unchanged.", plugin_text)
        self.assertLessEqual(len(next(line.split(":", 1)[1].strip() for line in user_text.splitlines() if line.startswith("name:"))), 64)
        self.assertLessEqual(len(next(line.split(":", 1)[1].strip() for line in plugin_text.splitlines() if line.startswith("description:"))), 1024)

        manifest = json.loads(Path(applied["rollback_manifest_path"]).read_text(encoding="utf-8"))
        self.assertTrue(any(item["plugin_cache_edit"] for item in manifest["touched"]))
        self.assertFalse(manifest["mutated_config_toml"])
        self.assertFalse(manifest["profile_apply_performed"])
        self.assertFalse(manifest["hard_load_or_disable_plugin_performed"])
        self.assertFalse(manifest["skill_body_edits_intended"])


if __name__ == "__main__":
    unittest.main()
