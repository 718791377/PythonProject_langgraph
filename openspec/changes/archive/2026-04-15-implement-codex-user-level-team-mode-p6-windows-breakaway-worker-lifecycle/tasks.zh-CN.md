## 1. OpenSpec Artifacts

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p6-windows-breakaway-worker-lifecycle` 的 proposal、design 与 capability spec delta。
- [x] 1.2 记录这一批是已归档 `P6` backend 批次之后的生命周期修正批次。

## 2. Runtime Follow-Up

- [x] 2.1 为 Windows prompt workers 增加更强的 breakaway launcher 路径。
- [x] 2.2 使用真实 controller pid 做 liveness 与 shutdown 跟踪，而不是短寿命 launcher 跳板 pid。
- [x] 2.3 让 shutdown 与新的 breakaway-launched worker 形态对齐。
- [x] 2.4 更新 Windows worker guidance，避免重复 controller-owned startup ACK / initial claim。

## 3. Validation

- [x] 3.1 验证新的 Windows durable team 在 launching shell 退出后仍能存活。
- [x] 3.2 针对新 launcher 路径验证 clean shutdown。
- [x] 3.3 在 follow-up lifecycle fix 之后重新验证跨仓库 tracked-team isolation。
