---
doc_id: operations_package_full_body_generation_plan
doc_class: implementation_plan
status: active
change: expand-operations-package-full-body-doc-generation-20260620
base_ref: main
lang: zh-CN
translation_of: docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.md
---

# 运营包正文级生成实施方案

> 执行说明：本方案是 Stage A 冻结后的 Stage B brief。Stage B 必须在本方案包提交并合入本地 `main` 后，基于本地 `main` 实施。

## 目标

把受治理双语运营包 runtime 从登记/治理包生成扩展为两套目标系统的正文级运营文档生成：

- Codex CLI 个人开发者生产级持久化团队：48 个英文正文文档加 48 个 zh-CN 伴随文件。
- 个人级生产级一人公司运营：60 个英文正文文档加 60 个 zh-CN 伴随文件。

48 和 60 是生成正文文档的验收数量，而不是登记表中的清单数字。

## Stage A 包

Stage A 冻结本方案、OpenSpec delta requirements 和本方案的 registry 条目。Stage A 不实现正文生成器。Stage A 必须先提交并合入本地 `main`，Stage B 才能开始。

Stage A 文件：

- `openspec/changes/expand-operations-package-full-body-doc-generation-20260620/` - 保存 Stage A OpenSpec proposal、design、tasks、management checklist 和 delta specs。
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.md` - 冻结英文 Stage B 实施 brief。
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.zh-CN.md` - 冻结中文伴随实施 brief。
- `docs_bilingual/docs_registry.yaml` - 当前登记方案，并在 Stage B 登记生成的正文文档。

## Stage B 写入范围

Stage B 只允许编辑：

- `tools/generate_operations_package.py` - 渲染确定性的运营包文档。
- `tools/check_operations_package_docs.py` - 校验生成包数量、结构、registry 和裁剪规则。
- `test/operations_package_docs.test.py` - 为生成器和检查器提供聚焦回归覆盖。
- `docs_bilingual/docs_registry.yaml` - 登记每一对生成的正文文档。
- `docs_bilingual/operations_packages/` - 保存生成的正文级运营包文档。

Stage B 不得修改 LangGraph durable orchestrator 源码、用户级 launcher/routing 逻辑、`.omx/state/`、无关治理脚本、无关实施方案或白皮书。

## 生成正文层

### Codex 持久化团队包

生成器必须在以下目录创建 48 个英文主正文文档和 48 个 zh-CN 伴随文档：

`docs_bilingual/operations_packages/codex_cli_durable_team/`

48 个正文文档来自已跟踪的 Codex 核心文档清单：

1. Strategy and business：`vision.md`、`thesis.md`、`business-model.md`、`pricing.md`、`unit-economics.md`、`strategy.md`。
2. Market and product：`user-segments.md`、`market-map.md`、`research-repository.md`、`product-strategy.md`、`prd.md`、`cli-ux.md`。
3. Metrics and data：`metrics.yaml`、`north-star.md`、`tracking-plan.md`、`data-dictionary.md`、`data-quality-checklist.md`、`experiment-log.md`。
4. Engineering and platform：`architecture.md`、`adr.md`、`module-boundaries.md`、`tech-stack.md`、`delivery-plan.md`、`observability.md`。
5. Security and risk：`security-policy.md`、`access-control.md`、`privacy-policy.md`、`incident-response.md`、`risk-register.md`、`backup-restore.md`。
6. Agent governance：`agent-role-map.md`、`agent-permissions.md`、`agent-tool-policy.md`、`human-review-checklist.md`、`agent-evaluation.md`、`agent-failure-modes.md`。
7. Growth and operations：`growth-model.md`、`docs-plan.md`、`support-playbook.md`、`faq.md`、`trust-page.md`、`changelog.md`。
8. Retrospective and knowledge：`decision-log.md`、`weekly-review.md`、`monthly-review.md`、`postmortem.md`、`learning-log.md`、`template-library.md`。

### 一人公司包

生成器必须在以下目录创建 60 个英文主正文文档和 60 个 zh-CN 伴随文档：

`docs_bilingual/operations_packages/one_person_company/`

60 个正文文档来自已跟踪的一人公司核心文档清单：

