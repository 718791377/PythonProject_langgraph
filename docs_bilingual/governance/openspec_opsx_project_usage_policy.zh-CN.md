---
doc_id: openspec_opsx_project_usage_policy
lang: zh-CN
canonical: docs_bilingual/governance/openspec_opsx_project_usage_policy.md
translation_of: docs_bilingual/governance/openspec_opsx_project_usage_policy.md
doc_class: governance
status: active
---

# OpenSpec OPSX 项目级使用约定

## 1. 目的

本文用于定义：在当前仓库内，如何在 Codex 驱动的工作中对齐 OpenSpec 官方当前推荐的 OPSX 工作流。

目标不是用仓库自定义流程替代 OpenSpec，而是在明确仓库边界的前提下，让仓库内工作方式与 OpenSpec 官方工作流表面保持一致。

对本仓库而言，OPSX 还应被理解为一套项目级承接工作流，用来衔接：

- 可被多个项目复用的用户级共享 runtime / control surface
- 必须继续留在本仓库内、作为权威面的 repo-local source、repo-local durable truth 与仓库级结构性变更

## 1A. 新会话统一入口规则

新会话默认不应从本文开始。

应先读取以下两份项目级启动摘要：

- [project_startup_summary.zh-CN.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.zh-CN.md)
- [project_startup_summary.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.md)

之后再由模型根据当前任务判断是否需要进入这份 OPSX 项目级使用约定。

## 2. 权威边界

权威顺序如下：

1. OpenSpec 官方上游行为与工作流模型
2. 本机已安装的 OpenSpec CLI 能力
3. 仓库级 OPSX 入口规则与路由约定

这意味着：

- OpenSpec CLI 仍是权威执行层
- 本仓库中的 `/opsx:*` 语义属于仓库级工作流约定
- 仓库文档不得把本地封装表述成 Codex 原生命令
- 仓库级 OPSX 流程可以消费用户级共享 runtime 表面，但不得把用户级 state 或 shared runtime 目录误当成本仓库的 canonical durable truth

## 3. 当前仓库状态

OpenSpec 已经在仓库的工件层生效：

- `openspec/config.yaml` - 本仓库的 OpenSpec 配置文件。
- `openspec/changes/...` - active 与 proposed OpenSpec change 工件目录树。
- `openspec/specs/...` - 稳定 OpenSpec capability spec 目录树。

仓库也已经物化了官方 Codex OpenSpec 指令面和所需的强制面：

- `.codex/skills/` 下的官方 Codex OpenSpec skills
- `tools/bootstrap-official-openspec.ps1` - 物化或刷新官方 Codex OpenSpec 指令面的 PowerShell 脚本。
- `tools/verify_official_openspec.py` - 检查官方 OpenSpec bootstrap 与生成工件的验证脚本。
- `tools/run_openspec_guard.py` - 聚合运行仓库 OpenSpec 检查的 guard 脚本。
- `.githooks/pre-commit` - 提交前运行仓库检查的本地 Git hook。
- `.github/workflows/openspec-guard.yml` - 运行 OpenSpec guard 的 GitHub Actions workflow。
- `.gitlab-ci.yml` - 配置仓库 guard job 的 GitLab CI pipeline 文件。

因此：

- OpenSpec 已经同时在工件层和强制层生效
- 当前仓库在仓库级工作流层面已经对齐当前官方 OPSX 工作流表面
- 仓库里的 `/opsx:*` 仍然是仓库级路由约定，而不是对 Codex 原生命令的声明

## 4. 仓库应对齐的官方 OPSX 命令集

根据当前已安装 OpenSpec 包及其工作流模板，仓库应对齐以下 OPSX 命令集：

- `/opsx:onboard` - 用于读取启动上下文与当前 OpenSpec 状态的项目级工作流路由。
- `/opsx:new` - 用于启动新的 OpenSpec-backed change 的项目级工作流路由。
- `/opsx:continue` - 用于恢复 active OpenSpec change 的项目级工作流路由。
- `/opsx:ff` - 用于快速补齐缺失 OpenSpec 工件的项目级工作流路由。
- `/opsx:propose` - 用于创建 proposal、design 与 task 工件的项目级工作流路由。
- `/opsx:explore` - 用于变更前探索和范围澄清的项目级工作流路由。
- `/opsx:apply` - 用于实现 active change 中任务的项目级工作流路由。
- `/opsx:verify` - 用于检查结构就绪度与 validation 的项目级工作流路由。
- `/opsx:sync` - 用于把已批准 delta 同步进稳定 specs 的项目级工作流路由。
- `/opsx:archive` - 用于归档 completed change 的项目级工作流路由。

