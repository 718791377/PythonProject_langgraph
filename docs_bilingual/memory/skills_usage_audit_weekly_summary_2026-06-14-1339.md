---
doc_id: skills_usage_audit_weekly_summary_2026_06_14_1339
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-14
audit_run_type: weekly_summary
canonical: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-14-1339.md
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-14-1339.zh-CN.md
---

# Skills Usage Audit Weekly Summary 2026-06-14 13:39 CST

This record preserves sanitized rolling seven-day evidence for the Codex skills usage audit. Raw JSON, stdout, transcripts, runtime logs, warning excerpts, thread IDs, and token counters remain local-only under `.tmp/` and are not committed.

## Audit window

- Since: `2026-06-07T05:39:41.805982+00:00`
- Until: `2026-06-14T05:39:41.805982+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## Configuration and warning pressure

- Enabled plugin entries in config: `40`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Budget warning count: `46`
- Last seven-day budget warning count: `46`
- All-descriptions-removed count: `46`
- Maximum omitted additional skills: `62`
- Skipped-loading count: `60`
- Latest retained warning time: `2026-06-14T13:36:53+08:00`
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

## Decision buckets from weekly run

- profile_review_candidates: `creative-content, customer-comms, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

## Review conclusion

1. The audit remains in `running` state because the real 30-day observation window is not complete.
2. The latest retained warning time is `2026-06-14T13:36:53+08:00`, preserving continued live-session pressure evidence after the 2026-06-13 23:13 record.
3. The current `full` profile still correlates with high live-turn skills-budget pressure.
4. This evidence is advisory and audit-only; it does not authorize profile apply.
5. Continue weekly evidence collection and narrow warning triage after future live-session warnings.