1. Company strategy：`company-thesis.md`、`vision.md`、`strategy.md`、`annual-plan.md`、`quarterly-plan.md`、`decision-log.md`。
2. Business and finance：`business-model.md`、`offer.md`、`pricing.md`、`unit-economics.md`、`finance-model.md`、`cashflow.md`。
3. Market and user：`market-map.md`、`user-segments.md`、`competitor-analysis.md`、`alternative-solutions.md`、`research-repository.md`、`interview-guide.md`。
4. Product and service：`product-strategy.md`、`prd.md`、`service-blueprint.md`、`onboarding.md`、`customer-journey.md`、`roadmap.md`。
5. Metrics and data：`metrics.yaml`、`north-star.md`、`funnel-dashboard.md`、`tracking-plan.md`、`data-dictionary.md`、`experiment-log.md`。
6. Growth and sales：`growth-model.md`、`channel-map.md`、`sales-playbook.md`、`landing-page.md`、`email-sequences.md`、`content-calendar.md`。
7. Operations and customer success：`ops-playbook.md`、`customer-success-playbook.md`、`support-policy.md`、`faq.md`、`refund-policy.md`、`feedback-triage.md`。
8. Technology and automation：`tech-stack.md`、`automation-map.md`、`tool-stack.md`、`vendor-register.md`、`api-dependency-map.md`、`backup-restore.md`。
9. Governance and risk：`legal-checklist.md`、`terms-of-service.md`、`privacy-policy.md`、`contract-template.md`、`risk-register.md`、`compliance-checklist.md`。
10. Agent and knowledge：`agent-governance.md`、`agent-role-map.md`、`agent-permissions.md`、`human-review-checklist.md`、`monthly-review.md`、`learning-log.md`。

## 单文档结构

每个生成正文文档必须包含：

1. YAML front matter，包含 `doc_id`、`doc_class`、`status`、`package`、`body_kind`、`generated_by` 和 `lang`。
2. Generated marker。
3. Purpose。
4. Authority Boundary。
5. Lifecycle Placement。
6. Tailoring Rules。
7. Inputs。
8. Tools And Techniques。
9. Outputs。
10. Process Group Operating Table。
11. Closeout And Registry。

中文伴随文件必须包含 `translation_of`，并使用执行章节的本地化等价标题。

## 过程组式写法

每个正文文档的执行层流程都使用过程组语法：

### Inputs

- 已提交到仓库的 Business Management、product lifecycle、PMP、白皮书、北极星、清单与裁剪规则等权威。
- 目标文档家族、package、owner、生命周期层、风险画像、依赖、验证需求、回滚或退役路径、远端发布边界。
- 当前本地 worktree 状态、OpenSpec 状态、registry 状态和分包生成器选择。

### Tools And Techniques

- 12 层生命周期落位、RACI/责任域映射、PMI 过程组思维、敏捷反馈循环和架构裁剪评分卡。
- 确定性生成器渲染、registry 更新、UTF-8 安全写入、检查器、聚焦测试、本地 CI、本地 MR review 和本地 main 集成 helper。
- 只在所有权隔离时使用 expert/durable 协作：runtime/checker/test 与 docs/registry 可作为 Stage B 两个切片；leader 负责 fan-in。

### Outputs

- 生成的 Markdown 正文文档和 zh-CN 伴随文件。
- 具有唯一 doc_id 和路径的 registry 条目。
- 正文数量、双语配对、I/T/O、裁剪模式、分包隔离和幂等验证证据。
- 本地 commit 与本地 `main` 集成；远端发布门保持关闭。

## 裁剪规则

每个正文文档必须包含五种架构模式：

| 模式 | 使用时机 | 轻量范围 |
| --- | --- | --- |
| 完整架构 | 跨阶段、外部客户、收入、合规、安全、发布、回滚、持久状态、共享 runtime 或多 Agent 工作 | 受影响风险范围端到端治理 |
| 全项目轻量 | 私有、可逆、低风险探索，且无外部承诺、持久状态影响、发布、敏感数据或共享 runtime | 整个项目可以轻量 |
| 阶段局部轻量 | 更大受治理项目中的某个发现、指标、增长或复盘阶段风险较低 | 只有被命名的阶段轻量 |
| 模块级轻量 | 单个有边界的文档家族、helper、原型或本地模块不改变 trust、state、public API、CI、release 或共享 runtime 行为 | 只有该模块轻量 |
| 混合架构 | 多数真实工作；低风险阶段可先轻量，但生产、客户、收入、信任、持久状态或发布影响需要更完整控制 | 关键层完整；低风险阶段/模块在升级触发前保持轻量 |

