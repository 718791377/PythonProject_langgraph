---
doc_id: skills_usage_audit_weekly_summary_2026_06_13_2031
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-13
audit_run_type: weekly_summary
canonical: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-13-2031.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-13-2031.md
---

# Skills Usage Audit 七日汇总 2026-06-13 20:31 CST

本文保留 Codex skills usage audit 的脱敏七日滚动证据。原始 JSON、stdout、会话 transcript、runtime log、warning excerpt、thread ID 与 token 计数都只保留在本地 `.tmp/`，不提交到 Git。

## 审计窗口

- Since: `2026-06-06T12:28:12.917636+00:00`
- Until: `2026-06-13T12:28:12.917636+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## 配置与 warning 压力

- Config 中 enabled plugin entries: `40`
- 推断 current profile: `full`
- Current profile source: `inferred_from_enabled_plugin_entries`
- Budget warning count: `44`
- Last 7d budget warning count: `44`
- All-descriptions-removed count: `44`
- Maximum omitted additional skills: `62`
- Skipped-loading count: `55`
- Latest retained warning time: `2026-06-13T20:27:44+08:00`
- Highest severity: `high`
- Severity reason: `all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## 门禁证据

- Field contract passed: `True`
- Field contract blockers: `0`
- Output retention gate: `passed` via `tools/check_skills_audit_output_retention.py`
- Output retention violations: `0`
- Pre-commit update/archive embedded gate: `passed` via `tools/check_precommit_update_archive.py`
- Pre-commit update/archive errors: `0`

## 本轮决策分桶

- profile_review_candidates: `creative-content, customer-comms, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

## 复核结论

1. 真实 30 天观察窗口尚未结束，审计状态保持 `running`。
2. 最新 retained warning time 推进到 `2026-06-13T20:27:44+08:00`，保留了持续 live-session pressure 证据。
3. 当前 `full` profile 仍与较高 live-turn skills-budget 压力相关。
4. 本证据仅用于 advisory / audit-only 复核，不授权 profile apply。
5. 继续收集 weekly evidence；未来 live-session warning 出现后继续执行窄窗口 warning triage。
