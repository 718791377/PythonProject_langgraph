import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_skills_audit_final_review_state.py"
MEMORY = Path("docs_bilingual/memory")


class SkillsAuditFinalReviewStateCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_required_files(
        self,
        root: Path,
        *,
        summary_review_state: str = "human_review_pending",
        candidate_state: str = "not_requested",
        apply_state: str = "not_authorized",
        final_extra: str = "",
    ) -> None:
        final_summary = "\n".join(
            [
                "# Skills Usage Audit 30-Day Summary",
                "",
                "- Summary review state: `" + summary_review_state + "`",
                "- Candidate generation state: `" + candidate_state + "`",
                "- Profile apply state: `" + apply_state + "`",
                "- Manual review required: `True`",
                final_extra,
            ]
        )
        self.write_file(root, MEMORY / "skills_usage_audit_30d_summary_2026-06-15-1059.md", final_summary)
        self.write_file(root, MEMORY / "skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md", final_summary)
        decision_template = "\n".join(
            [
                "# Skills Usage Audit Human Review Decision Template",
                "",
                "- `summary-reviewed + closed-no-change`",
                "- `summary-reviewed + preview-only candidate`",
                "- `review-pending + continue monitoring`",
            ]
        )
        self.write_file(root, MEMORY / "skills_usage_audit_human_review_decision_template_2026-06-15.md", decision_template)
        self.write_file(root, MEMORY / "skills_usage_audit_human_review_decision_template_2026-06-15.zh-CN.md", decision_template)
        continuation = "\n".join(
            [
                "# Skills Usage Audit Review-Pending Continuation",
                "",
                "- Final 30-day summary: `" + summary_review_state + "`",
                "- Candidate generation: `" + candidate_state + "`",
                "- Profile apply: `" + apply_state + "`",
            ]
        )
        self.write_file(root, MEMORY / "skills_usage_audit_review_pending_continuation_2026-06-18-0313.md", continuation)
        self.write_file(root, MEMORY / "skills_usage_audit_review_pending_continuation_2026-06-18-0313.zh-CN.md", continuation)
        index = "\n".join(
            [
                "# Skills Usage Audit Evidence Index",
                "",
                "- Final 30-day summary state: `" + summary_review_state + "`",
                "- Candidate generation state: `" + candidate_state + "`",
                "- Profile apply state: `" + apply_state + "`",
            ]
        )
        self.write_file(root, MEMORY / "skills_usage_audit_evidence_index_2026-06-18-0313.md", index)
        self.write_file(root, MEMORY / "skills_usage_audit_evidence_index_2026-06-18-0313.zh-CN.md", index)

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_review_pending_continuation_is_allowed_without_candidate_or_apply(self) -> None:
        root = self.make_repo("skills-final-review-pending")
        self.write_required_files(root)

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["decision_state"], "review_pending_continue_monitoring")
        self.assertTrue(payload["does_not_mutate_config"])
        self.assertTrue(payload["does_not_edit_plugin_cache"])
        self.assertTrue(payload["does_not_apply_profile"])
        self.assertIn("final_human_review_pending", payload["open_items"])
        self.assertEqual(payload["candidate_artifacts"], [])

    def test_candidate_artifact_before_summary_review_is_blocked(self) -> None:
        root = self.make_repo("skills-final-review-candidate-blocked")
        self.write_required_files(root)
        self.write_file(root, MEMORY / "skills_usage_audit_profile_apply_candidate_2026-06-18.md", "preview\n")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("profile candidate artifacts exist" in error for error in payload["errors"]))

    def test_summary_reviewed_requires_explicit_outcome(self) -> None:
        root = self.make_repo("skills-final-review-reviewed-missing-outcome")
        self.write_required_files(root, summary_review_state="summary-reviewed")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("summary-reviewed state requires an explicit outcome" in error for error in payload["errors"]))

    def test_summary_reviewed_closed_no_change_with_apply_still_blocked_passes(self) -> None:
        root = self.make_repo("skills-final-review-closed-no-change")
        self.write_required_files(
            root,
            summary_review_state="summary-reviewed",
            final_extra="Decision: summary-reviewed + closed-no-change",
        )

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["decision_state"], "summary_reviewed")
        self.assertEqual(payload["states"]["final_summary"]["profile_apply_state"], "not_authorized")

    def test_missing_final_summary_fails_closed(self) -> None:
        root = self.make_repo("skills-final-review-missing-summary")
        self.write_required_files(root)
        (root / MEMORY / "skills_usage_audit_30d_summary_2026-06-15-1059.md").unlink()

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("required final review evidence file is missing" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
