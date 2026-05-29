---
doc_id: general_2_local_git_openspec_subagents_only_bootstrap_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.md
translation_of: docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.md
status: active
plan_readiness: ready-for-implementation
doc_class: implementation_plan
last_reviewed: 2026-05-27
target_template: "D:\PythonProject_General_2"
capability_tier: local-git-openspec-superpowers-native-subagents-only
comet_workflow: full
---

# `D:\PythonProject_General_2` 本地 Git + OpenSpec + Superpowers + Native Subagents 模板方案

> **For agentic workers:** REQUIRED SUB-SKILL：使用 `comet` 作为 OpenSpec + Superpowers 控制层，然后按本方案逐个 checkbox 执行。不要向本模板加入 oh-my-codex、native_omx、LangGraph、remote CI/MR 或 `.omx/state/`。

**Goal:** 保持 `D:\PythonProject_General_2` 是轻量 local template：只面向需要 local Git、OpenSpec、Superpowers 与 native Codex subagents 的项目。模板应适合离线/本地项目，不暗示 durable orchestration 或 remote publication。

**Architecture:** 一个 local-only 仓库，包含双语启动文档、OpenSpec skeleton、Comet/Superpowers workflow 指南、成对 native agent TOML 目录、local-only bootstrap scripts、具有远端兼容 JSON 形状的 local gate scripts，以及禁止 orchestration/runtime surface 的 checkers。

**Tech Stack:** Local Git、OpenSpec、Comet、Superpowers、native Codex custom agent TOML、`.codex/agents/`、`template_assets/codex-agents/`、Python checkers、PowerShell local gate、UTF-8 bilingual Markdown。

---

## 0. 复核结论

旧方案正确排除了 oh-my-codex、OMX、LangGraph、remote CI/MR 与 `.omx/state/`，但对未来 worker 来说仍缺少任务级颗粒度。本版把 local-only 边界转换为可执行切片，包含文件所有权、检查、验收标准与回滚。

完整性复核：

| 领域 | 结论 | 落点 |
| --- | --- | --- |
| Local-only 能力边界 | 完整 | 第 1、2 节 |
| OpenSpec + Superpowers + Comet contract | 完整 | 第 1.2、4 节 |
| Native agent TOML 配对 | 完整 | 第 3.2、5 节 Task 3 |
| Local gate JSON 兼容形状 | 完整 | 第 3.4、5 节 Task 5 |
| 禁止 OMX/LangGraph surface | 完整 | 第 2.2、7 节 |
| 验证与回滚 | 完整 | 第 6、8 节 |

## 1. 关系模型与命名边界

### 1.1 这个模板是什么

`PythonProject_General_2` 是 local-only bootstrap template。新项目如果需要治理与 native Codex subagents，但不需要远端发布或 durable orchestration，应使用这个模板。

它包含：

- 本地 Git 历史；
- 本地 OpenSpec artifacts；
- Superpowers 与 Comet workflow instructions；
- native Codex custom agent TOML files；
- local checkers 与 local gate helpers；
- 双语文档配对。

### 1.2 这里的 Comet 是什么

Comet 表示 OpenSpec + Superpowers workflow：

- OpenSpec 负责 WHAT；
- Superpowers 负责 HOW；
- Comet 协调 Open -> Design -> Build -> Verify -> Archive。

Comet 不是 oh-my-codex、native_omx、LangGraph、persistent team，也不是 native subagent evidence。

### 1.3 `.codex/agents/` 与 `template_assets/codex-agents/`

- `.codex/agents/` 是项目本地 native Codex agent 目录，Codex 运行时可以读取。
- `template_assets/codex-agents/` 是可分发副本，用于比较、恢复或把同一套 agent definitions 安装到其他位置。
- 两个目录必须包含同一组预期 TOML 文件。
- 每个 standalone custom agent TOML 必须定义顶层 `name`、`description`、`developer_instructions`。

## 2. 目标与非目标

### 2.1 目标

