---
doc_id: skills_usage_audit_warning_triage_2026_06_18_0313
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-18
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0313.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0313.md
---
# Skills ???? Warning Triage 2026-06-18 03:13 CST

????? 30 ????????? warning triage ????? JSON??????transcript?runtime log?thread ID?token counter ??? warning excerpt ??????? `.tmp/`???????

## Triage ??

- Since: `2026-06-17T00:00:00+00:00`
- Until: `2026-06-17T19:13:21.971504+00:00`
- ??? warning triage: `True`
- Warning triage ??: `warning_found`
- ????: `use_days_1_or_since_for_warning_triage`
- ????: `True`
- Blockers: `none`

## Warning ??

- ??? budget warnings: `38`
- ??? skipped-loading warnings: `11`
- All-descriptions-removed ??: `38`
- ?? omitted additional skills: `16`
- ??? budget-warning ?????: `20`
- ??? skipped-loading ?????: `0`
- ?????: `high`
- ?????: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- ???????: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Triage ????: `review_recent_budget_warning_samples_and_record_turn_context`

## ?? 2026-06-17 23:28 ??????

- ??????? 2026-06-17 23:28 ???? `25` ? budget warnings?`15` ? skipped-loading warnings??? omitted additional skills ? `15`?
- ?? 2026-06-18 03:13 CST ???? post-final ????? `38` ? budget warnings?`11` ? skipped-loading warnings??? omitted additional skills ? `16`?
- Warning pressure ??? high??????? budget warning ?????? skill descriptions?
- skipped-loading ??????? monitoring package?? model-visible skills context budget ???????
- ???????? monitoring ????????? profile apply?

## ??????

- ???? excerpt ???? `.tmp/` summary/JSON ?????????????????????????? model-readable replay context?thread identifier?token counter ??? runtime metadata?
- ????: `record_source_and_do_not_edit_vendor_cache_without_authorization`?

## ????

- Audit state: `ready-for-summary`
- Audit reason: `audit_window_at_least_30_days`
- Next action: `generate_sanitized_30_day_markdown_summary_before_profile_apply_candidate`
- Profile apply allowed: `False`
- ???? profile: `full`
- config ? plugin ???: `40`
- ??? skills ??: `330`

## Gate ??

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## Triage run ????

- profile_review_candidates: `core-dev, creative-content, full, web-saas`
- on_demand_soft_load: `company-ops, customer-comms, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 16 | mapped_tool_calls_present_manual_review_required | 4892 | manual_review_required | candidate_for_project_or_default_profile_review |
| web-saas | 74 | mapped_tool_calls_present_manual_review_required | 4923 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 3 | no_mapped_tool_call_medium_evidence | 557 | manual_review_required | keep_module_on_demand_and_continue_audit |
| market-research | 2 | no_mapped_tool_call_medium_evidence | 347 | manual_review_required | keep_module_on_demand_and_continue_audit |
| customer-comms | 2 | no_mapped_tool_call_medium_evidence | 400 | manual_review_required | keep_module_on_demand_and_continue_audit |
| creative-content | 40 | no_mapped_tool_call_medium_evidence | 470 | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 102 | mapped_tool_calls_present_manual_review_required | 6637 | manual_review_required | candidate_for_project_or_default_profile_review |

## ????

1. ????? triage ?????? warning pressure ?? high?
2. ?? profile ???? `full`?warning pressure ????? model-visible skills surface ???
3. `core-dev`?`web-saas`?`creative-content` ? `full` ??? profile-review candidates?`company-ops`?`customer-comms` ? `market-research` ??? on-demand soft-load ?????
4. ?? 30 ? summary ??? `human_review_pending`?? monitoring evidence ??????
5. ? triage ? audit-only?????? `config.toml`?vendor/plugin cache?hard-load profiles ? user-level runtime settings?
6. ?????? preview-only candidate ? profile apply?
