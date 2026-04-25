---
doc_id: openspec_check_and_guard_json_output_policy
lang: zh-CN
canonical: docs_bilingual/governance/openspec_check_and_guard_json_output_policy.md
translation_of: docs_bilingual/governance/openspec_check_and_guard_json_output_policy.md
doc_class: governance
status: active
---

# OpenSpec 检查与 Guard JSON 输出策略

## 1. 目的

本文定义本仓库以下对象的 JSON 输出契约：

- 支持 `--json` 的仓库检查脚本
- `run_openspec_guard.py --json` 的聚合输出
- 读取这些报告的 CI artifact 消费方

目标是让机器可读的仓库检查结果保持稳定、清晰、可演进。

## 2. 适用范围

本策略适用于：

- `tools/verify_official_openspec.py`
- `tools/check_current_repo_authority_language.py`
- `tools/check_document_governance_rules.py`
- `tools/check_implementation_plan_rules.py`
- `tools/check_name_clarity_rules.py`：对 `docs_bilingual/` 与 `openspec/` 执行 OPSX 名称解释规则，且不会修改文档。
- `tools/run_openspec_guard.py`
- 后续新增、且支持 `--json` 并进入同一 guard surface 的仓库检查脚本

## 3. 输出类型

统一使用以下三类输出：

1. `check report`
   - 单个仓库检查脚本直接输出的 JSON
2. `guard report`
   - `run_openspec_guard.py` 输出的聚合 JSON
3. `guard step record`
   - guard report 中 `steps` 数组里的单步记录

## 4. 公共顶层契约

所有仓库检查 JSON 输出都必须包含以下顶层字段：

- `schema_version`
- `generated_at`
- `check_name`
- `ok`
- `errors`
- `warnings`
- `info`
- `root`
- `counts`

强制规则：

- `schema_version` 必须是整数
- `generated_at` 必须是 UTC ISO 8601 时间戳
- `check_name` 必须是稳定的机器可读标识
- `ok` 必须是布尔值
- `errors`、`warnings`、`info` 即使为空也必须输出数组
- `counts` 即使内容很少也必须输出对象

## 5. Check Report 契约

`check report` 指单个叶子检查脚本直接输出的 JSON。

它必须遵守公共顶层契约。

它可以增加脚本专属字段，例如：

- `rules_path`
- `violations`
- `allowed_context_matches`
- `implementation_plan_entries`
- `tool`
- `skip_validate`

这些专属字段必须保持 additive。

不得通过新增专属字段来重定义公共顶层字段的既有语义。

## 6. Guard Report 契约

`guard report` 指 `run_openspec_guard.py --json` 输出的聚合 JSON。

它必须遵守公共顶层契约。

它还必须包含：

- `tool`
- `refresh_managed_files`
- `require_clean_git`
- `skip_validate`
- `steps`

它可以包含：

- `failed_step`
- `error`

规则：

- `steps` 是 guard 实际执行步骤的权威有序列表
- 当 `ok=false` 时，`failed_step` 必须存在
- `error` 只是摘要字符串，不能替代 `errors`
- guard report 的 `counts` 至少应包含：
  - `steps_total`
  - `steps_passed`
  - `steps_failed`

## 7. Guard Step Record 契约

`steps` 中的每个对象至少应包含：

- `step`
- `command`
- `returncode`
- `stdout`
- `stderr`
- `ok`

它可以包含：

- `data`
- `parse_error`

规则：

- `step` 必须是稳定的内部步骤名
- 当子检查输出是合法 JSON 时，`data` 应保存解析后的子结果
- 消费方应优先读取 `data`，而不是重新解析 `stdout`
- `parse_error` 只在 `stdout` 存在但不是合法 JSON 时使用

## 8. 成功、失败与退出码规则

强制规则：

- 当 `ok=true` 时，脚本退出码必须是 `0`
- 当 `ok=false` 时，脚本退出码必须是非 `0`
- `errors` 继续作为权威阻断问题列表
- `warnings` 单独存在时不得强制把 `ok` 改成 `false`

## 9. 兼容与演进规则

强制规则：

- 每份报告都必须包含 `schema_version`
- 允许 additive 字段增长
- 既有字段语义不得被静默改写
- 消费方必须忽略未知字段
- 破坏性输出变化必须提升 schema version

## 10. CI Artifact 规则

仓库 CI guard surface 应保存聚合 guard JSON artifact。

当前规范 artifact 文件名为：

- `openspec-guard-report.json`

guard report 是仓库 OpenSpec enforcement 的权威机器可读 CI 报告。

叶子检查结果可以继续嵌入在 `steps[].data` 中。

## 11. 命名与稳定性规则

以下标识必须保持稳定：

- `check_name`
- `step`
- `counts` 下的键名

不得仅为了展示友好而改名。

如果以后需要展示友好标签，应新增字段，而不是重定义现有稳定字段。

## 12. 防漂移规则

后续新增的仓库检查，只要提供 `--json`，就必须遵守本策略。

`run_openspec_guard.py` 在聚合子检查时，必须通过 `steps[].data` 保留子检查结果的原始契约，而不是重新发明一套冲突结构。

只要这套 JSON 契约发生变化，文档、测试与实现就必须在同一批工作中一起更新。
