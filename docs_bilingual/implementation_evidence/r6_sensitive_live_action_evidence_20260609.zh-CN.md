# R6 敏感 Live Action 证据 - 2026-06-09

## 摘要

- 包：R6 敏感 live-action proof gate 与 follow-up live 证据。
- 防冲突优先级保持：`Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- Runtime 支撑：`tools/r6_live_runtime.py run --mode live-action --env-file <local-env> --proof-receipt <redacted-proof-json>`。
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

## 仍被阻塞的敏感动作

以下 lane 已进入 `live-action` 路径，即浏览器、外部消息或 harness 这类外部可见副作用路径。由于缺少必需的真实目标与脱敏执行 proof，它们按设计保持 `blocked`；这里的 `blocked` 含义见上方术语表，when proof gate 满足前，不得声称这些 lane 已达到 `R6 live-executed`。

### WXWork / CLI-Anything

- Lane：`user-level-cli-anything-wxwork-cli-governance`。
- Receipt：忽略的本地 receipt `.omx/r6-live-runtime/receipts/wxwork-live-action-blocked-followup.json`。
- 当前 receipt mode：`blocked`，which means runtime 记录的是缺失 proof gate，而不是声明 WXWork 发送成功。
- 当前 blocker 摘要：`external_execution_proof_action_performed_required`、`external_execution_proof_external_message_sent_required`、`external_execution_proof_message_body_hash_required`。
- 接受为 `live-executed` 前所需 proof：必须在当前 operator authorization 与 owner lease 下实际执行一次 WXWork/企业微信外部发送，同时只保留 message-body hash，不保留 raw recipient/body。
- 当前 helper 姿态已由 `tools/wxwork_cli_governance.py` 验证：仅 repo-local guard，无 process probe、无 GUI control、无企业微信 API/webhook 调用、无消息发送、无用户级 Codex config 修改。

### Codex Harnesses

- Lane：`codex-harnesses-governance`。
- Receipt：忽略的本地 receipt `.omx/r6-live-runtime/receipts/harness-live-action-blocked-followup.json`。
- 当前 receipt mode：`blocked`，which means runtime 记录的是缺失 proof gate，而不是声明 harness job 成功。
- 当前 blocker 摘要：缺少 `action_performed`、`read_guard`、`write_guard`、`isolated_worktree`、`job_state`、`changed_paths_report` 与 `no_codex_takeover` proof；这些字段已在上方术语表中定义。
- 接受为 `live-executed` 前所需 proof：必须有一个实际选定的 harness candidate job，并带有 read/write guards、isolated worktree、job state、changed-path report、no Codex takeover、timeout release、rollback 与 cleanup evidence。
- 当前 helper 姿态已由 `tools/run_codex_harnesses_smoke.py plan --json` 验证：只有 R4 read-only smoke registry；没有 install、没有 sidecar start、没有 write-capable harness job、没有 Codex takeover。

## 验证命令

本 follow-up 会话中的 fresh verification：

- `python tools\check_r6_live_runtime_receipts.py --root . --receipt-dir .omx\r6-live-runtime\receipts --require-coverage --max-age-hours 24 --json` - 在 primary local repository 中通过，接受全部 14 个 R6 lane，并为 Browser 与 Stop-Slop/Caveman 选择 `live-executed` 证据。
- `python test\r6_live_runtime.test.py -v` - 14/14 测试通过。
- `python test\check_r6_live_runtime_receipts.test.py -v` - 9/9 测试通过。
- `python tools\check_codex_harnesses_governance.py --root . --json` - 通过，确认 harness governance checker 姿态。
- `python tools\check_user_level_cli_anything_wxwork_cli_governance.py --root . --json` - 通过，确认 WXWork/CLI-Anything governance checker 姿态。

## 非声明项

- WXWork 在当前环境中**尚未** live-executed。
- Codex harness job 在当前环境中**尚未** live-executed。
- 这些 receipt 未执行 GitLab/GitHub 远端发布。
