## 1. OpenSpec Artifacts

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p6-windows-native-team-backend` 的 proposal、design 与 capability specs。
- [x] 1.2 记录已经完成的 P5 路由层与新增 P6 runtime-backend 层之间的分工边界。

## 2. Runtime Backend

- [x] 2.1 在 `omx team` 下增加 backend abstraction。
- [x] 2.2 实现第一版 native Windows backend。
- [x] 2.3 保持 repo-local `.omx/state/team/...` 语义在不同 backend 间稳定。

## 3. Validation

- [x] 3.1 在不依赖 WSL2 的条件下验证 native Windows 的 launch、status、shutdown。
- [x] 3.2 验证 Windows backend 下 `omx-team-auto.ps1 -Apply` 的 launch/status，以及 shutdown 失败时保留 tracked record 的语义。
- [x] 3.3 运行 `openspec validate --all` 与 `python .\tools\run_openspec_guard.py --root .`。
