---
doc_id: skills_usage_audit_warning_triage_2026_06_18_0313
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-18
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0313.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0313.zh-CN.md
---
# Skills Usage Audit Warning Triage 2026-06-18 03:13 CST

This record preserves sanitized post-final warning-triage evidence after additional live-session skills-budget warnings. Raw JSON, raw summaries, transcripts, runtime logs, thread IDs, token counters, and full warning excerpts remain local-only under `.tmp/` and are not committed.

## Triage window

- Since: `2026-06-17T00:00:00+00:00`
- Until: `2026-06-17T19:13:21.971504+00:00`
- Warning triage requested: `True`
- Warning triage status: `warning_found`
- Window policy: `use_days_1_or_since_for_warning_triage`
- Window OK: `True`
- Blockers: `none`

## Warning signals

- Budget warnings in triage window: `38`
- Skipped-loading warnings in triage window: `11`
- All-descriptions-removed count: `38`
- Maximum omitted additional skills: `16`
- Recent retained budget-warning samples: `20`
- Recent retained skipped-loading samples: `0`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Recommended severity action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Recommended triage action: `review_recent_budget_warning_samples_and_record_turn_context`

## New observation versus 2026-06-17 23:28 evidence

- The prior committed 2026-06-17 23:28 record had `25` budget warnings, `15` skipped-loading warnings, and maximum omitted additional skills of `15`.
- This 2026-06-18 03:13 CST probe has `38` budget warnings, `11` skipped-loading warnings, and maximum omitted additional skills of `16` in the narrow post-final window.
- Warning pressure remains high because every detected budget warning still removed all skill descriptions.
- Skipped-loading pressure is lower than the previous monitoring package, but the model-visible skills context budget pressure is still not resolved.
- This supports continued monitoring and human review, not profile apply.

## Sanitized sample handling

- Raw sample excerpts are retained only in `.tmp/` summary/JSON and are not copied here, because they may include model-readable replay context, thread identifiers, token counters, or other runtime metadata even after path redaction.
- Review policy: `record_source_and_do_not_edit_vendor_cache_without_authorization`.

## Audit state

- Audit state: `ready-for-summary`
- Audit reason: `audit_window_at_least_30_days`
- Next action: `generate_sanitized_30_day_markdown_summary_before_profile_apply_candidate`
- Profile apply allowed: `False`
- Current inferred profile: `full`
- Plugin entries in config: `40`
- Total discovered skills: `330`

## Gate evidence

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## Decision buckets from triage run

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

## Review conclusion

1. The narrow triage window is valid and found continued high warning pressure.
2. The current profile is still inferred as `full`, and warning pressure remains linked to a too-large model-visible skills surface.
3. `core-dev`, `web-saas`, `creative-content`, and `full` remain profile-review candidates; `company-ops`, `customer-comms`, and `market-research` remain on-demand soft-load review inputs.
4. The final 30-day summary remains `human_review_pending`; this monitoring evidence does not close the audit.
5. This triage is audit-only and does not authorize editing `config.toml`, vendor/plugin cache, hard-load profiles, or user-level runtime settings.
6. No preview-only candidate or profile apply is authorized by this record.
