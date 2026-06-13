---
doc_id: skills_usage_audit_weekly_summary_2026_06_13_2121
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-13
audit_run_type: weekly_summary
canonical: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-13-2121.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-13-2121.md
---

# Skills Usage Audit ?????? 2026-06-13 21:21 CST

???? Codex skills usage audit ??????????raw JSON?stdout?transcript?runtime log?warning excerpt?thread ID ? token counter ?????? `.tmp/`????? Git?

## ????

- Since: `2026-06-06T13:21:17.528840+00:00`
- Until: `2026-06-13T13:21:17.528840+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## ??? warning ??

- Config enabled plugin entries: `40`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Budget warning count: `47`
- Last seven-day budget warning count: `47`
- All-descriptions-removed count: `47`
- Maximum omitted additional skills: `62`
- Skipped-loading count: `57`
- Latest retained warning time: `2026-06-13T21:20:50+08:00`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## Gate evidence

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## ?????????

- profile_review_candidates: `creative-content, customer-comms, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

## ????

1. ???? `running`????? 30 ??????????
2. Latest retained warning time ???? `2026-06-13T21:20:50+08:00`??? 20:31 ?????? live-session pressure?
3. ?? `full` profile ?? high live-turn skills-budget pressure ???
4. ?????? advisory audit???? profile apply?
5. ????????????? live-session warning ?????????? warning triage?
