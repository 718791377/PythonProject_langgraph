---
doc_id: one_person_company_pmi_operations_refresh_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/one_person_company_pmi_operations_refresh_plan.md
translation_of: docs_bilingual/implementation_plans/one_person_company_pmi_operations_refresh_plan.md
doc_class: implementation_plan
status: active
---

# 个人级生产级一人公司运营 PMI 深化刷新实施方案

> **给 agentic workers：** 必须使用 superpowers:subagent-driven-development 或 superpowers:executing-plans 按任务执行本方案。步骤使用 checkbox（`- [ ]`）语法追踪。

**目标：** 基于 fresh reading 刷新个人级生产级一人公司运营文档族，并通过本地 `main` 集成，同时停在远程发布闸门。

**架构：** 本 rollout 采用两阶段 local-main-first 文档实施。Stage A 先冻结本方案作为实施权威。Stage B 再执行 fresh source extraction、更新一人公司白皮书、新建专属一人公司北极星、刷新生命周期与裁剪引用、验证双语文档族，并把实施包合入本地 `main`。

**技术栈：** Markdown、YAML registry、PowerShell local CI gates、Python source-extraction 和治理检查器、git worktrees、`complete_local_flow_to_remote_gate.py`、Codex native experts，以及 LangGraph-backed durable-team routing。

---

<!-- CURRENT_STATUS_START -->
Status: active frozen plan for Stage B
Stage: Stage A validation complete; local-main integration handoff
Owner session: main Codex leader session
Current gate: local commit, local-main integration, then Stage B live implementation from latest local main
Remote publication: not authorized; stop at the remote-publication gate
<!-- CURRENT_STATUS_END -->

<!-- TASK_BACKLOG_START -->
- [x] Stage A: create the English ASCII primary implementation plan.
- [x] Stage A: create the Chinese companion implementation plan.
- [x] Stage A: register the plan pair in `docs_bilingual/docs_registry.yaml`.
- [x] Stage A: run document pair, governance, precommit, OpenSpec, local gate, and local MR review checks.
- [ ] Stage A: commit and integrate the frozen plan into local `main` (commit prepared; integration performed by local helper after this package is committed).
- [ ] Stage B: start a fresh implementation worktree from the integrated local `main`.
- [ ] Stage B: run fresh source extraction for `Business Management/`, `PMP/`, and `docs_bilingual/product_lifecycle/`.
- [ ] Stage B: update the one-person-company white paper, dedicated North Star, lifecycle maps, tailoring rules, and registry.
- [ ] Stage B: validate, commit, integrate local `main`, preserve rollback evidence, and stop before remote publication.
<!-- TASK_BACKLOG_END -->

<!-- EVIDENCE_INDEX_START -->
- Stage A planned evidence: this frozen plan pair, `docs_bilingual/docs_registry.yaml`, `python tools/check_document_pair_policy.py --root . --json`, `python tools/check_document_governance_rules.py --root . --json`, `python tools/check_precommit_update_archive.py --root . --json`, `python tools/run_openspec_guard.py --root . --json`, `tools/ci/local_gate.ps1`, `tools/ci/local_mr_review.ps1`, and `tools/complete_local_flow_to_remote_gate.py --execute --json`.
- Stage B planned evidence: fresh extraction manifests under ignored `.omx/state/langgraph/extraction/`, updated tracked synthesis documents, validation command output, rollback ref, completed claim, and `remote_publication_performed=false`.
<!-- EVIDENCE_INDEX_END -->

## 1. 范围与来源权威

本方案落实用户要求：通过 fresh reading 更新 `个人级生产级一人公司运营` 文档族。必须读取并综合：

- `Business Management/`：商业、产品、增长、架构、运营、发现和一人公司参考资料。
- `PMP/`：PMBOK、过程组、项目集、项目组合、PMO 和敏捷实践参考资料。
- `docs_bilingual/product_lifecycle/`：当前仓库生命周期、清单、PMI 和裁剪文档。

实施不得依赖 stale cache-only claims。必须运行 fresh extraction，并且 tracked docs 只引用聚合证据。Raw extracted text 仍是本地忽略态证据。

本 rollout 的 PMI 权威顺序：

1. PMBOK 第 8 版是 value delivery、project canvas、performance domains、AI-era project work、hybrid delivery 和 tailoring 的主要权威。
2. The Standard for Program Management 第 5 版用于一人公司工作变成相关倡议集合，并需要共享收益、依赖、排序或能力增量时。
3. The Standard for Portfolio Management 第 4 版用于需要平衡价值、风险、runway、容量和竞争业务线时。
4. Project Management Offices: A Practice Guide 用于 solo PMO / chief-of-staff 治理服务模型。
5. Agile Practice Guide 用于 adaptive discovery、MVP slicing、feedback loops 和 lightweight reversible work。
6. PMBOK 第 6 版、PMBOK 第 7 版、Process Groups: A Practice Guide 和较早本地参考只作为 I/T/O 词汇、原则、对照和向后兼容解释的支撑来源。

## 2. 目标交付物

实施包必须更新或新建下列 tracked 双语 artifacts：

