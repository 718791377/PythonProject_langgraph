---
change: implement-r5-runtime-governance-batch-20260607
status: active-verification-evidence
translation_of: docs/superpowers/reports/2026-06-07-r5-runtime-governance-verification.md
---

# R5 Runtime Governance 验证报告

## 范围

本报告记录 R5 检查器支撑的 active-candidate receipt package 的本地验证。它不声称已执行任何真实敏感 live action。

## 权威与安全边界

- 强制顺序：`Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- Remote publication：未授权且未修改。
- User-level runtime mutation：未执行。
- Browser/GUI/WXWork/MCP/harness/Spec Kit live actions：未执行。
- R5 positive evidence 仅限 fixture-backed active-candidate receipt validation。
- blocked 或 dry-run receipts 仍是诚实的 blocked evidence，不计为 positive R5 active-candidate completion。

## 新鲜 focused 验证证据

英文主文件列出 2026-06-07 在 feature worktree 中运行的 focused commands。这些证据包括 generic receipt governance tests、R5 active-candidate receipt tests、durable routing smoke receipts tests、LangGraph release evidence tests、worktree receipt tests、repo-local selector tests、capability switch chain tests 和 safety-rule script-backing check。

## R5 lane coverage

`tools/check_r5_active_candidate_receipts.py` self-test 覆盖 MCP/skills CLI、Browser/CLI adapter、WXWork CLI、Stop-Slop/Caveman、gstack delivery loop、Codex harnesses、Spec Kit authority/subordinate 和 durable routing lanes。每个 lane 都拒绝 remote publication mutation；新增 blocked/dry-run 回归验证确认 `runtime_stage=blocked` 且 `dry_run_only=true` 不会被计为 active-candidate evidence。

## 接受结论

Build-phase R5 receipt/checker work 已准备进入 aggregate repository guard、precommit update/archive review、local CI、local MR review、OpenSpec archive 和 guarded local-main integration。
