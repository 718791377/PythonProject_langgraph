---
doc_id: general_template_phase0_update_patch_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md
translation_of: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md
status: active
plan_readiness: ready-for-implementation
doc_class: implementation_plan
last_reviewed: 2026-05-27
target_template: "D:\PythonProject_General"
capability_tier: fuller-codex-openspec-comet-governance-template
comet_workflow: full
---

# `D:\PythonProject_General` Phase 0 通用治理模板实施方案

> **For agentic workers:** REQUIRED SUB-SKILL：使用 `comet` 作为 OpenSpec + Superpowers 控制层，然后按任务使用 `superpowers:executing-plans` 或等价逐步执行方式。每个 checkbox 都是工作证据。没有完成目标仓库干净性预检和明确写入范围前，不要写入 `D:\PythonProject_General`。

**Goal:** 将 `D:\PythonProject_General` 做成更完整、可复用的 Codex/OpenSpec/Comet 生产模板，但不克隆 `D:\PythonProject_langgraph` 的 live state。模板必须能为新项目干净 hydrate，并提供可复用治理、检查与可选 durable orchestration 入口。

**Architecture:** 模板源码定义冷启动权威、OpenSpec/Superpowers/Comet 治理、MCP 与 launcher payload 边界、可选编排 profile、LangGraph 兼容源码模板，以及 manifest-driven 的 local/remote gate 一致性。运行时状态由 hydrate 后的新项目自行生成，绝不从本仓库复制。

**Tech Stack:** Git、OpenSpec、Comet、Superpowers、Codex 启动文档、native Codex agent TOML schema 检查、PowerShell gates、Python checkers、JSON reports、可选 `tools/langgraph_durable_orchestrator/` 模板源码、生成项目 `.omx/state/` ignore/state 规则。

---

## 0. 复核结论

旧方案方向正确，但对冷启动 worker 来说仍然偏粗：缺少可直接执行的源事实读取、模板拓扑、artifact contract、任务切片、验证证据、回滚路径和验收门槛。本版把这些内容拆成可执行结构。

完整性复核：

| 领域 | 结论 | 落点 |
| --- | --- | --- |
| General 与 General_2 边界 | 完整 | 第 1、2 节 |
| Comet/OpenSpec/Superpowers contract | 完整 | 第 1.2、4 节 |
| 可选 orchestration 模板边界 | 完整 | 第 3.4、5 节 Task 3、Task 4 |
| LangGraph source 与 runtime state | 完整 | 第 3.5、5 节 Task 4 |
| MCP 与 launcher payload policy | 完整 | 第 3.3、5 节 Task 3 |
| Local/remote CI/MR parity | 完整 | 第 3.6、5 节 Task 5 |
| 验证与回滚 | 完整 | 第 6、8 节 |

## 1. 关系模型与命名边界

### 1.1 `General` 与 `General_2`

- `PythonProject_General` 是 fuller governance template。它可以模板化 oh-my-codex、native_omx、LangGraph compatibility source、MCP scope policy、launcher payload policy、local/remote gate parity，以及生成项目的 repo-local durable-state 脚手架。
- `PythonProject_General_2` 是 local-only template。它必须保持 local Git + OpenSpec + Superpowers + native Codex subagents only。
- 两个模板都不得把 `D:\PythonProject_langgraph` 的 live `.omx/state/`、selector、worktree claim、runtime log、当前 mainline facts、凭据或用户专属绝对路径复制成默认值。

### 1.2 Comet / OpenSpec / Superpowers

- OpenSpec 负责 WHAT：proposal、design constraints、capability specs、tasks、validation 与 archive。
- Superpowers 负责 HOW：brainstorming、planning、execution discipline、TDD/debugging/review 与 verification-before-completion。
- Comet 协调五阶段控制环：Open -> Design -> Build -> Verify -> Archive。
- Comet 不是 native subagent、oh-my-codex、native_omx、LangGraph 或 durable-team backend。模板中引用 `/comet` 时必须显式保留这个边界。

### 1.3 可选编排产品线假设

General 可以把 Codex orchestration 产品线写成可复用假设：

- native Codex 仍是基础层；
- oh-my-codex 是 additive workflow layer；
- native_omx 是 worker-centric durable lane；
- LangGraph 是 graph-shaped durable orchestration lane；
- 一个 durable task 同一时间只使用一个 backend family；
- durable team 受阈值约束，不在模板启动时自动拉起。

这些是可模板化治理假设，不是生成项目已经有 running team 或 ready LangGraph backend 的证据。

## 2. 目标与非目标

### 2.1 目标

