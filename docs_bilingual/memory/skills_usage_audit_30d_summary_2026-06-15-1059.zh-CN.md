---
doc_id: skills_usage_audit_30d_summary_2026_06_15_1059
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-15
audit_run_type: final_30_day_summary
canonical: docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md
---

# Skills Usage Audit 30 天最终摘要 2026-06-15 10:59 CST

本记录保存 Codex skills usage audit 的脱敏 30 天证据摘要。原始 JSON、stdout、transcript、runtime log、warning excerpt、thread ID 与 token counter 仍仅保留在 `.tmp/` 本地目录，不提交到 Git。

## 审计窗口与状态

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

## 配置面

- Enabled plugin entries in config: `40`
- Disabled plugin entries in config: `0`
- Unknown plugin states: `0`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Manual review required: `True`

## Warning 结论

- 30-day budget warning count: `40`
- Seven-day budget warning count inside the 30-day report: `40`
- All-descriptions-removed count: `40`
- Maximum omitted additional skills: `62`
- Skipped-loading count: `51`
- Latest retained warning time in this 30-day report: `2026-06-14T19:31:07+08:00`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## 证据与决策分桶

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

## 噪声与人工复核

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

## 进入 profile 决策前的人工复核清单

- 复核 `full` 是否应继续作为默认 profile，或改为更小的默认/任务 profile。
- 按真实跨项目效用复核 profile-review candidates。
- 在将任何 plugin 视为 dormant 之前，先复核 on-demand soft-load modules。
- 在生成 candidate 前处理噪声误报和人工例外。
- 只有人工复核完成后，才能将最终摘要标记为 `summary-reviewed`。
- 只有明确选定 `target_profile` 后，才生成 preview-only candidate。
- 获得后续明确 `approved-to-apply` 授权前，不执行 profile apply。

## 非动作

- 未提交 raw JSON、stdout、session transcript、runtime log、warning excerpt、thread ID 或 token counter。
- 未修改 Codex `config.toml`、plugin cache、hard-load profile 或 user-level runtime settings。
- 未生成 profile candidate。
- 未将摘要标记为 `summary-reviewed`。
- 未推送 GitLab 或 GitHub。

## 2026-06-22 final human review and closure decision

This zh-CN companion uses ASCII-safe wording for the new closeout note to avoid Windows transport mojibake. The operator authorized final human review, closure decision, and profile apply in the current session. The review accepts `core-dev` as the conservative daily default profile because `full` has high warning pressure while `core-dev` keeps daily development, code review, security, OpenAI, browser verification, and document capability. `web-saas`, `company-ops`, `creative-content`, `customer-comms`, and `market-research` remain task profiles / soft-load or later hard-load choices; they are not deleted.

Closure outcome: `summary-reviewed + preview-only candidate`. Profile apply is recorded through the separate approved-to-apply receipt and rollback evidence. This final summary keeps `Profile apply state: not_authorized` so the checker boundary between summary review and later apply receipt remains explicit.
