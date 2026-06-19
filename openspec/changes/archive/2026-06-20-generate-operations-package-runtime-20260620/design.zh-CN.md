---
change_id: generate-operations-package-runtime-20260620
lang: zh-CN
status: proposed
owner: codex
created_at: 2026-06-20
translation_of: openspec/changes/generate-operations-package-runtime-20260620/design.md
---

# 设计：运营包生成与 Runtime

## 权威边界

Stage B 把现有白皮书、北极星、清单图、裁剪规则、PMI 参考图和过程组契约作为来源权威。新增运营包位于这些来源之下，是可执行层：文档系统图、台账、RACI、Agent 目录、裁剪决策树和过程组式 playbook。

## Stage A / Stage B 切分

Stage A 只冻结契约：OpenSpec 变更 artifacts、双语实施方案和 `docs_bilingual/docs_registry.yaml` 条目。Stage A 不修改 runtime helper、checker、test、生成的运营包文件或 CI manifest。

Stage B 实现冻结契约：

- `tools/generate_operations_package.py` 确定性生成双语运营包文档。
- `tools/check_operations_package_docs.py` 校验运营包覆盖、I/T/O、裁剪规则和 registry 引用。
- `test/operations_package_docs.test.py` 覆盖生成器与检查器行为。
- `tools/ci/ci_test_manifest.json` 注册新测试。
- `docs_bilingual/docs_registry.yaml` 注册新增生成文档配对。

## 生成的运营包范围

Codex 持久化团队运营包包含 BRD、PRD、模板更新策略、48 核心文档台账、24 责任域 RACI、12 个受治理 AI Agent 目录、18 个横切模块图、12 本参考书映射、4 个虚拟部门运营图、文档生成顺序和运营 slice 模板。

一人公司运营包包含运营文档系统图、裁剪决策树、12 个最小启动文档指南、60 核心文档台账、30 责任域 RACI、15 个受治理 AI Agent 目录、20 个横切模块图、PMI 过程组式 playbook、架构模式选择指南和运营指标/月度复盘包。

## 裁剪模式

检查器和生成文档保留这些架构模式定义：完整架构、全项目轻量、阶段局部轻量、模块级轻量和混合架构。每份裁剪决策都记录为什么所选模式不是更重或更轻，并列出升级触发条件。

## 过程组式 I/T/O 契约

每个涉及执行层面的生成文档都包含显式过程组部分。英文文件使用 `Inputs`、`Tools And Techniques`、`Outputs`；中文伴随文件使用 `输入`、`工具与技术`、`输出`。

## 协同与运行时 Lane

Stage A 由 leader 主会话负责，专家只提供 advisory，因为冻结方案尚未存在。Stage A 落入本地 `main` 后，Stage B 因具备 runtime/checker/test 与生成文档/registry 两个独立切片而满足 durable/persistent 执行阈值。