- 为新项目提供可复用冷启动 read order 与按任务补读的 policy routing。
- 提供 OpenSpec + Superpowers + Comet 治理文档与安全示例 change 脚手架。
- 提供本地和远端都能复用 JSON 输出形状的 CI/MR gate 脚本。
- 提供 Windows-safe 的 MCP scope 与 launcher payload 指南，避免长 inline startup payload。
- 提供可选 LangGraph compatibility/orchestration source 模板，同时保持官方 `langgraph` 安装在用户级共享环境。
- 提供生成项目 durable-state 规则：`.omx/state/` 可在 hydrate 后由项目运行时生成，但不得从本仓库复制。
- 提供 fail-closed checkers：未解析 placeholder、缺失双语配对、native agent TOML 格式错误、local/remote gate 漂移都要失败。

### 2.2 非目标

- 不克隆 `D:\PythonProject_langgraph`。
- 不安装或修改用户级 Codex 配置、全局 pip/npm/Git 配置、浏览器配置或凭据。
- 不复制 `.git/`、`.venv/`、`node_modules/`、`.env`、cache、token、runtime log 或 `.omx/state/`。
- 不在 Phase 0 实现业务应用代码、GUI flow、浏览器自动化、远端发布或 persistent team runtime。
- 不推送远端，也不创建 GitLab/GitHub MR/PR。

## 3. 目标模板拓扑

建议 hydrate 后结构：

```text
D:\PythonProject_General
|-- AGENTS.md
|-- README.md
|-- TEMPLATE_MANIFEST.md
|-- .gitignore
|-- .codex\agents\
|-- template_assets\codex-agents\
|-- docs_bilingual\
|   |-- project_startup_summary.md
|   |-- project_startup_summary.zh-CN.md
|   |-- docs_registry.yaml
|   `-- governance\
|-- openspec\
|   |-- changes\
|   `-- specs\
|-- tools\
|   |-- ci\
|   |-- langgraph_durable_orchestrator\
|   `-- template_checks\
`-- template_assets\
```

### 3.1 Startup authority

生成项目拥有自己的 `docs_bilingual/project_startup_summary.md` 与 `.zh-CN.md`。模板可以定义可复用 read order，但不得把本仓库当前 read order 当成 live fact 复制进去。上下文保留哨兵规则可以引用，但哨兵字面提示只属于生成项目的 startup summary pair。

### 3.2 OpenSpec 与 Comet assets

General 应创建本地 OpenSpec skeleton 与 template-safe example change。不得复制本仓库 active 或 archived changes。示例 artifacts 必须标注为 example，并允许项目初始化后删除。

### 3.3 MCP 与 launcher payload assets

MCP 文档必须区分：

- Codex-direct project tools；
- MCP Router shared tools；
- 默认不属于任一侧的工具。

Launcher 文档与 helper 必须优先使用短 file-backed payload reference，而不是通过 `-c developer_instructions=...` 传入长 inline 指令。

### 3.4 可选 orchestration assets

General 可以包含 oh-my-codex、native_omx 与 LangGraph 的可选 profile 文档。这些文档必须区分 `installed`、`enabled`、`selected`、`ready` 状态，并且不得声称生成项目已经选择或拉起 durable orchestration。

### 3.5 LangGraph compatibility source 与 state

- 官方 `langgraph` 包：用户级共享安装，不 vendored 到模板内。
- `tools/langgraph_durable_orchestrator/`：repo-local compatibility/orchestration source，可以模板化。
- `.omx/state/langgraph/`：只允许作为生成项目 runtime state；hydrate 后按需创建或 ignore。

### 3.6 CI/MR parity

Local CI、local MR review 与 remote CI/MR 必须调用同一套 manifest-driven scripts。远端配置可以安装前置依赖并调用共享脚本，但不得维护另一套漂移 checker sequence。

## 4. Comet / OpenSpec / Superpowers Contract

- 每个实质模板更新默认先有 OpenSpec change，除非明确归类为小 tweak/hotfix。
- Comet state 是 change governance metadata，不是生成项目的 durable runtime state。
- Superpowers planning 必须形成任务级 implementation slices，包含 files、steps、validation 与 rollback。
- Archive 只有在 verification evidence 存在后才关闭 OpenSpec loop。
- 本方案是源仓库方案；实际写入目标模板仍需要目标仓库 precheck 与目标本地 OpenSpec change。

## 5. 任务级实施切片

### Task 0：目标清点与写入范围冻结

**Files:**