仓库应通过项目级工作流指导来暴露这些命令语义，并由官方 CLI、仓库 bootstrap 或 refresh、校验脚本、hooks 和 CI guard 共同支撑。如果后续官方 CLI 命令面发生变化，应重新执行仓库 refresh 路径，而不是继续保留过时表述。

## 4A. 任务认领预检门槛

在 `/opsx:apply`、`/opsx:verify`、`/opsx:archive`、guard 失败修复、治理文件修复，或任何等价仓库工作流开始写入之前，当前会话必须先执行 `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md` 中定义的任务认领预检；该文件是多会话 Git worktree 隔离、脏文件处理和任务认领的治理政策。

即使疑似先前 owner 没有 dirty diff，这个门槛也仍然生效。只要存在匹配 branch、worktree、MR、OpenSpec change、claim file，或被 guard 扫描的 ignored target path，该任务就至少属于 claimed-not-started 状态，直到 leader 串行化 handoff。

如果预检发现 ownership signal：

- 当已有 worktree 是最安全的 single-writer path 时，继续使用该 worktree。
- 创建新写入范围前，先让 leader 释放或分类 stale claim。
- 除非 leader 明确串行化 handoff，否则不要从 `main` 或第二个 feature worktree 修同一个 guard failure。
- 对 `docs_bilingual/` 或 `openspec/` 下的 ignored files，在其仓库归属确定前，一律视为会影响 guard 的 task objects。

## 4B. `/plan` 之后的文档优先路由

当已确认的 `/plan` 退出并进入执行，且任务不是纯文档任务时，仓库工作流先进入本地治理包。

该治理包先更新 `docs_bilingual/`。目标应是最适合的 doc_class 与目录，而不是自动进入 `implementation_plans/`。有合适既有文件时优先更新既有文件。

完成该更新后，会话再判断是否还必须更新 OPSX/OpenSpec 或 `docs/`：

- 当任务改变 reusable rules、stable specs、structural governance、executable guards 或 repository validation meaning 时，使用 OPSX/OpenSpec。
- 只有需要 Superpowers runtime artifacts 或改变 `docs/` 目录契约时，才使用 `docs/`。
- 不得把 OpenSpec 或 `docs/` artifacts 当作更新 `docs_bilingual/` 的副作用来创建。

本地治理包 ready 后，按完整本地提交流程执行到本地 `main` 合入，并停在远端发布门。这个本地流程不授权远端发布。

## 5. 命令映射模型

### 5.1 `/opsx:onboard`

适用场景：

- 首次进入仓库
- 长时间中断后的重新进入
- 进入不熟悉的主线

期望行为：

- 先读取项目级启动摘要
- 如存在会话级摘要，再读取对应会话摘要
- 检查当前 OpenSpec 状态

最低 CLI 基线：

- `openspec list --json` - 官方 OpenSpec CLI 中以机器可读形式列出 OpenSpec 状态的命令。
- `openspec status` - 官方 OpenSpec CLI 中显示当前仓库 OpenSpec 状态的命令。
- 仓库启动摘要文档

### 5.2 `/opsx:new`

适用场景：

- 启动一条新的结构性 change
- 启动应产出 OpenSpec 工件的仓库级变更

最低 CLI 基线：

- `openspec new change "<name>"` - 官方 OpenSpec CLI 中创建具名 change 的命令。
- `openspec status --change "<name>" --json` - 官方 OpenSpec CLI 中以 JSON 读取具名 change 状态的命令。

### 5.3 `/opsx:continue`

适用场景：

- 继续一条已存在的 change
- 恢复未完成的 proposal、design、spec 或 tasks 工作

最低 CLI 基线：

- `openspec list --json` - 官方 OpenSpec CLI 中以机器可读形式列出 OpenSpec 状态的命令。
- `openspec status --change "<name>"` - 官方 OpenSpec CLI 中读取具名 change 状态的命令。

### 5.4 `/opsx:ff`

适用场景：

- change 已存在，但 apply 前所需工件尚未补齐
- 需要快速补齐工件以便进入实施

仓库规则：

- 不得把 `/opsx:ff` 当成跳过设计思考的捷径
- 只有在意图已经明确、瓶颈只是工件未补齐时才使用

### 5.5 `/opsx:propose`

适用场景：

- 一步生成 proposal、design、tasks 及其他 apply 前必需工件

最低 CLI 基线：

- `openspec new change "<name>"` - 官方 OpenSpec CLI 中创建具名 change 的命令。
- `openspec status --change "<name>" --json` - 官方 OpenSpec CLI 中以 JSON 读取具名 change 状态的命令。
- `openspec instructions <artifact> --change "<name>" --json` - 官方 OpenSpec CLI 中为具名 artifact 生成 instructions 的命令。

