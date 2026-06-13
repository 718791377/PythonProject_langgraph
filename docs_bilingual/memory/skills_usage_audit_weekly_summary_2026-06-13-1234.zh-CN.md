---
doc_id: skills_usage_audit_weekly_summary_2026_06_13_1234
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-13
audit_run_type: weekly_summary
canonical: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-13-1234.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-13-1234.md
---

# Skills Usage Audit 7 ????? 2026-06-13 12:34 CST

????? Codex skills usage audit ??? 7 ???????? JSON?stdout??? transcript?runtime log ? warning excerpt ?????? `.tmp/`????? Git?

## ????

- Since: `2026-06-06T04:35:56.037358+00:00`
- Until: `2026-06-13T04:35:56.037358+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## ???? warning ??

- Config ? enabled plugin entries: `40`
- ?? current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Budget warning count: `26`
- Last 7d budget warning count: `26`
- All-descriptions-removed count: `26`
- Maximum omitted additional skills: `15`
- Skipped-loading count: `26`
- Latest retained warning time: `2026-06-13T12:36:33+08:00`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## ????

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## ????????

- profile_review_candidates: `creative-content, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev`
- manual_review_medium_or_weak: `customer-comms, market-research`
- dormant_restorable: `none`

## ????

1. ?? 30 ???????????????? `running`?
2. ?????????????????????????/????????
3. ?? `full` profile ???? live-turn skills-budget ?????
4. ?????? advisory / audit-only ?????? profile apply?
5. ?????? weekly evidence??? live-session warning ?????? triage?
