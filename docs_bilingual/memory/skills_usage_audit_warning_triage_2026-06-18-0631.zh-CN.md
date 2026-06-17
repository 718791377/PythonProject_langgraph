---
doc_id: skills_usage_audit_warning_triage_2026_06_18_0631
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-18
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0631.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0631.md
---
# Skills Usage Audit Warning Triage 2026-06-18 06:31 CST

????? post-final ???? live-session skills-budget warning ????? triage ????? JSON?stdout?transcripts?runtime logs?thread IDs?token counters ??? warning excerpts ?????? `.tmp/`??????

## Triage ??

- Since: `2026-06-17T19:13:21+00:00`
- Until: `2026-06-17T22:36:53.106426+00:00`
- ?? warning triage: `True`
- Warning triage ??: `warning_found`
- ????: `use_days_1_or_since_for_warning_triage`
- ????: `True`
- ?? since override: `True`
- Blockers: `none`

## Warning ??

- triage ??? budget warnings: `9`
- triage ??? skipped-loading warnings: `0`
- All-descriptions-removed ??: `9`
- ?? omitted additional skills: `16`
- ???? budget-warning ???: `9`
- ???? skipped-loading ???: `0`
- ?????: `high`
- ?????: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- ???????: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Triage ????: `review_recent_budget_warning_samples_and_record_turn_context`

## ?? 2026-06-18 03:13 ??????

- ???? 2026-06-18 03:13 CST ???????? `38` ? budget warnings?`11` ? skipped-loading warnings??? omitted additional skills ? `16`?
- ?? 2026-06-18 06:31 CST probe ??? 03:13 ????????? `9` ? budget warnings?`0` ? skipped-loading warnings??? omitted additional skills ? `16`?
- Warning pressure ?? `high`??????? budget warnings ?????? skill descriptions?
- ???????? skipped-loading pressure?? model-visible skills context budget pressure ?????
- ???????? monitoring ????????? profile apply?

## ??????

- ???? excerpt ???? `.tmp/` summary/JSON????????????????????????? model-readable replay context?thread identifier?token counter ??? runtime metadata?
- ????: `record_source_and_do_not_edit_vendor_cache_without_authorization`?

## Audit ??

- Audit state: `ready-for-summary`
- Audit reason: `audit_window_at_least_30_days`
- Next action: `generate_sanitized_30_day_markdown_summary_before_profile_apply_candidate`
- Profile apply allowed: `False`
- ???? profile: `full`
- config ? plugin entries: `40`
- ??? skills ??: `330`

## Gate ??

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## Triage run ????

- profile_review_candidates: `creative-content, full, web-saas`
- on_demand_soft_load: `none`
- manual_review_medium_or_weak: `company-ops, core-dev, customer-comms, market-research`
- dormant_restorable: `none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 0 | no_mapped_tool_call_medium_evidence | 240 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| web-saas | 35 | no_mapped_tool_call_medium_evidence | 297 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 0 | no_mapped_tool_call_medium_evidence | 57 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| market-research | 0 | no_mapped_tool_call_medium_evidence | 22 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| customer-comms | 0 | no_mapped_tool_call_medium_evidence | 34 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| creative-content | 14 | no_mapped_tool_call_medium_evidence | 43 | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 42 | no_mapped_tool_call_medium_evidence | 439 | manual_review_required | candidate_for_project_or_default_profile_review |

## ????

1. ??? triage ?????? warning pressure ???? high?
2. ?? profile ???? `full`?warning pressure ????? model-visible skills surface ???
3. `web-saas`?`creative-content` ? `full` ?? profile-review candidates?`core-dev`?`company-ops`?`customer-comms` ? `market-research` ???????? medium/weak ?????????
4. ?? 30 ?????? `human_review_pending`?? monitoring evidence ??????
5. ? triage ?? audit-only?????? `config.toml`?vendor/plugin cache?hard-load profiles ? user-level runtime settings?
6. ?????? preview-only candidate????? profile apply?
