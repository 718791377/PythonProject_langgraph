# Comet 管理清单

Change: `refactor-automatic-routing-plan-full-comet`

## Open

- [x] 已检查 value and why：用户要求完整 `/comet` 重构并本地提交。
- [x] 已检查 success criteria：full artifacts、目标文档重构、验证、归档、本地提交。
- [x] 已检查 constraints：不实现 runtime、不合入 local main、不发布远端。

## Design

- [x] 已检查 delivery tailoring：documentation-only full workflow 与有边界的结构化编辑。
- [x] 已检查 risks and assumptions：bash 不可用、runtime evidence boundary、双语 companion 对齐。
- [x] 已检查 acceptance evidence path：`verification.md`、OpenSpec validation、local gate、local MR review。

## Build

- [x] 已检查 execution mode：isolated feature worktree 中 direct/inline execution；由于没有多切片 frozen implementation threshold，不启动 durable team。
- [x] 已检查 quality evidence：验证命令记录在 `verification.md`。
- [x] 已检查 blocker decision：记录 Comet shell helper blocker。

## Verify

- [x] 已检查 variance review：Phase 4 仍是 planned follow-up，未添加 runtime claims。
- [x] 已检查 risk/change impact：仅 docs 与 OpenSpec/Superpowers trace artifacts。
- [x] 已检查 control decision：验证后继续归档。

## Archive

- [x] 已检查 value outcome：计划已具备 full Comet traceability。
- [x] 已检查 lessons learned：bash 不可用时可以记录 blocker，不伪称 shell guard 成功。
- [x] 已检查 archive/sync evidence：documentation-only archive 使用 `--skip-specs`。
