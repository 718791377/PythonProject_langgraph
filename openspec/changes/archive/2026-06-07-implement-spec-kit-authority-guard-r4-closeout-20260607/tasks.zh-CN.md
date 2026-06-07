# 任务

## 1. 收口包

- [x] 1.1 为 Spec Kit authority guard R4 创建边界明确的 OpenSpec closeout package。
- [x] 1.2 记录 local-only scope、dry-run boundary 与 remote-publication gate。

## 2. Runtime 与 checker

- [x] 2.1 收紧 runtime receipt，要求严格优先级顺序 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- [x] 2.2 收紧 authority guard，使 receipt 缺失或篡改该优先级顺序时 fail closed。
- [x] 2.3 扩展更严格 receipt 契约的定向测试。

## 3. Stable 证据提升

- [x] 3.1 将 R4 收口 requirement 提升进稳定的 safety-rule spec 双语对。
- [x] 3.2 更新 safety-rule script-backing registry，登记 runtime helper 与收口说明。
- [x] 3.3 更新 Spec Kit governance 与 implementation-plan 文本，使其与严格优先级顺序一致。

## 4. 验证与本地集成

- [x] 4.1 运行定向 Spec Kit 测试与 guard 校验。
- [x] 4.2 运行 OpenSpec validation、precommit update/archive review 与 repository guard。
- [x] 4.3 Archive 完成后的 change，并重新运行验证。
- [ ] 4.4 在干净 feature worktree 上运行 local gate 与 local MR review。
- [ ] 4.5 合入本地 `main`、运行 post-merge validation、清理已集成的 feature worktree/branch，并停在 remote-publication gate。