- 提供 minimal local Git + OpenSpec + Superpowers + Comet governance template。
- 在成对 source/distribution 目录中提供 native Codex subagent TOML definitions。
- 提供 local-only bootstrap scripts；除非后续显式运行安装命令，否则不修改用户级 Codex 配置。
- 提供 local gate scripts：JSON 输出兼容更完整模板的 gate 格式，但不添加 remote CI/MR 配置。
- 提供 UTF-8 双语 startup summaries 与 governance docs。
- 提供 checkers：如果引入 oh-my-codex、native_omx、LangGraph、`.omx/state/` 或 remote CI/MR 文件则失败。

### 2.2 非目标

- 默认不配置 `origin`、`gitlab` 或 `github` remote。
- 不创建 `.gitlab-ci.yml`、`.github/workflows/`、GitLab MR helper 或 GitHub PR helper。
- 不安装或调用 oh-my-codex、native_omx、OMX durable team、LangGraph、LangGraph CLI wrapper 或 `tools/langgraph_durable_orchestrator/`。
- 不创建 `.omx/state/`、`.omx/session-claims/`、LangGraph backend JSON、durable selector 或 durable-team receipt。
- 不复制 `C:\Users\lenovo\.codex\config.toml`、token、`.env`、credential cache、`.venv/`、`node_modules/`、`.git/` 或 `D:\PythonProject_langgraph` live facts。

## 3. 目标模板拓扑

建议结构：

```text
D:\PythonProject_General_2
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
`-- tools\
    |-- ci\
    `-- template_checks\
```

### 3.1 Startup docs

Startup summaries 必须解释 local-only scope、read order、OpenSpec/Comet/Superpowers roles、native subagent boundaries 与 local gate commands。如果未来加入上下文保留哨兵，其字面提示只属于 startup summary pair。

### 3.2 Native agent assets

模板只应包含明确维护的通用 TOML 文件。默认不从用户级目录或无关 repo-local 目录复制 agents。若未来支持安装到用户级目录，必须显式触发、先备份、可回滚。

### 3.3 OpenSpec assets

创建本地 OpenSpec skeleton 与可选 sample change。不得复制本仓库 active changes、archived changes、Comet state 或当前 mainline facts。

### 3.4 Local gate assets

Local gate scripts 可以使用与 remote-capable templates 相同的 JSON report 格式，方便下游自动化统一解析。这只是格式兼容，不表示启用 remote CI/MR。

## 4. Comet / OpenSpec / Superpowers Contract

- 使用 OpenSpec 管理本地 change lifecycle 与 durable WHAT evidence。
- 使用 Superpowers 管理 HOW discipline、planning、execution 与 verification。
- 使用 Comet 协调 phase evidence 与 archive readiness。
- 所有 Comet/OpenSpec state 都保持项目本地、人类可读。
- 不把 Comet 使用解释成 native subagent execution 或 durable orchestration 证据。

## 5. 任务级实施切片

### Task 0：目标清点与 local-only 写入范围

**Files:**

- Read: `D:\PythonProject_General_2\AGENTS.md`
- Read: `D:\PythonProject_General_2\README.md`
- Read: `D:\PythonProject_General_2\openspec\`
- Read: `D:\PythonProject_General_2\.codex\agents\`

**Steps:**

- [ ] 确认目标目录是否已存在。
- [ ] 如果目标是 Git 仓库，运行 `git status --short`，遇到未提交人工修改则停止。
- [ ] 记录是否存在 remotes；如果意外存在 remotes，只报告，不自动删除。
- [ ] 为 local-only governance bootstrap 创建目标本地 OpenSpec change。
- [ ] 编辑文件前冻结 write scope。

**Validation:**

- [ ] 已记录目标状态与 blocker。
- [ ] 本任务没有添加 remote configuration。

### Task 1：Local-only docs 与 startup authority

**Files:**

- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `TEMPLATE_MANIFEST.md`
- Modify: `docs_bilingual/project_startup_summary.md`
- Modify: `docs_bilingual/project_startup_summary.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

**Steps:**

