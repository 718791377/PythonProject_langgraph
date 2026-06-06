# 变更：实现 Durable Capability Readiness R4 运行时刷新

## 为什么
readiness projection 已经区分 `installed`、`enabled`、`selected`、`ready`，但 `codex-durable-state-status.ps1` 还没有持久化显式 smoke-tested repo-local projection receipt。

## 变更内容
- 为 `codex-durable-state-status.ps1` 增加显式 `-RefreshReadiness`。
- 保持默认 status 只读且无 mutation。
- 只有显式 refresh 才写 `.omx/state/readiness/durable-capability-readiness-projection.json`。
- 记录来源、selector、安装/版本证据、blockers 与非 adoption 布尔值。

## 非目标
- 不安装或升级 LangGraph。
- 不启动 native_omx、LangGraph 或 persistent team。
- 不推送或修改远端 refs。

## 验证
- `python .\test\check_capability_switch_chain.test.py` - 验证 capability readiness receipt checker 的单元覆盖。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1` - 验证生成的 status helper、默认只读行为与显式 refresh receipt 写入路径。
- `python tools/check_capability_switch_chain.py --root . --json` - 校验当前 user-level capability switch chain 以及可选 readiness projection evidence。
- `python tools/run_openspec_guard.py --root .` - 运行仓库 OpenSpec 与治理 guard 套件。
- local gate 与 local MR review 后再本地集成。
