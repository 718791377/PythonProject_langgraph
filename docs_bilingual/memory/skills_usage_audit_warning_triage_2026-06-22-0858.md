---
doc_id: skills_usage_audit_warning_triage_2026_06_22_0858
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-22
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-22-0858.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-22-0858.zh-CN.md
---
# Skills Usage Audit Warning Triage 2026-06-22 08:58 CST

This record preserves sanitized post-final warning-triage evidence after fresh live-session `2% skills context budget` warnings on 2026-06-22. Raw JSON, generated stdout, transcripts, runtime logs, warning excerpts, runtime identifiers, request identifiers, response identifiers, call identifiers, token counters, and full runtime context remain local-only and are not committed.

## Triage window

- Command family: `tools/audit_codex_skills_usage.py --since 2026-06-22 --warning-triage`
- Approximate command time: `2026-06-22 08:58 CST`
- Warning triage requested: `True`
- Window policy: `use_days_1_or_since_for_warning_triage`
- Window OK: `True`
- Triage status: `warning_found`
- Blockers: `none`

## Warning signals

- Budget-warning count: `9`
- Last-7-day budget-warning count: `9`
- All-descriptions-removed count: `9`
- Maximum omitted additional skills: `15`
- Skipped-loading count: `9`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Current frontmatter invalid skills: `0`
- Frontmatter resolution: `historical_warning_current_inventory_clean`
- Field contract: `passed`
- Output retention gate: `passed`
- Pre-commit update/archive embedded gate: `passed`

## Source review conclusion

- New post-final warnings were found in the current live session, so monitoring remains active.
- The warning pressure remains high and supports smaller task profiles plus `skills2cli profile suggest` rerank guidance instead of treating `full` as an ordinary task top-1 profile.
- Current frontmatter compatibility is clean: `invalid_total=0`; skipped-loading/frontmatter repair remains resolved unless a future current inventory check contradicts it.
- Skipped-loading pressure is source evidence only; it does not authorize vendor/plugin cache edits.
- This report is advisory-only: `profile_apply_allowed=false`, `mutates_config=false`, `edits_plugin_cache=false`, and `hard_load_apply_performed=false`.

## Verification evidence

- `tools/audit_codex_skills_usage.py --since 2026-06-22 --warning-triage`: passed and generated local-only raw JSON under `.tmp/` plus this curated sanitized Markdown evidence.
- Embedded field contract: `passed`.
- Output-retention contract: `passed`; committed evidence is sanitized Markdown only.
- Current frontmatter bridge: `invalid_total=0`.

## Final-review state preserved

- Final 30-day summary remains `human_review_pending`.
- Closure decision remains pending.
- Candidate generation remains `not_requested`.
- Profile apply remains `not_authorized`.

## Non-actions

- Did not mark the final summary as `summary-reviewed`.
- Did not generate candidate JSON or candidate Markdown.
- Did not run profile apply.
- Did not edit Codex `config.toml`, plugin cache, hard-load profiles, user-level wrappers, or user-level runtime settings.
- Did not commit raw JSON, stdout, transcripts, runtime logs, warning excerpts, runtime identifiers, or token counters.
- Did not mutate remote refs.
