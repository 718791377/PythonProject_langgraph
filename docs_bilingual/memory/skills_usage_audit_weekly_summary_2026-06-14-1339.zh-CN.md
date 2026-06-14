---
doc_id: skills_usage_audit_weekly_summary_2026_06_14_1339
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-14
audit_run_type: weekly_summary
canonical: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-14-1339.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_weekly_summary_2026-06-14-1339.md
---

# Skills Usage Audit 周报摘要 2026-06-14 13:39 CST

本记录保存 Codex skills usage audit 的脱敏滚动七天证据。原始 JSON、stdout、transcript、runtime log、warning excerpt、thread ID 与 token counter 仍仅保留在 `.tmp/` 本地目录，不提交到 Git。

## 审计窗口

- Since: `2026-06-07T05:39:41.805982+00:00`
- Until: `2026-06-14T05:39:41.805982+00:00`
- Days: `7`
- Audit state: `running` (`audit_window_shorter_than_30_days`)
- Next action: `continue_audit_collection_without_profile_apply`
- Profile apply allowed: `False`
- Weekly report review: `manual_review_required`

## 配置与 warning 压力

- Config enabled plugin entries: `40`
- Inferred current profile: `full`
- Budget warning count: `46`
- Last seven-day budget warning count: `46`
- All-descriptions-removed count: `46`
- Maximum omitted additional skills: `62`
- Skipped-loading count: `60`
- Latest retained warning time: `2026-06-14T13:36:53+08:00`
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

## 本次周报决策分桶

- profile_review_candidates: `creative-content, customer-comms, full, web-saas`
- on_demand_soft_load: `company-ops, core-dev, market-research`
- manual_review_medium_or_weak: `none`
- dormant_restorable: `none`

## 复核结论

1. 审计仍处于 `running` 状态，因为真实 30 天观察窗口尚未完成。
2. Latest retained warning time 为 `2026-06-14T13:36:53+08:00`，保留 2026-06-13 23:13 记录之后继续出现的 live-session pressure 证据。
3. 当前 `full` profile 仍与 high live-turn skills-budget pressure 相关。
4. 本证据仅为 advisory audit-only 证据，不授权 profile apply。
5. 继续收集周报证据，并在未来 live-session warnings 后运行窄窗口 warning triage。