每个裁剪记录必须说明所选模式为什么不是更重也不是更轻，并列出升级触发器。

## Stage B 测试

Stage B 必须更新测试并断言：

- Codex 正文主文档数量为 48，正文文件数量为 96。
- 一人公司正文主文档数量为 60，正文文件数量为 120。
- 每个正文主文档都有 zh-CN 伴随文件，每个伴随文件都指向主文档。
- I/T/O 章节存在、顺序正确且非空。
- 五种裁剪模式和升级触发器语言存在。
- Registry 全覆盖、doc_id 唯一、路径唯一。
- 分包写入模式不会写入另一个包。
- 写入模式幂等，生成后检查模式通过。
- 英文正文主文档 ASCII-only；zh-CN 伴随文件是严格 UTF-8 且无 replacement character。
- Codex 和一人公司 package 语义不串包。

## 验证命令

Stage A：

```powershell
openspec validate expand-operations-package-full-body-doc-generation-20260620 --strict
python .\tools\check_document_pair_policy.py --root . --base-ref main --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --tool codex --json
```

Stage B：

```powershell
python .\tools\generate_operations_package.py --root . --package all --check --json
python .\tools\generate_operations_package.py --root . --package codex --check --json
python .\tools\generate_operations_package.py --root . --package one-person-company --check --json
python .\tools\check_operations_package_docs.py --root . --json
python .\tools\ci\run_python_tests.py --root . --pattern operations_package_docs.test.py
openspec validate expand-operations-package-full-body-doc-generation-20260620 --strict
openspec validate --all --strict
python .\tools\run_openspec_guard.py --root . --tool codex --json
```

每次提交前运行 pre-commit update/archive checker。本地 main 集成前运行仓库 local gate 与 local MR review，或使用会运行这些 gate 的受保护本地集成 helper。

## 协作和 durable-team 规则

Stage A 由 leader 拥有，因为冻结方案尚未落入本地 `main`。咨询专家可以评审方案。

Stage B 在 Stage A 落入本地 `main` 后至少有两个基本独立切片：

1. Runtime/checker/test 切片。
2. Generated docs/registry 切片。

当 backend preflight ready 且所有权可以保持隔离时，Stage B 应采用最小充分 durable 或 expert 执行面。如果 durable team 工具被阻塞，则使用有边界的 native experts，并由 leader 负责最终集成和验证。

## 完成边界

完成需要两次本地 main 集成：

1. Stage A 方案冻结 commit 合入本地 `main`。
2. Stage B runtime/正文文档 commit 合入本地 `main`。

除非用户显式授权远端发布，否则工作停在远端发布门。

## 当前状态

<!-- CURRENT_STATUS_START -->
- Stage A artifacts 已在 feature worktree 中起草，正在等待验证、提交和本地 `main` 集成。
- Stage A 方案冻结包合入本地 `main` 之前，Stage B 不得开始。
- 远端发布未获授权。
<!-- CURRENT_STATUS_END -->

## 任务积压

<!-- TASK_BACKLOG_START -->
- Stage A：验证 OpenSpec、双语配对策略、pre-commit update/archive 策略和仓库 OpenSpec guard。
- Stage A：提交方案冻结包并合入本地 `main`。
- Stage B：实现正文级 runtime，生成 48/60 正文层，验证、提交并合入本地 `main`。
- 收尾：Stage B 验证和 stable-spec sync 后归档 OpenSpec change。
<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- `openspec/changes/expand-operations-package-full-body-doc-generation-20260620/` - Stage A OpenSpec proposal、design、tasks、management 和 delta specs。
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.md` - 冻结的英文实施方案。
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.zh-CN.md` - 冻结的中文伴随实施方案。
- `docs_bilingual/docs_registry.yaml` - 实施方案 registry 条目和 Stage B 正文文档 registry 目标。
<!-- EVIDENCE_INDEX_END -->
