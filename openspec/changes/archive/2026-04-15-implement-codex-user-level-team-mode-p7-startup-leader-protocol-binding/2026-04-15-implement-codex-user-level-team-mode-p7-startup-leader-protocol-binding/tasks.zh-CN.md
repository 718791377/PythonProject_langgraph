## 1. OpenSpec Artifacts

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p7-startup-leader-protocol-binding` 的 proposal、design 与 capability spec delta。
- [x] 1.2 记录这一批解决的是 startup-time leader binding，而不是 backend availability。

## 2. Startup Binding

- [x] 2.1 让每个新的 wrapped Codex 会话都绑定到稳定的 leader-first startup protocol。
- [x] 2.2 让启动期在第一次实质回答前完成 first-turn task-shape classification。
- [x] 2.3 输出可检查的 first-turn routing trace。
- [x] 2.4 在首轮解释正向与负向的 `omx team` threshold 决策。

## 3. Validation

- [x] 3.1 验证新的 wrapped 会话会报告 leader-first routing posture。
- [x] 3.2 验证新的 wrapped 会话会解释当前是否需要 expert subagents。
- [x] 3.3 验证新的 wrapped 会话会解释为什么这次选择或没有选择 `omx team`。
