---
doc_id: skills_usage_audit_warning_triage_2026_06_22_0858
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-22
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-22-0858.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-22-0858.md
---
# Skills Usage Audit 警告分诊 2026-06-22 08:58 CST

本记录仅保存 2026-06-22 当前 live session 中新出现的 `2% skills context budget` warning 的脱敏 post-final 分诊证据。
原始 JSON、stdout、transcript、runtime log、warning excerpt、运行时标识、请求或响应标识、token 计数和完整上下文均保持为本地临时文件，不提交入库。

## 分诊窗口

- 命令族：`tools/audit_codex_skills_usage.py --since 2026-06-22 --warning-triage`
- 近似执行时间：`2026-06-22 08:58 CST`
- 已请求 warning triage：`True`
- 窗口策略：`use_days_1_or_since_for_warning_triage`
- 窗口通过：`True`
- 分诊状态：`warning_found`
- 阻塞项：`none`

## 警告信号

- Budget warning 次数：`9`
- 最近 7 天 budget warning 次数：`9`
- All descriptions removed 次数：`9`
- 最大 omitted additional skills：`15`
- Skipped-loading 次数：`9`
- 最高严重度：`high`
- 严重度原因：`all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- 当前 frontmatter invalid skills：`0`
- Frontmatter 结论：`historical_warning_current_inventory_clean`
- 字段契约：`passed`
- 输出留存门禁：`passed`
- pre-commit update/archive 内嵌门禁：`passed`

## 来源复核结论

- 当前 live session 中发现新的 post-final warning，因此 monitoring 事项继续保持 active。
- 当前 warning pressure 仍为 high，继续支持使用更小的 task profile 和 `skills2cli profile suggest` 重排建议，而不是把 `full` 当成普通任务 top-1 profile。
- 当前 frontmatter compatibility 干净：`invalid_total=0`。
- Skipped-loading pressure 只是来源证据，不授权编辑 vendor/plugin cache。
- 本报告仍为 advisory-only：`profile_apply_allowed=false`、`mutates_config=false`、`edits_plugin_cache=false`、`hard_load_apply_performed=false`。

## 验证证据

- `tools/audit_codex_skills_usage.py --since 2026-06-22 --warning-triage`：通过，并在 `.tmp/` 生成本地临时 raw JSON，同时生成本脱敏 Markdown 证据。
- 内嵌字段契约：`passed`。
- 输出留存契约：`passed`；长期入库证据仅为脱敏 Markdown。
- 当前 frontmatter bridge：`invalid_total=0`。

## 最终复核状态保持不变

- 最终 30 天摘要仍为 `human_review_pending`。
- closure decision 仍待定。
- candidate generation 仍为 `not_requested`。
- profile apply 仍为 `not_authorized`。

## 未执行事项

- 未把最终摘要标记为 `summary-reviewed`。
- 未生成 candidate JSON 或 candidate Markdown。
- 未执行 profile apply。
- 未编辑 Codex `config.toml`、plugin cache、hard-load profiles、user-level wrappers 或 user-level runtime settings。
- 未提交 raw JSON、stdout、transcripts、runtime logs、warning excerpts、runtime identifiers 或 token counters。
- 未修改远端 refs。
