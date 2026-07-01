import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_skills_audit_cadence_contract.py"
MEMORY = Path("docs_bilingual/memory")
PLAN_EN = Path("docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md")


PLAN_EN_TEXT = """
# Codex Skills Usage Audit Plan

Use a fixed cadence so the one-month audit does not drift.

| Cadence item | Date or trigger | Repeat count |
| --- | --- | ---: |
| Day 0 baseline | 2026-05-16 | 1 |
| Weekly audit | 2026-05-23, 2026-05-30, 2026-06-06, 2026-06-13 | 4 |
| Day 30 final audit | 2026-06-15 | 1 |
| Warning triage | After each new `2% skills context budget` warning | Event-triggered, one narrow run per new warning |

Standard scheduled audit repeats are therefore fixed at 6 runs total: 1 baseline, 4 weekly runs, and 1 final 30-day run.
Warning triage and late recovery are exception/event-triggered paths and are not assigned a fixed repeat count.
The original audit end date is 2026-06-15. Runs after that date are post-final monitoring only.
"""


PLAN_ZH_TEXT = """
# Codex Skills Usage Audit 计划

为避免一个月 audit 过程中偏离，使用固定节奏。

| 节奏项 | 日期或触发条件 | 重复次数 |
| --- | --- | ---: |
| Day 0 baseline | 2026-05-16 | 1 |
| Weekly audit | 2026-05-23、2026-05-30、2026-06-06、2026-06-13 | 4 |
| Day 30 final audit | 2026-06-15 | 1 |
| Warning triage | 每次新的 `2% skills context budget` warning 之后 | 事件触发 |

因此，标准计划内审计重复次数固定为 6 次：1 次 baseline、4 次 weekly、1 次 final 30-day run。
Warning triage 与漏跑补跑属于异常/事件触发路径，不分配固定重复次数。
该日期之后的运行仅属于 post-final monitoring。
"""


FINAL_SUMMARY_TEXT = """
# Skills Usage Audit 30-Day Summary

- Since: `2026-05-16T03:24:08.085668+00:00`
- Until: `2026-06-15T03:24:08.085668+00:00`
- Days: `30`
- Profile apply allowed: `False`
"""


INDEX_TEXT = """
# Skills Usage Audit Evidence Index 2026-06-18 03:13 CST

## Cadence lock summary

- Original audit window: `2026-05-16` through `2026-06-15`.
- Scheduled repeat count: `6` total planned runs.
- Scheduled run shape: Day 0 baseline `1`, weekly evidence `4`, Day 30 final evidence `1`.
- Scheduled frequency: baseline once, weekly evidence every 7 days, final evidence once on 2026-06-15.
- Weekly evidence dates: `2026-05-23`, `2026-05-30`, `2026-06-06`, `2026-06-13`.
- Warning triage cadence: event-triggered only, one narrow-window run after each new warning event, no fixed repeat count.
- Post-final runs after 2026-06-15: monitoring evidence only; they do not reopen the 30-day window and do not authorize profile apply.
"""


class SkillsAuditCadenceContractCheckTest(unittest.TestCase):
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
        plan_en: str = PLAN_EN_TEXT,
        plan_zh: str = PLAN_ZH_TEXT,
        final_summary: str = FINAL_SUMMARY_TEXT,
        index: str = INDEX_TEXT,
    ) -> None:
        self.write_file(root, PLAN_EN, plan_en)
        self.write_file(root, PLAN_ZH, plan_zh)
        self.write_file(root, MEMORY / "skills_usage_audit_30d_summary_2026-06-15-1059.md", final_summary)
        self.write_file(root, MEMORY / "skills_usage_audit_evidence_index_2026-06-18-0313.md", index)

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

    def test_locked_cadence_contract_passes(self) -> None:
        root = self.make_repo("skills-audit-cadence-pass")
        self.write_required_files(root)

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["cadence_contract"]["original_window_start"], "2026-05-16")
        self.assertEqual(payload["cadence_contract"]["original_window_end"], "2026-06-15")
        self.assertEqual(payload["cadence_contract"]["scheduled_repeat_count"], 6)
        self.assertEqual(payload["cadence_contract"]["scheduled_run_shape"]["weekly_evidence"], 4)
        self.assertEqual(payload["cadence_contract"]["warning_triage_frequency"], "event_triggered_only_no_fixed_repeat_count")

    def test_plan_missing_fixed_repeat_count_fails(self) -> None:
        root = self.make_repo("skills-audit-cadence-missing-repeat")
        self.write_required_files(root, plan_en=PLAN_EN_TEXT.replace("fixed at 6 runs total", "kept flexible"))

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("scheduled_repeat_count" in error for error in payload["errors"]))

    def test_final_summary_with_wrong_end_date_fails(self) -> None:
        root = self.make_repo("skills-audit-cadence-wrong-end")
        self.write_required_files(root, final_summary=FINAL_SUMMARY_TEXT.replace("2026-06-15T", "2026-06-18T"))

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("until_date" in error for error in payload["errors"]))

    def test_latest_index_must_keep_post_final_boundary(self) -> None:
        root = self.make_repo("skills-audit-cadence-index-boundary")
        self.write_required_files(root, index=INDEX_TEXT.replace("monitoring evidence only", "normal audit evidence"))

        result = self.run_check(root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("post_final_boundary" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
