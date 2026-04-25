## Context

P2 已经让 `omx team` 能通过生成的 wrapper 直接调用，P3 也已经让专家路由阈值变成可检查的 policy，P4 又把 adversarial bug-review triad 做成了真实可调用的用户级角色。

P4 之后的剩余缺口是：

- enhanced mode 虽然知道 durable team features 存在，但还没有一层一等公民的自动 durable-team 路由面
- leader 还没有一个可复用的 helper 来判断 `launch`、`reuse`、`switch`、`shutdown`
- 一个仓库虽然已经有 `.omx` team state root，但还没有“安全 tracked-team 合同”来支撑自动复用

P5 要补的正是这个缺口，同时不改变底层启动模型：

- native Codex 仍然是永久基座
- 包装后的 `codex` 启动仍然不会在每次启动时自动拉起 durable team
- durable-team 自动化是会话内、按阈值触发的，不是 launcher 强制触发的

## Goals / Non-Goals

**Goals:**

- 在用户级 Codex home 中生成可复用的 `omx-team-auto.ps1`
- 通过共享 runtime policy 输出一套可检查的自动 durable-team 路由模型
- 让 enhanced auto mode 明确告诉 Codex CLI：什么时候应该优先 durable-team helper，而不是直接敲 raw `omx team`
- 增加仓库级 tracked-team record，让自动 `reuse` / `switch` 决策始终被约束在当前仓库边界内
- 保证未知的 unmanaged 既有 team 不会被误自动接管
- 在临时 Codex home 中用 fake `omx` 验证 launch / reuse / switch / shutdown 闭环

**Non-Goals:**

- 不在每次包装后的 `codex` 启动时自动拉起 durable team
- 不替换 native `codex.cmd`、native `omx.cmd` 或 PowerShell host 行为
- 不实现 mixed persistent pane compose layer
- 不自动接管任何不是 helper 创建并跟踪的未知 team
- 不修改 OpenClaw runtime 配置或仓库级 OpenClaw 启动行为

## Decisions

### Decision 1：自动 durable-team 路由放在 shared runtime 加一个生成的 helper 中

安装器会生成：

- `bin/omx-team-auto.ps1`

共享 runtime 还会通过 `Get-CodexUserLevelRoutingPolicy` 暴露结构化的 automatic durable-team routing model。

Why:

- 路由决策规则必须保持可检查、可测试
- 包装启动、routing policy、team-leader 指南、playbook 指南和 helper 自身应该共用一份真相来源
- 把行为放在生成的用户级资产里，才能保持跨仓库复用

### Decision 2：helper 使用已经批准的七阶段模型，而不是临时拼出来的任务措辞

helper 将基于显式项目阶段来做 durable-team 路由：

- `define-target`
- `read-context`
- `freeze-plan`
- `execute-parallel`
- `integrate-converge`
- `stabilize`
- `verify-accept`

默认 durable-team 规则：

- `define-target`、`read-context`、`freeze-plan`、`verify-accept` 不启 durable team
- `execute-parallel` 与 `integrate-converge`
  - 当 parallel slices 至少为 `2` 时，启动或复用 `2:team-executor`
  - 当 parallel slices 至少为 `3` 时，提升到 `3:team-executor`
- `stabilize`
  - 当 blocking issues 至少为 `1` 时，切换到或复用 `2:debugger`

Why:

- 这和已经批准的七阶段 operating model 一致
- 可以把 durable team 明确绑定到执行和稳定化阶段，而不是模糊启发式

### Decision 3：自动 `reuse` / `switch` 只管理 tracked 的 repo-local team

helper 会在仓库内维护一个 tracked-team record：

- `.omx/state/team/codex-auto-managed-team.json`

只有 tracked record 存在，并且记录中的 team 仍存在于当前仓库 `.omx` state root 中时，自动行为才可以管理该 team。

如果仓库里已经有 team 目录，但没有 tracked record，helper 会返回一个安全的非变更决策，例如 `manual-inspection-required`，而不是自动接管它。

Why:

- 这能保持你要求的“不同项目运行态不串台”
- 可以防止自动 shutdown / switch 误碰未知 unmanaged team
- 也让自动路由具备可回滚、可审计的边界

### Decision 4：Apply 模式明确区分 launch、reuse、switch、shutdown

`omx-team-auto.ps1` 默认输出 plan，只有显式带 `-Apply` 才执行变更。

Apply 行为：

- `launch`
  - 调用解析后的原生 `omx` 路径执行 `team` 启动参数
  - 检测新创建的 team 目录
  - 写入 tracked-team record
- `reuse`
  - 对 tracked team 调用 `omx team api create-task`
  - 保留 tracked-team record
- `switch`
  - 先 shutdown tracked team
  - 再启动新的目标 team
  - 更新 tracked-team record
- `shutdown`
  - shutdown tracked team
  - 删除 tracked-team record

Why:

- P5 的核心就是让 Codex CLI 能决定 durable team 是该启动、复用、切换还是停止
- Apply 必须显式，这样 planning surface 才仍然安全、可检查

### Decision 5：启动语义保持保守，但 developer instructions 要更强

包装启动仍然保留以下规则：

- startup itself does not auto-launch a durable team

但在 `oh_my_codex=on` 且 `subagent_routing=auto` 时，developer instructions、`team-leader.toml` 和生成的 playbook 现在要明确写出：

- enhanced auto mode 下 automatic durable-team routing 可用
- durable-team 阈值满足时，应优先使用 `omx-team-auto.ps1`，而不是 raw `omx team`
- raw `omx team` 只用于有意的人工覆盖

Why:

- 这样可以在不隐藏变更动作的前提下，给 Codex CLI 更强的执行合同
- 也符合你“由 Codex CLI 决定是否真的调用 durable team”的目标

## Risks / Trade-offs

- [Risk] 自动 shutdown 可能关错 team。
  Mitigation：只管理当前仓库中有 tracked-team record 的 team。

- [Risk] 自动 reuse 可能把新任务派发给过时 team。
  Mitigation：要求 tracked team 目录仍存在，并在 tracked record 中保留 phase / role / worker-count 元数据。

- [Risk] 操作员可能误以为现在每次启动都会自动拉起 durable team。
  Mitigation：保持 `automatic_durable_team_launch=false`，并在 policy、leader profile、playbook 中写清区别。

- [Risk] helper 可能演化成 OpenClaw 专属流程物。
  Mitigation：保持生成资产用户级、additive-only，并只依赖 native Codex 和 native `omx` 语义。

## Migration Plan

1. 创建 P5 的 proposal、design、tasks 和 capability specs。
2. 扩展 installer 与 shared support runtime，加入 automatic durable-team routing 元数据和 helper 函数。
3. 生成 `omx-team-auto.ps1`，并更新 policy、leader、playbook 指南。
4. 扩展 PowerShell 测试，在 fake `omx` 上验证 plan、launch、reuse、switch、shutdown。
5. 校验 OpenSpec 与 repo guard。
6. 只有仓库验证通过后，才重新安装到真实用户 Codex home。
