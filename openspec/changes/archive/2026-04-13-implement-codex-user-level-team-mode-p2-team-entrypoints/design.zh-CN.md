## Context

方案里在 P1 之后已经明确列出了下一层 operator surface：

- `omx-team-dev.ps1`
- `omx-team-debug.ps1`
- `omx-team-verify.ps1`
- `omx-team-ops.ps1`
- `omx-team-hybrid.ps1`
- `docs/team-mode-playbook.md`

本机当前现实也已经确认：

- 本地 `omx team` 可用
- 当前支持的生命周期命令是 `status`、`await`、`resume`、`shutdown` 与 `api`
- 当前 `omx team` 默认就会自动创建 dedicated worktree
- user-scope 下已经存在 `analyst`、`architect`、`planner`、`researcher`、`verifier`、`test-engineer`、`security-reviewer`、`writer`、`executor`、`team-executor`、`debugger` 等原生 agent

所以，下一刀最有价值的实现不是再加一层状态开关，而是把批准过的 team-mode 工作流落成一组真正可复用的用户级入口脚本。

## Goals / Non-Goals

**Goals:**

- 生成可复用的用户级 `omx team` 包装脚本
- 保持这些脚本是 additive-only，并显式绑定到解析出的真实 `omx` 命令路径
- 通过一个 `ops` wrapper 暴露安全的 team 生命周期命令
- 提供一个 hybrid staffing wrapper，把专家计数翻译成“leader 侧计划 + 一组同构持久 worker”
- 提供一个 verification wrapper，强化 leader 侧原生验证角色，而不是默认持久 verifier pane
- 在目标 Codex home 下生成一份简洁的 playbook
- 保持新资产继续受备份快照与回滚保护
- 让这些 wrapper 能够在临时 Codex home 中通过 fake `omx` 进行测试

**Non-Goals:**

- 不实现 mixed persistent pane compose manifest
- 不修改原生 `omx` 可执行文件，也不对 `omx` 增加 startup binding
- 不把 `verifier` 变成默认持久团队 worker
- 不在 PowerShell wrapper 里自动强行拉起原生专家 subagent
- 不改 OpenClaw runtime 或服务配置

## Decisions

### Decision 1：复用现有 shared support script，而不是新开第二套运行时

P0/P1 已经在 `bin/_codex-user-level-team-mode.ps1` 里生成了共享 support script。

P2 直接扩展这层 support，增加：

- 从 `.omx/state/team` 解析最新 team name
- 构造 team 启动默认值
- 构造 `omx team api` 的只读请求
- 输出 hybrid plan 与 verification plan

原因：

- 保持用户级运行时只有一个事实来源
- 让 wrapper 脚本继续保持很薄
- 测试不需要复制逻辑

### Decision 2：安装时显式解析原生 `omx` 路径

安装器将解析真实 `omx` 命令路径，或者接受显式覆盖，如 `-OmxCommandPath`。

生成后的 wrapper 将直接调用这个解析结果。

原因：

- 避免将来因为 wrapper alias 再次递归调用自己
- 可用 fake `omx` 做测试
- 保持原生 `omx` 作为真正后端

### Decision 3：`omx-team-dev.ps1` 与 `omx-team-debug.ps1` 保持为薄 preset

`omx-team-dev.ps1`：

- 默认 worker 数：`2`
- 默认 worker role：`team-executor`
- 可选切换到 `executor`

`omx-team-debug.ps1`：

- 默认 worker 数：`2`
- 固定 worker role：`debugger`

两者都使用 canonical CLI 形式：

- `omx team N:role "<task>"`

原因：

- 能把批准过的默认值固化下来，同时不掩盖真实 CLI 面
- 不发明仓库级编排器

### Decision 4：`omx-team-ops.ps1` 包装生命周期命令和安全只读 API 操作

该 wrapper 支持：

- `status`
- `await`
- `resume`
- `shutdown`
- `list-tasks`
- `mailbox-list`
- `get-summary`
- `read-manifest`

如果 operator 没有显式给出 team name，wrapper 可以在当前仓库的 `.omx/state/team/` 下解析最近更新的 team。

原因：

- 忘记 team name 是常见摩擦点
- 这些正是计划和当前 CLI help 里列出来的最常用控制面
- 把 API 包装限定在只读操作，避免 mutation creep

### Decision 5：`omx-team-hybrid.ps1` 是 planning-and-launch bridge，不是 mixed-pane orchestrator

hybrid wrapper 接受如下计数：

- `-Architect 1`
- `-Planner 1`
- `-Executor 2`
- `-Verifier 1`

它输出一个结构化 plan，说明：

- 哪些专家角色由 leader 侧原生 subagent 承担
- 持久 worker swarm 是什么
- 对应 swarm 的 canonical `omx team` 启动命令是什么
- 在哪些检查点要调用专家角色

它可以选择性地启动 durable swarm，但不会假装把所有专家都拉成 persistent pane。

原因：

- 这正符合批准过的“异构编排、同构持久 worker”规则
- 今天就能落地，不需要提前引入更重的 compose layer

### Decision 6：`omx-team-verify.ps1` 默认输出 verification plan，而不是拉起持久 verifier 团队

verification wrapper 将输出一个 leader 侧原生验证计划，可包含：

- `verifier`
- `test-engineer`
- `security-reviewer`
- `writer`

是否纳入这些角色，由行为变更、安全敏感范围、文档/运维影响等简易标志决定。

原因：

- 方案明确要求最终裁决应回到 leader 侧原生 subagent
- 让它成为 verification plan surface 才与方案一致
- 也避免把 `verifier` 做成错误的默认团队形态

### Decision 7：wrapper 旁边一并生成用户级 playbook

playbook 将说明：

- `oh_my_codex` 与 `subagent_routing` 的含义
- 每个 wrapper 的用途
- 支持的 `omx team` 生命周期
- hybrid staffing 的解释
- 开放式任务应由“研究角色”和“实现角色”分离承担

原因：

- 只有 wrapper 还不够支撑“跨仓库复用”
- 用户明确要求这套流程能被其他 Codex CLI 项目复用

## Risks / Trade-offs

- [Risk] wrapper 可能与未来 `omx team` CLI 行为漂移。
  Mitigation：基于本机真实 `omx team --help` 与 `omx team api --help` 来实现，并让 wrapper 保持很薄。

- [Risk] 自动发现最新 team name 可能在多 team 共存时选错对象。
  Mitigation：优先支持显式 `-TeamName`，自动发现只作为 convenience fallback。

- [Risk] operator 可能把 `omx-team-hybrid.ps1` 误解成“全异构持久 pane 启动器”。
  Mitigation：让它明确输出“专家角色留在 leader 侧原生 subagent”。

- [Risk] `omx-team-verify.ps1` 可能被误读为 durable verification swarm。
  Mitigation：它只做 verification plan surface，并在文档里明确最终签收回到 leader 侧。

## Migration Plan

1. 为 P2 创建 proposal、design、spec、tasks 工件。
2. 扩展安装器，增加 `-OmxCommandPath` 解析与新的 wrapper/playbook 生成。
3. 扩展 shared support script，加入 team name 发现、ops 分发、hybrid plan 与 verification plan 帮助函数。
4. 用 fake `omx` 扩展 PowerShell 测试，验证 wrapper 行为。
5. 跑 OpenSpec 与 repo guard 校验。
6. 仓库校验通过后，再重新安装到真实用户 Codex home。
