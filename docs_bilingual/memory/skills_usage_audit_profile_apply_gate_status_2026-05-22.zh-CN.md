---
doc_id: skills_usage_audit_profile_apply_gate_status_2026-05-22
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-05-22
audit_run_type: profile_apply_gate_status
---

# Skills Usage Audit profile apply 门禁状态证据（2026-05-22）

本文件记录 `codex_skills_usage_audit_plan` 中 candidate、profile apply 与 rollback 相关清单项的当前门禁状态。它不是 profile apply 候选记录，也不是 apply 授权记录；它只说明当前为什么不能提前执行 hard-load/profile apply。

## 当前门禁结论

- 30 天 usage audit 观察期尚未以本计划要求的方式完成。
- 最终 30 天 JSON 报告尚未生成。
- 最终脱敏 Markdown 摘要尚未生成。
- 最终摘要尚未经过人工复核并标记为 `summary-reviewed`。
- 当前没有 `approved-to-apply` 授权。
- 因此不得生成正式 apply 操作，不得修改 `config.toml`，不得编辑 vendor/plugin cache，不得执行 hard-load/profile apply。

## candidate 预览门禁

在生成 preview-only candidate 之前，必须同时满足：

1. 已完成 30 天观察期。
2. 已生成最终 JSON 报告和最终脱敏 Markdown 摘要。
3. 最终摘要已人工复核并标记为 `summary-reviewed`。
4. 已处理最终摘要中的噪声误报、人工冲突或例外。
5. 已明确候选 `target_profile`。
6. candidate JSON 与 candidate Markdown 均保持 preview-only，不得产生配置副作用。
7. candidate 记录必须包含 source reports、source report privacy、current profile、target profile、plugin diff、evidence basis、risk review、rollback path 与 validation plan。

## apply 授权门禁

即使 preview-only candidate 已生成，也必须等待用户明确 `approved-to-apply` 授权后才能执行 profile apply。普通“继续”“实施计划”“提交本地仓库”不等于 apply 授权。

获得授权前允许：

- 继续收集 usage audit 证据。
- 继续生成 7 天周报、warning triage、人工复核和来源复核证据。
- 生成 preview-only candidate，但前提是满足 candidate 预览门禁。

获得授权前禁止：

- 修改 `config.toml`。
- 修改 plugin cache 或 vendor `SKILL.md`。
- 执行 hard-load/profile apply。
- 将 advisory-only recommendation 当成自动 apply 指令。

## rollback 预案门禁

如果未来获得授权并执行 profile apply，必须保存 apply 前后脱敏 diff，并至少验证：

- `2% skills context budget` warning 是否消失或显著降低。
- 常用能力是否仍可见或可按需加载。
- browser/web、Vercel、Cloudflare、GitHub、OpenAI Developers、Documents、Presentations、Spreadsheets 等高价值能力是否未被误伤。
- 如果 warning 仍出现，按 candidate rollback path 回滚。
- 如果关键能力缺失，按 candidate rollback path 回滚。

## 本轮安全边界

- 本文件不包含 raw JSON、stdout、session transcript 或本地绝对路径。
- 本文件不修改 runtime 配置、plugin cache 或 hard-load profile。
- 本文件只作为门禁状态证据，不等于 30 天审计完成，也不等于 `summary-reviewed`。