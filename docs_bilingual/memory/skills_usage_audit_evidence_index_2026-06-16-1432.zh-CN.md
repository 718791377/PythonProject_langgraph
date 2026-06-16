---
doc_id: skills_usage_audit_evidence_index_2026_06_16_1432
lang: zh-CN
status: active
doc_class: audit_evidence_index
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-16
canonical: docs_bilingual/memory/skills_usage_audit_evidence_index_2026-06-16-1432.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_evidence_index_2026-06-16-1432.md
---
# Skills 使用审计证据索引 2026-06-16 14:32 CST

本索引登记最终摘要后的最新 monitoring 证据包。它仅为 audit-only，不改变决策状态。

## 当前决策状态

- 最终 30 天摘要状态: `human_review_pending`
- 候选生成状态: `not_requested`
- Profile apply 状态: `not_authorized`

## 证据包

| Evidence | Path | Purpose |
| --- | --- | --- |
| 人工待复核延续记录 | `docs_bilingual/memory/skills_usage_audit_review_pending_continuation_2026-06-16-1432.md` | 记录最终摘要后的 monitoring 决策边界 |
| 人工待复核延续记录 zh-CN | `docs_bilingual/memory/skills_usage_audit_review_pending_continuation_2026-06-16-1432.zh-CN.md` | 中文伴随文件 |
| 一日 warning triage | `docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.md` | 脱敏一日 warning-triage 指标 |
| 一日 warning triage zh-CN | `docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.zh-CN.md` | 中文伴随文件 |

## 最新运行摘要

- Budget warnings: `32`
- Skipped-loading warnings: `38`
- All descriptions removed: `32`
- Maximum omitted additional skills: `16`
- Severity: `high`
- Recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## 未执行动作

- 未标记 summary-reviewed。
- 未生成 preview-only candidate output。
- 未执行 profile apply。
- 未编辑 Codex `config.toml`、plugin cache、hard-load profile 或用户级 runtime settings。
- 未提交 raw JSON、stdout、transcripts、runtime logs、warning excerpts、thread IDs 或 token counters。
