import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_skills_audit_zh_evidence_encoding.py"
MEMORY = Path("docs_bilingual/memory")


GOOD_ZH = (
    "---\n"
    "lang: zh-CN\n"
    "---\n"
    "# Skills Usage Audit \u8bc1\u636e\u8bb0\u5f55\n\n"
    "\u672c\u8bb0\u5f55\u4fdd\u5b58\u8131\u654f\u540e\u7684\u5ba1\u8ba1\u8bc1\u636e\uff0c\u53ea\u5305\u542b\u805a\u5408\u8ba1\u6570\u3001\u590d\u6838\u7ed3\u8bba\u3001\u95e8\u7981\u72b6\u6001\u548c\u540e\u7eed\u52a8\u4f5c\u3002\n"
    "\u5f53\u524d\u6458\u8981\u4fdd\u6301\u4eba\u5de5\u590d\u6838\u5f85\u5b9a\uff0c\u5019\u9009\u751f\u6210\u672a\u8bf7\u6c42\uff0cprofile apply \u672a\u6388\u6743\u3002\n"
)


class SkillsAuditZhEvidenceEncodingCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_memory(self, root: Path, name: str, content: str, *, encoding: str = "utf-8") -> None:
        path = root / MEMORY / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding=encoding)

    def run_check(self, root: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=run_env,
        )

    def git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        git = shutil.which("git") or shutil.which("git.exe")
        if git is None:
            self.skipTest("git executable is required for changed legacy evidence detection")
        result = subprocess.run([git, *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def init_git_repo(self, root: Path) -> None:
        self.git(root, "init", "-b", "main")
        self.git(root, "config", "user.email", "skills-audit-test@example.invalid")
        self.git(root, "config", "user.name", "Skills Audit Test")
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "initial evidence")

    def test_init_git_repo_uses_main_even_when_git_default_branch_differs(self) -> None:
        root = self.make_repo("skills-audit-zh-non-main-default")
        self.write_memory(root, "skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md", GOOD_ZH)
        git_config = root / "gitconfig"
        git_config.write_text("[init]\n\tdefaultBranch = trunk\n", encoding="utf-8")

        with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(git_config)}):
            self.init_git_repo(root)

        self.assertEqual(self.git(root, "branch", "--show-current").stdout.strip(), "main")

    def test_current_clean_zh_evidence_passes_while_legacy_warns(self) -> None:
        root = self.make_repo("skills-audit-zh-clean")
        self.write_memory(root, "skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md", GOOD_ZH)
        self.write_memory(
            root,
            "skills_usage_audit_warning_triage_2026-05-22_1337.zh-CN.md",
            "# Skills Usage Audit ????????\n\n???? ???? ????",
        )

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["protected_findings"], 0)
        self.assertEqual(payload["counts"]["legacy_findings"], 1)
        self.assertTrue(payload["warnings"])

    def test_current_repeated_question_marks_fail_closed(self) -> None:
        root = self.make_repo("skills-audit-zh-current-qmarks")
        self.write_memory(
            root,
            "skills_usage_audit_evidence_index_2026-06-21-1149.zh-CN.md",
            "# Skills Usage Audit ????\n\n???? ???? ????",
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("repeated_ascii_question_mark_placeholder" in error for error in payload["errors"]))

    def test_current_replacement_character_fails_closed(self) -> None:
        root = self.make_repo("skills-audit-zh-current-replacement")
        self.write_memory(
            root,
            "skills_usage_audit_warning_triage_2026-06-22-0900.zh-CN.md",
            GOOD_ZH + "\n\ufffd",
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("unicode_replacement_character" in error for error in payload["errors"]))

    def test_active_current_mojibake_sentinel_fails_closed(self) -> None:
        root = self.make_repo("skills-audit-zh-current-sentinel")
        self.write_memory(root, "skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md", GOOD_ZH)
        self.write_memory(
            root,
            "skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md",
            GOOD_ZH + "\n" + "\u7480\ufe40\u61a1",
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("known_utf8_as_legacy_codepage_mojibake_marker" in error for error in payload["errors"]))

    def test_edited_legacy_target_fails_closed(self) -> None:
        root = self.make_repo("skills-audit-zh-edited-legacy")
        self.write_memory(root, "skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md", GOOD_ZH)
        legacy_name = "skills_usage_audit_warning_triage_2026-05-22_1337.zh-CN.md"
        self.write_memory(root, legacy_name, GOOD_ZH)
        self.init_git_repo(root)
        self.write_memory(root, legacy_name, "# Skills Usage Audit ????\n\n???? ???? ????")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("changed_or_new_target_file" in error for error in payload["errors"]))


    def test_gitlab_default_branch_merge_commit_uses_second_parent_base(self) -> None:
        root = self.make_repo("skills-audit-zh-gitlab-main-merge")
        self.write_memory(root, "skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md", GOOD_ZH)
        legacy_name = "skills_usage_audit_warning_triage_2026-06-13-1234.zh-CN.md"
        self.write_memory(root, legacy_name, GOOD_ZH)
        self.init_git_repo(root)

        self.git(root, "checkout", "-b", "feature")
        self.write_memory(root, legacy_name, "# Skills Usage Audit ????\n\n???? ???? ????")
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "add legacy mojibake payload")

        self.git(root, "checkout", "main")
        self.write_memory(root, "skills_usage_audit_warning_triage_2026-06-21-0900.zh-CN.md", GOOD_ZH)
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "advance main")
        self.git(root, "merge", "--no-ff", "feature", "-m", "Merge branch 'feature' into 'main'")
        merge_head = self.git(root, "rev-parse", "HEAD").stdout.strip()
        self.git(root, "checkout", "--detach", merge_head)

        result = self.run_check(
            root,
            env={
                "GITLAB_CI": "true",
                "CI_DEFAULT_BRANCH": "main",
                "CI_COMMIT_BRANCH": "main",
            },
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["protected_findings"], 0)
        legacy_path = str(MEMORY / "skills_usage_audit_warning_triage_2026-06-13-1234.zh-CN.md").replace("\\", "/")
        main_side_path = str(MEMORY / "skills_usage_audit_warning_triage_2026-06-21-0900.zh-CN.md").replace("\\", "/")
        self.assertNotIn(legacy_path, payload["changed_or_new_target_paths"])
        self.assertIn(main_side_path, payload["changed_or_new_target_paths"])

    def test_non_target_markdown_is_ignored(self) -> None:
        root = self.make_repo("skills-audit-zh-non-target")
        self.write_memory(root, "skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md", GOOD_ZH)
        non_target = root / MEMORY / "not_skills_usage_audit_2026-06-21.zh-CN.md"
        non_target.parent.mkdir(parents=True, exist_ok=True)
        non_target.write_text("# Not target ????\n\n????\n", encoding="utf-8")

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["protected_findings"], 0)

    def test_missing_zh_evidence_fails(self) -> None:
        root = self.make_repo("skills-audit-zh-missing")
        (root / MEMORY).mkdir(parents=True)

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("no skills_usage_audit" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
