---
doc_id: skills_usage_audit_weekly_summary_2026_06_15_2030
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-15
audit_run_type: weekly_summary
canonical: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-15-2030.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-15-2030.md
---

# Skills Usage Audit 周报摘要 2026-06-15 20:30 CST

本记录保存 Codex skills usage audit 的脱敏滚动七天证据；最终 30 天摘要仍处于人工待复核状态。原始 JSON、stdout、transcript、runtime log、warning excerpt、thread ID 与 token counter 仍仅保留在 `.tmp/` 本地目录，不提交到 Git。

## 审计窗口

- Since: `2026-06-08T12:27:58.917076+00:00`
- Until: `2026-06-15T12:27:58.917076+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## 配置与 warning 压力

- Enabled plugin entries in config: `40`
- Inferred current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Budget warning count: `38`
- Last seven-day budget warning count: `38`
- All-descriptions-removed count: `38`
- Maximum omitted additional skills: `62`
- Skipped-loading count: `51`
- Latest retained budget warning time: `2026-06-14T19:31:07+08:00`
- Latest retained skipped-loading time: `2026-06-15T20:07:39+08:00`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## Gate evidence

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## 本次周报决策分档

- profile_review_candidates: `creative-content, customer-comms, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

## 复核结论

1. 本滚动七天报告的审计状态仍为 `running`，不改变最终 30 天摘要的人工复核门禁。
2. 滚动窗口仍显示与当前推断的 `full` profile 相关的高预算 warning 压力。
3. 滚动窗口内仍有较新的 skipped-loading 信号，因此 skipped-loading 来源复核仍是监控事项。
4. 本证据仅为 advisory 与 audit-only，不授权 profile apply、candidate generation 或编辑 user-level runtime settings。
5. 最终 30 天摘要保持 `human_review_pending`，直到记录明确的人工决策。
