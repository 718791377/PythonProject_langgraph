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

- `tools/verify_official_openspec.py` - 检查本仓库的官方 OpenSpec 工作流 bootstrap 与生成工件是否健康。
- `tools/check_current_repo_authority_language.py` - 检查文档中声明本仓库为编排工作权威来源的措辞。
- `tools/check_document_governance_rules.py` - 检查治理文档是否满足必需策略模式并避免漂移。
- `tools/check_implementation_plan_rules.py` - 按仓库规划规则检查 implementation plan 文档。
- `tools/check_name_clarity_rules.py` - 对 `docs_bilingual/` 与 `openspec/` 执行 OPSX 名称解释规则，且不会修改文档；聚合 guard 会以 strict no-baseline 模式运行它。
- `tools/run_openspec_guard.py` - 将仓库 OpenSpec 检查聚合成一个本地 guard 命令与 JSON 报告。
- 后续新增、且支持 `--json` 并进入同一 guard surface 的仓库检查脚本

## 3. 输出类型

统一使用以下三类输出：

1. `check report` - 单个仓库检查脚本直接输出的 JSON。
2. `guard report` - `run_openspec_guard.py` 输出的聚合 JSON。
3. `guard step record` - guard report 中 `steps` 数组里的单步记录。

## 4. 公共顶层契约

所有仓库检查 JSON 输出都必须包含以下顶层字段：

- `schema_version` - 供消费方解释报告契约的整数 schema 版本。
- `generated_at` - 报告生成时间的 UTC ISO 8601 时间戳。
- `check_name` - 生成该报告的检查所使用的稳定机器可读标识。
- `ok` - 整份报告的布尔成功标志。
- `errors` - 阻断问题数组；没有阻断问题时为空数组。
- `warnings` - 非阻断提示数组；没有提示时为空数组。
- `info` - 面向人和日志消费方的信息数组。
- `root` - 本次检查使用的仓库根路径。
- `counts` - 包含报告数值汇总指标的对象。

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

- `rules_path` - 检查使用的治理规则文件路径。
- `violations` - 检查发现的规则违规列表。
- `allowed_context_matches` - 因符合允许上下文而被接受的匹配项。
- `implementation_plan_entries` - 检查读取的 implementation plan 记录。
- `tool` - 生成或控制该报告的工具或入口名称。
- `skip_validate` - 表示是否有意跳过 OpenSpec validation 的标志。

这些专属字段必须保持 additive。

不得通过新增专属字段来重定义公共顶层字段的既有语义。

## 6. Guard Report 契约

`guard report` 指 `run_openspec_guard.py --json` 输出的聚合 JSON。

它必须遵守公共顶层契约。

它还必须包含：

- `tool` - 聚合报告所对应的 guard 入口名称。
- `refresh_managed_files` - 表示检查前是否刷新 managed OpenSpec 文件的布尔标志。
- `require_clean_git` - 表示 guard 是否强制要求 Git 工作区干净的布尔标志。
- `skip_validate` - 表示是否跳过官方 OpenSpec validation 的布尔标志。
- `steps` - 本次运行实际执行的有序 guard step 记录。

它可以包含：

- `failed_step` - 当 `ok` 为 `false` 时失败的 guard step 稳定名称。
- `error` - guard 级失败的简短摘要字符串。

规则：

- `steps` 是 guard 实际执行步骤的权威有序列表
- 当 `ok=false` 时，`failed_step` 必须存在
- `error` 只是摘要字符串，不能替代 `errors`
- guard report 的 `counts` 至少应包含：
  - `steps_total` - 本次运行计划执行的 guard step 总数。
  - `steps_passed` - 成功完成的 guard step 数量。
  - `steps_failed` - 失败或阻断完成的 guard step 数量。

## 7. Guard Step Record 契约

`steps` 中的每个对象至少应包含：

- `step` - guard step 的稳定内部名称。
- `command` - 该 guard step 调用的命令行。
- `returncode` - 命令返回的进程退出码。
- `stdout` - 命令捕获到的标准输出。
- `stderr` - 命令捕获到的标准错误。
- `ok` - 该 guard step 的布尔成功标志。

它可以包含：

- `data` - 当子检查输出是合法 JSON 时保存的解析后子结果。
- `parse_error` - 当 `stdout` 存在但不是合法 JSON 时使用的解析失败消息。

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

- `openspec-guard-report.json` - 聚合 guard JSON 报告的规范 CI artifact 文件名。

guard report 是仓库 OpenSpec enforcement 的权威机器可读 CI 报告。

叶子检查结果可以继续嵌入在 `steps[].data` 中。

## 11. 命名与稳定性规则

以下标识必须保持稳定：

- `check_name` - 供消费方路由与聚合使用的稳定检查标识。
- `step` - guard `steps` 记录中使用的稳定步骤标识。
- `counts` 下的键名 - 供消费方汇总报告使用的稳定指标名称。

不得仅为了展示友好而改名。

如果以后需要展示友好标签，应新增字段，而不是重定义现有稳定字段。

## 12. 防漂移规则

后续新增的仓库检查，只要提供 `--json`，就必须遵守本策略。

`run_openspec_guard.py` 在聚合子检查时，必须通过 `steps[].data` 保留子检查结果的原始契约，而不是重新发明一套冲突结构。

只要这套 JSON 契约发生变化，文档、测试与实现就必须在同一批工作中一起更新。
