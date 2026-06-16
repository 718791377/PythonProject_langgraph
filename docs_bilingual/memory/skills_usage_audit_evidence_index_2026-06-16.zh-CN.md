---
doc_id: skills_usage_audit_evidence_index_2026_06_16
lang: zh-CN
status: active
doc_class: audit_evidence_index
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-16
canonical: docs_bilingual/memory/skills_usage_audit_evidence_index_2026-06-16.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_evidence_index_2026-06-16.md
---

# Skills Usage Audit 证据索引 2026-06-16

本滚动索引用于发现 2026-06-16 最新的人工待复核 monitoring 证据包，但不改变审计决策状态。它不标记最终摘要已复核，不生成 candidate，也不授权 profile apply。

## 当前决策状态

- 最终 30 天摘要状态: `human_review_pending`
- 候选生成状态: `not_requested`
- Profile apply 状态: `not_authorized`
- 当前允许动作: 只允许人工复核或继续 monitoring

## 主证据包

| Evidence | Path | Purpose |
| --- | --- | --- |
| 最终 30 天摘要 | `docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md` | 脱敏 30 天报告与 gate 证据 |
| 人工复核准备 | `docs_bilingual/memory/skills_usage_audit_summary_review_prep_2026-06-15-1209.md` | 机器预复核与安全决策路径 |
| 人工复核决策模板 | `docs_bilingual/memory/skills_usage_audit_human_review_decision_template_2026-06-15.md` | 记录显式人工决策的模板 |

## 最新延续证据

| Evidence | Path | Purpose |
| --- | --- | --- |
| 人工待复核延续记录 | `docs_bilingual/memory/skills_usage_audit_review_pending_continuation_2026-06-16-1432.md` | 新一轮高压 warning-triage 后的最终摘要后 monitoring 证据 |
| 人工待复核延续记录 zh-CN | `docs_bilingual/memory/skills_usage_audit_review_pending_continuation_2026-06-16-1432.zh-CN.md` | 中文伴随文件 |
| 一日 warning triage | `docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.md` | 脱敏一日 live warning triage 证据 |
| 一日 warning triage zh-CN | `docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-16-1432.zh-CN.md` | 中文伴随文件 |

## 最新运行摘要

- Budget warnings: `32`
- Skipped-loading warnings: `38`
- All descriptions removed: `32`
- Maximum omitted additional skills: `16`
- Severity: `high`
- Recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`

## 相对 10:35 monitoring 记录的变化

- 已提交的 10:35 记录: `33` 个 budget warnings，`23` 个 skipped-loading warnings。
- 14:32 probe: `32` 个 budget warnings，`38` 个 skipped-loading warnings。
- 主要新增信号: skipped-loading 证据升高，并且本地 `.tmp` probe 输出已能提取样本。

## 安全下一步

1. 复核最终 30 天摘要和 review-prep 记录。
2. 将最新 14:32 延续证据作为 monitoring input 复核，而不是 closure authorization。
3. 使用人工复核决策模板选择一个显式 outcome。
4. 在后续明确 `approved-to-apply` 授权前，不执行任何 profile apply。

## 未执行动作

- 未标记 summary-reviewed。
- 未生成 preview-only candidate output。
- 未执行 profile apply。
- 未编辑 Codex `config.toml`、plugin cache、hard-load profile 或用户级 runtime settings。
- 未提交 raw JSON、stdout、transcripts、runtime logs、warning excerpts、thread IDs 或 token counters。
