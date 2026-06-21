---
doc_id: skills_usage_audit_warning_triage_2026_06_21_0826
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-21
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0826.md
---
# Skills Usage Audit 警告分诊 2026-06-21 08:26 CST

本记录保存新的 post-final `2% skills context budget` 警告分诊证据。原始 JSON、stdout、会话转录、运行时日志、警告原文摘录、线程 ID、请求 ID、响应 ID、调用 ID、token 计数和完整运行时上下文都只保留在本地，不提交到仓库。

## 分诊窗口

- since 参数：`1d`
- 近似运行时间：`2026-06-21 08:26 CST`
- 是否为 warning triage：`True`
- 窗口策略：`event_triggered_narrow_window`
- 窗口是否合规：`True`
- 阻塞项：`none`

## 警告信号

- 汇总 budget warning 数：`998`
- 汇总 skipped-loading 数：`1881`
- 汇总 all-descriptions-removed 数：`200`
- 最大 omitted additional skills：`16`
- `sessions_jsonl` budget/skipped/all-removed：`291` / `621` / `96`
- `logs_2.sqlite` budget/skipped/all-removed：`707` / `1260` / `104`
- 最高严重度：`high`
- 建议动作：继续保持 review-pending monitoring；没有后续明确授权前，不编辑 plugin cache、hard-load profiles 或 `config.toml`。

## 脱敏增强证据

本次运行基于 `tools/skills2cli.py audit warnings` 的运行时脱敏加固：

- call ID 替换为 `[REDACTED_ID]`；
- response ID 替换为 `[REDACTED_ID]`；
- UUID 形态运行时标识替换为 `[REDACTED_ID]`；
- request、thread、session、submission、turn、connection 等赋值形态运行时标识替换为 `[REDACTED_ID]`；
- token 计数字段替换为 `[REDACTED_TOKEN_COUNT]`；
- 私有路径和 secret 继续替换为 `[REDACTED_PATH]` 与 `[REDACTED_SECRET]`。

本证据记录故意不复制原始摘录。长期保留证据只包含汇总计数和上述脱敏契约。

## 人工/来源复核结论

- 已发现新的 post-final 警告，因此 monitoring 事项继续保持 active。
- skipped-loading 压力只是来源证据，不授权编辑 vendor/plugin cache。
- 最终 30 天摘要仍为 `human_review_pending`。
- candidate generation 仍为 `not_requested`。
- profile apply 仍为 `not_authorized`。

## 未执行动作

- 未将最终摘要标记为 `summary-reviewed`。
- 未生成 candidate JSON 或 candidate Markdown。
- 未执行 profile apply。
- 未编辑 Codex `config.toml`、plugin cache、hard-load profiles、用户级 wrapper 或用户级 runtime 设置。
- 未提交 raw JSON、stdout、会话转录、运行时日志、警告原文摘录、线程 ID、请求 ID、响应 ID、调用 ID 或 token 计数。
- 未修改远端 refs。
