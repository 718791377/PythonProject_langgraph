# 管理检查清单

## Open

- [x] 已记录价值与原因：runtime release helper 补齐 checker-only evidence 留下的运行时缺口。
- [x] 已记录成功标准：release receipt、non-running thread status、projection evidence 和 tests。
- [x] 已记录约束：仅本地实现，未授权任何远端发布。

## Design

- [x] 已记录交付裁剪：在隔离 worktree 中串行完成一个 R4 runtime slice。
- [x] 已记录风险与假设：不自动切换 backend family，也不删除 artifact。
- [x] 已记录验收证据路径：targeted runtime tests、checker tests、OpenSpec guard、local gate 和 local MR review。

## Build

- [x] 已记录执行模式：在隔离 worktree 中按 executing-plans 与 TDD 证据实施。
- [x] 已记录质量证据：failing-first runtime test 曾因缺少 `release-thread` 失败；runtime helper 覆盖已并入既有 CI-managed state-release test module，并与 checker tests 一起通过。
- [x] 已记录 blocker decision：build 期间无阻塞；CLI 入口不一致问题已通过同步 top-level 与 package helper copies 解决。

## Verify

- [x] 已记录差异复核：实现覆盖 receipt path、close/release/handoff actions、handoff 必填字段、non-running terminal status，以及 status/inspect/backend projections。
- [x] 风险与变更影响已记录在 design 和 proposal。
- [x] 控制决策：OpenSpec guard 通过后继续归档。

## Archive

- [x] 价值结果由 archive 与 stable spec promotion 汇总。
- [x] 经验记录保留在 stable backend spec，而不只留在 chat。
- [x] Archive/sync evidence 已捕获：归档到 `openspec/changes/archive/2026-06-05-implement-langgraph-state-release-runtime-r4/`，并在本地 main integration 前推进到 `openspec/specs/langgraph-durable-orchestration-backend/spec.md`。

## Monitoring

- [x] 当前事实已检查：单 execution slice 与 active worktree claim。
- [x] Return/no-return decision：continue。
