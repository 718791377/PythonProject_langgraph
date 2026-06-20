# 设计：正文级运营包生成

## 决策

Stage B 将把现有运营包 runtime 扩展为正文级文档生成器。当前治理/登记文档保持不变；新的正文层添加到 `docs_bilingual/operations_packages/` 下。

## 文档数量契约

正文文档数量是精确的生成主文档数量：

| 运营包 | 英文正文文档 | zh-CN 伴随文件 | 正文文件 |
| --- | ---: | ---: | ---: |
| Codex 持久化团队 | 48 | 48 | 96 |
| 一人公司 | 60 | 60 | 120 |
| 正文层合计 | 108 | 108 | 216 |

既有治理/登记层文档继续由生成器生成和检查。Stage B 可以报告“治理/登记层 + 216 个新增正文文件”的总生成文件数，但 48/60 的验收门槛指向正文层。

## 路径设计

生成的正文层使用分包根目录：

- `docs_bilingual/operations_packages/codex_cli_durable_team/<family>/<document>.md` - 保存每个 Codex 英文正文主文档。
- `docs_bilingual/operations_packages/codex_cli_durable_team/<family>/<document>.zh-CN.md` - 保存每个 Codex 中文正文伴随文档。
- `docs_bilingual/operations_packages/one_person_company/<family>/<document>.md` - 保存每个一人公司英文正文主文档。
- `docs_bilingual/operations_packages/one_person_company/<family>/<document>.zh-CN.md` - 保存每个一人公司中文正文伴随文档。

`<family>` 来自当前 Codex 的 8 个六文档家族和一人公司的 10 个六文档家族。文件名来自已跟踪的核心文档清单。

## 正文文档结构

每个生成正文文档必须包含：

- YAML front matter，包含 `doc_id`、`doc_class`、`status`、`package`、`body_kind`、`generated_by` 和 `lang`。
- generated marker。
- 目的 / 权威边界。
- 运营包清单摘要。
- 12 层落位。
- 裁剪规则。
- Inputs。
- Tools And Techniques。
- Outputs。
- 过程组运行表。
- 收尾 / registry 说明。

中文伴随文件必须包含 `translation_of`，并对目的、裁剪、输入、工具与技术、输出、过程组使用本地化标题。

## 裁剪规则

正文层保留五种模式：

1. 完整架构。
2. 全项目轻量。
3. 阶段局部轻量。
4. 模块级轻量。
5. 混合架构。

每个生成正文文档都必须说明所选或默认模式为什么不是更重也不是更轻，并列出升级触发器。检查器必须拒绝缺少裁剪模式、缺少裁剪理由或缺少升级触发器语言的正文文档。

## 过程组式写法

涉及执行层面的流程文本必须使用过程组语法。对每个生成正文文档：

- Inputs 定义来源证据、风险画像、owner、约束和当前工作状态。
- Tools And Techniques 定义生命周期映射、PMI 过程组分析、敏捷反馈、RACI、检查器、本地 CI 和评审方法。
- Outputs 定义文档产物、registry 条目、验证证据、裁剪决策、owner、收尾和远端发布停止点。

## 写入范围

Stage B 只允许编辑：

- `tools/generate_operations_package.py` - 根据已跟踪 package 权威渲染正文文档。
- `tools/check_operations_package_docs.py` - 校验生成正文数量、结构、registry、裁剪、编码和分包隔离。
- `test/operations_package_docs.test.py` - 用聚焦回归测试证明生成器和检查器行为。
- `docs_bilingual/docs_registry.yaml` - 把生成正文文档记录为一等双语产物。
- `docs_bilingual/operations_packages/` 下生成的文件 - 保存生成器产出的正文层。

Stage B 不得编辑 `.omx/state/`、LangGraph durable orchestrator 源码、launcher routing 或无关治理脚本。

## 验证策略

Stage B 检查必须证明：

- 存在 48 个 Codex 正文英文主文档和 48 个 zh-CN 伴随文件。
- 存在 60 个一人公司正文英文主文档和 60 个 zh-CN 伴随文件。
- 正文文档 `doc_id`、路径和 registry 条目唯一。
- 每个正文文档都有按顺序出现且非空的 I/T/O。
- 每个正文文档都有五种裁剪模式和升级触发器语言。
- 英文主文档保持 ASCII-only。
- 中文伴随文件是严格 UTF-8，且不含 replacement character。
- 串包检查保持 Codex 专属语义和一人公司专属语义相互隔离。
- 生成器写入模式幂等，并且分包模式不会写入另一个包。