- Read: `D:\PythonProject_General\AGENTS.md`
- Read: `D:\PythonProject_General\README.md`
- Read: `D:\PythonProject_General\docs_bilingual\`
- Read: `D:\PythonProject_General\openspec\`

**Steps:**

- [ ] 确认 `D:\PythonProject_General` 是本地 Git 仓库。
- [ ] 运行 `git status --short`，若存在未提交人工修改则停止。
- [ ] 运行 `openspec list --json`，记录目标本地 active changes，但不复制本仓库 changes。
- [ ] 为治理模板更新创建目标本地 OpenSpec change。
- [ ] 修改文件前记录精确 write scope。

**Validation:**

- [ ] 目标状态已知且干净，或 blocker 已报告。
- [ ] 目标本地 OpenSpec change 已存在。

### Task 1：Startup summaries、README、registry 与 AGENTS

**Files:**

- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs_bilingual/project_startup_summary.md`
- Modify: `docs_bilingual/project_startup_summary.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

**Steps:**

- [ ] 定义模板目标与非目标。
- [ ] 加入可复用冷启动 read order 与按任务补读的 policy categories。
- [ ] 解释 Comet、OpenSpec 与 Superpowers 边界。
- [ ] 加入上下文保留哨兵位置规则，但不复制本仓库任何 corrupted 或 live literal sentinel text。
- [ ] 登记长期维护的双语 governance docs 与 implementation plans。

**Validation:**

- [ ] 双语配对检查通过。
- [ ] Startup summaries 不含 unresolved placeholders 或 mojibake。

### Task 2：治理文档集合

**Files:**

- Create/modify: `docs_bilingual/governance/` 下治理文档
- Modify: `TEMPLATE_MANIFEST.md`

**Steps:**

- [ ] 增加 multi-session/worktree isolation 规则。
- [ ] 增加 MCP scope 规则。
- [ ] 增加 launcher-payload 规则。
- [ ] 增加 orchestration activation 规则。
- [ ] 增加 OpenSpec official workflow 与 Comet/Superpowers workflow 规则。
- [ ] 将项目专属示例标为 placeholders。

**Validation:**

- [ ] `docs_bilingual/docs_registry.yaml` 登记每个长期治理文档。
- [ ] Policy docs 不声称本仓库 live state。

### Task 3：可选 orchestration profile 模板

**Files:**

- Create/modify: `docs_bilingual/governance/codex_orchestration_profile.md`
- Create/modify: `docs_bilingual/governance/codex_orchestration_profile.zh-CN.md`
- Modify: `AGENTS.md`

**Steps:**

- [ ] 定义 native Codex 为 base layer。
- [ ] 定义 oh-my-codex、native_omx、LangGraph 为 optional profiles。
- [ ] 区分 installed/enabled/selected/ready 状态。
- [ ] 写明 durable-team thresholds 与 single-backend-family 规则。
- [ ] 不把 General_2 exclusions 写成 General optional profile default。

**Validation:**

- [ ] 生成文档不暗示 durable orchestration 已经 running。
- [ ] Activation trace 示例引用阈值或 blocker。

### Task 4：LangGraph compatibility source 与 runtime-state scaffold

**Files:**

- Create/modify: `tools/langgraph_durable_orchestrator/`
- Modify: `.gitignore`
- Modify: `TEMPLATE_MANIFEST.md`
- Modify: 相关 LangGraph governance docs

**Steps:**

- [ ] 如目标模板支持 LangGraph，则模板化 repo-local compatibility/orchestration source。
- [ ] 文档写明官方 `langgraph` 安装在用户级共享 LangGraph venv。
- [ ] 将 `.omx/state/` 与 generated runtime reports 加入 ignore。
- [ ] 为 `.omx/state/langgraph/` 提供 placeholder 或 generator note，而不是复制 live state。
- [ ] 提供 readiness-check commands，能分别报告 installed/enabled/selected/ready。

**Validation:**

- [ ] 模板源码中不存在复制来的 `.omx/state/` 文件。
- [ ] LangGraph 文档区分源码、官方包与运行时状态。

### Task 5：Manifest-driven CI/local gate parity

**Files:**

- Create/modify: `tools/ci/local_gate.ps1`
- Create/modify: `tools/ci/local_mr_review.ps1`
- Create/modify: `tools/ci/ci_test_manifest.json`
- Create/modify: Python/Node/PowerShell checker scripts
- Create/modify: remote CI config（仅当模板明确包含 remote CI）

**Steps:**

- [ ] 用一个 manifest 定义所有 check steps。
- [ ] 本地与远端 CI 都输出稳定 JSON report。
- [ ] local MR review 调用同一 checker sequence。
- [ ] 增加 drift checker，远端 CI 若使用漂移脚本序列则失败。
- [ ] 将新增 tests 登记进 manifest。

**Validation:**

- [ ] `tools/ci/local_gate.ps1 -Root . -Json` 通过。
- [ ] `tools/ci/local_mr_review.ps1 -Root . -Json` 通过。
- [ ] 本地与远端配置共享同一 entrypoint。

### Task 6：Hydration 与模板健康

**Files:**

- Create/modify: `tools/test_template_hydration.py`
- Create/modify: `tools/check_template_health.py`
- Create/modify: `tools/check_bilingual_pairs.py`
- Create/modify: `tools/check_custom_agent_toml_schema.py`

**Steps:**

- [ ] 从模板 hydrate 一个临时项目。
- [ ] 验证 placeholders 已解析或被明确标记为 intentionally documented。
- [ ] 验证 startup summaries、OpenSpec skeleton、optional profile docs 与 gate scripts 存在。
- [ ] 验证 ignored runtime directories 未被复制。
- [ ] 验证双语文档配对且 UTF-8 干净。

**Validation:**

- [ ] `python .\tools\test_template_hydration.py --root . --json` 通过。
- [ ] `git diff --check` 通过。

### Task 7：目标本地提交与源仓库方案维护

**Files:**

- Tasks 0-6 修改的目标仓库文件
- 源仓库 `docs_bilingual/implementation_plans/` 下方案文件

**Steps:**

- [ ] 只有目标验证通过后，才在 `D:\PythonProject_General` 提交目标模板更新。
- [ ] 当 scope 或 validation 改变时，同步维护本源仓库方案配对。
- [ ] 没有明确远端发布批准时，不推送任何远端。

**Validation:**

- [ ] 目标仓库有本地 commit 且 status clean。
- [ ] 源仓库 plan checker 与 OpenSpec guard 通过。

## 6. 验证计划

在 `D:\PythonProject_General` 目标仓库运行：

```powershell
python .\tools\test_template_hydration.py --root . --json
.\tools\ci\local_gate.ps1 -Root . -Json
.\tools\ci\local_mr_review.ps1 -Root . -Json
openspec validate --all
git diff --check
git status --short
```

在 `D:\PythonProject_langgraph` 维护本方案时运行：

```powershell
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --json
.\tools\ci\local_mr_review.ps1 -Root . -Json
.\tools\ci\local_gate.ps1 -Root . -Json
git diff --check
```

## 7. 验收标准

- [ ] General 明确是 fuller governance template，而不是 `D:\PythonProject_langgraph` 克隆。
- [ ] Comet 被定义为 OpenSpec + Superpowers governance，而不是 subagent 或 durable backend。
- [ ] MCP scope、launcher payload、orchestration activation、LangGraph source/state 与 CI/MR parity 均有 template-safe docs 和 checker paths。
- [ ] 未复制 live `.omx/state/`、selectors、worktree claims、logs、credentials 或当前 mainline facts。
- [ ] Hydrated project 会 ignore 或本地生成 `.omx/state/`、`.venv/`、`node_modules/`、`.env`、tokens、coverage 与 temporary reports。
- [ ] 英文与中文文档成对、UTF-8 干净，长期文档已登记。

## 8. 回滚与清理

- 文档误改：使用本地 Git revert 回滚，并重新运行 `git diff --check` 与 OpenSpec guard。
- `D:\PythonProject_General` 目标模板误改：使用目标仓库本地 Git 回滚；若未提交，则按 `git status --short` 文件清单逐项恢复。
- Hydration 失败：保留失败临时目录与 JSON report 直到定位根因，修复后重新跑 smoke test。
- LangGraph 模板错误：只回滚模板 `tools/langgraph_durable_orchestrator/` 源码或文档，不删除用户级官方 `langgraph` 安装。
- Launcher/helper payload 错误：回滚模板生成逻辑，不修改用户级 launcher 或全局 Codex 配置。
- Phase 0 回滚不删除远端分支、不推送远端、不修改 protected remote settings。

## 9. 风险与默认决策

- 风险：模板文档误继承 live facts。默认：使用 placeholders 与 target-local probes，永不复制 runtime state。
- 风险：文档让 LangGraph 看起来已经启用。默认：描述 optional profile states，并要求 readiness checks。
- 风险：local 与 remote gates 漂移。默认：remote CI 调用 local manifest-driven gate。
- 风险：Windows 命令行 payload 过长。默认：使用 file-backed instruction payloads。
- 风险：中文文档因终端复制产生 mojibake。默认：直接读写 UTF-8 文件并验证源文本，而不是相信 console rendering。

## 10. 自检清单

- [ ] 每个 implementation slice 都列出 files、steps 与 validation。
- [ ] 可选 orchestration source 与 runtime state 已分离。
- [ ] 官方 LangGraph 包安装位置是用户级，不 vendored。
- [ ] `.omx/state/` 只是生成项目状态。
- [ ] Comet、OpenSpec 与 Superpowers 角色显式分离。
- [ ] CI/MR parity 是 manifest-driven。
- [ ] 回滚不修改用户级配置或远端。
