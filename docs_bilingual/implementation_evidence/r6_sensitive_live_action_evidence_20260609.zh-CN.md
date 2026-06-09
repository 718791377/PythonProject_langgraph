# R6 敏感 Live Action 证据 - 2026-06-09

## 摘要

- 包：R6 敏感 live-action 支撑与 Stop-Slop/Caveman 真实执行证据。
- 防冲突优先级保持：`Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- Runtime 新增支撑：`tools/r6_live_runtime.py run --mode live-action --env-file <local-env> --proof-receipt <redacted-proof-json>`。
- 安全修正：Browser/WXWork/Harness 的 `live-action` 不能只凭环境目标变成 `live-executed`；必须额外提供已脱敏的外部执行 proof receipt。
- Stop-Slop/Caveman 结果：`live-executed`，副作用族为 `user_level_install`。
- Browser/WXWork/Harness 在当前环境中的结果：由于没有真实目标与 proof 输入，继续 fail-closed；fail-closed 表示缺少证据时运行时拒绝把敏感动作标记为通过，`blocked` 表示 receipt 记录未满足执行门禁而不是记录为真实执行成功。
- 远端发布变更：`false`。

## Stop-Slop/Caveman 真实执行

- Lane：`stop-slop-caveman-response-density-runtime`。
- Mode：`user-level-install`。
- Checker 状态：有效 R6 receipt。
- 用户级安装只写入所选用户级隔离根下的 R6 子目录。
- 已增加 native Codex 防护：如果安装根包含原生 `codex`、`codex-raw` 或 `codex-ohmy` launcher，会在写入前拒绝。
- 脱敏证据 hash：
  - receipt path hash：`0dd315d03e0311c8`
  - target env hash：`482fbdffc289f365`
  - install root hash：`16a2ea60066dd693`
  - installed path hash：`6b9311abd8fc030f`
  - wrapper path hash：`4e8866e0019bfa51`
  - env file hash：`8b3dac5c257dc058`

## 仍缺真实执行目标的敏感动作

以下 lane 已通过 `live-action` 尝试；`live-action` 表示浏览器、外部消息或 harness job 这类外部可见副作用的运行路径，但因为缺少真实目标和 redacted proof receipt，按设计保持 `blocked`，即 receipt 只记录未满足的执行门禁：

- `user-level-browser-cli-adapter-boundary` - 浏览器 CLI 适配边界 lane，必须提供 allowlisted browser action proof 后才能接受为真实执行。
- `user-level-cli-anything-wxwork-cli-governance` - WXWork CLI 治理 lane，必须提供脱敏外部消息 proof 后才能接受为真实执行。
- `codex-harnesses-governance` - harness 治理 lane，必须提供受门禁保护的 harness job proof 后才能接受为真实执行。

这些 lane 要被接受为 `live-executed` 前必须提供的 proof：

- Browser proof 必须证明 allowlisted browser action 已发生，且未保存 raw browser data。
- WXWork proof 必须证明外部消息已发送，但只保留 message hash，不保留正文或原始接收方。
- Harness proof 必须证明 read/write guard、isolated worktree、job state、changed-path report、no Codex takeover，以及 timeout/cleanup evidence。

## 验证命令

- `python test\r6_live_runtime.test.py -v` - 验证 R6 runtime 在 live-ready、live-action、安装和 Spec Kit 模式下的单元行为。
- `python test\check_r6_live_runtime_receipts.test.py -v` - 验证 R6 runtime evidence 的 receipt checker 接受与拒绝场景。
- `python tools\r6_live_runtime.py run --root . --lane browser-cli-adapter --mode live-action --json` - 证明 browser live-action 在缺少必需脱敏 proof 时保持 blocked。
- `python tools\r6_live_runtime.py run-all --root . --json` - 为全部受治理 lane 重新生成默认安全 R6 receipt 集。
- `python tools\check_r6_live_runtime_receipts.py --root . --receipt-dir .omx\r6-live-runtime\receipts --require-coverage --max-age-hours 24 --json` - 检查全部 R6 lane 的近期 receipt 覆盖。
