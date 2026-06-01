---
doc_id: spec_kit_subordinate_adapter_policy
lang: zh-CN
status: active
doc_class: governance
translation_of: docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md
---

# Spec Kit 从属适配器政策

## 权威顺序

1. Native Codex 仍是本仓库的基础执行层。
2. Comet 负责协调 OpenSpec 的 WHAT 与 Superpowers 的 HOW。
3. OpenSpec 仍是本仓库的规格权威。
4. Superpowers 仍是实现方法指导层。
5. Spec Kit 只能作为可选从属 adapter、模板来源或文档参考被引用。

除非另一个单独的 active implementation plan 明确改变该边界并通过本地门禁，否则 Spec Kit 不是本仓库的项目治理权威。

## 允许用途

- 在明确说明其为从属参考的语境中链接 Spec Kit 文档。
- 将 Spec Kit 模板与 OpenSpec 或 Comet 工件对比，但不得转移权威。
- 只能通过保留上述权威顺序的仓库计划、checker 或 OpenSpec change 复用模板想法。

## 没有单独 active plan 时阻止的用途

- 运行 `specify init --force` - 该命令可能覆盖或迁移项目规格权威。
- 添加 `.specify/` - 该路径被视为治理/runtime 接管表面，不是普通文档目录。
- 将 Spec Kit 描述为 primary source of truth、primary governance authority 或 Comet/OpenSpec/Superpowers 的替代者。
- 仅靠提示词把仓库工作流所有权从 OpenSpec 或 Comet 转移到 Spec Kit。

## 脚本支撑

`tools/check_spec_kit_authority_guard.py` - fail-closed checker，用来扫描已提交和工作区表面中的不安全 Spec Kit 初始化、`.specify` 路径创建和权威接管措辞。

`tools/run_openspec_guard.py` - 聚合 guard，会在仓库本地门禁中运行 Spec Kit authority checker。

`tools/ci/ci_test_manifest.json` - 本地 CI manifest，包含 Spec Kit authority guard 回归测试。
