---
doc_id: skills_usage_audit_human_review_decision_template_2026_06_15
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-15
audit_run_type: human_review_decision_template
canonical: docs_bilingual/memory/skills_usage_audit_human_review_decision_template_2026-06-15.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_human_review_decision_template_2026-06-15.md
---

# Skills Usage Audit 人工复核决策模板 2026-06-15

本模板把最终 30 天 Skills usage audit 转成结构化的人类复核决策记录。它本身不会把摘要标记为 reviewed，不会生成 candidate，也不会授权 profile apply。

## 源证据

- 最终 30 天摘要：`docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md`
- 中文最终 30 天摘要：`docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md`
- 复核准备记录：`docs_bilingual/memory/skills_usage_audit_summary_review_prep_2026-06-15-1209.md`
- 中文复核准备记录：`docs_bilingual/memory/skills_usage_audit_summary_review_prep_2026-06-15-1209.zh-CN.md`

## 决策字段

只填写一个结论：

- `summary-reviewed + closed-no-change` - 最终审计关闭且不变更 profile
- `summary-reviewed + preview-only candidate` - 准备一个 preview-only 的 profile 提案
- `review-pending + continue monitoring` - 在决策前继续收集证据

如果选择 preview-only candidate，还需要补充：

- `target_profile` - 为该 candidate 选定的明确 profile 或模块名
- candidate 复核备注
- rollback path 复核备注
- validation plan 复核备注
- 后续 `approved-to-apply` 记录：yes/no

## 复核清单

- 确认已完整阅读 30 天摘要。
- 确认是否要把摘要标记为 `summary-reviewed`。
- 确认是否将审计关闭为 `closed-no-change`。
- 如果需要 candidate，选择一个明确的 `target_profile`。
- 确认 candidate 输出保持 preview-only。
- 确认在后续明确授权前不执行 profile apply。
- 记录任何噪声误报或人工例外。

## 推荐操作

从下面三种结果中选择一种，并把决策写入 companion note 文件：

1. `summary-reviewed + closed-no-change` - 最终审计关闭且不变更 profile
2. `summary-reviewed + preview-only candidate` - 准备一个 preview-only 的 profile 提案
3. `review-pending + continue monitoring` - 在决策前继续收集证据

## 未执行事项

- 未生成 profile candidate。
- 未将摘要标记为 reviewed。
- 未应用任何 profile。
- 未编辑 config.toml、plugin cache 或 hard-load profiles。
