---
doc_id: skills_usage_audit_warning_triage_2026_06_21_0050
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-21
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0050.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0050.zh-CN.md
---
# Skills Usage Audit Warning Triage 2026-06-21 00:50 CST

This record preserves sanitized post-final warning-triage evidence after additional live-session skills-budget warnings. Raw JSON, generated stdout, transcripts, runtime logs, thread IDs, token counters, and full warning excerpts remain local-only under `.tmp/` and are not committed.

## Triage window

- Since: `2026-06-19T16:51:02.434214+00:00`
- Until: `2026-06-20T16:51:02.434214+00:00`
- Days: `1`
- Warning triage requested: `True`
- Warning triage status: `warning_found`
- Window policy: `use_days_1_or_since_for_warning_triage`
- Window OK: `True`
- Since override used: `False`
- Blockers: `none`

## Warning signals

- Budget warnings in triage window: `43`
- Skipped-loading warnings in triage window: `29`
- All-descriptions-removed count: `35`
- Maximum omitted additional skills: `16`
- Recent retained budget-warning samples: `20`
- Recent retained skipped-loading samples: `20`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Recommended severity action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Recommended triage action: `review_recent_budget_warning_samples_and_record_turn_context`

## New observation versus 2026-06-18 06:31 evidence

- The prior committed 2026-06-18 06:31 CST record found `9` budget warnings, `0` skipped-loading warnings, and maximum omitted additional skills of `16` in its narrow post-final window.
- This 2026-06-21 00:50 CST probe found `43` budget warnings, `29` skipped-loading warnings, `35` all-descriptions-removed events, and maximum omitted additional skills of `16` in the current one-day window.
- Warning pressure remains `high` because all-descriptions-removed events continue to be present and the 1-day budget warning count is well above the high-pressure threshold.
- Skipped-loading pressure reappeared in this window and must be reviewed as source evidence only; it does not authorize editing vendor/plugin cache.
- This supports continued monitoring and human review, not profile apply.

## Sanitized sample handling

- Raw sample excerpts are retained only in `.tmp/` summary/JSON and are not copied here, because they may include model-readable replay context, thread identifiers, token counters, or other runtime metadata even after path redaction.
- Review policy: `record_source_and_do_not_edit_vendor_cache_without_authorization`.

## Audit state

- Audit state: `running`
- Audit reason: `audit_window_shorter_than_30_days`
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Current inferred profile: `full`
- Plugin entries in config: `40`
- Total discovered skills: `1270`

## Gate evidence

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## Decision buckets from triage run

- profile_review_candidates: `core-dev, creative-content, customer-comms, full, web-saas`
- on_demand_soft_load: `none`
- manual_review_medium_or_weak: `company-ops, market-research`
- dormant_restorable: `none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 26 | mapped_tool_calls_present_manual_review_required | 3980 | manual_review_required | candidate_for_project_or_default_profile_review |
| web-saas | 111 | mapped_tool_calls_present_manual_review_required | 3977 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 0 | no_mapped_tool_call_medium_evidence | 818 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| market-research | 0 | no_mapped_tool_call_medium_evidence | 521 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| customer-comms | 12 | no_mapped_tool_call_medium_evidence | 629 | manual_review_required | candidate_for_project_or_default_profile_review |
| creative-content | 40 | no_mapped_tool_call_medium_evidence | 869 | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 148 | mapped_tool_calls_present_manual_review_required | 5978 | manual_review_required | candidate_for_project_or_default_profile_review |

## Review conclusion

1. The narrow triage window is valid and found continued high warning pressure.
2. The current profile is still inferred as `full`, and warning pressure remains linked to an oversized model-visible skills surface.
3. Candidate-looking buckets in this record remain review inputs only; they are not authorization to generate a candidate or apply a profile.
4. The final 30-day summary remains `human_review_pending`; this monitoring evidence does not close the audit.
5. This triage is audit-only and does not authorize editing `config.toml`, vendor/plugin cache, hard-load profiles, or user-level runtime settings.
6. No preview-only candidate or profile apply is authorized by this record.
