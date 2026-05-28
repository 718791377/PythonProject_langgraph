# 任务

## 1. OpenSpec 包

- [x] 1.1 为 Project MOE readiness 输出契约加固创建有边界的 OpenSpec 变更包。
- [x] 1.2 记录仅本地范围、回滚、验证路径和 archive deferral。

## 2. 实施

- [ ] 2.1 给 Phase 1 readiness 输出增加顶层 `warnings`、`checked_files` 和 `redacted_paths` 字段。
- [ ] 2.2 保持既有 adaptation lane、blockers 和 `control_mode_allowed` 行为。
- [ ] 2.3 增加 Ready Lane readiness 输出契约的回归覆盖。
- [ ] 2.4 为已覆盖的 readiness 证据更新 Project MOE GUI 实施方案清单。

## 3. 验证和本地集成

- [ ] 3.1 运行定向 Project MOE GUI toolchain 测试。
- [ ] 3.2 运行 OpenSpec validation、precommit update/archive review 和仓库 guard。
- [ ] 3.3 在干净 feature worktree 上运行本地 gate 和本地 MR review。
- [ ] 3.4 创建 rollback ref，合入本地 `main`，运行合入后本地 gate，并清理已集成 worktree/branch。
