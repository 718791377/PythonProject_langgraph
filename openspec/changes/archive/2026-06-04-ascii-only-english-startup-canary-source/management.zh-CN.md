# Comet 管理清单

## Open / Value Definition

- [x] 已说明价值/原因：防止英文/ASCII 传输链路损坏内嵌非 ASCII canary 文本。
- [x] 已说明成功标准：英文摘要 ASCII-only、中文摘要保留字面标记、检查器/测试通过。
- [x] 已识别相关约束：冷启动恢复、launcher payload safety、不授权远端发布。

## Design / Delivery Framing

- [x] 交付方式已按变更规模裁剪：tweak-style 单执行切片。
- [x] 已记录风险和关键假设：用户可见标记语义不变。
- [x] 已识别接受证据路径：目标测试、checker 命令、OpenSpec guard、local gate、local MR review。

## Build / Execution

- [x] 已选择并完成执行模式。
  - 证据：在隔离的 `ascii-startup-canary-markers` worktree 中直接执行 tweak。
- [x] 已记录质量证据。
  - 证据：`verification.zh-CN.md` 记录目标 unittest、checker 与 OpenSpec validation 命令。
- [x] 阻塞项已清除或显式决策。
  - 证据：实现无剩余阻塞；最终集成仍按 local-main-first，并停在远程发布门前。

## Verify / Acceptance

- [x] 已检查 proposal/design/tasks 偏差。
  - 证据：仅改变存储位置；用户可见 canary 语义不变。
- [x] 已评估风险和变更影响。
  - 证据：英文来源变为 ASCII-only，中文来源保留 UTF-8 字面文本，回滚方式为 revert 单个本地 feature commit。
- [x] 已记录控制决策。
  - 证据：继续执行 archive、最终本地 gate、本地 `main` 集成，并停在远程发布门。

## Archive / Closing

- [x] 已总结价值结果。
  - 证据：英文启动摘要保持 ASCII-only，中文伴随文件保留字面可见标记来源。
- [x] 已记录经验教训或可复用指导。
  - 证据：不要在英文/ASCII 启动面存放非 ASCII 哨兵文本；通过检查器强制拆分来源。
- [x] 已确认 delta spec sync、验证证据和 archive path。
  - 证据：稳定 spec 已按完整规格手工同步；archive 已使用 `openspec archive --skip-specs` 保留完整稳定 spec；archive path 为 `openspec/changes/archive/2026-06-04-ascii-only-english-startup-canary-source/`，验证报告路径为 `openspec/changes/archive/2026-06-04-ascii-only-english-startup-canary-source/verification.zh-CN.md`。

## Monitoring Loop

- [x] 已检查当前事实。
- [x] 已作出继续、调整、停止或返回决策。
