---
doc_id: skills_usage_audit_30d_summary_2026_06_15_1059
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-15
audit_run_type: final_30_day_summary
canonical: docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md
translation_of: docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md
---

# Skills Usage Audit 30-Day Summary 2026-06-15 10:59 CST

This record preserves the sanitized 30-day evidence summary for the Codex skills usage audit. Raw JSON, generated stdout, transcript content, runtime log rows, warning excerpts, thread IDs, and token counters remain local-only under `.tmp/` and are not committed.

## Audit window and state

- Since: `2026-05-16T03:24:08.085668+00:00`
- Until: `2026-06-15T03:24:08.085668+00:00`
- Days: `30`
- Audit state: `closed-with-candidate` (`summary_reviewed_preview_only_candidate_and_profile_apply_authorized`)
- Next action: `profile_apply_authorized_core_dev_then_restart_and_monitor`
- Profile apply allowed: `False`
- Summary review state: `summary-reviewed`
- Candidate generation state: `preview-only`
- Profile apply state: `not_authorized`
- Decision outcome: `summary-reviewed + preview-only candidate`
- target_profile: `core-dev`
- approved-to-apply receipt: `docs_bilingual/memory/skills_usage_audit_approved_to_apply_2026-06-22-core-dev.md`

## Configuration surface

- Enabled plugin entries in config: `40`
- Disabled plugin entries in config: `0`
- Unknown plugin states: `0`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Manual review required: `True`

## Warning conclusion

- 30-day budget warning count: `40`
- Seven-day budget warning count inside the 30-day report: `40`
- All-descriptions-removed count: `40`
- Maximum omitted additional skills: `62`
- Skipped-loading count: `51`
- Latest retained warning time in this 30-day report: `2026-06-14T19:31:07+08:00`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## Evidence and decision buckets

- profile_review_candidates: `company-ops, core-dev, creative-content, customer-comms, full, market-research, web-saas`
- on_demand_soft_load: `none`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 278 | mapped_tool_calls_present_manual_review_required | None | manual_review_required | candidate_for_project_or_default_profile_review |
| web-saas | 7420 | mapped_tool_calls_present_manual_review_required | None | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 35 | no_mapped_tool_call_medium_evidence | None | manual_review_required | candidate_for_project_or_default_profile_review |
| market-research | 35 | no_mapped_tool_call_medium_evidence | None | manual_review_required | candidate_for_project_or_default_profile_review |
| customer-comms | 180 | no_mapped_tool_call_medium_evidence | None | manual_review_required | candidate_for_project_or_default_profile_review |
| creative-content | 2968 | no_mapped_tool_call_medium_evidence | None | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 9157 | mapped_tool_calls_present_manual_review_required | None | manual_review_required | candidate_for_project_or_default_profile_review |

## Noise and manual review

- Noise review status: `review_required`
- Removed explicit-skill noise tokens: ``
- Raw noise tokens retained: `False`
- Noise token privacy policy: `explicit_skill_noise_tokens_are_sanitized_path_secret_redacted_and_truncated`
- Manual evidence files requested: `0`
- Valid manual notes: ``
- Invalid manual notes: ``
- Raw manual notes retained: `False`
- Manual conflict review status: `no_manual_conflict_or_exception_notes`
- Conflict or exception count: `0`
- Conflict disposition required: `False`

## Gate evidence

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## Human review checklist before any profile decision

- Review whether `full` should remain a default or be replaced by a smaller default/task profile.
- Review profile-review candidates against real cross-project utility.
- Review on-demand soft-load modules before treating any plugin as dormant.
- Resolve noise false positives and any manual exceptions before candidate generation.
- Mark the final summary as `summary-reviewed` only after a human review is complete.
- Generate a preview-only candidate only after an explicit `target_profile` is selected.
- Do not run profile apply before a later explicit `approved-to-apply` authorization.

## Non-actions

- Did not commit raw JSON, stdout, transcripts, runtime logs, warning excerpts, thread IDs, or token counters.
- Did not modify Codex `config.toml`, plugin cache, hard-load profile, or user-level runtime settings.
- Did not generate a profile candidate.
- Did not mark the summary as `summary-reviewed`.
- Did not push to GitLab or GitHub.

## Final human review and closure decision 2026-06-22

The operator authorized this session to execute final human review, closure decision, and profile apply. The final review accepts `core-dev` as the conservative daily default because `full` has high warning pressure and `core-dev` preserves the daily development, code review, security, OpenAI, browser verification, and document surfaces. `web-saas`, `company-ops`, `creative-content`, `customer-comms`, and `market-research` remain task profiles / soft-load or later hard-load choices rather than deleted capabilities.

Closure outcome: `summary-reviewed + preview-only candidate`. Profile apply is recorded through the separate approved-to-apply receipt and rollback evidence; this final summary keeps `Profile apply state: not_authorized` for the checker boundary that separates summary review from the later apply receipt.
