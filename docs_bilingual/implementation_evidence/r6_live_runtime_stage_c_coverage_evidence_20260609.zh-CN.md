# R6 Live Runtime Stage C 覆盖证据 - 2026-06-09

## 摘要

- 包：Package 3: R6 lane coverage audit and default receipt generation。
- 覆盖结果：14 个 R6 lane 中 14 个已被接受；缺失 lane 数：0。
- repo-local/default-safe lane 已在无外部副作用下 live-executed：7 个。
- 缺少环境目标的敏感 lane 生成有效 blocked receipt，而不是静默执行外部动作：7 个。
- receipt 目录：`.omx/r6-live-runtime/receipts`。
- runtime 命令：`python tools/r6_live_runtime.py run-all --root . --json`。
- coverage 命令：`python tools/check_r6_live_runtime_receipts.py --root . --receipt-dir .omx/r6-live-runtime/receipts --require-coverage --json`。
- 机器可读证据：`docs_bilingual/implementation_evidence/r6_live_runtime_stage_c_coverage_evidence_20260609.json`。

## 已 live-executed 的 default-safe lane

- `durable-capability-readiness-projection` - 模式 `live-executed` 表示 repo-local readiness projection 已运行；副作用 `none` 表示未调用外部 runtime。
- `durable-smoke-adoption-gate-template` - 模式 `live-executed` 表示 gate-template runtime path 已运行；副作用 `none` 表示未调用外部 runtime。
- `gstack-codex-delivery-loop-runtime-governance` - 模式 `live-executed` 表示 advisory delivery-loop runtime check 已运行；副作用 `none` 表示未调用外部 runtime。
- `langgraph-state-release-evidence` - 模式 `live-executed` 表示 repo-local state-release evidence path 已运行；副作用 `none` 表示未调用外部 runtime。
- `repo-local-selector-ownership` - 模式 `live-executed` 表示 selector ownership path 已运行；副作用 `none` 表示未调用外部 runtime。
- `user-level-capability-receipt-rollback-redaction` - 模式 `live-executed` 表示 receipt/rollback/redaction path 已运行；副作用 `none` 表示未调用外部 runtime。
- `worktree-receipt-claim-lifecycle` - 模式 `live-executed` 表示 worktree receipt/claim path 已运行；副作用 `none` 表示未调用外部 runtime。

## 缺少目标时 blocked 的敏感 lane

- `codex-harnesses-governance` - 模式 `blocked` 表示缺少目标证据，因此未启动副作用族 `harness_job`。
- `spec-kit-authority-guard` - 模式 `blocked` 表示缺少目标证据，因此未启动副作用族 `spec_kit_apply`。
- `spec-kit-subordinate-adapter-governance` - 模式 `blocked` 表示缺少目标证据，因此未启动副作用族 `spec_kit_apply`。
- `stop-slop-caveman-response-density-runtime` - 模式 `blocked` 表示缺少目标证据，因此未启动副作用族 `user_level_install`。
- `user-level-browser-cli-adapter-boundary` - 模式 `blocked` 表示缺少目标证据，因此未启动副作用族 `browser_gui`。
- `user-level-cli-anything-wxwork-cli-governance` - 模式 `blocked` 表示缺少目标证据，因此未启动副作用族 `external_message`。
- `user-level-mcp-skills-cli-runtime` - 模式 `blocked` 表示缺少目标证据，因此未启动副作用族 `user_level_install`。

## 安全姿态

Stage C 默认批处理没有执行 browser/GUI、外部消息、harness job、用户级安装、Spec Kit apply 或远程发布变更。敏感 lane 在提供当前环境目标与授权前，通过 checker 接受的 blocked receipt 保持默认可执行且 fail-closed。

## 模板同步证据

- 命令：`python tools/r6_live_runtime.py sync-templates --root . --general-root D:/PythonProject_General --general2-root D:/PythonProject_General_2 --update-managed --json`。
- General 完整模板目标 hash `328f348e55364ea2`：复制 0，更新 5，跳过既有 0。
- General_2 stub 目标 hash `7a9bf480ab6da20f`：复制 0，更新 1，跳过既有 2。
- 同步 receipt 报告 `remote_publication_mutated=false`，表示没有变更远程 ref/MR/mirror；并报告 `redaction_status=pass`，表示目标路径只以 hash 形式记录。
