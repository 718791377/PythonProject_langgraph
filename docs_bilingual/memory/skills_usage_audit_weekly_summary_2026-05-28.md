---
doc_id: skills_usage_audit_weekly_summary_2026-05-28
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-05-28
audit_run_type: weekly_summary
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-05-28.zh-CN.md
---

# Skills Usage Audit Weekly Summary (2026-05-28)

This record preserves sanitized weekly evidence for the Codex skills usage audit. It intentionally stores summary fields only; raw JSON, stdout, transcripts, and runtime logs remain local-only under `.tmp/` and are not committed.

## Audit window

- Since: `2026-05-20T23:16:34.253616+00:00`
- Until: `2026-05-27T23:16:34.253616+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## Configuration and warning pressure

- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Budget warning count: `45`
- All-descriptions-removed count: `44`
- Maximum omitted additional skills: `15`
- Skipped-loading count: `51`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## Gate evidence

- Field contract: `passed`
- Output retention gate: `passed`
- Pre-commit update/archive embedded gate: `passed`

## Decision buckets from weekly run

- profile_review_candidates: `core-dev, creative-content, customer-comms, full, web-saas`
- on_demand_soft_load: `company-ops, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

## Review conclusion

1. The current evidence remains audit-only and does not authorize profile apply.
2. The full profile is still producing high live-turn skills-budget pressure in the observed window.
3. The recommended action is to avoid the full profile as the default during audit and prefer smaller default or task profiles only after manual review.
4. This weekly summary does not prove that soft-load failed; it proves that live-turn pressure still recurred while the inferred active surface is `full`.
5. Continue the 30-day audit and keep future profile changes preview-only unless the user gives separate explicit apply approval.
