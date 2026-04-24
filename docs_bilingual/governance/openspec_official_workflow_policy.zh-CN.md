---
doc_id: openspec_official_workflow_policy
lang: zh-CN
doc_class: governance
status: active
---

# OpenSpec 官方工作流策略

## 1. 目的

本文定义当前仓库如何与当前已安装的官方 OpenSpec CLI 保持一致。

对本仓库而言，官方 OpenSpec 工作流治理作用在项目级承接层：

- 用户级共享 runtime 与控制面可以被同一台机器上的多个项目复用
- repo-local source、repo-local durable truth 与仓库级结构变更继续是本仓库内部的权威面
- 任何影响这种承接边界的结构性改动，都应在本仓库内进入 OpenSpec，而不是只藏在用户级资产里

## 2. 权威顺序

权威顺序如下：

1. OpenSpec 官方上游行为与官方文档
2. 当前机器上安装的官方 OpenSpec CLI，以及它为本仓库生成的托管指令文件
3. 仓库级工作流策略与治理文件

## 3. 启动入口

- 新会话统一从 `docs_bilingual/project_startup_summary.zh-CN.md` 和 `docs_bilingual/project_startup_summary.md` 开始
- `AGENTS.md`、OpenSpec 治理文件、稳定 specs 和 active changes 都是从 startup summary 继续展开的下游读取面
- 不允许用仓库私有捷径静默替代这条 startup-summary-first 顺序

## 4. 必要初始化或刷新

- 当本机还没有 `openspec` 命令时，先安装官方 CLI：`npm install -g @fission-ai/openspec@latest`
- 在真 Git 仓库中克隆后、切换 AI 工具后、升级 OpenSpec CLI 后，或需要刷新仓库本地官方指令面时，运行 `powershell -ExecutionPolicy Bypass -File .\tools\bootstrap-official-openspec.ps1`
- 对 Codex 来说，bootstrap 脚本必须实际物化当前官方 Codex 集成，而不是依赖手写 slash-command 描述去“假装已接入”

## 5. 默认官方生命周期

- 使用当前已安装 CLI 为当前 AI 工具生成的 OpenSpec 命令面
- 在实施前先创建或完善 change proposal
- 用 `openspec list --json`、`openspec status`、`openspec show`、`openspec validate` 做检查与评审
- 只有在必需 artifacts 已经就绪后才进入实施
- 当实现、specs 和验证都稳定后，才用 `openspec archive <change> --yes` 归档
- 不要发明会覆盖官方 OpenSpec 语义的仓库私有别名命令
- 只要结构性改动会影响 repo-local source、repo-local durable-state contract，或用户级共享表面进入本仓库的项目级承接边界，就应把这类改动视为本仓库的 OpenSpec 工作

## 6. Experimental 工作流规则

- 只有在以下条件同时满足时，才可以启用 OpenSpec 的 experimental 工作流：
  - 官方上游文档仍然明确描述该工作流
  - 当前本机安装的 CLI 明确支持，或会为当前 AI 工具生成该工作流
  - 当前仓库明确选择启用该工作流
- 只要其中任一条件不成立，就必须退回默认官方生命周期

## 7. 强制校验

- `python .\tools\run_openspec_guard.py --root .` 是统一的本地强制入口
- 在把本仓库视为“已完成官方 OpenSpec 工作流接入”之前，必须通过 `python .\tools\verify_official_openspec.py --root .`
- 在把结构性 OpenSpec 工作视为完成之前，必须通过 `openspec validate --all`
- 执行 `git init` 或克隆已有仓库后，应运行 `powershell -ExecutionPolicy Bypass -File .\tools\install-git-hooks.ps1` 安装 `.githooks/pre-commit`
- 仓库内必须保留至少一个受支持的 CI 守卫面，例如 `.github/workflows/openspec-guard.yml` 或 `.gitlab-ci.yml`
- 如果托管平台支持 required status checks，应把 OpenSpec guard job 设为 required，避免合并仍然只依赖维护者自律

仓库检查脚本与聚合 guard 报告的 JSON 输出契约定义在：

- `docs_bilingual/governance/openspec_check_and_guard_json_output_policy.md`

## 7A. 治理文件的双语与编码规则

对于 `docs_bilingual/` 与 `openspec/` 下的治理类工件：

- 只要某个权威面已进入双语维护，就必须同时维护英文 `.md` 主版与中文 `.zh-CN.md` 对照版
- 英文 `.md` 主版是规范主版，正文应保持 ASCII
- 中文对照版必须使用 UTF-8 保存
- 读取中文对照版时，必须先走显式 UTF-8 路径；只有显式 UTF-8 读取仍失败后，才允许考虑其他 fallback 诊断或修复路径

## 8. 可跳过的例外

- 一次性运行时排查
- 临时日志检查
- 不涉及结构变化的窄范围 bug 确认
- 不改变策略或工作流的轻微文档修订
