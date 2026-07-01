# 管理记录：用户级文档工具运行时确认

## Open

- [x] 价值：在声明 live runtime 完成之前，证明可复用文档/PDF/向量工具线已经从 `D:\PythonProject_langgraph` 完成确认。
- [x] 成功标准：Stage 1 冻结可验证的后续方案；Stage 2 从共享仓库验证 Poppler/PDF、文档流水线和向量/检索行为。
- [x] 约束：不做远程发布；不造成 `D:\project` 受保护来源漂移；不跟踪第三方 Poppler 二进制。

## Design

- [x] 交付裁剪：拆成两个本地 main 集成包，先冻结方案，再实施运行时。
- [x] 风险/假设：`D:\project` 有无关 dirty files，必须作为受 guard 保护的消费/对照项目处理。
- [x] 验收证据路径：`tasks.md` 和更新后的实施计划对中的验证命令。

## Build

- [x] 执行模式：worktree 隔离，本地 main 优先集成。
- [x] 质量证据：OpenSpec 验证、方案/文档检查、precommit checker、本地 gate、本地 MR review。
- [x] 阻塞决策：Stage 1 不声明运行时完成；Stage 2 保留为实现 backlog。

## Verify

- [x] Stage 2 runtime 完成后复核偏差。
- [x] Stage 2 runtime 完成后复核风险/变更影响。
- [x] Stage 2 runtime 完成后记录控制决策。

## Archive

- [ ] Stage 2 runtime 完成后记录价值结果。
- [ ] Stage 2 runtime 完成后记录经验。
- [ ] Stage 2 runtime 完成后记录归档/同步证据。

## Monitoring

- [x] 当前事实：Stage 2 已填充 ignored `.local` Poppler cache，修复 3 个文档流水线 PowerShell parser failures，并只把 `D:\project` 作为受保护 no-drift 证据来源。
- [x] 返回/继续决策：无需返回前序阶段；继续 Stage 2 验证和本地 main 优先集成。
