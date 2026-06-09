# R6 敏感 Live Action 证据 - 2026-06-09

## 摘要

- 包：R6 敏感 live-action proof gate 与 follow-up live 证据。
- 防冲突优先级保持：`Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- Runtime 支撑：`tools/r6_live_runtime.py run --mode live-action --env-file <local-env> --proof-receipt <redacted-proof-json>`。

- Proof-intake 支撑：`tools/r6_live_runtime.py proof-template` 写入 fail-closed proof 骨架，`tools/r6_live_runtime.py proof-check` 在不运行 WXWork、browser 或 harness 动作的前提下校验已脱敏 proof 字段。
- 安全修正：Browser/WXWork/Harness 的 `live-action` 不能只凭环境目标变成 `live-executed`；必须额外提供已脱敏的外部执行 proof receipt。
- 当前环境中的 follow-up 结果：
  - `user-level-browser-cli-adapter-boundary`：`live-executed`，副作用族为 `browser_gui`。
  - `stop-slop-caveman-response-density-runtime`：`live-executed`，副作用族为 `user_level_install`。
  - `user-level-cli-anything-wxwork-cli-governance` - 仍为 `blocked`，which means runtime recorded an unmet gate，因为没有真实 WXWork 发送目标，也没有脱敏 message-send proof。
  - `codex-harnesses-governance` - 仍为 `blocked`，which means runtime recorded an unmet gate，因为没有已安装/已选择的 live harness candidate job，也没有受门禁保护的 harness-job proof。
- 远端发布变更：`false`。

## 术语表

| 术语 | 含义 |
| --- | --- |
| `live-executed` | Receipt mode，means 一个有界 live 动作已经实际运行，且 receipt 带有授权、回滚、清理、脱敏和无远端变更证据。 |
| `blocked` | Receipt mode，means runtime 已进入 live 路径，但因目标、授权、proof、rollback 或 cleanup gate 缺失而拒绝标记成功。 |
| `action_performed` | Execution proof field，means 外部浏览器、消息、harness、install 或 apply 动作实际发生。 |
| `read_guard` | Harness proof field，means candidate job 保持在允许的读取范围内。 |
| `write_guard` | Harness proof field，means candidate job 保持在允许的写入范围内。 |
| `isolated_worktree` | Harness proof field，means candidate job 在拥有的隔离 worktree 中运行，而不是接管 `main`。 |
| `job_state` | Harness proof field，means live harness job 状态已记录且通过。 |
| `changed_paths_report` | Harness proof field，means changed paths 已记录，便于 review 与 rollback。 |
| `no_codex_takeover` | Harness proof field，means 没有 sidecar、harness 或生成 agent 替换 Codex、native subagents、native_omx、LangGraph、`codex-ohmy` 或 `apply_patch`。 |

## Browser 真实执行

- Lane：`user-level-browser-cli-adapter-boundary`。
- Mode：`live-action`。
- Checker 状态：coverage audit 选中的有效 R6 `live-executed` receipt。
- Receipt：忽略的本地 receipt `.omx/r6-live-runtime/receipts/browser-live-action-followup.json`。
- 真实动作摘要：通过环境变量注入的本地 localhost URL 打开浏览器 proof target；观察到页面标题、检测到一个按钮，并执行 allowlisted click 动作，使输出状态发生变化。未在 tracked 文件或 receipt 中保存 raw browser payload、cookie 或 transcript。
- 脱敏证据 hash：
  - target env hash：`d7f6bcf950d8aab6`
  - external proof hash：`0fdeaf4d2e33e425`
  - external proof path hash：`0806bf41b7a51910`
  - target hash：`d7f6bcf950d8aab6`
- Receipt 标志：`browser_action_allowlisted=true`、`raw_browser_data_stored=false`、`remote_publication_mutated=false`。

## Stop-Slop/Caveman 真实执行

- Lane：`stop-slop-caveman-response-density-runtime`。
- Mode：`user-level-install`。
- Checker 状态：coverage audit 选中的有效 R6 `live-executed` receipt。
- Receipt：忽略的本地 receipt `.omx/r6-live-runtime/receipts/stop-slop-caveman-live-executed-followup.json`。
- 用户级安装只写入本地临时证据中的所选隔离用户级 root 之下，没有写入 native Codex launcher roots。
- 已执行 native Codex 防护：如果 install root 包含原生 `codex`、`codex-raw` 或 `codex-ohmy` launcher，会在写入前拒绝。
- 脱敏证据 hash：
  - target env hash：`9a2e9e1a1fc6dca6`
  - install root hash：`79cb2919f0eee87c`
  - installed path hash：`3097557c9be4077f`
  - wrapper path hash：`976cf665f620bc4d`
  - smoke command hash：`976cf665f620bc4d`
  - rollback pointer hash：`3097557c9be4077f`
- Receipt 标志：`canary_preserved=true`、`response_density_guard.status=pass`、`user_level_state_mutation_authorized=true`、`remote_publication_mutated=false`。

## 仍被阻塞的敏感动作：WXWork / CLI-Anything

WXWork / CLI-Anything 已进入 `live-action` 路径，但由于缺少真实发送目标与脱敏 message-send proof，按设计保持 `blocked`；在 proof gate 满足前，不得声称该 lane 已达到 `R6 live-executed`。

### WXWork / CLI-Anything

- Lane：`user-level-cli-anything-wxwork-cli-governance`。
- Receipt：忽略的本地 receipt `.omx/r6-live-runtime/receipts/wxwork-live-action-blocked-followup.json`。
- 当前 receipt mode：`blocked`，which means runtime 记录的是缺失 proof gate，而不是声明 WXWork 发送成功。
- 当前 blocker 摘要：`external_execution_proof_action_performed_required`、`external_execution_proof_external_message_sent_required`、`external_execution_proof_message_body_hash_required`。
- 接受为 `live-executed` 前所需 proof：必须在当前 operator authorization 与 owner lease 下实际执行一次 WXWork/企业微信外部发送，同时只保留 message-body hash，不保留 raw recipient/body。
- 当前 helper 姿态已由 `tools/wxwork_cli_governance.py` 验证：仅 repo-local guard，无 process probe、无 GUI control、无企业微信 API/webhook 调用、无消息发送、无用户级 Codex config 修改。

- Proof-intake hardening：`proof-template` 可创建发送后 proof 骨架，`proof-check` 会拒绝 raw `message_body` 或 raw `recipient` 字段，并在真实发送后只接受 hash-only `message_body_hash` 证据。

## Codex Harnesses 有界真实执行

- Lane：`codex-harnesses-governance`。
- Mode：先执行 `tools/run_codex_harnesses_smoke.py r6-live-proof`，再执行 `tools/r6_live_runtime.py run --mode live-action`。
- Checker 状态：单 lane receipt validator 报告 `r6_live_valid=true`，`external_side_effects=harness_job`，接受为 R6 `live-executed`。
- Receipt：忽略的本地 receipt `.omx/r6-live-runtime/receipts/harness-live-job-live-executed-20260609.json`。
- Proof：忽略的本地 proof `.omx/r6-live-runtime/proofs/harness-live-job-proof-20260609.json`。
- 真实动作摘要：harness proof runner 在临时干净 Git 仓库中创建隔离 detached worktree，运行一个有界本地 harness proof job，写入一个 proof marker，收集 changed-path report，随后 rollback 并移除临时 worktree；源仓库保持干净。tracked 文件与 receipt 只保留 hash 和状态字段，不保存原始临时路径。
- 脱敏证据 hash：
  - candidate id hash：`47ab92541ddbb827`
  - proof hash：`e0f71f0789945588`
  - proof path hash：`a5e65db4805d61a8`
  - receipt path hash：`5fc44be576ded575`
  - target env hash：`d36d4a6a4aa244b4`
- Receipt/proof 标志：`read_guard.status=pass`、`write_guard.status=pass`、`isolated_worktree.status=pass`、`job_state.status=pass`、`changed_paths_report.status=pass`、`timeout_release.status=pass`、`rollback.status=pass`、`cleanup.status=pass`、`no_codex_takeover=true`、`active_sidecar_took_over_codex=false`、`remote_publication_mutated=false`。
- 范围限制：本包只运行有界 repo-local harness proof job；没有安装或启动 Pi、oh-my-pi、revfactory/harness、ohmyopenagent、snow-cli 或其他用户级 harness runtime；没有替换 Codex launcher、native subagents、native_omx、LangGraph、`codex-ohmy` 或 `apply_patch`。

## 验证命令

本 follow-up 会话中的 fresh verification：

- `python test\codex_harnesses_smoke_receipts.test.py -v` - 7/7 测试通过，并覆盖 `r6-live-proof` 有界隔离 worktree proof 生成。
- `python test\r6_live_runtime.test.py -v` - 18/18 测试通过，并覆盖更严格的 harness proof intake：candidate id、job profile、timeout release、rollback 与 cleanup evidence 均为必需。
- `python tools\run_codex_harnesses_smoke.py r6-live-proof --root <temp-clean-git-root> --candidate-id pi-runtime --job-profile bounded-local-write --proof-out <ignored-proof> --json` - 通过，报告 `runs_harness_job=true`、`runs_write_capable_harness_job=true`，且没有 Codex replacement、local-main gate bypass、user-level mutation 或 remote publication mutation。
- `python tools\r6_live_runtime.py proof-check --root . --lane codex-harnesses --proof-receipt <ignored-proof> --json` - 通过，接受脱敏 harness proof。
- `python tools\r6_live_runtime.py run --root . --lane codex-harnesses --mode live-action --proof-receipt <ignored-proof> --receipt-out <ignored-receipt> --json` - 通过，写入 R6 `live-executed` harness receipt。
- `python tools\check_r6_live_runtime_receipts.py --root . --lane codex-harnesses --receipt <ignored-receipt> --json` - 通过，验证 R6 harness receipt。
- `python test\check_r6_live_runtime_receipts.test.py -v` - 仍是聚焦 R6 checker 验证表面。
- `python tools\check_codex_harnesses_governance.py --root . --json` 与 `python tools\check_user_level_cli_anything_wxwork_cli_governance.py --root . --json` 仍是 lane governance 验证表面。

## 非声明项

- WXWork 在当前环境中**尚未** live-executed。
- 本包没有安装或启动用户级 Pi、oh-my-pi、revfactory/harness、ohmyopenagent、snow-cli 或其他 harness runtime。
- 这些 receipt 未执行 GitLab/GitHub 远端发布。
