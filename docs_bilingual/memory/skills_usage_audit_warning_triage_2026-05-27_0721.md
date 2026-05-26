---
doc_id: skills_usage_audit_warning_triage_2026-05-27_0721
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-05-27
audit_run_type: warning_triage
audit_window_days: 1
followup_run: true
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-05-27_0721.zh-CN.md
---

# Skills Usage Audit One-Day Warning Triage (2026-05-27 07:21)

This is an audit-only continuation run for `codex_skills_usage_audit_plan`. Raw JSON, stdout, and temporary summaries remain local-only under `.tmp/`. This evidence does not authorize changes to `config.toml`, plugin cache, or hard-load profiles.

## Key facts

- Latest warning time: `2026-05-27T07:23:47+08:00`
- Audit window: `2026-05-25T23:24:01.376257+00:00` to `2026-05-26T23:24:01.376257+00:00`, days `1`
- Audit state: `running`; reason `audit_window_shorter_than_30_days`; next action `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`; audit-only: `True`
- Current profile inference: `full`; enabled plugins: `39`
- Skills inventory: total `310`; user `57`; repo `29`; plugin `224`
- Warning triage: status `warning_found`; window_ok `True`; budget_warning_count `21`; skipped_loading_count `25`
- Warning severity: `high`; reason `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`; recommended_action `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- All-descriptions-removed count: `21`; maximum omitted additional skills: `15`
- Field contract: `passed`; output retention: `passed`; precommit update/archive: `passed`; changed paths at report generation: `4`
- Triage recommended action: `review_recent_budget_warning_samples_and_record_turn_context`

## Review conclusion

1. The latest one-day window still shows skills context budget pressure, with the latest warning at `2026-05-27T07:23:47+08:00`.
2. Severity remains `high` because all skill descriptions were removed and additional skills were omitted.
3. Soft-load does not reduce the model-visible skills budget by itself; continue the 30-day audit before any hard-load/profile apply decision.
4. `company-ops`, `customer-comms`, and `market-research` still require manual review or stronger evidence before any default-profile decision.
5. `core-dev`, `creative-content`, `web-saas`, and `full` remain profile review candidates only; no apply action is authorized.

# Codex Skills Usage Audit Summary

## Audit window

- Since: `2026-05-25T23:24:01.376257+00:00`
- Until: `2026-05-26T23:24:01.376257+00:00`
- Days: `1`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Audit next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Audit state blockers: `none`
- Field contract: `passed`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`
- Late run: `False`
- Missed weekly runs: `None`
- Weekly report review: `manual_review_required`

## Current configuration surface

- Enabled plugins: `39`
- Disabled plugins: `0`
- Unknown plugin states: `0`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Current profile manual review required: `True`

## Warning conclusion

- Budget warning count: `21`
- Last 7d budget warning count: `21`
- Recent budget warning samples: `20`
- All descriptions removed count: `21`
- Max omitted additional skills: `15`
- Skipped loading count: `25`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## Warning triage

- Requested: `True`
- Status: `warning_found`
- Window policy: `use_days_1_or_since_for_warning_triage`
- Window OK: `True`
- Budget warnings in triage window: `21`
- Skipped loading in triage window: `25`
- Recent skipped-loading samples: `20`
- Skipped-loading review: `record_source_and_do_not_edit_vendor_cache_without_authorization`
- Recommended action: `review_recent_budget_warning_samples_and_record_turn_context`

## Module evidence

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 13 | no_mapped_tool_call_medium_evidence | 534 | manual_review_required | candidate_for_project_or_default_profile_review |
| web-saas | 98 | no_mapped_tool_call_medium_evidence | 571 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 0 | no_mapped_tool_call_medium_evidence | 84 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| market-research | 0 | no_mapped_tool_call_medium_evidence | 54 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| customer-comms | 0 | no_mapped_tool_call_medium_evidence | 58 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| creative-content | 34 | no_mapped_tool_call_medium_evidence | 86 | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 115 | no_mapped_tool_call_medium_evidence | 787 | manual_review_required | candidate_for_project_or_default_profile_review |

## Decision recommendation

- Decision status: `advisory_only_no_profile_apply`
- Decision policy: `decision_buckets_are_review_inputs_and_never_apply_profiles`
- Warning pressure: `high`
- Profile apply allowed by summary: `False`
- Profile review candidates: `core-dev`, `creative-content`, `full`, `web-saas`
- On-demand soft-load modules: `none`
- Manual-review medium/weak modules: `company-ops`, `customer-comms`, `market-research`
- Dormant/restorable modules: `none`
- This sanitized summary is review evidence only.
- Reports with failed field contracts must be rerun or fixed before profile decisions.
- It does not modify `config.toml`, plugin cache, or hard-load profiles.
- Create a separate profile apply candidate record before any apply action.
- Review `medium_evidence_rationale` and `cross_project_utility` manually before any default-profile decision.

## Risks and restore path

- If a plugin is later removed from the default profile, restore through `set_plugin_profile.ps1 -RestoreLatest -Apply` or apply the prior approved profile.
- Restart Codex through `codex-ohmy` after any future hard-load/profile apply.
- Keep this audit summary separate from any future apply-candidate record.

## Non-action list

- Did not modify user-level `config.toml`.
- Did not edit plugin/vendor cache.
- Did not perform hard-load/profile apply.
- Did not include raw session transcripts or raw log databases.
