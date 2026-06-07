---
change: implement-r5-runtime-governance-batch-20260607
status: active
x_change_class: code
---

# Implement R5 Runtime Governance Batch

## Why

The repository already has R4 local checker and dry-run/runtime-smoke packages for multiple user-level orchestration plans, but the R5 boundary remains uneven: some lanes describe active-candidate or bounded-live handoff in documentation without a shared, checker-backed receipt schema for authorization, owner leases, target/action allowlists, transcript redaction, rollback, timeout release, cleanup, and no-remote-mutation evidence.

## What

Implement the requested R5 batch in the conflict-priority order:

1. Comet/OpenSpec/Superpowers governed foundation surfaces:
   - user-level capability receipt / rollback / redaction
   - worktree receipt / claim lifecycle
   - repo-local selector ownership
   - durable capability readiness projection
   - LangGraph state release evidence
   - durable smoke adoption gate template
2. user-level MCP / Browser / WXWork CLI runtime handoff receipts.
3. gstack / harness runtime safety / Stop-Slop-Caveman runtime gates.
4. Spec Kit authority and subordinate adapter guard receipts.

## Scope

In scope:
- repo-local scripts, checkers, tests, implementation-plan status updates, and OpenSpec specs for R5 receipt validation;
- local fixture-backed active-candidate receipts and fail-closed validation;
- exact no-remote-publication and no-user-level-mutation boundaries unless a receipt explicitly and safely permits only the intended local R5 handoff.

Out of scope:
- remote publication;
- force-push, remote ref deletion, GitLab MR mutation, GitHub sync;
- real sensitive live actions without scoped receipts;
- replacing Comet/OpenSpec/Superpowers authority with gstack, harnesses, or Spec Kit.

## Success Criteria

- Each named plan has an R5 implementation status and a fresh local commit in the feature branch.
- Positive R5 receipts require authorization, owner lease, allowlist, timeout release, redaction, rollback, cleanup, and no remote mutation evidence.
- Blocked or dry-run receipts are accepted only as blocked/dry-run evidence and do not count as active-candidate success.
- Focused tests and repository guard paths pass before local-main integration.
