# 任务清单

## 1. OpenSpec 变更包

- [x] 1.1 创建边界明确的 R4 OpenSpec 变更包。
- [x] 1.2 记录范围、非目标、验证路径和归档暂缓说明。

## 2. 运行时实现

- [x] 2.1 在 repo-local `.omx/state/langgraph/store/releases/` 下增加 release receipt 路径 helper。
- [x] 2.2 增加支持 `close`、`release`、`handoff` 的 `release-thread` CLI command。
- [x] 2.3 将 release receipt evidence 投射到 thread state、backend projection、status output 和 inspect output。
- [x] 2.4 保留 rollback/restore note、redaction status、survivor queue status、checkpoint path、artifact path、handoff target 和 timeout release 字段。

## 3. 测试与方案更新

- [x] 3.1 在实现前增加失败的 runtime tests。
- [x] 3.2 将 runtime release-helper 覆盖加入既有 CI-managed state-release test module。
- [x] 3.3 更新双语 implementation plan 状态和 evidence index。

## 4. 验证与归档包

- [x] 4.1 运行 targeted state-release runtime tests。
- [x] 4.2 运行 durable artifact state-release checker tests。
- [x] 4.3 归档前运行 OpenSpec validation 和 repository guard。
- [x] 4.4 本地 main 集成前归档该 change，并将 release-runtime requirement 推进到 stable spec。
- [x] 4.5 保持 local-main-first 发布边界：archive 和 commit 后继续 guarded local integration；远端发布仍未授权。
