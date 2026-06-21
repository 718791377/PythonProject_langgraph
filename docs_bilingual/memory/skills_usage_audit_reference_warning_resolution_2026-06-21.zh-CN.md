---
doc_id: skills_usage_audit_reference_warning_resolution_2026_06_21_zh_cn
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-21
canonical: docs_bilingual/memory/skills_usage_audit_reference_warning_resolution_2026-06-21.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_reference_warning_resolution_2026-06-21.md
---
# Skills Usage Audit reference warning 收口证据 2026-06-21

本记录把本地历史 warning 样本与当前 Codex skill frontmatter inventory 连接起来。
它只作为审计证据，不授权 profile apply、hard-load apply、禁用插件或编辑 vendor cache。

## 历史 warning 类别

- 历史 warning 样本：`reference_files/10.md`。
- 历史 loader warning 标记：`Skipped loading 286 skill(s) due to invalid SKILL.md files.`
- 历史 name 长度标记：`invalid name: exceeds maximum length of 64 characters`。
- 历史 description 长度标记：`invalid description: exceeds maximum length of 1024 characters`。
- 解释：该样本是已保留的本地 warning 类别，不是当前编辑 plugin cache 的授权。

## 当前兼容性证据

- 当前摘要来源：`tools/skills2cli.py index` 与 `tools/repair_codex_skill_frontmatter.py audit`。
- 当前 `skills2cli` 摘要：`invalid_total=0`。
- 当前 repair-audit 摘要：`invalid_total=0`。
- 本实施切片中观察到的 repair-audit total：`1236`。
- 本实施切片中观察到的 `skills2cli` inventory total：`1270`。
- 当前 Codex frontmatter 限制：`name<=64`、`description<=1024`。

## Checker-backed closure

- Checker：`tools/check_skills_audit_frontmatter_resolution.py`。
- 必要桥接：历史 skipped-loading / metadata-limit 标记存在，并且当前 frontmatter compatibility 报告 `invalid_total=0`。
- 收口解释：`historical_warning_current_inventory_clean`。
- 失败方式：如果当前 invalid total 非零，或找不到历史标记，checker 必须 fail closed。

## 安全边界

- 没有编辑用户级 `config.toml`。
- 没有编辑 plugin cache 或 skill bodies。
- 没有执行 profile apply 或 hard-load apply。
- 没有保留原始用户路径、原始 session transcript、原始 logs、warning excerpt、thread ID 或 token counter。
- 没有修改远端 refs。
