---
doc_id: codex_langgraph_repository_split_migration_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/codex_langgraph_repository_split_migration_plan.md
---

# Codex / LangGraph 仓库拆分迁移方案

## 目标

把 `D:\PythonProject_OpenClaw` 中的 Codex 用户级编排主线迁移到新的主仓库 `D:\PythonProject_langgraph`，并且在迁移过程中不丢失执行上下文、OpenSpec 权威层和当前主线。

## 唯一主权规则

从迁移开始起：

- `D:\PythonProject_langgraph` 成为 Codex `subagent / omx / langgraph` 用户级编排工作的唯一 source of truth。
- `D:\PythonProject_OpenClaw` 不再继续承接这条主线的新实现。
- `D:\PythonProject_OpenClaw` 只允许暂时保留桥接或跳转说明，直到清理完成。

## 迁移边界

迁入新仓库的内容：

- 用户级 Codex / oh-my-codex 编排代码
- LangGraph durable orchestrator 代码
- 用户级安装器与 wrapper 生成代码
- 这条用户级 Codex 编排主线的直接测试
- 用户级双语主方案文档
- 这条主线对应的用户级 OpenSpec specs 与 change 历史

继续保留在 `D:\PythonProject_OpenClaw` 的内容：

- OpenClaw runtime 与 service 代码
- 仍然属于 OpenClaw 项目本身的启动和运行治理
- 面向 OpenClaw 项目的 LangGraph 改造方案
- WeCom、local-control、retention、search-chain 以及其他不属于用户级 Codex 编排产品面的内容

## 计划迁移清单

主要代码：

- `tools/install-codex-user-level-team-mode.ps1`
- `tools/langgraph_durable_orchestrator/`
- `tools/openclaw-omx-windows-bootstrap-fix.mjs`

主要测试：

- `test/install-codex-user-level-team-mode.test.ps1`
- `test/run-install-codex-user-level-team-mode-test.cmd`
- `test/langgraph_durable_orchestrator_*.test.py`
- `test/openclaw-omx-windows-bootstrap-fix.test.mjs`

主要双语方案：

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`

主要 OpenSpec specs：

- `openspec/specs/codex-user-level-*`
- `openspec/specs/langgraph-durable-orchestration-backend/`

主要 OpenSpec changes：

- active：
  - `openspec/changes/implement-langgraph-reusable-subgraph-library/`
- 已归档的用户级编排历史：
  - `openspec/changes/archive/*codex-user-level*`
  - `openspec/changes/archive/*langgraph*`
  - `openspec/changes/archive/*omx*`
  - `openspec/changes/archive/*team-mode*`

## 防跑偏控制

1. 先冻结迁移清单。
   - 先固定迁移边界和目标映射，再复制文件。
2. 新仓库先建立 startup summary。
   - 新仓库必须先有自己的启动入口和当前主线说明。
3. OpenSpec 历史必须跟代码一起迁。
   - 不能只迁实现文件，不迁工件。
4. 同一条主线只能有一个活跃位置。
   - 用户级编排新实现只允许发生在 `D:\PythonProject_langgraph`。
5. 旧仓库先变成 bridge-only。
   - 在 OpenClaw 里先写明“已迁出”，再删旧内容。
6. 新仓库验证通过后才能清理旧仓库。
   - 旧仓库里的相关内容只能在新仓库校验通过后再删除。

## 执行顺序

1. 创建 `D:\PythonProject_langgraph`
2. 在新目录初始化 git 和 OpenSpec
3. 在新仓库建立 startup entry、`AGENTS.md` 和迁移标记文件
4. 从 `D:\PythonProject_OpenClaw` 复制迁移清单内容
5. 把新仓库重建为主编排工作区
6. 在新仓库执行验证
7. 在 `D:\PythonProject_OpenClaw` 中加入 redirect 说明
8. 从 `D:\PythonProject_OpenClaw` 中删除已迁出的编排内容

## 验证

新仓库至少要通过：

- `openspec validate --all`
- `python .\tools\run_openspec_guard.py --root .`
- Python LangGraph durable orchestrator 测试
- PowerShell 安装器集成测试

## 迁移后要继续的当前主线

迁移后必须继续推进的当前主线是：

- `implement-langgraph-reusable-subgraph-library`

这条主线应被视为迁移完成后的第一个正式实现目标。
