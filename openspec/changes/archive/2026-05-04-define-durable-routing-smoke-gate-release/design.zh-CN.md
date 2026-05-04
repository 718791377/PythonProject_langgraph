## Context（背景）

active team-mode 与 durable-state 方案已经完成 MR 1 到 MR 6 的有界队列。下一步不应该再次实现 automatic routing runtime，而应该先定义一个小的 release gate，用来约束未来何时可以 exercise `omx-team-auto.ps1`。`omx-team-auto.ps1` 是生成到用户级的 helper，用来规划或执行 automatic durable routing。

最终 production durable-team plan 仍然是 draft。它需要一个 release-train overlay，让后续工作可以按 MVP 或 release slice 讨论，而不是让人误以为完整目标态已经可以直接实施。

## Goals / Non-Goals（目标与非目标）

**Goals（目标）：**

- 把 Release 0.6 定义为 read-first durable routing smoke/adoption gate。
- 要求未来 live routing exercise 必须声明 `target_repository`、`phase`、`task` 和 `operator_consent_boundary`。
- 说明默认边界是 dry-run/read-only：不执行 `-Apply`，不写 `.omx/state/`，不启动 durable team。
- 让 production durable-team plan 继续保持 draft，只补充 MVP/release 拆分。

**Non-Goals（非目标）：**

- 不执行 `omx-team-auto.ps1 -Apply`；`-Apply` 是 helper 的变更执行开关。
- 不运行 `omx team`；`omx team` 是 durable worker-team runtime 命令。
- 不修改 `.omx/state/`；`.omx/state/` 是仓库本地 durable-state 目录。
- 不修改用户级 Codex 配置或 MCP Router state。

## Decisions（决策）

1. 使用 Release 0.6 标签，而不是继续增加 MR 编号。
   - 理由：MR 1 到 MR 6 已经完成，release label 更适合表达用户可见的 readiness。
   - 替代方案：重开 MR 6。拒绝原因是 MR 6 readiness review 已关闭，重复 runtime work 会造成漂移。

2. smoke/adoption gate 必须是单独 reviewed OpenSpec change。
   - 理由：runtime exercise 依赖 target repository、phase、具体 task 和 explicit operator consent boundary。
   - 替代方案：在本次方案更新中直接运行 smoke。拒绝原因是本 change 只做文档和 spec sequencing。

3. production durable-team draft 继续作为北极星材料。
   - 理由：该 draft 有长期架构价值，但完整范围太大，不适合一次实施。
   - 替代方案：把整个 draft 提升为 active。拒绝原因是这会混淆已落地 MVP-shaped 行为和未完成 production target。

## Risks / Trade-offs（风险与权衡）

- [Risk] Release labels 可能和实现现实发生漂移。-> Mitigation：把 label 绑定到 OpenSpec requirement 和 checker-backed validation。
- [Risk] 未来会话可能把 smoke 当成写状态授权。-> Mitigation：默认 read-only，并要求 `-Apply` 或 state writes 前必须有 operator consent。
- [Risk] draft production goals 仍可能被误读为 active work。-> Mitigation：明确 Release 1.0 和 Release 2.0 是未来阶段，不是当前实施声明。
