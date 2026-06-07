---
change: implement-r5-runtime-governance-batch-20260607
status: active
x_change_class: code
translation_of: openspec/changes/implement-r5-runtime-governance-batch-20260607/proposal.md
---

# 实施 R5 Runtime Governance Batch

## Why

仓库已经为多个用户级编排方案具备 R4 local checker 和 dry-run/runtime-smoke package，但 R5 边界仍不一致。部分 lane 在文档中描述 active-candidate 或 bounded-live handoff，但缺少共享的 checker-backed receipt schema，用于 authorization、owner lease、target/action allowlist、transcript redaction、rollback、timeout release、cleanup 和 no-remote-mutation evidence。

## What

按冲突优先级实施 R5 batch：

1. Comet/OpenSpec/Superpowers 治理的 foundation surfaces：capability receipt/rollback/redaction、worktree receipt/claim lifecycle、repo-local selector ownership、durable readiness projection、LangGraph release evidence 和 durable smoke adoption gate template。
2. user-level MCP / Browser / WXWork CLI runtime handoff receipts。
3. gstack / harness runtime safety / Stop-Slop-Caveman runtime gates。
4. Spec Kit authority 和 subordinate adapter guard receipts。

## Scope

范围内：repo-local scripts、checkers、tests、implementation-plan status updates 和 OpenSpec specs，用于 R5 receipt validation；fixture-backed active-candidate receipts 和 fail-closed validation。

范围外：remote publication、force-push、remote ref deletion、GitLab MR mutation、GitHub sync、没有 scoped receipts 的真实敏感 live actions，以及用 gstack/harness/Spec Kit 取代 Comet/OpenSpec/Superpowers authority。

## Success Criteria

- 每个命名 plan 都具有 R5 implementation status 和 feature branch 中的本地 commit。
- Positive R5 receipts 需要 authorization、owner lease、allowlist、timeout release、redaction、rollback、cleanup 和 no remote mutation evidence。
- Blocked 或 dry-run receipts 只能作为 blocked/dry-run evidence，不计为 active-candidate success。
- local-main integration 前 focused tests 和 repository guard paths 必须通过。
