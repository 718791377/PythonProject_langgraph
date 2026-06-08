# 设计：LangGraph State Release Runtime R4

## 背景

当前 LangGraph evidence checker 已经会拒绝 completed work 仍处于 `running` 等 active status 的情况。runtime 代码已经可以创建、resume、inspect、recover 并扩展 thread state，但还没有一个 operator-facing helper 来记录 release event，并把 thread 更新为 non-active state。

## 目标

- 为 `close`、`release`、`handoff` 提供一个边界明确的 release command。
- 将 release receipt 持久化到 repo-local LangGraph state，而不是 transient chat context。
- 保存 rollback 或 restore note，确保 release mistake 可以恢复，而不是隐式切换 backend family。
- backend-family handoff 必须显式记录 handoff target 与 reason。
- 不改变现有 Codex leader 与七阶段 LangGraph shell。

## 非目标

- 不实现新的 durable backend family。
- 不修改任何远端发布状态。
- 不删除 thread、checkpoint、history、interrupt、brief 或 survivor artifacts。
- 不自动切换到 `native_omx`；handoff record 只让后续显式切换变得安全。

## 决策

### 决策 1：在现有 LangGraph store tree 下增加 release receipt

Receipt 位于 `.omx/state/langgraph/store/releases/`，因为它是 durable thread evidence，不是 activation selector，也不是共享 user-level state。

### 决策 2：close、release、handoff 共用一个 helper

该 command 为每种 action 记录相同 common fields，并只在 backend-family handoff 时增加 handoff fields。这样既保持 release evidence 一致，又保留 action-specific semantics。

### 决策 3：rollback evidence 记录为文本，不自动重写 state

Helper 记录 rollback 或 restore guidance，但不 rewind thread state。显式 recovery 仍由 bounded recovery mechanism 负责。

## 验证计划

1. 先为缺失的 release helper command 增加失败 runtime test。
2. 实现 helper 与 receipt path。
3. 通过 status/inspect output 验证 close 与 handoff receipt。
4. 运行目标 LangGraph state-release 测试与仓库门禁。
