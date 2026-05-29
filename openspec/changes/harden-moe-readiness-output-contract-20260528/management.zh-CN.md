# 管理清单

## Open

- [x] 已检查价值/原因证据：GUI preflight 需要稳定的顶层 readiness 证据字段。
- [x] 已检查成功标准证据：输出字段、回归断言和方案清单更新。
- [x] 已检查干系人/约束：Codex operator、目标项目、本地优先策略，以及未授权远端发布。

## Design

- [x] 已检查交付裁剪：有边界的 feature worktree 切片；不写真实目标项目。
- [x] 已检查风险和假设：增量输出字段不得改变既有 lane 语义。
- [x] 已检查验收证据路径：定向测试、OpenSpec validation、仓库 guard、本地 gate 和本地 MR review。

## Build

- [x] 实现派生 readiness 输出契约字段。
- [x] 增加回归断言。
- [x] 根据证据更新方案清单。

## Verify

- [x] 运行定向测试和仓库门禁。
- [x] 运行本地 gate 和本地 MR review。
- [x] 在合入本地 main 前检查控制决策。

## Monitoring

- [x] 已检查当前事实：本地 `main` 领先 GitLab，且本切片没有远端发布授权。
- [x] 已检查返回/不返回决策：有边界的实现可以从 Build 继续。

## Archive

- [x] archive/sync 证据已在 `.openspec.yaml` 中延后到集成闭环后处理。