| Artifact | 必需动作 |
| --- | --- |
| `docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md` 与 `.zh-CN.md` | 扩展成 PMI-informed operating white paper。保留 12 层目标清单，并让每个执行相关层级显式采用输入 / 工具与技术 / 输出形式。 |
| `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` 与 `.zh-CN.md` | 新建专属一人公司 North Star 双语文档。它必须与 Codex durable-team platform North Star 分离。 |
| `docs_bilingual/product_lifecycle/one_person_company_inventory_map.md` 与 `.zh-CN.md` | 刷新数量权威，并交叉链接白皮书和新 North Star。 |
| `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md` 与 `.zh-CN.md` | 把一人公司工作中的 full / lightweight / hybrid 裁剪策略写成决策完备规则。 |
| `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` 与 `.zh-CN.md` | 记录一人公司 PMI overlay 和 latest-primary authority rule。 |
| `docs_bilingual/product_lifecycle/business_management_source_synthesis.md` 与 `.zh-CN.md` | 使用新的 extraction run 刷新 source synthesis 与 Business Management / PMP 解释。 |
| `docs_bilingual/docs_registry.yaml` | 登记新的 North Star 双语文档和本实施方案双语文档。 |

只有现有证据文档需要 tracked summary 时，实施才可以补充小型 `fresh_source_reading_evidence` 更新。不得把 raw book/source excerpts 加入 tracked docs。

## 3. 必须实现的裁剪规则

刷新后的文档族必须明确回答什么时候采用每种架构深度：

| 裁剪结果 | 使用场景 | 最小治理面 |
| --- | --- | --- |
| 受影响范围完整架构 | 用户可见发布、支付、受监管或敏感数据、外部承诺、支持义务、重复交付、重大收入/风险、跨系统自动化或广泛 governed-agent execution。 | 受影响层级显示输入 / 工具与技术 / 输出、owner、风险、验证、发布/回滚和复盘路径。 |
| 整个项目轻量 | 整个项目都是私有、可逆、低风险，无外部用户、无资金流动、无敏感数据、无支持承诺、无 shared runtime、无发布承诺。 | 12 个最小启动文档或其紧凑等价物、明确停止条件、一个 owner 和一个 review cadence。 |
| 阶段局部轻量 | discovery、prototype、interview、content exploration 或 spike 在较大受治理事项内风险较低。 | 轻量处理仅限该阶段，并且必须在触达收入、客户、信任、发布或合规影响前扩展。 |
| 模块级轻量 | 有边界的模块可逆，且不改变整体 operating model。 | 模块 I/T/O、owner、验证、回滚路径和耦合检查。 |
| 混合方式 | discovery 不确定，但后续交付可能影响生产、用户、收入、信任、合规、runtime behavior 或 release safety。 | 轻量 discovery，随后在外部影响前对受影响交付层级使用完整控制。 |

默认规则：使用局部轻量，而不是整体随意。只扩展承载风险的层级、阶段或模块；只有耦合变成系统性时才扩展整个项目。

## 4. Process-Group Contract For This Refresh (过程组式契约)

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 用户请求、当前 source-evidence 边界、受影响权威文档、非目标、本地-only 发布边界 | 范围边界审查、权威分层审查、no-runtime / no-remote framing | 刷新范围、成功标准、约束条件、明确的远程发布停止点 |
| 规划 | 白皮书、生命周期文档、PMI map、裁剪规则、docs registry、source traceability docs | 目标文件映射、裁剪审查、验证设计、协作阈值检查 | 冻结文件清单、章节意图、验收清单、验证路径 |
| 执行 | 已冻结方案、fresh extraction outputs、双语源文件、worker handoffs | 只编辑受治理文档、双语 pair 对齐、排除 raw cache、leader-owned fan-in | 文档 delta、changed-path list、traceability 更新、新 North Star 双语 pair |
| 监控与控制 | 当前 diff、registry、数量权威、PMI 权威顺序、source evidence claims | 权威漂移检查、数量漂移检查、PMI 误用检查、alias 误用检查、registry mismatch 检查 | 已校正 diff、验证证据、未解决问题清单或 clean acceptance |
| 收尾 | 验证输出、本地 MR review、本地 main helper 结果、rollback ref、completed claim | local-main-first 集成、cleanup helper、lesson / next-cycle note | local `main` commit、rollback evidence、completed claim、远程发布门停止 |

## 5. 协同与 Runtime 计划

本方案合入本地 `main` 后，Stage B 必须从最新 local `main` 创建新的 implementation worktree。

- Native expert fan-out：使用最小充分角色集合。优先用 `researcher` 做 PMI/source synthesis，用 `verifier` 做最终 completion review。只有主会话无法保持双语文档结构对齐时才使用 `writer`。
- Durable team：因为 Stage B 已有 frozen plan 且至少三块独立切片，必须采用 durable-team routing，三块并行切片如下：
  - Worker A：fresh extraction 与 source-evidence synthesis。
  - Worker B：white paper 与 inventory map update。
  - Worker C：dedicated North Star、tailoring rules、PMI reference map update。
