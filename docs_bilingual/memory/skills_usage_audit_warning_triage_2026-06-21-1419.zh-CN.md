---
doc_id: skills_usage_audit_warning_triage_2026_06_21_1419
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-21
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-1419.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-1419.md
---
# Skills Usage Audit 警告分诊 2026-06-21 14:19 CST

本记录保存新的 post-final `2% skills context budget` 警告分诊证据。原始 JSON、stdout、会话转录、运行时日志、警告原文摘录、运行时标识和 token 计数都仅保留在本地，不提交到仓库。

## 分诊窗口

- 命令族：`tools/audit_codex_skills_usage.py --days 1 --warning-triage`
- 近似运行时间：`2026-06-21 14:19 CST`
- 是否为 warning triage：`True`
- 窗口策略：`use_days_1_or_since_for_warning_triage`
- 窗口是否合规：`True`
- 分诊状态：`warning_found`
- 阻塞项：`none`

## 警告信号

- Budget warning 数：`123`
- Skipped-loading 数：`99`
- All-descriptions-removed 数：`97`
- 最大 omitted additional skills：`16`
- 最高严重度：`high`
- 字段契约：`passed`
- 输出留存门禁：`passed`
- 提交前更新/归档嵌入门禁：`passed`

## 脱敏加固证据

本次运行基于 `tools/audit_codex_skills_usage.py` 的长期保留 warning 摘录脱敏加固：

- 运行时赋值标识替换为 `[REDACTED_ID]`；
- 调用与响应实例标识替换为 `[REDACTED_ID]`；
- UUID 形态标识替换为 `[REDACTED_ID]`；
- token 计数字段替换为 `[REDACTED_TOKEN_COUNT]`；
- 私有路径和 secret 继续替换为 `[REDACTED_PATH]` 与 `[REDACTED_SECRET]`；
- 脱敏标记不会被截断成半个标记；
- 字段契约现在会在长期保留的 budget-warning 或 skipped-loading 摘录仍包含原始运行时标识或 token 计数时 fail closed。

本证据记录故意不复制原始摘录。长期证据只保留汇总计数、门禁状态和上述脱敏契约。

## 验证证据

- `python -m py_compile tools/audit_codex_skills_usage.py`：通过。
- `python test/audit_codex_skills_usage.test.py`：通过，`69` 个测试。
- `tools/audit_codex_skills_usage.py --days 1 --warning-triage`：通过，并在 `.tmp/` 下生成本地-only JSON / Markdown。
- 对生成的 `.tmp` JSON、Markdown 与 stdout JSON 执行本地脱敏扫描，未发现本切片目标中的原始运行时标识或 token 计数模式。

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
- 未提交 raw JSON、stdout、会话转录、运行时日志、警告原文摘录、运行时标识或 token 计数。
- 未修改远端 refs。
