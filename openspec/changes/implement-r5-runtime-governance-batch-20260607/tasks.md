---
change: implement-r5-runtime-governance-batch-20260607
status: active
---

# Tasks

## Foundation family

- [x] Add generic R5 active-candidate receipt validation tests and implementation.
- [x] Add worktree receipt lifecycle R5 evidence tests and implementation.
- [x] Tighten repo-local selector R5 active-candidate ownership checks.
- [x] Tighten durable readiness projection and LangGraph release evidence for R5 close/handoff.
- [x] Add durable smoke adoption R5 apply-gate receipt template/checks.
- [ ] Commit each foundation plan result locally.

## User-level CLI family

- [x] Add MCP/skills CLI R5 handoff receipt tests and implementation.
- [x] Add Browser/CLI adapter R5 sensitive action receipt tests and implementation.
- [x] Add WXWork_CLI R5 send/action receipt tests and implementation.
- [ ] Commit each CLI-family plan result locally.

## Delivery and harness family

- [x] Add Stop-Slop/Caveman R5 active-candidate hook/compression receipt checks.
- [x] Add gstack R5 active-candidate delivery-loop receipt checks.
- [x] Add Codex harness R5 bounded job receipt checks.
- [ ] Commit each delivery/harness plan result locally.

## Spec Kit family

- [x] Add Spec Kit authority guard R5 subordinate receipt checks.
- [x] Add Spec Kit subordinate adapter runtime R5 blocked/subordinate receipt checks.
- [ ] Commit each Spec Kit plan result locally.

## Verification and integration

- [ ] Run focused tests and affected checkers.
- [ ] Run OpenSpec validation/guard and precommit update/archive review.
- [ ] Archive the OpenSpec change in the same integration package if ready.
- [ ] Run local gate and local MR review.
- [ ] Merge into local `main` using the guarded helper and stop at remote-publication gate.