- Leader responsibilities：当前 main Codex session 负责 docs registry、冲突解决、双语 pair alignment、validation gates、本地 main 集成、rollback evidence 和 remote-publication stop。
- 如果 native expert invocation 被平台限制，routing trace 记录 `experts=blocked:platform_subagent_invocation_constraint`，并继续用 durable team 或 leader-owned execution。
- 如果 durable-team launch 失败，不得放弃任务；继续由主会话执行，并记录具名 blocker。

## 6. Stage B 工作分解

### Task 1: 创建实施 worktree 与证据 receipt

**Files：** 只写 ignored `.omx/` receipt/claim files。

- [ ] 从最新 local `main` 创建新的 feature worktree。
- [ ] 在 ignored `.omx/` 下记录 worktree receipt 与 session claim，状态为 `in-progress`。
- [ ] 开始前确认 local `main` 不落后于 `gitlab/main`。

### Task 2: 运行 fresh source extraction

**Files：** 只写 ignored `.omx/state/langgraph/extraction/`。

- [ ] 对 `Business Management/` 运行 `tools/fresh_extract_sources.py`。
- [ ] 对 `PMP/` 运行 `tools/fresh_extract_sources.py`。
- [ ] 对 `docs_bilingual/product_lifecycle/` 运行 `tools/fresh_extract_sources.py`。
- [ ] 汇总每个 source root 的 source count、format、unit count 和 extraction status。
- [ ] unsupported 的非 PDF/EPUB/Markdown 残留视为本轮范围外，除非工具对 supported files 报 source error。

### Task 3: 更新 source synthesis 与 PMI authority docs

**Files：** `business_management_source_synthesis.*`、`pmi_project_management_reference_map.*`。

- [ ] 加入新的 extraction-run summary 和 source boundaries。
- [ ] 解释 PMBOK 8、项目集、项目组合、PMO、敏捷实践如何映射到一人公司运营。
- [ ] 保留旧版本为支撑，而不是主要权威。

### Task 4: 更新白皮书与 inventory map

**Files：** `personal_production_one_person_company_operations_whitepaper.*`、`one_person_company_inventory_map.*`。

- [ ] 保留规范数量：12 层、5 个虚拟部门、30 个责任域、20 个模块、60 个文档、15 个受治理 AI Agent、15 本书、12 个启动文档。
- [ ] 确保 12 层每一行或小节包含输入、工具与技术、输出。
- [ ] 在 PMBOK / 项目集 / 项目组合 / PMO / 敏捷实践改变运营规则处加入明确解释。
- [ ] 链接专属一人公司 North Star。

### Task 5: 创建专属一人公司 North Star

**Files：** `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` 与 `.zh-CN.md`。

- [ ] 把主指标定义为 validated operating-loop throughput。
- [ ] 定义客户证据、收入/现金、交付稳定、支持负载、学习节奏和 governed-agent review 输入指标。
- [ ] 定义未评审 AI commitments、runway、support risk、privacy/compliance risk 和 over-documentation 护栏。
- [ ] 定义触发完整架构、轻量模式、模块级升级或 stop/pivot 的 decision thresholds。

### Task 6: 更新 tailoring rules 与 registry

**Files：** `lifecycle_tailoring_rules.*`、`docs_registry.yaml`。

- [ ] 加入一人公司专属 full / lightweight / hybrid tailoring matrix。
- [ ] 登记新 North Star 双语 pair。
- [ ] 现有 policy 要求时保持英文主文件 ASCII-clean。

### Task 7: 验证、提交并本地集成

**Files：** 除非 validation 要求修复，否则不增加额外内容文件。

- [ ] 运行 `python tools/check_document_pair_policy.py --root . --json`。
- [ ] 运行 `python tools/check_document_governance_rules.py --root . --json`。
- [ ] 运行 `python tools/check_precommit_update_archive.py --root . --json`。
- [ ] 运行 `python tools/run_openspec_guard.py --root . --json`。
- [ ] 运行 `powershell -NoProfile -ExecutionPolicy Bypass -File tools\ci\local_gate.ps1`。
- [ ] 运行 `powershell -NoProfile -ExecutionPolicy Bypass -File tools\ci\local_mr_review.ps1`。
- [ ] 提交 implementation package。
- [ ] 从 primary root 使用 `tools/complete_local_flow_to_remote_gate.py --execute --json` 集成本地 `main`。
- [ ] 确认 rollback ref、completed claim、cleanup 和 `remote_publication_performed=false`。

## 7. 验收标准

只有满足下列条件，rollout 才算完成：

- 本 frozen plan pair 已在 Stage B 开始前提交并合入 local `main`。
- Stage B 文档引用覆盖三个 source roots 的新 fresh extraction run。
- 新一人公司 North Star 双语 pair 存在、被 registry 登记，并从白皮书或 inventory map 链接。
- 白皮书和 inventory map 保留全部规范数量。
- 执行相关流程使用输入 / 工具与技术 / 输出格式。
- 裁剪规则清楚区分完整架构、整个项目轻量、阶段局部轻量、模块级轻量和混合方式。
- 所有 local validation gates 通过。
- 本地 `main` 包含最终 implementation commit 和 rollback evidence。
- 没有明确远程发布授权时，不执行 remote publication。
