import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_skills_audit_human_review_decision_record.py"
MEMORY = Path("docs_bilingual/memory")


FINAL_SUMMARY = """
# Skills Usage Audit 30-Day Summary

- Summary review state: `human_review_pending`
- Candidate generation state: `not_requested`
- Profile apply state: `not_authorized`
"""


def decision_record(
    *,
    outcome: str,
    summary_state: str,
    candidate_state: str,
    apply_state: str = "not_authorized",
    extra: str = "",
) -> str:
    return f"""
# Skills Usage Audit Human Review Decision

- Outcome: `{outcome}`
- Summary review state: `{summary_state}`
- Candidate generation state: `{candidate_state}`
- Profile apply state: `{apply_state}`
{extra}
"""


class SkillsAuditHumanReviewDecisionRecordCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: Path | str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")

    def write_final_summary(self, root: Path) -> None:
        self.write_file(root, MEMORY / "skills_usage_audit_30d_summary_2026-06-15-1059.md", FINAL_SUMMARY)

    def write_decision(self, root: Path, content: str, name: str = "skills_usage_audit_human_review_decision_2026-06-21.md") -> None:
        self.write_file(root, MEMORY / name, content)
        zh_name = name[:-3] + ".zh-CN.md"
        self.write_file(root, MEMORY / zh_name, content)

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

    def test_no_decision_record_is_valid_pending_state_without_candidate_artifacts(self) -> None:
        root = self.make_repo("skills-human-decision-none")
        self.write_final_summary(root)

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["decision_record_state"], "no_decision_record")
        self.assertIn("final_human_review_pending", payload["open_items"])
        self.assertTrue(payload["does_not_mutate_config"])
        self.assertTrue(payload["does_not_edit_plugin_cache"])
        self.assertTrue(payload["does_not_apply_profile"])

    def test_candidate_artifact_before_any_decision_record_is_blocked(self) -> None:
        root = self.make_repo("skills-human-decision-candidate-before-record")
        self.write_final_summary(root)
        self.write_file(root, MEMORY / "skills_usage_audit_profile_apply_candidate_2026-06-21.json", "{}")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("before any human-review decision record" in error for error in payload["errors"]))

    def test_review_pending_continue_monitoring_record_passes_without_candidate_or_apply(self) -> None:
        root = self.make_repo("skills-human-decision-pending")
        self.write_final_summary(root)
        self.write_decision(
            root,
            decision_record(
                outcome="review-pending + continue monitoring",
                summary_state="human_review_pending",
                candidate_state="not_requested",
            ),
        )

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["decision_record_state"], "review_pending_continue_monitoring_recorded")
        self.assertIn("closure_decision_pending", payload["open_items"])

    def test_closed_no_change_requires_summary_reviewed_and_blocks_candidate_artifacts(self) -> None:
        root = self.make_repo("skills-human-decision-closed-candidate-block")
        self.write_final_summary(root)
        self.write_decision(
            root,
            decision_record(
                outcome="summary-reviewed + closed-no-change",
                summary_state="summary-reviewed",
                candidate_state="not_requested",
            ),
        )
        self.write_file(root, MEMORY / "skills_profile_candidate_2026-06-21.md", "preview")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("closed-no-change" in error and "candidate artifacts" in error for error in payload["errors"]))

    def test_preview_only_candidate_requires_target_profile_and_review_notes(self) -> None:
        root = self.make_repo("skills-human-decision-preview-missing-fields")
        self.write_final_summary(root)
        self.write_decision(
            root,
            decision_record(
                outcome="summary-reviewed + preview-only candidate",
                summary_state="summary-reviewed",
                candidate_state="preview-only",
                extra="- target_profile: `core-dev`\n",
            ),
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("candidate review notes" in error for error in payload["errors"]))
        self.assertTrue(any("rollback path review notes" in error for error in payload["errors"]))
        self.assertTrue(any("validation plan review notes" in error for error in payload["errors"]))

    def test_preview_only_candidate_with_target_profile_review_notes_and_apply_blocked_passes(self) -> None:
        root = self.make_repo("skills-human-decision-preview-pass")
        self.write_final_summary(root)
        self.write_decision(
            root,
            decision_record(
                outcome="summary-reviewed + preview-only candidate",
                summary_state="summary-reviewed",
                candidate_state="preview-only",
                extra="\n".join(
                    [
                        "- target_profile: `core-dev`",
                        "- Candidate review notes: `Preview only candidate is needed for smaller default profile review.`",
                        "- Rollback path review notes: `Use the latest profile-helper rollback receipt before any apply.`",
                        "- Validation plan review notes: `Run startup smoke and skills warning triage after preview review.`",
                    ]
                ),
            ),
        )

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["decision_record_state"], "summary_reviewed_preview_only_candidate")
        self.assertIn("profile_apply_not_authorized", payload["open_items"])

    def test_decision_record_must_contain_exactly_one_outcome(self) -> None:
        root = self.make_repo("skills-human-decision-two-outcomes")
        self.write_final_summary(root)
        self.write_decision(
            root,
            """
# Skills Usage Audit Human Review Decision

- Outcome: `summary-reviewed + closed-no-change`
- Also considered: `review-pending + continue monitoring`
- Summary review state: `summary-reviewed`
- Candidate generation state: `not_requested`
- Profile apply state: `not_authorized`
""",
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("exactly one explicit allowed outcome" in error for error in payload["errors"]))

    def test_raw_paths_and_secrets_are_blocked_in_decision_record(self) -> None:
        root = self.make_repo("skills-human-decision-raw-path-secret")
        self.write_final_summary(root)
        self.write_decision(
            root,
            decision_record(
                outcome="review-pending + continue monitoring",
                summary_state="human_review_pending",
                candidate_state="not_requested",
                extra=r"- Review note: `C:\Users\lenovo\.codex\sessions\raw.json api_key=sk-test-secret-123456`",
            ),
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("raw_private_path_retained", "\n".join(payload["errors"]))
        self.assertIn("raw_secret_assignment_retained", "\n".join(payload["errors"]))

    def test_raw_transcript_excerpt_label_without_non_retention_language_is_blocked(self) -> None:
        root = self.make_repo("skills-human-decision-raw-excerpt")
        self.write_final_summary(root)
        self.write_decision(
            root,
            decision_record(
                outcome="review-pending + continue monitoring",
                summary_state="human_review_pending",
                candidate_state="not_requested",
                extra="- Raw transcript excerpt: `assistant said use full profile`",
            ),
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("raw_transcript_or_log_excerpt_retained" in error for error in payload["errors"]))

    def test_multiple_decision_records_fail_closed(self) -> None:
        root = self.make_repo("skills-human-decision-multiple")
        self.write_final_summary(root)
        content = decision_record(
            outcome="review-pending + continue monitoring",
            summary_state="human_review_pending",
            candidate_state="not_requested",
        )
        self.write_decision(root, content, name="skills_usage_audit_human_review_decision_2026-06-21.md")
        self.write_decision(root, content, name="skills_usage_audit_review_decision_2026-06-22.md")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("multiple canonical human-review decision records" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
