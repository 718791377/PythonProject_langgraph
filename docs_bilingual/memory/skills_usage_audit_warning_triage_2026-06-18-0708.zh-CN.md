---
doc_id: skills_usage_audit_warning_triage_2026_06_18_0708
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-18
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0708.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-18-0708.md
---
# Skills Usage Audit Warning Triage 2026-06-18 07:08 CST

本记录保存额外 live-session skills-budget warnings 之后的脱敏 post-final warning-triage 证据。Raw JSON、generated stdout、transcripts、runtime logs、thread IDs、token counters 与完整 warning excerpts 仍仅保留在 `.tmp/` 本地目录，不提交到 Git。

## Triage 窗口

- Since：`2026-06-17T22:36:53.106426+00:00`
- Until：`2026-06-18T01:30:34.662157+00:00`
- Warning triage requested：`True`
- Warning triage status：`warning_found`
- Window policy：`use_days_1_or_since_for_warning_triage`
- Window OK：`True`
- Since override used：`True`
- Blockers：`none`

## Warning 信号

- Budget warnings in triage window：`5`
- Skipped-loading warnings in triage window：`5`
- All-descriptions-removed count：`5`
- Maximum omitted additional skills：`15`
- Recent retained budget-warning samples：`5`
- Recent retained skipped-loading samples：`5`
- Highest severity：`high`
- Severity reason：`all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Recommended severity action：`avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Recommended triage action：`review_recent_budget_warning_samples_and_record_turn_context`

## 相比 2026-06-18 06:31 证据的新观察

- 之前已提交的 2026-06-18 06:31 CST 记录在窄 post-final 窗口内发现 `9` 个 budget warnings、`0` 个 skipped-loading warnings，maximum omitted additional skills 为 `16`。
- 本 2026-06-18 07:08 CST probe 在 06:31 证据 cutoff 之后发现 `5` 个 budget warnings、`5` 个 skipped-loading warnings，maximum omitted additional skills 为 `15`。
- Warning pressure 仍为 `high`，因为每个被检测到的 budget warning 仍然移除了全部 skill descriptions。
- Skipped-loading pressure 在这个窄 continuation 窗口中重新出现，必须作为 source signal 复核，不得通过编辑 vendor cache 直接修复。
- 这支持继续 monitoring 与人工复核，不支持 profile apply。

## 脱敏样本处理

- Raw sample excerpts 只保留在 `.tmp/` summary/JSON 中，此处不复制，因为即使完成路径脱敏后，它们仍可能包含 model-readable replay context、thread identifiers、token counters 或其他 runtime metadata。
- Review policy：`record_source_and_do_not_edit_vendor_cache_without_authorization`。

## Audit state

- Audit state：`ready-for-summary`
- Audit reason：`audit_window_at_least_30_days`
- Next action：`generate_sanitized_30_day_markdown_summary_before_profile_apply_candidate`
- Profile apply allowed：`False`
- Current inferred profile：`full`
- Plugin entries in config：`40`
- Total discovered skills：`330`

## Gate 证据

- Field contract passed：`True`
- Field contract blockers：`0`
- Output retention gate：`passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations：`0`
- Pre-commit update/archive embedded gate：`passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors：`0`

## Triage run 决策分桶

- profile_review_candidates：`full`, `web-saas`
- on_demand_soft_load：`creative-content`
- manual_review_medium_or_weak：`company-ops`, `core-dev`, `customer-comms`, `market-research`
- dormant_restorable：`none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 0 | no_mapped_tool_call_medium_evidence | 41 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| web-saas | 10 | no_mapped_tool_call_medium_evidence | 55 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 0 | no_mapped_tool_call_medium_evidence | 25 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| market-research | 0 | no_mapped_tool_call_medium_evidence | 17 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| customer-comms | 0 | no_mapped_tool_call_medium_evidence | 13 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| creative-content | 4 | no_mapped_tool_call_medium_evidence | 18 | manual_review_required | keep_module_on_demand_and_continue_audit |
| full | 12 | no_mapped_tool_call_medium_evidence | 133 | manual_review_required | candidate_for_project_or_default_profile_review |

## 复核结论

1. 窄 triage 窗口有效，并发现 warning pressure 仍持续为 high。
2. 当前 profile 仍推断为 `full`，warning pressure 仍与过大的 model-visible skills surface 相关。
3. `full` 与 `web-saas` 仍是 profile-review candidates；`creative-content` 当前是 on-demand soft-load evidence；`core-dev`、`company-ops`、`customer-comms` 与 `market-research` 仍需要 manual review。
4. 最终 30 天摘要仍为 `human_review_pending`；本 monitoring evidence 不关闭 audit。
5. 本 triage 是 audit-only，不授权编辑 `config.toml`、vendor/plugin cache、hard-load profiles 或 user-level runtime settings。
6. 本记录未授权 preview-only candidate 或 profile apply。
