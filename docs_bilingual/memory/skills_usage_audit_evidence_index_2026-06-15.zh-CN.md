---
doc_id: skills_usage_audit_evidence_index_2026_06_15
lang: zh-CN
status: active
doc_class: audit_evidence_index
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-15
canonical: docs_bilingual/memory/skills_usage_audit_evidence_index_2026-06-15.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_evidence_index_2026-06-15.md
---

# Skills Usage Audit 证据索引 2026-06-15

本索引用于让当前最终复核证据包可发现，但不改变审计决策状态。它不会把摘要标记为 reviewed，不会生成 candidate，也不会授权 profile apply。

## 当前决策状态

- 最终 30 天摘要状态：`human_review_pending`
- Candidate generation state: `not_requested`
- Profile apply state: `not_authorized`
- 当前允许动作：仅人工复核或继续监控

## 证据包

| 证据 | 路径 | 用途 |
| --- | --- | --- |
| 最终 30 天摘要 | `docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md` | 脱敏 30 天报告与 gate 证据 |
| 中文最终 30 天摘要 | `docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md` | 最终报告的中文 companion |
| 人工复核准备 | `docs_bilingual/memory/skills_usage_audit_summary_review_prep_2026-06-15-1209.md` | 机器预复核与安全决策路径 |
| 中文人工复核准备 | `docs_bilingual/memory/skills_usage_audit_summary_review_prep_2026-06-15-1209.zh-CN.md` | 预复核记录的中文 companion |
| 待复核延续记录 | `docs_bilingual/memory/skills_usage_audit_review_pending_continuation_2026-06-15-2030.md` | 最终复核待定期间的后续监控证据 |
| 中文待复核延续记录 | `docs_bilingual/memory/skills_usage_audit_review_pending_continuation_2026-06-15-2030.zh-CN.md` | 后续监控记录的中文 companion |
| 人工复核决策模板 | `docs_bilingual/memory/skills_usage_audit_human_review_decision_template_2026-06-15.md` | 用于记录明确人工决策的模板 |
| 中文人工复核决策模板 | `docs_bilingual/memory/skills_usage_audit_human_review_decision_template_2026-06-15.zh-CN.md` | 决策模板的中文 companion |

## 安全下一步

1. 阅读最终 30 天摘要和复核准备记录。
2. 使用人工复核决策模板选择一个明确结果。
3. 如果结果是 `summary-reviewed + closed-no-change`，使用 `--summary-reviewed --close-audit no-change` 运行审计脚本并保存脱敏关闭记录。
4. 如果结果是 `summary-reviewed + preview-only candidate`，使用 `--summary-reviewed --target-profile <profile> --candidate-output ... --candidate-summary-output ...` 运行审计脚本，并保持 candidate 为 `preview-only`。
5. 后续没有明确 `approved-to-apply` 授权前，不执行任何 profile apply。

## 未执行事项

- 未将摘要标记为 `summary-reviewed`。
- 未生成 candidate JSON 或 candidate Markdown。
- 未应用任何 profile。
- 未编辑 config.toml、plugin cache、hard-load profile 或 user-level runtime settings。
