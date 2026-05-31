# 管理清单

## Open
- [x] proposal 中已记录价值和原因。
- [x] 成功标准记录为 checker 背书的 launcher payload 边界。
- [x] 已记录约束：不进行远程发布，不修改用户级配置。

## Design
- [x] 已记录交付裁剪：验证源头生成器并注册 checker，而不是编辑已安装 wrapper。
- [x] 已记录风险：内联 payload 回归、编码回归、测试 manifest 归属冲突。
- [x] 已记录验收证据路径：聚焦 checker/tests、OpenSpec 校验、guard、local gate、local MR review。

## Build
- [x] 已记录执行模式：在隔离 feature worktree 中执行计划。
- [x] 已记录质量证据：新增 checker、回归测试、guard 与安全规则注册。
- [x] 已记录 blocker 决策：CI manifest 被另一个活跃会话声明，因此本包有意不编辑它。

## Verify
- [x] 变更偏差复核会写入 verification report。
- [x] proposal 和 design 中已记录风险与变更影响。
- [x] 控制决策：继续。

## Archive
- [x] 价值结果会通过稳定 startup-binding spec 提升总结。
- [x] 经验记录为文件化 payload 传输要求。
- [x] 归档与同步证据会由 archive 路径、稳定 spec 和验证命令记录。

## Monitoring
- [x] 已记录当前事实。
- [x] 返回/不返回决策：继续。