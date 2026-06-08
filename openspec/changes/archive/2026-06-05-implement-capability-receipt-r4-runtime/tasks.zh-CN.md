# 任务

## 1. OpenSpec 与 ownership

- [x] 1.1 创建 R4 receipt runtime governance 的 bounded OpenSpec change package。
- [x] 1.2 记录 local worktree claim 与 task receipt metadata。

## 2. TDD 实现

- [x] 2.1 为 R4 smoke receipt required fields 与 fail-closed write/live markers 增加失败测试。
- [x] 2.2 为 rollback receipt authorization 与 sanitized output behavior 增加失败测试。
- [x] 2.3 实现 smoke receipt validation、summary 与 template support。
- [x] 2.4 实现 rollback receipt validation、summary 与 template support。
- [x] 2.5 更新 OpenSpec delta 与 stable governance spec evidence，记录 R4 完成。

## 3. 验证与本地集成

- [x] 3.1 运行 focused receipt governance tests。
- [x] 3.2 运行 OpenSpec validation、precommit update/archive review 与 repository guard。
- [x] 3.3 archive 已完成 change 并重新验证。
- [ ] 3.4 在干净 feature worktree 上运行 local gate 与 local MR review。
- [ ] 3.5 合入本地 `main`、运行 post-merge validation，并清理 integrated worktree/branch。
