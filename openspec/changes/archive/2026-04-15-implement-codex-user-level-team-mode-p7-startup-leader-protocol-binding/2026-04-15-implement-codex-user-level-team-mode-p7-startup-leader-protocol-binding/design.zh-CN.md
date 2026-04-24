## Context

用户级 team mode 现在已经有安装资产、全局控制面、角色阈值和 durable-team helpers。

剩余的可用性缺口并不是“平台能不能路由”，而是“新会话是否稳定地以 routing-first posture 启动”。

当前状态是：

- 启动期会注入动态 `developer_instructions`
- leader 语义也已经体现在安装资产中
- 但启动期并没有强制执行稳定的 first-turn leader protocol
- 所以用户仍然需要猜测这次自动专家路由或 durable-team 阈值判定到底有没有发生

## Goals / Non-Goals

**Goals**

- 让每个新 wrapped Codex 会话都以 leader-first routed session 的姿态开始
- 让启动期在第一次实质回答前完成任务分型
- 让启动期输出 routing trace
- 让启动期同时解释正向与负向的路由判定

**Non-Goals**

- 不在每次 startup 时自动拉起 durable team
- 不改变 `oh_my_codex` 或 `subagent_routing` 的语义
- 不替换 native Codex bypass startup

## Decisions

### Decision 1: 把 startup leadership 视为运行时协议，而不是只视为一个已安装文件

Why:

- 单独安装 `team-leader.toml` 并不能保证启动期行为
- 启动包装器必须主动绑定这套协议

### Decision 2: 先分类，再决定是否 launch

Why:

- 启动期应该先判定 durable-team 阈值是否满足
- 在任务阶段未明前，不应急切地自动启动 `omx team`

### Decision 3: 让首轮 routing 具备可解释性

Why:

- 用户不应该靠后续行为去猜测是否发生了路由
- 像“当前并行切片不足”这样的负判定，也应当可见

## Validation Plan

1. 启动一个新的 wrapped Codex 会话，验证它会报告 leader-first routing posture。
2. 验证首轮 routing trace 能解释当前是否需要 expert subagents。
3. 验证首轮 routing trace 能解释当前是否满足 `omx team` 阈值。
4. 验证前期任务不会在 startup 时自动拉起 durable team。
5. 验证 execute-parallel 类型任务能指出会触发 `omx team` 的具体阈值。
