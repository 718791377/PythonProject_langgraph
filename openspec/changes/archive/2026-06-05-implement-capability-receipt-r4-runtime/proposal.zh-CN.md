# 变更：实现 R4 Capability Receipt Runtime 治理

## 为什么

用户级 capability receipt 方案存在明确的 Stage D 缺口：后续 runtime lanes 需要可复用的 receipt validation，以覆盖 install/update/smoke/live/cleanup/rollback evidence。现有 helper 已覆盖 authorization 与 R3 风格 update/install receipts，但尚不能校验包含 bounded read-only smoke evidence、timeout release、rollback readiness 与 transcript redaction 的 R4 `smoke-tested` receipt。

## 变更内容

- 在 `tools/user_level_receipt_governance.py` 中增加 R4 smoke receipt validation，但不运行任何真实用户级命令。
- 增加 rollback receipt validation，用于校验 dry-run/apply evidence，但不执行 rollback commands。
- 扩展 receipt templates 与 tests，使后续 runtime lanes 能在任何 R5 live handoff 前产出 sanitized `smoke-tested` evidence。
- 更新 OpenSpec delta 与 stable governance spec，反映已实现的 R4 helper contract；implementation-plan 文件归属保留给既有 plan-maintenance worktree。

## 范围

- `tools/user_level_receipt_governance.py` - 增加只读 R4 smoke 与 rollback receipt validation 的 receipt governance helper。
- `test/user_level_receipt_governance.test.py` - 覆盖 smoke、rollback 与 template behavior 的聚焦回归测试。
- `openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md` 和 `.zh-CN.md` - archive 阶段更新的稳定治理规范。
- 本 OpenSpec change package - R4 package 的 proposal、design、tasks、management 与 delta spec 证据。

## 非目标

- 不安装、更新、启动、smoke 或 live-run 任何真实用户级 MCP、browser、CLI、WXWork、Pi、oh-my-pi 或 harness runtime。
- 不执行 R5 live handoff、browser actions、cookie reads、external message sends 或 sensitive MCP calls。
- 不修改用户级 Codex configuration、browser profiles、MCP Router state 或 remote Git refs。

## Rollout

1. 创建本 OpenSpec package 与 local worktree claim。
2. 增加失败的 R4 smoke/rollback receipt tests。
3. 实现 helper validation 与 sanitized summaries。
4. 更新 plan evidence 与 delta spec。
5. 运行 focused tests、OpenSpec validation、repository guard、local gate 与 local MR review。
6. 归档 change，并把已验证 package 合入本地 `main`。

## Rollback

- revert feature commit 或 local `main` merge commit。
- 如果 local `main` 已移动，使用 local integration helper 创建的 rollback ref。
- 本 slice 不修改任何 external user-level runtime state。

## 验证

- `python test/user_level_receipt_governance.test.py` - 运行 focused receipt governance regression suite。
- `openspec validate implement-capability-receipt-r4-runtime --strict` - archive 前校验 active OpenSpec change。
- `python tools/check_precommit_update_archive.py --root . --json` - commit 前检查 update/archive readiness。
- `python tools/run_openspec_guard.py --root .` - 运行 repository OpenSpec aggregate guard。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行 shared local CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - local main integration 前运行 local MR review。
