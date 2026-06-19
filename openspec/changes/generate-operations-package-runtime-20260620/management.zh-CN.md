# 管理记录：生成运营包 Runtime

## Open

- [x] 价值：把两套已经刷新的运营系统语料转成可执行、可检查、双语成对的运营包。
- [x] 成功标准：Stage A 在本地 `main` 冻结契约；Stage B 在本地 `main` 生成并验证 live operations-package runtime 与文档。
- [x] 约束：仅本地集成、双语配对、registry 覆盖、执行层流程具备过程组式 I/T/O、不远端发布。

## Design

- [x] 交付裁剪：两个串行本地 main 集成包，先冻结方案，再实现 runtime/package。
- [x] 风险/假设：生成文档不得替代白皮书/北极星；Stage B 不要求一次性写满未来 48/60 正文，但台账和必需运营包文档必须完整。
- [x] 验收证据路径：OpenSpec 验证、package checker、focused tests、本地 gate、本地 MR review 和本地 main helper 证据。

## Build

- [x] Stage A 执行模式：隔离 worktree，leader 本地集成，专家 advisory。
- [x] Stage A 质量证据：proposal/design/tasks/management/spec/plan artifacts。
- [x] blocker 决策：durable/persistent team 等到 Stage A 集成且 Stage B 打开 2+ 独立执行切片后再启动。

## Verify

- [ ] Stage A 验证后的偏差审查。
- [ ] Stage A 验证后的风险/变更影响审查。
- [ ] Stage A 验证后的控制决策。

## Archive

- [ ] Stage B runtime 工作后的价值结果记录。
- [ ] Stage B runtime 工作后的经验教训记录。
- [ ] Stage B runtime 工作后的 archive/sync 证据记录。

## Monitoring

- [x] 当前事实：来源白皮书、北极星、清单、生命周期裁剪、PMI map 和过程组契约均已存在。
- [x] Stage A return/no-return 决策：继续本地验证和本地 main 集成；不需要返回循环。
