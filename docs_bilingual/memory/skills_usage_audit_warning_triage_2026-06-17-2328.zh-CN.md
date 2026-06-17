---
doc_id: skills_usage_audit_warning_triage_2026_06_17_2328
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-17
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-17-2328.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-17-2328.md
---
# Skills ???????? 2026-06-17 23:28 CST

????????? 1 ???? skills-budget warning ????????? JSON???????? transcript?runtime log?thread ID?token counter ??? warning excerpt ?????? `.tmp/`???????

## ????

- Since: `2026-06-16T15:28:33.300709+00:00`
- Until: `2026-06-17T15:28:33.300709+00:00`
- Days: `1`
- ???? warning triage: `True`
- Warning triage ??: `warning_found`
- ????: `use_days_1_or_since_for_warning_triage`
- ??????: `True`
- Blockers: `none`

## Warning ??

- ??? budget warnings: `25`
- ??? skipped-loading warnings: `15`
- All descriptions removed ??: `25`
- ?? omitted additional skills: `15`
- ????? budget-warning ???: `20`
- ????? skipped-loading ???: `15`
- ?????: `high`
- ?????: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- ???????: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Triage ????: `review_recent_budget_warning_samples_and_record_turn_context`

## ?? 2026-06-16 14:32 ??????

- ???? 2026-06-16 14:32 ??? `32` ? budget warnings?`38` ? skipped-loading warnings??? omitted additional skills ? `16`?
- ?? 2026-06-17 23:28 ??? 1 ?????? `25` ? budget warnings?`15` ? skipped-loading warnings??? omitted additional skills ? `15`?
- ?? skipped-loading ??????? 14:32 ???????? budget warning ?????? skill descriptions????? warning pressure ?? high?
- ??????????????????? profile apply ???

## ??????

- ?????????? `.tmp/` summary/JSON ??????????????????????????? model-readable replay context?thread identifier?token counter ??? runtime metadata?
- ????: `record_source_and_do_not_edit_vendor_cache_without_authorization`?

## ????

- ????: `running`
- ????: `audit_window_shorter_than_30_days`
- ???: `continue_audit_collection_without_profile_apply`
- ???? profile apply: `False`
- ???? profile: `full`
- config ? plugin ???: `40`
- ??? skills ??: `315`

## Gate ??

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## ?? triage ?????

- profile_review_candidates: `core-dev, creative-content, full, web-saas`
- on_demand_soft_load: `company-ops, customer-comms, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 11 | mapped_tool_calls_present_manual_review_required | 4051 | manual_review_required | candidate_for_project_or_default_profile_review |
| web-saas | 29 | mapped_tool_calls_present_manual_review_required | 4007 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 2 | no_mapped_tool_call_medium_evidence | 438 | manual_review_required | keep_module_on_demand_and_continue_audit |
| market-research | 2 | no_mapped_tool_call_medium_evidence | 298 | manual_review_required | keep_module_on_demand_and_continue_audit |
| customer-comms | 2 | no_mapped_tool_call_medium_evidence | 340 | manual_review_required | keep_module_on_demand_and_continue_audit |
| creative-content | 11 | no_mapped_tool_call_medium_evidence | 392 | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 35 | mapped_tool_calls_present_manual_review_required | 5237 | manual_review_required | candidate_for_project_or_default_profile_review |

## ????

1. ?? 1 ? triage ???????? warning pressure ?? high?
2. ?? profile ???? `full`?warning pressure ?? model-visible skills surface ?????
3. `core-dev`?`web-saas`?`creative-content` ? `full` ?? profile-review candidates?`company-ops`?`customer-comms`?`market-research` ??? on-demand soft-load ?????
4. ?? 30 ????? `human_review_pending`?? monitoring ????????
5. ?? triage ?? audit-only?????? `config.toml`?vendor/plugin cache?hard-load profiles ???? runtime settings?
6. ?????? preview-only candidate ? profile apply?
