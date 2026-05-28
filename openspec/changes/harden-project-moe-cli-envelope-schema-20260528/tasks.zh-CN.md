# 任务

## 1. OpenSpec 包

- [x] 1.1 创建 Project MOE CLI envelope schema 加固的有界 OpenSpec change 包。
- [x] 1.2 记录本地范围、回滚、验证路径和 archive deferral。

## 2. 实施

- [x] 2.1 增加稳定的 `blocked:cli_envelope_schema_version_mismatch` blocker 与 remediation 元数据。
- [x] 2.2 在共享 read-contract 校验器中拒绝不受支持的目标 Mode CLI envelope `schema_version`。
- [x] 2.3 增加 unsupported read-contract envelope schema 的 Phase 1 readiness 回归测试。
- [x] 2.4 根据已覆盖的 readiness 证据更新 Project MOE GUI 实施方案勾选项。

## 3. 验证与本地集成

- [x] 3.1 运行 Project MOE GUI 工具链定向测试。
- [x] 3.2 运行 OpenSpec validation、precommit update/archive review 与仓库 guard。
- [x] 3.3 在干净 feature worktree 上运行 local gate 与 local MR review。
- [ ] 3.4 创建 rollback ref，合入本地 `main`，运行合入后 local gate，并清理已集成 worktree/branch。
