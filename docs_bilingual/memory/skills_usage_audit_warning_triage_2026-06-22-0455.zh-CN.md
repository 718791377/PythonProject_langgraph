---
doc_id: skills_usage_audit_warning_triage_2026_06_22_0455
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-22
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-22-0455.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-22-0455.md
---
# Skills Usage Audit 警告分诊 2026-06-22 04:55 CST

本记录保存 2026-06-22 live session 再次出现 `2% skills context budget` 警告后的 post-final warning triage 脱敏证据。原始 JSON、生成的 stdout、会话转录、运行时日志、警告原文摘录、thread/request/response/call 标识、token 计数以及完整运行时上下文都仅保留在本地，不提交到仓库。

## 分诊窗口

- 命令族：`tools/audit_codex_skills_usage.py --since 2026-06-21 --warning-triage`
- 近似运行时间：`2026-06-22 04:55 CST`
- 是否请求 warning triage：`True`
- 窗口策略：`use_days_1_or_since_for_warning_triage`
- 窗口是否合规：`True`
- 分诊状态：`warning_found`
- 阻塞项：`none`

## 警告信号

- Budget warning 数：`145`
- Skipped-loading 数：`128`
- All-descriptions-removed 数：`137`
- 最大 omitted additional skills：`16`
- 最高严重度：`high`
- 严重度原因：`all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3`
- 当前 frontmatter invalid skills：`0`
- frontmatter resolution：`historical_warning_current_inventory_clean`
- 字段契约：`passed`
- 输出留存门禁：`passed`
- 提交前更新/归档嵌入门禁：`passed`

## 来源复核结论

- 已发现新的 post-final 警告，因此 monitoring 事项继续保持 active。
- 当前 warning pressure 为 high，仍支持优先使用较小任务 profile 或 advisory profile suggestion，而不是把普通任务推荐到 `full` profile。
- 当前 frontmatter compatibility 干净：`invalid_total=0`；除非未来当前 inventory 检查给出相反证据，否则 skipped-loading/frontmatter warning 修复闭环保持 resolved。
- skipped-loading 压力只是来源证据，不授权编辑 vendor/plugin cache。
- 本报告仍是 advisory-only：`profile_apply_allowed=false`、`mutates_config=false`、`edits_plugin_cache=false`、`hard_load_apply_performed=false`。

## 验证证据

- `tools/audit_codex_skills_usage.py --since 2026-06-21 --warning-triage`：通过，并在 `.tmp/` 下生成 local-only 原始 JSON，同时生成本脱敏 Markdown 证据。
- 内嵌字段契约：`passed`。
- 输出留存契约：`passed`；提交到仓库的长期证据仅为脱敏 Markdown。
- 当前 frontmatter bridge：`invalid_total=0`。

## 保持最终复核状态

- 最终 30 天摘要仍为 `human_review_pending`。
- closure decision 仍待处理。
- candidate generation 仍为 `not_requested`。
- profile apply 仍为 `not_authorized`。

## 未执行动作

- 未将最终摘要标记为 `summary-reviewed`。
- 未生成 candidate JSON 或 candidate Markdown。
- 未执行 profile apply。
- 未编辑 Codex `config.toml`、plugin cache、hard-load profiles、用户级 wrapper 或用户级 runtime 设置。
- 未提交 raw JSON、stdout、会话转录、运行时日志、警告原文摘录、运行时标识或 token 计数。
- 未修改远端 refs。