- [ ] 声明此模板只包含 local Git + OpenSpec + Superpowers + native subagents。
- [ ] 定义 read order 与按任务补读的 docs。
- [ ] 解释 Comet 是 OpenSpec + Superpowers 控制层，不是 durable orchestration。
- [ ] 加入 forbidden-surface reminders：oh-my-codex、OMX、LangGraph、remote CI/MR、`.omx/state/`。
- [ ] 登记需要长期维护的双语文档。

**Validation:**

- [ ] 双语配对检查通过。
- [ ] 文档不含 mojibake 或复制来的 live facts。

### Task 2：OpenSpec 与 Comet local skeleton

**Files:**

- Create/modify: `openspec/config.yaml`
- Create/modify: `openspec/changes/`
- Create/modify: `openspec/specs/`
- Create/modify: `docs_bilingual/governance/openspec_comet_local_workflow.md`
- Create/modify: `docs_bilingual/governance/openspec_comet_local_workflow.zh-CN.md`

**Steps:**

- [ ] 缺失时创建本地 OpenSpec 目录。
- [ ] 添加 template-safe example change 或 bootstrap note。
- [ ] 说明 change history 属于项目本地，不从本仓库复制。
- [ ] 记录 Comet phase loop 与 archive criteria。

**Validation:**

- [ ] 目标仓库中 `openspec validate --all` 通过。
- [ ] 示例 artifacts 明确标记为 template examples。

### Task 3：Native agent TOML pairing

**Files:**

- Modify/create: `.codex/agents/*.toml`
- Modify/create: `template_assets/codex-agents/*.toml`
- Create/modify: `tools/check_custom_agent_toml_schema.py`
- Create/modify: `tools/check_agent_asset_pairs.py`

**Steps:**

- [ ] 只选择属于此模板的通用 local agents。
- [ ] 保持 `.codex/agents/` 与 `template_assets/codex-agents/` 文件名一致。
- [ ] 验证每个 TOML 都有 `name`、`description`、`developer_instructions`。
- [ ] 默认不复制本仓库中缺失或无关的 agents。
- [ ] 如果未来支持用户级安装，覆盖前必须备份。

**Validation:**

- [ ] `python .\tools\check_custom_agent_toml_schema.py --root .` 通过。
- [ ] Pair checker 通过。

### Task 4：Local-only policy checker

**Files:**

- Create/modify: `tools/check_subagent_only_policy.py`
- Create/modify: `tools/check_local_git_only_policy.py`
- Create/modify: `tools/check_template_health.py`
- Create/modify: `.gitignore`

**Steps:**

- [ ] 如果模板中存在 `.omx/state/` 或 `.omx/session-claims/` 则失败。
- [ ] 如果引入 LangGraph runtime/source 文件则失败。
- [ ] 如果 oh-my-codex/native_omx launcher docs 被写成 enabled 则失败。
- [ ] 如果出现 remote CI/MR config 则失败。
- [ ] 确保 `.gitignore` 排除 local caches、`.venv/`、`node_modules/`、`.env`、coverage 与 temp reports。

**Validation:**

- [ ] `python .\tools\check_subagent_only_policy.py --root .` 通过。
- [ ] `python .\tools\check_local_git_only_policy.py --root .` 通过。

### Task 5：具有兼容 JSON 形状的 local gate

**Files:**

- Create/modify: `tools/ci/local_gate.ps1`
- Create/modify: `tools/ci/local_mr_review.ps1`
- Create/modify: `tools/ci/ci_test_manifest.json`（如果使用 manifest）

**Steps:**

- [ ] local gate 运行 template health、subagent-only、TOML schema、bilingual pair、local Git-only、OpenSpec 与 `git diff --check`。
- [ ] JSON 输出保持稳定，并兼容 fuller template gate shape。
- [ ] `local_mr_review` 只作为本地 review/report helper；不配置远端 MR 创建。
- [ ] 文档说明 remote CI/MR 不属于此模板范围。

**Validation:**

- [ ] `tools\ci\local_gate.ps1 -Root . -Json` 通过。
- [ ] `tools\ci\local_mr_review.ps1 -Root . -Json` 通过。

