# 任务

## 1. OpenSpec package
- [x] 1.1 创建 R4 readiness refresh 的有界 OpenSpec package。
- [x] 1.2 记录 local-only 范围、非 adoption 边界、回滚与验证路径。

## 2. 实现
- [x] 2.1 为 `codex-durable-state-status.ps1` 增加显式 `-RefreshReadiness` 支持。
- [x] 2.2 只有显式 refresh 才写 `.omx/state/readiness/durable-capability-readiness-projection.json`。
- [x] 2.3 保留独立 readiness 字段以及 blockers/source evidence。
- [x] 2.4 确保 receipt 声明未 adoption durable workflow 或 persistent team。

## 3. 验证与本地集成
- [x] 3.1 增加 checker 与 PowerShell regression coverage。
- [x] 3.2 运行 targeted tests、OpenSpec validation、precommit review 与 local gate。
- [x] 3.3 更新计划证据，并准备在同一个本地集成包中 archive/sync 本 change。
- [x] 3.4 记录 post-archive handoff：archive 与 commit 后运行 local MR review、合入 local `main`、运行 post-merge validation，并停在远端发布授权门。
