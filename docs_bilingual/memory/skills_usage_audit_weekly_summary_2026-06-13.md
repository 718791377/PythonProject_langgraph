---
doc_id: skills_usage_audit_weekly_summary_2026-06-13
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-13
audit_run_type: weekly_summary
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-13.zh-CN.md
---

# Skills Usage Audit Weekly Summary (2026-06-13)

This record preserves sanitized rolling seven-day evidence for the Codex skills usage audit. It stores summary fields only; raw JSON, stdout, transcripts, and runtime logs remain local-only under `.tmp/` and are not committed.

## Audit window

- Since: `2026-06-06T01:00:07.100343+00:00`
- Until: `2026-06-13T01:00:07.100343+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## Configuration and warning pressure

- Enabled plugin entries in config: `40`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Budget warning count: `35`
- All-descriptions-removed count: `35`
- Maximum omitted additional skills: `15`
- Skipped-loading count: `35`
- Latest retained warning time: `2026-06-13T09:00:35+08:00`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## Gate evidence

- Field contract: `passed`
- Output retention gate: `passed`
- Pre-commit update/archive embedded gate: `passed`

## Decision buckets from weekly run

- profile_review_candidates: `creative-content, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev`
- manual_review_medium_or_weak: `customer-comms, market-research`
- dormant_restorable: `none`

## Review conclusion

1. The audit remains in `running` state because the full 30-day window is not ready.
2. The current evidence remains audit-only and does not authorize profile apply.
3. The inferred `full` profile still correlates with high live-turn skills-budget pressure in this seven-day window.
4. The evidence supports continued monitoring and manual review, not direct edits to `config.toml`, plugin cache, or hard-load profile settings.
5. Future profile changes must remain preview-only until the 30-day summary is reviewed and a separate explicit apply approval exists.
