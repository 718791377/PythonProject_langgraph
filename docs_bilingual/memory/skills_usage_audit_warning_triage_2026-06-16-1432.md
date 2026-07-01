---
doc_id: skills_usage_audit_warning_triage_2026_06_16_1432
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-16
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.zh-CN.md
---
# Skills Usage Audit Warning Triage 2026-06-16 14:32 CST

This record preserves sanitized one-day warning-triage evidence after additional live-session skills-budget warnings. Raw JSON, raw summaries, transcripts, runtime logs, thread IDs, token counters, and full warning excerpts remain local-only under `.tmp/` and are not committed.

## Triage window

- Since: `2026-06-15T06:32:35.530324+00:00`
- Until: `2026-06-16T06:32:35.530324+00:00`
- Days: `1`
- Warning triage requested: `True`
- Warning triage status: `warning_found`
- Window policy: `use_days_1_or_since_for_warning_triage`
- Window OK: `True`
- Blockers: `none`

## Warning signals

- Budget warnings in triage window: `32`
- Skipped-loading warnings in triage window: `38`
- All-descriptions-removed count: `32`
- Maximum omitted additional skills: `16`
- Recent retained budget-warning samples: `3`
- Recent retained skipped-loading samples: `3`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Recommended severity action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Recommended triage action: `review_recent_budget_warning_samples_and_record_turn_context`

## New observation versus 10:35 evidence

- The prior committed 10:35 record had `33` budget warnings and `23` skipped-loading warnings.
- This 14:32 probe has `32` budget warnings and `38` skipped-loading warnings in the one-day window.
- Skipped-loading evidence is now materially higher and includes bounded sanitized sample excerpts; this supports continued monitoring and review, not profile apply.

## Sanitized skipped-loading sample shape

- Sample count rendered in raw summary: `3`
- Sample excerpts are retained only in `.tmp/` summary/JSON and are not copied here, because they may include model-readable replay context even after path redaction.
- Review policy: `record_source_and_do_not_edit_vendor_cache_without_authorization`

## Audit state

- Audit state: `running`
- Audit reason: `audit_window_shorter_than_30_days`
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Current inferred profile: `full`
- Plugin entries in config: `40`
- Total discovered skills: `315`

## Gate evidence

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## Decision buckets from triage run

- profile_review_candidates: `creative-content, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev, customer-comms`
- manual_review_medium_or_weak: `market-research`
- dormant_restorable: `none`

## Review conclusion

1. The one-day triage window is valid and found continued high warning pressure.
2. Skipped-loading warning evidence increased to `38` in this probe; that is the main new monitoring signal.
3. The evidence still points at avoiding `full` as the default profile during audit, but it is not profile-apply authorization.
4. The final 30-day summary remains `human_review_pending`; this monitoring evidence does not close the audit.
5. This triage is audit-only and does not authorize editing `config.toml`, vendor/plugin cache, hard-load profiles, or user-level runtime settings.
6. No preview-only candidate or profile apply is authorized by this record.
