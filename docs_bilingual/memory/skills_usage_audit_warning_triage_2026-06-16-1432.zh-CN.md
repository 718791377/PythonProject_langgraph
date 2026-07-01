---
doc_id: skills_usage_audit_warning_triage_2026_06_16_1432
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-16
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.md
---
# Skills 使用审计预警复核 2026-06-16 14:32 CST

本文保存新增 live-session skills-budget warning 后的一日窄窗口脱敏复核证据。原始 JSON、原始摘要、transcript、runtime log、thread ID、token counter 与完整 warning excerpt 只保留在本地 `.tmp/`，不提交入库。

## 复核窗口

- Since: `2026-06-15T06:32:35.530324+00:00`
- Until: `2026-06-16T06:32:35.530324+00:00`
- Days: `1`
- 是否请求 warning triage: `True`
- Warning triage 状态: `warning_found`
- 窗口策略: `use_days_1_or_since_for_warning_triage`
- 窗口是否合规: `True`
- Blockers: `none`

## Warning 信号

- 复核窗口内 budget warnings: `32`
- 复核窗口内 skipped-loading warnings: `38`
- All descriptions removed 次数: `32`
- 最大 omitted additional skills: `16`
- 保留的 budget-warning 样本数量: `3`
- 保留的 skipped-loading 样本数量: `3`
- 最高严重度: `high`
- 严重度原因: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- 严重度建议动作: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`
- Triage 建议动作: `review_recent_budget_warning_samples_and_record_turn_context`

## 相对 10:35 证据的新观察

- 已提交的 10:35 记录为 `33` 个 budget warnings 与 `23` 个 skipped-loading warnings。
- 本次 14:32 探针在一日窗口内为 `32` 个 budget warnings 与 `38` 个 skipped-loading warnings。
- skipped-loading 证据明显升高，并且脚本能够提取有界脱敏样本；这支持继续 monitoring 与人工复核，但不授权 profile apply。

## 脱敏 skipped-loading 样本形态

- 原始摘要中渲染的样本数量: `3`
- 样本摘录只保留在 `.tmp/` summary/JSON 中，不复制到本文，因为即使路径已脱敏，仍可能包含 model-readable replay context。
- 复核策略: `record_source_and_do_not_edit_vendor_cache_without_authorization`

## 审计状态

- 审计状态: `running`
- 审计原因: `audit_window_shorter_than_30_days`
- 下一步: `continue_audit_collection_without_profile_apply`
- 是否允许 profile apply: `False`
- 当前推断 profile: `full`
- config 中 plugin 条目数: `40`
- 发现的 skills 总数: `315`

## Gate 证据

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## 本次 triage 的决策分桶

- profile_review_candidates: `creative-content, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev, customer-comms`
- manual_review_medium_or_weak: `market-research`
- dormant_restorable: `none`

## 复核结论

1. 一日 triage 窗口有效，并且发现持续高压 warning。
2. 本次 probe 的 skipped-loading warning 证据升至 `38`，这是本轮主要新增 monitoring 信号。
3. 证据仍支持审计期间避免把 `full` 作为默认 profile，但不构成 profile apply 授权。
4. 最终 30 天摘要仍处于 `human_review_pending`；本 monitoring 证据不关闭审计。
5. 本次 triage 仅为 audit-only，不授权编辑 `config.toml`、vendor/plugin cache、hard-load profiles 或用户级 runtime settings。
6. 本记录不授权 preview-only candidate 或 profile apply。
