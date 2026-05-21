---
doc_id: skills_usage_audit_weekly_summary_2026-05-21
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-05-21
---

# Skills Usage Audit 7 天周报（2026-05-21）

本报告记录 `codex_skills_usage_audit_plan` 的 7 天 audit-only 周报证据。原始 JSON 仅保留在 `.tmp/`，不进入 Git；本 Markdown 为脱敏后的长期证据。

# Codex Skills Usage Audit Summary

## Audit window

- Since: `2026-05-14T15:09:00.340658+00:00`
- Until: `2026-05-21T15:09:00.340658+00:00`
- Days: `7`
- Audit state: `running` (audit_window_shorter_than_30_days)
- Audit next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Audit state blockers: `none`
- Field contract: `passed`
- Field contract passed: `True`
- Field contract blockers: `0`
- Field contract required fields: `21`
- Field contract missing fields: `0`
- Field contract invalid-type fields: `0`
- Field contract requires embedded contract: `False`
- Field contract safety violations: `0`
- Field contract audit-state violations: `0`
- Field contract log-evidence violations: `0`
- Field contract warning-severity violations: `0`
- Field contract warning-triage violations: `0`
- Field contract cadence-review violations: `0`
- Field contract manual-evidence violations: `0`
- Field contract noise-review violations: `0`
- Field contract script-capability violations: `0`
- Field contract output-retention violations: `0`
- Field contract precommit-update-archive violations: `0`
- Field contract runtime-path violations: `0`
- Field contract module-evidence violations: `0`
- Field contract decision-recommendation violations: `0`
- Field contract embedded-contract violations: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`
- Late run: `False`
- Missed weekly runs: `None`
- Weekly report review: `manual_review_required`

## Current configuration surface

- Enabled plugins: `38`
- Disabled plugins: `0`
- Unknown plugin states: `0`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Current profile manual review required: `True`

## Warning conclusion

- Budget warning count: `29`
- Last 7d budget warning count: `29`
- Recent budget warning samples: `20`
- Recent budget warning sample excerpts: `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input_with_turn_context" submission.id="019e4b11-033c-7e83-b6da-ea40c46477b6" codex.op="user_input_with_turn_context"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 cwd=[REDACTED_PATH][truncated]`, `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input_with_turn_context" submission.id="019e4b11-033c-7e83-b6da-ea40c46477b6" codex.op="user_input_with_turn_context"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 cwd=[REDACTED_PATH][truncated]`, `session_loop{thread_id=019e4350-bb08-7aa3-abc9-c670649ffb03}:submission_dispatch{otel.name="op.dispatch.user_input_with_turn_context" submission.id="019e4b04-a3cd-72c2-bc6b-b5048cb61c93" codex.op="user_input_with_turn_context"}:turn{otel.name="session_task.turn" thread.id=019e4350-bb08-7aa3-abc9-c670649ffb03 turn.id=019e4b04-a3cd-72c2-bc6b-b5048cb61c93 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e4b04-a3cd-72c2-bc6b-b5048cb61c93 model=gpt-5.5 cwd=[REDACTED_PATH][truncated]`
- All descriptions removed count: `28`
- Max omitted additional skills: `15`
- Skipped loading count: `28`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## Warning triage

- Requested: `False`
- Status: `not_requested`
- Window policy: `use_days_1_or_since_for_warning_triage`
- Window OK: `False`
- Budget warnings in triage window: `29`
- Skipped loading in triage window: `28`
- Recent skipped-loading samples: `20`
- Recent skipped-loading sample excerpts: `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input_with_turn_context" submission.id="019e4b11-033c-7e83-b6da-ea40c46477b6" codex.op="user_input_with_turn_context"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 cwd=[REDACTED_PATH][truncated]`, `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input_with_turn_context" submission.id="019e4b11-033c-7e83-b6da-ea40c46477b6" codex.op="user_input_with_turn_context"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e4b11-033c-7e83-b6da-ea40c46477b6 model=gpt-5.5 cwd=[REDACTED_PATH][truncated]`, `session_loop{thread_id=019e4350-bb08-7aa3-abc9-c670649ffb03}:submission_dispatch{otel.name="op.dispatch.user_input_with_turn_context" submission.id="019e4b04-a3cd-72c2-bc6b-b5048cb61c93" codex.op="user_input_with_turn_context"}:turn{otel.name="session_task.turn" thread.id=019e4350-bb08-7aa3-abc9-c670649ffb03 turn.id=019e4b04-a3cd-72c2-bc6b-b5048cb61c93 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e4b04-a3cd-72c2-bc6b-b5048cb61c93 model=gpt-5.5 cwd=[REDACTED_PATH][truncated]`
- Skipped-loading review: `record_source_and_do_not_edit_vendor_cache_without_authorization`
- Recommended action: `run_with_warning_triage_after_a_live_session_budget_warning`

## Module evidence

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 199 | mapped_tool_calls_present_manual_review_required | 13118 | manual_review_required | candidate_for_project_or_default_profile_review |
| web-saas | 2981 | mapped_tool_calls_present_manual_review_required | 15129 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 24 | no_mapped_tool_call_medium_evidence | 4124 | manual_review_required | candidate_for_project_or_default_profile_review |
| market-research | 24 | no_mapped_tool_call_medium_evidence | 2679 | manual_review_required | candidate_for_project_or_default_profile_review |
| customer-comms | 116 | no_mapped_tool_call_medium_evidence | 2867 | manual_review_required | candidate_for_project_or_default_profile_review |
| creative-content | 1225 | no_mapped_tool_call_medium_evidence | 3713 | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 3762 | mapped_tool_calls_present_manual_review_required | 28433 | manual_review_required | candidate_for_project_or_default_profile_review |

## Noise review

- Status: `review_required`
- Removed explicit-skill noise tokens: `191`
- Removed explicit-skill noise token samples: `redacted_from_long_term_markdown`; raw examples stay in local `.tmp/` JSON only during immediate debugging.
- Strong evidence policy: `removed_noise_tokens_are_not_counted_as_strong_evidence`
- Raw noise tokens retained: `False`
- Max noise token length: `120`
- Token privacy policy: `explicit_skill_noise_tokens_are_sanitized_path_secret_redacted_and_truncated`

## Manual evidence

- Files requested: `0`
- Files read: `0`
- Valid notes: `0`
- Invalid notes: `0`
- Raw notes retained: `False`
- Source paths retained: `False`
- Max source path length: `300`
- Privacy policy: `manual_notes_are_sanitized_markdown_fields_only_no_raw_transcripts`
- Source path privacy policy: `manual_note_source_paths_are_redacted_and_bounded_before_report_retention`
- Conflict review status: `no_manual_conflict_or_exception_notes`
- Conflict/exception count: `0`
- Conflict disposition required: `False`
- Conflict policy: `manual_notes_do_not_override_script_evidence`
- Conflict disposition: `none`

## Script coverage and human review boundaries

- Policy: `audit_helper_reports_evidence_boundaries_and_is_not_an_omniscient_source_of_truth`
- Reliable coverage items: `7`
- Human-review items: `5`
- Enhancement triggers: `5`
- Stable tool-call alias registry policy: `stable_aliases_are_medium_evidence_only_and_never_profile_apply_evidence`
- Stable tool-call alias evidence level: `medium`
- Stable tool-call aliases count as strong evidence: `False`
- Stable tool-call plugin alias targets: `2`
- Stable tool-call module alias targets: `1`
- Audit output long-term evidence format: `sanitized_markdown_summary`
- `.tmp/` outputs local only: `True`
- Raw audit JSON local only: `True`
- Pre-commit existing-file update review: `True`
- Pre-commit OpenSpec archive gate: `True`
- Pre-commit changed path count: `0`
- Pre-commit active change reviews: `0`
- Runtime path raw values retained: `False`
- Runtime path privacy policy: `runtime_paths_are_kind_labels_and_placeholders_no_raw_user_paths`

### Reliable coverage

- `plugin_enabled_disabled_unknown_state_from_config_toml` - reads plugin enabled/disabled/unknown state from Codex config.
- `user_repo_plugin_skill_inventory_counts` - counts user, repository, and plugin skills.
- `session_explicit_skill_announcements_skill_path_reads_helper_calls_and_tool_call_names` - extracts session-level skill announcements, skill-file reads, helper calls, and tool-call names.
- `logs_2_sqlite_budget_warnings_all_descriptions_removed_omitted_skills_and_skipped_loading_samples` - extracts budget-warning and skipped-loading evidence from runtime logs.
- `profile_module_aggregation_from_helper_calls_and_plugin_skill_path_reads` - aggregates helper calls and skill reads by profile module.
- `stable_tool_call_aliases_for_medium_evidence_only_module_review` - maps stable tool-call aliases as medium evidence only.
- `precommit_existing_file_update_and_openspec_archive_gate_status` - embeds pre-commit update/archive gate status.

### Human review required for

- `weak_plugin_mentions_are_text_trends_not_real_invocation_evidence` - requires human review because weak mentions are text trends, not invocation evidence.
- `explicit_skills_can_contain_natural_language_or_example_token_false_positives` - requires human review for natural-language or example-token false positives.
- `tool_call_names_and_stable_aliases_are_medium_evidence_not_plugin_or_profile_apply_evidence` - requires human review because tool aliases are not profile-apply evidence.
- `unreadable_rotated_or_missing_logs_can_underreport_warning_counts` - requires human review because missing logs can underreport warnings.
- `missing_or_stale_profile_registry_data_can_make_module_evidence_incomplete` - requires human review because stale registry data can make module evidence incomplete.

### Enhancement triggers

- `same_false_positive_pattern_repeats_in_two_weekly_reports` - triggers script enhancement when the same false positive repeats in two weekly reports.
- `thirty_day_summary_needs_evidence_that_is_only_reported_as_weak_mentions` - triggers script enhancement when 30-day decisions need evidence currently reported only as weak mentions.
- `stable_tool_call_pattern_maps_to_a_plugin_or_module_but_is_not_in_the_alias_registry` - triggers alias-registry enhancement for stable unmapped tool-call patterns.
- `live_session_warning_cannot_be_localized_from_logs_2_sqlite` - triggers evidence-source enhancement when a live warning cannot be localized from runtime logs.
- `profile_registry_and_enabled_plugin_surface_diverge_enough_to_mislead_module_evidence` - triggers registry enhancement when profile registry and enabled-plugin surface diverge.

### Stable tool-call alias registry

- Plugin `Browser` aliases: `mcp__chrome_devtools__, mcp__cdp_bridge__`
- Plugin `Cloudflare` aliases: `mcp__cloudflare_api__`
- Module `creative-content` aliases: `mcp__pencil__`

## Decision recommendation

- Decision status: `advisory_only_no_profile_apply`
- Decision policy: `decision_buckets_are_review_inputs_and_never_apply_profiles`
- Warning pressure: `high`
- Profile apply allowed by summary: `False`
- Profile review candidates: `company-ops`, `core-dev`, `creative-content`, `customer-comms`, `full`, `market-research`, `web-saas`
- On-demand soft-load modules: `none`
- Manual-review medium/weak modules: `none`
- Dormant/restorable modules: `none`
- This sanitized summary is review evidence only.
- Reports with failed field contracts must be rerun or fixed before profile decisions.
- It does not modify `config.toml`, plugin cache, or hard-load profiles.
- Create a separate profile apply candidate record before any apply action.
- Review `medium_evidence_rationale` and `cross_project_utility` manually before any default-profile decision.

## Risks and restore path

- If a plugin is removed from the default profile later, restore through `set_plugin_profile.ps1 -RestoreLatest -Apply` or apply the prior approved profile.
- Restart Codex through `codex-ohmy` after any future hard-load/profile apply.
- Keep this audit summary separate from any future apply-candidate record.

## Non-action list

- Did not modify user-level `config.toml`.
- Did not edit plugin/vendor cache.
- Did not perform hard-load/profile apply.
- Did not include raw session transcripts or raw log databases.
