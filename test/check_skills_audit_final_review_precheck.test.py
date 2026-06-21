import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_skills_audit_final_review_precheck.py"
MEMORY = Path("docs_bilingual/memory")


FINAL_SUMMARY = """
# Skills Usage Audit 30-Day Summary

## Audit window and state

- Summary review state: `human_review_pending`
- Candidate generation state: `not_requested`
- Profile apply state: `not_authorized`

## Noise and manual review

- Noise review status: `review_required`
- Raw noise tokens retained: `False`
- Manual evidence files requested: `0`
- Manual conflict review status: `no_manual_conflict_or_exception_notes`
- Conflict or exception count: `0`
- Conflict disposition required: `False`
"""


PRECHECK_EVIDENCE = """
# Skills Usage Audit Review-Pending Continuation

## Noise false-positive pre-review

Machine evidence supports closing the script-level noise item for this audit round:

- Raw noise tokens are not retained in long-term evidence.
- The field contract reports zero `noise_review` violations.

## Manual conflict and exception pre-review

Machine evidence supports closing the script-level manual-conflict item for this audit round:

- Manual conflict review status: `no_manual_conflict_or_exception_notes`.
- Conflict or exception count: `0`.
- The field contract reports zero `manual_evidence` violations.

## Non-actions

- Did not mark the summary as `summary-reviewed`.
- Did not generate candidate JSON or candidate Markdown.
- Did not run profile apply.
"""


class SkillsAuditFinalReviewPrecheckTest(unittest.TestCase):
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

    def write_required_files(
        self,
        root: Path,
        *,
        final_summary: str = FINAL_SUMMARY,
        precheck_evidence: str | None = PRECHECK_EVIDENCE,
    ) -> None:
        self.write_file(root, MEMORY / "skills_usage_audit_30d_summary_2026-06-15-1059.md", final_summary)
        if precheck_evidence is not None:
            self.write_file(
                root,
                MEMORY / "skills_usage_audit_review_pending_continuation_2026-06-21-0523.md",
                precheck_evidence,
            )

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

    def test_machine_precheck_allows_review_pending_monitoring_without_apply(self) -> None:
        root = self.make_repo("skills-final-precheck-pass")
        self.write_required_files(root)

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["decision_state"], "review_pending_continue_monitoring")
        self.assertTrue(payload["precheck"]["noise_review_machine_prechecked"])
        self.assertTrue(payload["precheck"]["manual_conflict_machine_prechecked"])
        self.assertEqual(payload["precheck"]["noise_review_violation_count"], 0)
        self.assertEqual(payload["precheck"]["manual_evidence_violation_count"], 0)
        self.assertTrue(payload["does_not_mutate_config"])
        self.assertTrue(payload["does_not_edit_plugin_cache"])
        self.assertTrue(payload["does_not_apply_profile"])
        self.assertIn("final_human_review_pending", payload["open_items"])

    def test_candidate_artifact_before_summary_review_is_blocked(self) -> None:
        root = self.make_repo("skills-final-precheck-candidate-blocked")
        self.write_required_files(root)
        self.write_file(root, MEMORY / "skills_profile_candidate_2026-06-21.json", "{}")

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("profile candidate artifacts exist" in error for error in payload["errors"]))

    def test_missing_precheck_evidence_fails_closed(self) -> None:
        root = self.make_repo("skills-final-precheck-missing")
        self.write_required_files(root, precheck_evidence=None)

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("no retained sanitized precheck evidence" in error for error in payload["errors"]))

    def test_precheck_without_manual_violation_count_fails_closed(self) -> None:
        root = self.make_repo("skills-final-precheck-incomplete")
        self.write_required_files(
            root,
            precheck_evidence=PRECHECK_EVIDENCE.replace(
                "The field contract reports zero `manual_evidence` violations.",
                "The manual evidence contract was reviewed.",
            ),
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("no retained sanitized precheck evidence" in error for error in payload["errors"]))

    def test_final_summary_must_keep_profile_apply_unauthorized(self) -> None:
        root = self.make_repo("skills-final-precheck-apply-blocked")
        self.write_required_files(
            root,
            final_summary=FINAL_SUMMARY.replace(
                "Profile apply state: `not_authorized`",
                "Profile apply state: `approved-to-apply`",
            ),
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("not_authorized" in error for error in payload["errors"]))

    def test_manual_conflict_count_must_be_zero(self) -> None:
        root = self.make_repo("skills-final-precheck-manual-count")
        self.write_required_files(
            root,
            final_summary=FINAL_SUMMARY.replace(
                "Conflict or exception count: `0`",
                "Conflict or exception count: `1`",
            ),
        )

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Conflict or exception count" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
