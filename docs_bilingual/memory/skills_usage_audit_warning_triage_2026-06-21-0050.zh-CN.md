---
doc_id: skills_usage_audit_warning_triage_2026_06_21_0050
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-21
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0050.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0050.md
---
# Skills Usage Audit Warning Triage 2026-06-21 00:50 CST

本记录保存额外 live-session skills-budget warnings 之后的脱敏 post-final warning-triage 证据。Raw JSON、generated stdout、transcripts、runtime logs、thread IDs、token counters 与完整 warning excerpts 仍仅保留在 `.tmp/` 本地目录，不提交到 Git。

## Triage 窗口

- Since：`2026-06-19T16:51:02.434214+00:00`
- Until：`2026-06-20T16:51:02.434214+00:00`
- Days：`1`
- Warning triage requested：`True`
- Warning triage status：`warning_found`
- Window policy：`use_days_1_or_since_for_warning_triage`
- Window OK：`True`
- Since override used：`False`
- Blockers：`none`

## Warning 信号

- Budget warnings in triage window：`43`
- Skipped-loading warnings in triage window：`29`
- All-descriptions-removed count：`35`
- Maximum omitted additional skills：`16`
- Recent retained budget-warning samples：`20`
- Recent retained skipped-loading samples：`20`
- Highest severity：`high`
- Severity reason：`all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Recommended severity action：`avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Recommended triage action：`review_recent_budget_warning_samples_and_record_turn_context`

## 相比 2026-06-18 06:31 证据的新观察

- 之前已提交的 2026-06-18 06:31 CST 记录在窄 post-final 窗口内发现 `9` 个 budget warnings、`0` 个 skipped-loading warnings，maximum omitted additional skills 为 `16`。
- 本 2026-06-21 00:50 CST probe 在当前一天窗口内发现 `43` 个 budget warnings、`29` 个 skipped-loading warnings、`35` 个 all-descriptions-removed events，maximum omitted additional skills 为 `16`。
- Warning pressure 仍为 `high`，因为 all-descriptions-removed events 持续存在，且一天 budget warning count 明显高于 high-pressure 阈值。
- Skipped-loading pressure 在此窗口重新出现，必须只作为 source evidence 复核；它不授权编辑 vendor/plugin cache。
- 这支持继续 monitoring 与人工复核，不支持 profile apply。

## 脱敏样本处理

- Raw sample excerpts 只保留在 `.tmp/` summary/JSON 中，此处不复制，因为即使完成路径脱敏后，它们仍可能包含 model-readable replay context、thread identifiers、token counters 或其他 runtime metadata。
- Review policy：`record_source_and_do_not_edit_vendor_cache_without_authorization`。

## Audit state

- Audit state：`running`
- Audit reason：`audit_window_shorter_than_30_days`
- Next action：`continue_audit_collection_without_profile_apply`
- Profile apply allowed：`False`
- Current inferred profile：`full`
- Plugin entries in config：`40`
- Total discovered skills：`1270`

## Gate 证据

- Field contract passed：`True`
- Field contract blockers：`0`
- Output retention gate：`passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations：`0`
- Pre-commit update/archive embedded gate：`passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors：`0`

## Triage run 决策分桶

- profile_review_candidates：`core-dev, creative-content, customer-comms, full, web-saas`
- on_demand_soft_load：`none`
- manual_review_medium_or_weak：`company-ops, market-research`
- dormant_restorable：`none`

| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |
| --- | ---: | --- | ---: | --- | --- |
| core-dev | 26 | mapped_tool_calls_present_manual_review_required | 3980 | manual_review_required | candidate_for_project_or_default_profile_review |
| web-saas | 111 | mapped_tool_calls_present_manual_review_required | 3977 | manual_review_required | candidate_for_project_or_default_profile_review |
| company-ops | 0 | no_mapped_tool_call_medium_evidence | 818 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| market-research | 0 | no_mapped_tool_call_medium_evidence | 521 | manual_review_required | mentioned_only_do_not_apply_without_strong_evidence |
| customer-comms | 12 | no_mapped_tool_call_medium_evidence | 629 | manual_review_required | candidate_for_project_or_default_profile_review |
| creative-content | 40 | no_mapped_tool_call_medium_evidence | 869 | manual_review_required | candidate_for_project_or_default_profile_review |
| full | 148 | mapped_tool_calls_present_manual_review_required | 5978 | manual_review_required | candidate_for_project_or_default_profile_review |

## 复核结论

1. 窄 triage 窗口有效，并发现 warning pressure 仍持续为 high。
2. 当前 profile 仍推断为 `full`，warning pressure 仍与过大的 model-visible skills surface 相关。
3. 本记录中看似 candidate 的分桶仍只是 review inputs；它们不是生成 candidate 或 apply profile 的授权。
4. 最终 30 天摘要仍为 `human_review_pending`；本 monitoring evidence 不关闭 audit。
5. 本 triage 是 audit-only，不授权编辑 `config.toml`、vendor/plugin cache、hard-load profiles 或 user-level runtime settings。
6. 本记录未授权 preview-only candidate 或 profile apply。
