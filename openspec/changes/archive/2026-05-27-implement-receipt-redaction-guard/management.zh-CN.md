# Comet 管理记录

## Open / Initiating
- [x] 已说明价值与原因。
- [x] 已定义可衡量成功标准。
- [x] 已识别干系人、约束和运行边界。

## Design / Planning
- [x] 交付方式已裁剪：先做 repo-local deterministic guard，再考虑用户级安装激活。
- [x] 已记录主要风险和假设。
- [x] 已定义验收证据路径。

## Build / Executing
- [x] 已选择执行模式：隔离 worktree 加直接实现。
- [x] 已通过 unit tests、baseline checker、OpenSpec guard、local gate、local MR review 记录质量证据。
- [x] 阻塞已清除或序列化。

## Verify / Controlling
- [x] 已检查范围、设计与验收标准偏差。
- [x] 已评估风险和变更影响。
- [x] 控制决策记录为 `continue`，含义是本切片已通过范围与风险检查，可以继续进入本地提交和本地 main 集成，不需要回到设计阶段。

## Archive / Closing
- [x] 已总结价值结果。
- [x] 已记录经验。
- [x] 已确认 delta spec sync、验证证据与 archive 路径。

## Monitoring Loop
- [x] 已检查当前事实。
- [x] 已做出继续推进决策。
- [x] 不需要回退到早期阶段。

