# 管理清单

## Open

- [x] 已检查价值/原因证据：不支持的目标 Mode CLI envelope schema 必须在 GUI 控制前 fail-closed。
- [x] 已检查成功标准证据：稳定 blocker、定向回归测试、实施方案证据更新和本地验证。
- [x] 已检查干系人与约束：Codex operator、目标项目、local-first 发布政策，以及当前没有远端发布授权。

## Design

- [x] 已检查交付裁剪：在独立 feature worktree 中执行小型 tweak 切片；不写真实目标项目。
- [x] 已检查风险与假设：schema mismatch 是兼容性 blocker，不能被视为 ready。
- [x] 已检查验收证据路径：定向测试、OpenSpec validation、仓库 guard、local gate 与 local MR review。

## Build

- [x] 已检查执行模式：主会话在专用 worktree 中执行单一有界切片。
- [x] 已检查质量证据：blocker catalog、共享 envelope 校验器、回归测试和方案勾选清单保持同步。
- [x] 已检查 blocker 决策：当前 Windows surface 无法运行 Comet bash，使用仓库/OpenSpec gate 作为替代证据。

## Verify

- [ ] 测试与 gate 完成后检查偏差。
- [ ] local MR review 后检查风险/变更影响。
- [ ] 合入本地 main 前检查控制决策。

## Monitoring

- [x] 已检查当前事实：本地 `main` 干净并领先 GitLab；该单一切片未达到 durable-team 阈值。
- [x] 已检查 return/no-return 决策：切片已有有界实施计划，不需要回退到 Open/Design。

## Archive

- [x] 本地集成证据可用后检查价值结果。
- [x] 如有需要，在最终验证/清理报告记录 lessons learned。
- [x] `.openspec.yaml` 已记录 archive/sync 证据延后到合入后闭环。
