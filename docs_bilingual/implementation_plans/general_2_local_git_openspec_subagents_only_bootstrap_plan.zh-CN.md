---
doc_id: general_2_local_git_openspec_subagents_only_bootstrap_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.zh-CN.md
status: active-local-plan
updated_at: 2026-05-27
target_template: D:\PythonProject_General_2
comet_change: refactor-general-template-plans-comet
capability_tier: local-git-openspec-superpowers-native-subagents-only
---

# D:\PythonProject_General_2 本地 Git + OpenSpec + Superpowers + native Codex subagents 模板实施计划

## 1. 目标

`D:\PythonProject_General_2` 是轻量本地模板，面向没有远程仓库和 durable orchestration 需求的新项目。它只提供本地 Git、OpenSpec、Superpowers 治理方法和 native Codex subagents 配置，不启用 oh-my-codex、native_omx、LangGraph durable backend、远程 CI/MR 或 `.omx/state/` 运行时状态。

本计划的成功标准是：未来冷启动会话读取本文件后，可以在目标目录中生成或修复一个本地-only 模板，并且不会误把 `D:\PythonProject_langgraph` 的 live session facts、用户级配置、远端发布流程或 LangGraph runtime 当成 General_2 的当前能力。

## 2. 能力边界

### 2.1 当前启用能力

- 本地 Git：`git init -b main` 用来创建本机版本历史，不默认配置 `origin`、`gitlab` 或 `github` remote。
- OpenSpec：`openspec/` 用来保存本地 proposal、design、spec 和 tasks 文件，作为 WHAT 与变更生命周期治理。
- Superpowers：Superpowers skills 用作 HOW 层的方法论，例如 brainstorming、writing-plans、executing-plans 和 verification-before-completion。
- Comet：`/comet` 只表示 OpenSpec + Superpowers 的治理工作流，负责 Open、Design、Build、Verify、Archive 阶段证据，不是 native subagent、oh-my-codex、native_omx、LangGraph 或 durable-team backend。
- native Codex subagents：`.codex/agents/` 存放项目内可复用的原生 agent TOML；每个 TOML 必须有 `name`、`description`、`developer_instructions`。

### 2.2 明确不启用能力

- 不配置 GitLab/GitHub remote，也不创建 `.gitlab-ci.yml` 或 `.github/workflows/`。
- 不安装或调用 oh-my-codex、native_omx、LangGraph durable backend、LangGraph CLI wrapper 或 `.omx/state/`。
- 不复制本机 `C:\Users\lenovo\.codex\config.toml`、token、`.env`、credential cache、`.venv/`、`node_modules/` 或 `.git/`。
- 不把 `D:\PythonProject_langgraph` 的 current mainline、active worktree claim、Comet state、LangGraph state 或提示词哨兵字面内容写成模板默认事实。

## 3. 目标目录结构

生成后的模板根目录建议如下：

```text
D:\PythonProject_General_2
├── AGENTS.md
├── README.md
├── TEMPLATE_MANIFEST.md
├── .gitignore
├── .codex\agents\
├── template_assets\codex-agents\
├── docs_bilingual\project_startup_summary.md
├── docs_bilingual\project_startup_summary.zh-CN.md
├── docs_bilingual\governance\
├── openspec\changes\
├── openspec\specs\
└── tools\
```

关键目录说明：

- `.codex\agents\` 是 Codex 运行时读取的项目级 native subagent TOML 目录。
- `template_assets\codex-agents\` 是模板分发副本，用来在生成新项目或安装用户级 agents 前做文件对比和恢复。
- `docs_bilingual\project_startup_summary.md` 与 `.zh-CN.md` 是冷启动摘要对；如果未来加入上下文保留哨兵，字面哨兵只能放在这对摘要中。
- `openspec\changes\` 与 `openspec\specs\` 是本地 OpenSpec 变更和稳定规格目录，不需要远端仓库。
- `tools\` 存放 bootstrap、checker 和本地 gate 脚本；脚本必须使用 `$env:USERPROFILE` 或参数，不得硬编码 `C:\Users\lenovo`。

## 4. 实施顺序

1. 备份目标目录：如果 `D:\PythonProject_General_2` 已存在，先检查 `git status --short`；发现本地改动时停止并报告，不覆盖。
2. 写入基础文档：更新 `AGENTS.md`、`README.md`、`TEMPLATE_MANIFEST.md`、启动摘要和 governance 文档，明确 local-only 能力边界。
3. 初始化 OpenSpec：创建 `openspec/changes/`、`openspec/specs/` 和本地示例 change；示例不得复制本仓库既有 active changes 或 archive 历史。
4. 同步 native agents：保持 `.codex/agents/` 与 `template_assets/codex-agents/` 文件名和 TOML schema 一致；安装到用户级目录前必须备份同名文件。
5. 写入本地脚本：提供 `bootstrap-new-pc.ps1`、`bootstrap-local-project.ps1`、`install-subagents-user-level.ps1`、`check_template_health.py`、`check_subagent_only_policy.py`、`check_custom_agent_toml_schema.py`、`check_bilingual_pairs.py` 和 `check_local_git_only_policy.py`。
6. 初始化本地 Git：仅在用户确认的目标目录中运行 `git init -b main`、`git add .` 和本地初始化 commit；不添加 remote。

## 5. 验证命令

在 `D:\PythonProject_General_2` 模板根目录运行：

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

命令用途：模板健康检查确认关键文件存在；subagent-only 检查确认未启用 OMX/LangGraph；TOML schema 检查确认 agent 文件可被 Codex 读取；双语配对检查确认 Markdown 对齐；本地 Git-only 检查确认没有 remote-first 配置；OpenSpec 与 Git 检查确认治理和文本格式健康。

## 6. 验收标准

- General_2 明确保持 local Git + OpenSpec + Superpowers + native Codex subagents only。
- `.codex/agents/` 与 `template_assets/codex-agents/` 成对一致，且所有 agent TOML 有必需字段。
- 目标目录没有 `.omx/state/`、`.omx/session-claims/`、LangGraph runtime、oh-my-codex launcher、GitLab/GitHub remote 或远程 CI 配置。
- 所有脚本可重复运行；遇到已存在目标目录、本地 Git 改动或用户级同名 agent 时先报告并备份，不静默覆盖。
- 中文文档以 UTF-8 保存，不包含乱码、替换字符或从终端复制来的 mojibake。

## 7. 回滚策略

- 目标目录错误时先重命名为 `D:\PythonProject_General_2.backup.<timestamp>`，确认没有需要保留的本地提交后再人工删除。
- 用户级 agents 安装错误时，从 `%USERPROFILE%\.codex\agents.backup.<timestamp>\` 恢复同名 TOML。
- pip 用户级镜像不再需要时，运行 `python -m pip config --user unset global.index-url` 和 `python -m pip config --user unset global.timeout`。
- 本地 Git 初始化错误时，只能在确认没有需要保留的提交后人工删除 `.git/`；脚本不得自动删除 Git 历史。
- OpenSpec 初始化错误时，先查看 `git status --short`，按文件清单回退；脚本不得自动清空 `openspec/`。
