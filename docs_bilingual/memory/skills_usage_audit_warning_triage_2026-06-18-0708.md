---
doc_id: skills_usage_audit_warning_triage_2026_06_18_0708
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-18
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0708.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0708.zh-CN.md
---
# Skills Usage Audit Warning Triage 2026-06-18 07:08 CST

This record preserves sanitized post-final warning-triage evidence after additional live-session skills-budget warnings. Raw JSON, generated stdout, transcripts, runtime logs, thread IDs, token counters, and full warning excerpts remain local-only under `.tmp/` and are not committed.

## Triage window

- Since: `2026-06-17T22:36:53.106426+00:00`
- Until: `2026-06-18T01:30:34.662157+00:00`
- Warning triage requested: `True`
- Warning triage status: `warning_found`
- Window policy: `use_days_1_or_since_for_warning_triage`
- Window OK: `True`
- Since override used: `True`
- Blockers: `none`

## Warning signals

- Budget warnings in triage window: `5`
- Skipped-loading warnings in triage window: `5`
- All-descriptions-removed count: `5`
- Maximum omitted additional skills: `15`
- Recent retained budget-warning samples: `5`
- Recent retained skipped-loading samples: `5`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Recommended severity action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Recommended triage action: `review_recent_budget_warning_samples_and_record_turn_context`

## New observation versus 2026-06-18 06:31 evidence

- The prior committed 2026-06-18 06:31 CST record had `9` budget warnings, `0` skipped-loading warnings, and maximum omitted additional skills of `16` in its narrow post-final window.
- This 2026-06-18 07:08 CST probe found `5` budget warnings, `5` skipped-loading warnings, and maximum omitted additional skills of `15` after the previous 06:31 evidence cutoff.
- Warning pressure remains `high` because every detected budget warning still removed all skill descriptions.
- Skipped-loading pressure reappeared in this narrow continuation window and must be reviewed as a source signal, not fixed by editing vendor cache.
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

- profile_review_candidates: `full`, `web-saas`
- on_demand_soft_load: `creative-content`
- manual_review_medium_or_weak: `company-ops`, `core-dev`, `customer-comms`, `market-research`
- dormant_restorable: `none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 0 | no_mapped_tool_call_medium_evidence | 41 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| web-saas | 10 | no_mapped_tool_call_medium_evidence | 55 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 0 | no_mapped_tool_call_medium_evidence | 25 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| market-research | 0 | no_mapped_tool_call_medium_evidence | 17 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| customer-comms | 0 | no_mapped_tool_call_medium_evidence | 13 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| creative-content | 4 | no_mapped_tool_call_medium_evidence | 18 | manual_review_required | keep_module_on_demand_and_continue_audit |
| full | 12 | no_mapped_tool_call_medium_evidence | 133 | manual_review_required | candidate_for_project_or_default_profile_review |

## Review conclusion

1. The narrow triage window is valid and found continued high warning pressure.
2. The current profile is still inferred as `full`, and warning pressure remains linked to a too-large model-visible skills surface.
3. `full` and `web-saas` remain profile-review candidates; `creative-content` is currently on-demand soft-load evidence; `core-dev`, `company-ops`, `customer-comms`, and `market-research` still require manual review.
4. The final 30-day summary remains `human_review_pending`; this monitoring evidence does not close the audit.
5. This triage is audit-only and does not authorize editing `config.toml`, vendor/plugin cache, hard-load profiles, or user-level runtime settings.
6. No preview-only candidate or profile apply is authorized by this record.
