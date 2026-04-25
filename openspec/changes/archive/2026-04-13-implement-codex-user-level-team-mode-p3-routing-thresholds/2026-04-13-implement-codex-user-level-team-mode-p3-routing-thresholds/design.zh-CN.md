## Context

方案文档已经定义了自动角色路由原则、状态语义与项目隔离规则，但当前生成的用户级资产还没有把这些规则结构化编码进去。

P2 后的现状是：

- 包装 `codex` 启动已经会读取 `oh_my_codex` 和 `subagent_routing`
- 但启动时注入的仍然只是一个很短的 developer-instructions 摘要
- 还没有直接可用的用户级 routing policy 检查命令
- 生成的 `team-leader.toml` 和 `team-mode-playbook.md` 也还没有完整镜像文档里批准的阈值规则

这会让 leader 侧的路由行为更难验证，也更容易和方案文档发生漂移。

## Goals / Non-Goals

**Goals:**

- 把文档里批准的角色路由阈值编码为统一的生成式运行时真源
- 让包装 `codex` 的启动器注入更完整、与模式相关的 developer instructions
- 通过一个小型用户级脚本提供操作者可见的策略检查面
- 让生成的 `team-leader.toml` 和 `team-mode-playbook.md` 与批准规则保持一致
- 保持所有新增资产都是 additive-only，并继续落在现有 backup-and-rollback 事务中
- 让策略在临时 Codex home 中即可测试，而不需要碰真实用户安装

**Non-Goals:**

- 不构建 mixed-pane compose manifest
- 不在普通 `codex` 启动时自动拉起 durable team
- 不把全局开关改成项目级开关
- 不修改原生 `codex.cmd` 或原生 `omx.cmd`
- 不修改 OpenClaw 运行时或服务行为

## Decisions

### Decision 1: 把 routing thresholds 放进生成的 shared support script

P0/P1/P2 已经把 `bin/_codex-user-level-team-mode.ps1` 作为生成的共享运行时。

P3 在这个运行时中增加：

- 结构化的 routing-threshold 定义
- routing-policy 快照函数
- 从结构化策略渲染 developer instructions
- 从当前模式导出 startup 参数

Why:

- 保持一个生成运行时真源
- 减少启动行为、检查脚本与测试之间的漂移
- 让未来脚本也能复用同一份策略模型

### Decision 2: 增加 `codex-routing-policy.ps1` 作为只读检查面

安装器将生成一个小型用户级脚本，用于以 JSON 或文本形式输出当前 routing policy。

检查输出至少包括：

- 当前模式与开关状态
- 是否开启自动路由
- `codex` 与 `codex-native` 的启动路径语义
- 仓库级运行态隔离说明
- 默认角色阈值
- 研究到实现交接规则
- 对抗式 bug 评审规则

Why:

- 给操作者和测试一个可以直接检查的策略输出面
- 避免只靠注入的 developer-instructions 字符串来验证行为

### Decision 3: 启动器从 routing-policy 模型派生 developer instructions

生成的启动器不再维护另一套手写的路由摘要。

它会改为：

1. 读取当前状态
2. 推导当前 routing policy
3. 从该策略渲染 developer instructions
4. 把这些 instructions 传给原生 `codex.cmd`

Why:

- 确保启动器遵循和检查脚本相同的策略规则
- 保持 `auto / manual / off` 三种语义的一致性

### Decision 4: 生成的 leader profile 与 playbook 必须镜像批准规则

`team-leader.toml` 和 `team-mode-playbook.md` 将显式覆盖：

- 包装 `codex` 与 `codex-native`
- native-routed / enhanced / pure-debugging 三种启动形态
- 核心专家角色的路由阈值
- 研究到实现交接
- 对抗式 bug 评审用法
- 通过每仓库 `.omx` 实现的仓库级运行态隔离

Why:

- 它们是面向操作者的解释层
- 用户已经明确要求把这些规则写清楚

## Risks / Trade-offs

- [Risk] developer-instructions 负载可能变得过长。
  Mitigation: 每个角色阈值只保留一条紧凑 bullet，并保持模式说明简洁。

- [Risk] 单独的检查脚本可能和启动器行为漂移。
  Mitigation: 两者都从同一份 shared support-script 函数生成。

- [Risk] 操作者可能把 `oh_my_codex=on` 误解为自动拉起 durable team。
  Mitigation: 在 policy 输出与 playbook 中都明确说明，增强启动只代表启用 durable-team 能力，不代表自动启动团队。

- [Risk] 新增检查面可能被误解为项目级策略文件。
  Mitigation: 保持其为用户级生成脚本，并明确说明项目隔离依赖的是仓库级运行态，不是项目级全局开关。

## Migration Plan

1. 为 P3 创建 proposal、design、spec 与 tasks 工件。
2. 在安装器 shared runtime 中加入 routing-policy 与 developer-instruction helper。
3. 生成 `codex-routing-policy.ps1`，并更新启动器、leader profile 与 playbook。
4. 扩展 PowerShell 测试，覆盖 policy 检查与 developer-instructions 注入。
5. 校验 OpenSpec 与仓库 guard。
6. 仅在仓库校验通过后重新安装到真实用户 Codex home。