### 5.6 `/opsx:explore`

适用场景：

- 在变更形状尚不清楚前先探索问题
- 澄清需求、范围和主线归属

仓库规则：

- explore 模式允许调查代码和工件
- explore 模式不得静默跳到实现

### 5.7 `/opsx:apply`

适用场景：

- 实现一条活跃 change 里的任务

最低 CLI 基线：

- `openspec status --change "<name>" --json` - 官方 OpenSpec CLI 中以 JSON 读取具名 change 状态的命令。
- `openspec instructions apply --change "<name>" --json` - 官方 OpenSpec CLI 中为具名 change 生成 apply instructions 的命令。

### 5.8 `/opsx:verify`

适用场景：

- 判断当前 change 是否已结构完备、可继续推进或可完成

最低 CLI 基线：

- `openspec status` - 官方 OpenSpec CLI 中显示当前仓库 OpenSpec 状态的命令。
- `openspec validate --all` - 官方 OpenSpec CLI 中验证全部 specs 与 changes 的命令。
- 与该 change 相关的仓库测试

### 5.9 `/opsx:sync`

适用场景：

- 将稳定的 delta spec 结论同步回主 spec

仓库规则：

- 不得把所有实现笔记都当成 spec sync 素材
- 只有可复用、跨场景、长期有效的规则才应提升进稳定 spec

### 5.10 `/opsx:archive`

适用场景：

- 在工件、实现、验证都稳定后归档 change
- 为小型 completed change 在打开 GitLab MR 前构建默认 single-MR publication package（单 MR 发布包）

最低 CLI 基线：

- `openspec status --change "<name>"` - 官方 OpenSpec CLI 中读取具名 change 状态的命令。
- `openspec archive <name>` - 官方 OpenSpec CLI 中把已完成 change 移入 archive history，并把 delta specs 提升为 stable specs 的命令；或采用能保留同等仓库本地结果的等价归档流程。

仓库归档门槛：

- 不得归档自身 artifact 仍有明确 archive blocker 的 change。
- 不得归档仍缺少 `proposal.md`、`design.md` 或 `tasks.md` 等核心 artifacts 的 change；这些文件分别是 OpenSpec change 的提案、设计说明和任务清单。
- 不得把 metadata-only 或 smoke-test 占位目录当成正常 completed change 归档；metadata-only 或 smoke-test 占位目录只是元数据或冒烟测试占位，不代表真实完成。
- 如果后续仍需要新工作但原归档快照本身有效，应优先新建 forward follow-up change，而不是静默把无效归档状态继续正常化；forward follow-up change 是在原归档之后继续推进的新 OpenSpec change。

默认发布前归档包：

- 对已经本地完成、准备发布的 OpenSpec change，除非用户明确要求 implementation-only MR，或存在合理 two-MR exception，否则应在同一个 feature branch 内先 archive，再打开 GitLab MR。
- 该 MR 应同时包含实现或文档更新、归档后的 change 目录，以及 archive 产生的 stable spec 更新。
- 这个默认流程适用于本地验证已经证明完成的小型 governance（治理）、documentation（文档）、checker（检查脚本）和 test（测试）类变更。
- 对大型或高风险实现、需要先远端评审确认的工作，或会产生大量 stable-spec 冲突的归档提升，使用 two-MR flow（双 MR 流程）。

仓库归档隔离流程：

- 如果 change 会修改 source code、scripts、tests、CI、checkers、runtime behavior、stable specs、startup instructions、作为仓库指令面的 `AGENTS.md`，或结构性治理规则，必须使用本流程。纯说明性文本改动如果不改变可执行行为，可以使用轻量归档流程；不确定时按专用 archive worktree 流程处理。
- 在 single-MR path 中，先完成实现验证，再在同一个隔离 feature worktree 内执行归档，然后再发布。如果单独 archive worktree 更安全，必须先把该 archive 结果合回同一个发布分支，再打开 MR。
- archive 前验证一次，archive 提升后再次验证。worktree-local verification 必须包含该 change 要求的仓库 guard 命令，确保归档生成的 stable specs 在集成前已经被检查。
- 只有 post-archive validation（归档后验证）通过后，才能提交发布分支。
- 通过正常 local-main-first 流程发布。核心规则是：先实现验证，再 archive 与 stable-spec 提升，然后归档后复验；除非存在已说明的 two-step exception，否则只形成一个本地集成包。

## 6. 本仓库何时必须走 OPSX

以下情况应视为必须走 OPSX：

- 会产生长期仓库影响的新功能
- 架构或工作流调整
- 可复用规则、spec 或长期治理规则变更
- 需要明确 rollout 顺序的多文件实现
- 明确会产出或更新 OpenSpec change 工件的工作

