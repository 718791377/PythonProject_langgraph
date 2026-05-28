# Comet 管理记录

## Open / Initiating
- [x] 已说明价值与原因。
- [x] 成功标准可度量。
- [x] 已识别相关方、约束与运行边界。

## Design / Planning
- [x] 已裁剪交付方法：完整 workflow，repo-local，且是不产生运行时副作用的 guard 切片。
- [x] 已记录主要风险与假设。
- [x] 已定义验收证据路径。

## Build / Executing
- [x] 已选择执行模式：在隔离 worktree 中使用 `executing-plans`。
- [x] 已通过测试与 guard 检查记录质量证据。
- [x] blocker 已清除，或已有明确处理决策。

## Verify / Controlling
- [x] 已检查相对 scope、design 与 acceptance criteria 的偏差。
- [x] 已评估风险与变更影响。
- [x] 控制决策是 `continue`：当前证据支持继续推进到仓库 guard、本地 gate、本地 MR review 与本地 `main` 合入。

## Archive / Closing
- [x] 已汇总价值结果。
- [x] 已记录经验教训或可复用指导。
- [x] 已确认 delta spec 同步、验证证据与 archive 路径。

## Monitoring Loop
- [x] 已检查当前事实。
- [x] 已做出监控循环决策：本轮继续推进收尾，不需要回到前序阶段。
- [x] 不需要 return。
