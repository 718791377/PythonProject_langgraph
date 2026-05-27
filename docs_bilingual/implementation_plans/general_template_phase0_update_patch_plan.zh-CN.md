---
doc_id: general_template_phase0_update_patch_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md
zh_cn_path: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md
status: active
updated_at: 2026-05-27
target_template: D:\PythonProject_General
comet_change: refactor-general-template-plans-comet
capability_tier: fuller-codex-openspec-comet-governance-template
---

# D:\PythonProject_General Phase 0 通用治理模板实施计划

## 1. 目标

`D:\PythonProject_General` 是更完整的通用 Codex/OpenSpec/Comet 生产模板。Phase 0 的目标不是把它变成 `D:\PythonProject_langgraph` 的克隆，而是把可复用的治理能力做成模板化、可验证、可回滚的基础层。

Phase 0 完成后，新项目应能继承清晰的冷启动摘要、OpenSpec 治理、Superpowers 方法论、Comet 工作流说明、local/remote gate 一致性、MCP scope 边界、Windows-safe launcher payload 规则，以及可选 LangGraph/OMX 能力的模板入口。所有 live runtime state 必须在生成项目运行后再产生，不能从本仓库复制。

## 2. 能力定位

### 2.1 General 与 General_2 的区别

- General 是 fuller governance template：允许模板化 oh-my-codex、native_omx、LangGraph 兼容源码、MCP scope policy、launcher payload policy、local/remote CI/MR gate parity 和生成项目的 repo-local durable-state 脚手架。
- General_2 是 local-only template：只允许本地 Git、OpenSpec、Superpowers governance 和 native Codex subagents，不启用 remote CI/MR、oh-my-codex、native_omx、LangGraph durable backend 或 `.omx/state/`。

### 2.2 Comet 边界

`/comet` 在本计划中表示 OpenSpec + Superpowers 的双星治理流程：OpenSpec 负责 WHAT、proposal、spec、tasks、validate 和 archive；Superpowers 负责 HOW、brainstorming、writing-plans、executing-plans、verification-before-completion；Comet 负责阶段调度、状态证据和归档闭环。

Comet 不是 native subagent evidence，不是 oh-my-codex，不是 native_omx，不是 LangGraph，也不是 durable-team backend。文档中引用 Comet 时必须同时说明这个边界。

## 3. Phase 0 范围

### 3.1 范围内

- 更新 `AGENTS.md`：写入冷启动读取顺序、OpenSpec/Comet/Superpowers 边界、multi-session/worktree isolation、MCP scope、launcher payload、orchestration activation 和提示词哨兵规则。
- 更新 `README.md` 与启动摘要：让没有历史聊天上下文的新 Codex 会话知道模板目标、生成方式、验证命令和回滚方式。
- 更新 `docs_bilingual/docs_registry.yaml`：登记需要长期维护的双语治理文档和 implementation plans。
- 提供 `tools/test_template_hydration.py`：用于生成临时项目并验证 hydrate 后没有未解析占位符。
- 提供 `tools/ci/local_gate.ps1` 与 `tools/ci/local_mr_review.ps1`：本地 gate 与 MR review helper，远端 CI/MR 只调用同一套脚本，不维护漂移序列。
- 提供 manifest-driven gate：用清单声明 Python、Node 和 PowerShell 检查项，输出 JSON report，便于 local/remote 结果对齐。
- 模板化 LangGraph 兼容源码入口：`tools/langgraph_durable_orchestrator/` 可作为通用源码模板，但官方 `langgraph` 包仍属于用户级共享安装。
- 模板化 repo-local durable state 规则：`.omx/state/langgraph/` 只作为生成项目运行后可产生的本地状态目录，不复制本仓库 live state。

### 3.2 范围外

- 不复制 `D:\PythonProject_langgraph` 的 `.omx/state/`、active selector、worktree claim、LangGraph backend JSON、运行日志或当前 mainline facts。
- 不修改用户级 `C:\Users\lenovo\.codex\config.toml`、全局 pip/npm/Git 配置或浏览器配置。
- 不把 legacy consumer project 的事实写入通用模板默认值。
- 不在 Phase 0 中实现业务项目代码、GUI、浏览器自动化、Vercel/GitHub 发布策略或长期 persistent team runtime。
- 不推送远端、不创建 GitLab/GitHub MR/PR。

## 4. 实施顺序

1. 读取当前源事实：以 `docs_bilingual/project_startup_summary.md` 与 `.zh-CN.md` 为冷启动入口，再补读 OpenSpec、MCP scope、launcher payload、LangGraph runtime、多会话 worktree isolation 和 orchestration activation 政策。
2. 清点目标目录：在 `D:\PythonProject_General` 中运行 `git status --short`、`openspec list --json` 和模板 checker；发现未提交人工改动时停止并报告。
3. 更新治理文档：优先写入模板可复用规则，避免复制本仓库 live state 或当前会话结论。
4. 更新脚本与 gate：让 local gate、local MR review 和远端 CI/MR 使用同一 manifest 与 checker 顺序；JSON 输出字段保持一致。
5. 更新通用 runtime scaffold：把 LangGraph 兼容/编排源码作为可选模板源码，把 `.omx/state/` 写入 ignore 和生成后本地状态说明。
6. 运行 hydration smoke test：生成临时项目，验证占位符、启动摘要、OpenSpec、background process、launcher payload 和 local gate 基础路径。
7. 形成本地提交：提交前运行 pre-commit update/archive 检查、OpenSpec guard、local gate 和 local MR review；不推送远端。

## 5. 验证命令

在 `D:\PythonProject_General` 模板根目录运行：

```powershell
python .\tools\test_template_hydration.py --root . --json
.\tools\ci\local_gate.ps1 -Root . -Json
.\tools\ci\local_mr_review.ps1 -Root . -Json
openspec validate --all
git diff --check
git status --short
```

在本仓库 `D:\PythonProject_langgraph` 中维护本计划时运行：

```powershell
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --json
.\tools\ci\local_gate.ps1 -Root . -Json
.\tools\ci\local_mr_review.ps1 -Root . -Json
```

## 6. 验收标准

- General 文档清楚说明 fuller governance template 的目标，不把 General_2 或本仓库 live runtime state 混入默认模板事实。
- Comet 被定义为 OpenSpec + Superpowers governance，而不是 native subagent、OMX、LangGraph 或 durable team。
- MCP scope、launcher payload、LangGraph runtime source、repo-local `.omx/state/`、local/remote CI/MR gate parity 均有模板化说明和验证路径。
- 新项目模板中的 `.omx/state/`、`.venv/`、`node_modules/`、`.env`、token、coverage 和临时 report 均被 ignore 或标记为生成后本地状态。
- 所有中文文档以 UTF-8 保存，不包含乱码、替换字符或从终端复制来的 mojibake。

## 7. 回滚策略

- 文档误改：使用本地 Git revert 回退本计划提交，并重新运行 `git diff --check` 与 OpenSpec guard。
- 目标模板误改：在 `D:\PythonProject_General` 中使用本地 Git 回退；如果未提交，按 `git status --short` 文件清单逐项恢复。
- hydration 失败：保留失败临时目录和 JSON report 作为诊断材料，修复模板脚本后重新运行 smoke test。
- LangGraph 模板化错误：只回退 `tools/langgraph_durable_orchestrator/` 模板源码或说明，不删除用户级官方 `langgraph` 安装。
- launcher payload 错误：回退模板内 launcher/helper 生成逻辑，不修改用户级 launcher 或全局 Codex 配置。
