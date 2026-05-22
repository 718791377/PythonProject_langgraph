---
doc_id: skills_usage_audit_skipped_loading_source_review_2026-05-22
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
source_report: .tmp/skills-usage-audit-skipped-loading-source-review-2026-05-22.json
generated_at: 2026-05-22
audit_run_type: skipped_loading_source_review
audit_window_days: 1
---

# Skills Usage Audit skipped-loading 来源复核（2026-05-22）

本文件落实 `codex_skills_usage_audit_plan` 清单中“对新的 skipped-loading 样本做来源复核”的长期证据要求。原始 JSON、stdout 与临时 summary 仅保留在 `.tmp/`，不进入 Git；本文件只保存脱敏后的复核结论。

## 复核窗口

- 生成时间：`2026-05-22T02:25:43.969907+00:00`
- 审计窗口：`2026-05-21T02:25:43.969907+00:00` 至 `2026-05-22T02:25:43.969907+00:00`，共 `1` 天。
- 审计状态：`running`；原因：`audit_window_shorter_than_30_days`；下一步：`continue_audit_collection_without_profile_apply`。
- profile apply allowed：`False`。

## skipped-loading 信号

- warning triage status：`warning_found`
- window_ok：`True`
- budget_warning_count：`29`
- skipped_loading_count：`29`
- recent_skipped_loading_samples：`20`
- all_descriptions_removed_count：`29`
- max_omitted_additional_skills：`15`
- skipped_loading_review：`record_source_and_do_not_edit_vendor_cache_without_authorization`
- warning severity：`high`；reason：`all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`；recommended_action：`avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## 来源判断

1. 本轮 skipped-loading 证据来自 Codex runtime 日志中的 model-visible skills surface / skills context budget 裁剪事件，而不是某个具体业务仓库文件读取失败。
2. 本轮样本与 `All skill descriptions were removed`、`omitted additional skills` 同时出现，说明主要来源是 skills context budget 超限后的运行时裁剪。
3. 本轮 evidence 不足以证明某个 vendor/plugin cache `SKILL.md` 文件格式错误；因此不能据此手改 plugin cache。
4. 当前正确动作是记录来源与 turn context，继续 audit-only 观察，并在 30 天汇总后再决定是否生成 preview-only profile candidate。
5. 如果后续日志明确指出具体 `SKILL.md` 缺少 YAML frontmatter、description 超长或 schema 违法，应另行生成“vendor skill metadata source review”证据，并在用户明确授权后处理 vendor cache。

## 安全与留存边界

- mutates_config：`False`
- edits_plugin_cache：`False`
- hard_load_apply_performed：`False`
- raw_paths_retained：`False`
- field_contract：`passed`
- output_retention：`passed`
- precommit_update_archive：`passed`

## 后续动作

- 继续按真实日历完成 30 天 usage audit 观察期。
- 会话中再次出现 budget warning 时，继续运行 1 天或 `--since` 窄窗口 warning triage。
- 每次新的 skipped-loading 样本出现后，优先区分“runtime budget 裁剪”与“具体 SKILL.md metadata 错误”。
- 30 天期满后，基于 summary-reviewed 与 preview-only candidate 再决定是否调整默认 profile。