### Task 6：Bootstrap scripts 与本地 Git 初始化

**Files:**

- Create/modify: `tools/bootstrap-local-project.ps1`
- Create/modify: `tools/bootstrap-new-pc.ps1`
- Create/modify: `tools/install-subagents-user-level.ps1`（仅当支持用户级安装）

**Steps:**

- [ ] Bootstrap 必须幂等且参数化。
- [ ] 使用 `$env:USERPROFILE` 或参数，不硬编码用户路径。
- [ ] 只在确认的目标 root 内运行 `git init -b main`。
- [ ] 不添加 remotes。
- [ ] 如需提交初始内容，只在验证通过后本地提交。

**Validation:**

- [ ] Bootstrap dry-run 报告 planned actions。
- [ ] Bootstrap 后 local Git 没有默认 remote。

### Task 7：源仓库方案维护与本地集成

**Files:**

- 源仓库 `docs_bilingual/implementation_plans/` 下方案配对
- Tasks 0-6 修改的目标仓库文件

**Steps:**

- [ ] 保持本方案配对与目标模板实际 contract 一致。
- [ ] 运行源仓库 implementation-plan 与 OpenSpec checks。
- [ ] 目标验证通过后，只在目标仓库本地 commit。
- [ ] 没有明确远端发布批准时，不推送任何远端。

**Validation:**

- [ ] 源方案配对通过仓库 checks。
- [ ] 目标仓库 local commit 后 status clean。

## 6. 验证计划

在 `D:\PythonProject_General_2` 运行：

```powershell
python .\tools\check_template_health.py --root .
python .\tools\check_subagent_only_policy.py --root .
python .\tools\check_custom_agent_toml_schema.py --root .
python .\tools\check_bilingual_pairs.py --root .
python .\tools\check_local_git_only_policy.py --root .
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

- [ ] General_2 保持 local Git + OpenSpec + Superpowers + native Codex subagents only。
- [ ] `.codex/agents/` 与 `template_assets/codex-agents/` 保持成对。
- [ ] 每个 agent TOML 都有 `name`、`description`、`developer_instructions`。
- [ ] 不存在 `.omx/state/`、`.omx/session-claims/`、LangGraph、oh-my-codex、native_omx、remote CI 或 remote MR/PR config。
- [ ] Local gates 输出稳定 JSON，且不需要远端。
- [ ] 中文与英文文档成对且 UTF-8 干净。

## 8. 回滚与清理

- 错误目标目录先重命名为 `D:\PythonProject_General_2.backup.<timestamp>`，再人工清理。
- 文档或 checker 误改使用目标本地 Git 回滚。
- 如果曾显式运行 user-level agent install，从 `%USERPROFILE%\.codex\agents.backup.<timestamp>\` 恢复。
- 只有确认没有需要保留的 commits 后，才人工删除 `.git/`。
- OpenSpec 文件按 `git status --short` 列表逐项恢复，不自动清空 `openspec/`。
- 不使用会递归删除已确认目标 root 之外内容的清理脚本。

## 9. 风险与默认决策

- 风险：local-only 模板误加入 durable orchestration。默认：`check_subagent_only_policy.py` fail closed。
- 风险：agent TOML runtime 与 template assets 漂移。默认：pair checker 比较文件名与必需 schema。
- 风险：gate JSON 兼容导致误以为启用了 remote CI/MR。默认：文档说明 JSON compatibility 只是格式兼容。
- 风险：复制终端输出污染中文文档。默认：直接写 UTF-8 文件并检查源文本。
- 风险：用户级 agent install 覆盖既有文件。默认：不默认安装；显式安装必须备份。

## 10. 自检清单

- [ ] 未启用 oh-my-codex、OMX、LangGraph、remote CI/MR 或 `.omx/state/` surface。
- [ ] OpenSpec 与 Comet 只是 local governance。
- [ ] Native agent TOML 文件成对且 schema-valid。
- [ ] Local gates 与 checkers 有明确命令。
- [ ] 回滚绝不自动删除 Git history。
- [ ] 源仓库与目标仓库保持分离。