这一要求尤其适用于以下边界变化：

- 用户级共享层与本仓库项目级承接层之间的边界
- repo-local source contract
- repo-local durable-state semantics
- 仓库级 OpenSpec 工件
- 仓库级验证或验收语义

出现这类情况时，应把 `/opsx:new`、`/opsx:propose` 或 `/opsx:continue` 视为结构性入口，而不是只做治理文档层面的补写。

以下情况可不强制走 OPSX：

- 一次性 runtime 调查
- 临时日志查看
- 不涉及结构调整的窄范围问题确认
- 不改变项目规则的轻量文档勘误

如果任务一开始只是 runtime 调查，但后续演化成可复用或结构性工作，就应显式重路由进 OPSX 流。

## 7. OpenSpec 与 docs_bilingual 的分工

### 7.1 OpenSpec

OpenSpec 应承载：

- 稳定的 change 工件
- proposal / design / tasks 结构
- 可复用 spec
- 面向验证的变更状态

### 7.2 `docs_bilingual/`

`docs_bilingual/` 应承载：

- 项目级启动摘要
- 会话级摘要
- 治理政策
- 方法论文档
- rollout / migration 计划
- 运维说明

应按内容选择 `docs_bilingual/` 位置。治理变更进入 governance，操作员说明进入 guides 或 operations，交接事实进入 memory，生命周期综合进入 product_lifecycle，实施排序进入 implementation plans。不要把每个实施前决策都强塞进 implementation plans。

### 7.3 同步规则

当两层都受影响时：

- OpenSpec change 工件必须保持结构正确
- `docs_bilingual/` 文档必须保持路由正确、职责正确
- 任何一层都不得静默替代另一层

### 7.4 名称解释规则

当 OPSX 工件或面向 OPSX 的治理文档列出脚本、路径、命令、变量、profile、skill 名称或其他类似代码的名字时，必须给该条目补一句简短用途解释。

目标是提升冷启动可读性：一个没有聊天上下文的新会话，应能在不先搜索整个仓库的情况下，知道这个名字是什么、用来做什么。

仓库规则：

- 不要留下只有代码名的裸列表，除非名称本身已经足够自解释
- 在名称后补一个短语，说明它的职责或使用场景
- 示例要简短；解释的目的只是帮助路由，不应扩写成完整手册

示例格式：

- `tools/example-check.py`：在 CI 接受变更前验证一个具体仓库不变量的脚本。

## 8. 仓库级默认入口顺序

在本仓库内，Codex 的默认 OPSX 入口顺序应为：

1. `/opsx:onboard`：冷启动或长时间断档后重新进入
2. `/opsx:explore`：问题形状尚不清楚时
3. `/opsx:new` 或 `/opsx:propose`：需要建立新 change 时
4. `/opsx:continue`：继续已有 change 时
5. `/opsx:apply`：进入实现
6. `/opsx:verify`：完成前验证
7. `/opsx:sync`：需要提升稳定 spec 结论时
8. `/opsx:archive`：change 真正完成后归档

`/opsx:ff` 是这个序列里的 change 准备捷径，不是替代整个序列。

## 9. 验证关口

仓库级 OpenSpec 工作在以下条件同时满足前，不应视为完成：

- 相关 change 工件一致
- `openspec status` 显示状态符合预期
- 结构性 OpenSpec 工作已执行 `openspec validate --all`
- 实现与相关仓库文档已同步

## 10. 当前缺口与下一步对齐

当前仓库状态是：

- 在仓库级工作流层面已经对齐当前官方 OPSX 工作流表面
- 已由仓库本地 bootstrap、校验、hook 和 CI 强制面共同支撑

下一步对齐动作是：

- 持续让仓库级指导层对齐后续官方 OPSX 命令面变化
- 让项目级 Codex 入口规则明确化
- 不要把仓库里的 `/opsx:*` 路由语义误写成 Codex 原生命令
- 只有在获得明确授权后，才修改本地或全局 OpenSpec profile

## 11. 非目标

本文不做以下事情：

- 重新定义 OpenSpec 上游行为
- 声称本仓库里的全部 `/opsx:*` 都是 Codex CLI 原生命令
- 强迫所有仓库文档都进入 `openspec/specs`
- 授权静默修改全局 OpenSpec 配置
## 归档门槛补充

`/opsx:archive` 只适用于真正完成的 change。

以下情况不得直接 archive：

- change 自身 artifact 仍有明确 archive blocker
- 缺少 `proposal.md`、`design.md`、`tasks.md` 等核心 artifacts
- 目录只是 metadata-only 或 smoke-test 占位

如果原归档快照当时有效、但后续仍有新工作，应优先新建 forward follow-up change，而不是把无效归档状态继续正常化。
