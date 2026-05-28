# Comet Management Record

## Open / Initiating
- [x] 已说明 value 与 why。
- [x] success criteria 可度量。
- [x] 已识别 stakeholders、constraints 与 operating boundaries。

## Design / Planning
- [x] delivery approach 已裁剪为 full workflow + repo-local non-mutating guard slice。
- [x] 已记录主要 risks 与 assumptions。
- [x] 已定义 acceptance evidence path。

## Build / Executing
- [x] execution mode 选择为 isolated worktree 中的 `executing-plans`。
- [x] quality evidence 通过 tests 与 guard checks 记录。
- [x] blockers 已清除或已有明确决策。

## Verify / Controlling
- [x] 已检查 scope、design 与 acceptance criteria 偏差。
- [x] 已评估 risk 与 change impact。
- [x] control decision `continue` 表示本地包可继续进入 repository guard、local gate、local MR review 与本地 `main` 集成。

## Archive / Closing
- [x] 已总结 value outcome。
- [x] 已记录 lessons learned 或 reusable guidance。
- [x] 已确认 delta spec sync、verification evidence 与 archive path。

## Monitoring Loop
- [x] 已检查 current facts。
- [x] 已作出 continue/adjust/stop/return 决策。
- [x] 不需要 return。
