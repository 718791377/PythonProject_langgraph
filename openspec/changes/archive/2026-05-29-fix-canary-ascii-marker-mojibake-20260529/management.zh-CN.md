# Comet 管理清单

## Open / Value Definition

- [x] 已说明价值/原因。
- [x] 已说明成功标准。
- [x] 已识别相关约束。

## Design / Delivery Framing

- [x] 交付方式已按变更规模裁剪。
- [x] 已记录风险和关键假设。
- [x] 已识别接受证据路径。

## Build / Execution

- [x] 已选择执行模式。
- [x] 已记录 TDD / review / quality 证据。
- [x] 阻塞项已清除或显式决策。

## Verify / Acceptance

- [x] 已检查 proposal/design/tasks 的偏差。
- [x] 已评估风险和变更影响。
- [x] 已记录控制决策。

## Archive / Closing

- [x] 已总结价值结果：启动 canary 当前标记改为传输稳定形式，同时历史/损坏证据仍失败关闭。
- [x] 已记录经验教训：可见 sentinel 文本应保持 ASCII 稳定，检查器/测试常量应通过片段或码点组装。
- [x] 已确认 delta spec 同步、验证证据和归档路径：归档前目标测试、检查器和 OpenSpec guard 已通过；归档路径为 `openspec/changes/archive/2026-05-29-fix-canary-ascii-marker-mojibake-20260529`。

## Monitoring Loop

- [x] 已检查当前事实。
- [x] 已作出继续/调整/停止/返回决策。
