---
change: implement-r5-runtime-governance-batch-20260607
status: archived
translation_of: openspec/changes/archive/2026-06-07-implement-r5-runtime-governance-batch-20260607/tasks.md
---

# 任务

## Foundation family

- [x] 添加 generic R5 active-candidate receipt validation tests 和 implementation。
- [x] 添加 worktree receipt lifecycle R5 evidence tests 和 implementation。
- [x] 加强 repo-local selector R5 active-candidate ownership checks。
- [x] 加强 durable readiness projection 和 LangGraph release evidence，用于 R5 close/handoff。
- [x] 添加 durable smoke adoption R5 apply-gate receipt template/checks。
- [x] 分别提交每个 foundation plan result。

## User-level CLI family

- [x] 添加 MCP/skills CLI R5 handoff receipt tests 和 implementation。
- [x] 添加 Browser/CLI adapter R5 sensitive action receipt tests 和 implementation。
- [x] 添加 WXWork_CLI R5 send/action receipt tests 和 implementation。
- [x] 分别提交每个 CLI-family plan result。

## Delivery and harness family

- [x] 添加 Stop-Slop/Caveman R5 active-candidate hook/compression receipt checks。
- [x] 添加 gstack R5 active-candidate delivery-loop receipt checks。
- [x] 添加 Codex harness R5 bounded job receipt checks。
- [x] 分别提交每个 delivery/harness plan result。

## Spec Kit family

- [x] 添加 Spec Kit authority guard R5 subordinate receipt checks。
- [x] 添加 Spec Kit subordinate adapter runtime R5 blocked/subordinate receipt checks。
- [x] 分别提交每个 Spec Kit plan result。

## Verification and integration

- [x] 运行 focused tests 和 affected checkers。
- [x] 运行 OpenSpec validation/guard 和 precommit update/archive review。
- [x] 如果 ready，则在同一个 integration package 中归档 OpenSpec change。
- [ ] 运行 local gate 和 local MR review。
- [ ] 使用 guarded helper 合入 local `main`，并停在 remote-publication gate。
