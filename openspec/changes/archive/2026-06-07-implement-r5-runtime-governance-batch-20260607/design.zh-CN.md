---
change: implement-r5-runtime-governance-batch-20260607
status: archived
translation_of: openspec/changes/archive/2026-06-07-implement-r5-runtime-governance-batch-20260607/design.md
---

# 设计：R5 Runtime Governance Batch

## 权威顺序

所有 runtime handoff gates 都必须保持以下顺序：

`Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`

Comet 和 OpenSpec 保持 WHAT/change lifecycle authority，Superpowers 保持 HOW discipline。gstack 只能在这些门禁通过后补充 delivery-loop guidance。Harness runtime safety 可进一步限制执行。Spec Kit 保持 subordinate，不能在没有单独批准 migration plan 的情况下创建 `.specify/`、root `specs/`、`/speckit.*` 或 `$speckit-*` 这类 repository authority surfaces。

## R5 Receipt Model

在 `tools/user_level_receipt_governance.py` 中增加 generic active-candidate receipt validator，并由 lane-specific checkers 复用。Positive R5 receipt 必须包含 `runtime_stage`、operator authorization receipt、owner lease、target/action allowlist、redacted transcript、timeout release、cleanup evidence、rollback pointer/readiness、no remote-publication mutation evidence 和 lane-specific authority decision。Blocked 或 dry-run receipts 可以作为 blocked/dry-run evidence，但不能计为 R5 active-candidate success。

## Family Slices

1. Foundation：generic receipt validation、worktree receipt lifecycle R5 fields、selector ownership、capability readiness projection、LangGraph release evidence 和 durable smoke adoption receipt templates。
2. CLI adapter family：MCP/skills、Browser/OpenCLI/CDP 和 WXWork_CLI receipts。
3. Delivery/harness family：Stop-Slop/Caveman、gstack 和 Codex harness bounded-live receipts。
4. Spec Kit family：authority guard 和 subordinate adapter receipts。

## Validation Strategy

每个 slice 按 TDD 执行：先加失败的 fixture/unit test，再实现最小验证逻辑，然后重跑 focused tests 和 affected checker，并在继续下一个 plan 前提交该 slice。

## Safety Boundaries

本 batch 不执行真实 user-level install/start/send/browser/GUI/MCP action；未来任何 live R5 action 都必须先提供当前 scoped receipt。Remote publication 仍然未授权。
