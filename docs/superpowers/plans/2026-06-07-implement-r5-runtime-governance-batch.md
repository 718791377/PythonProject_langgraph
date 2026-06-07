---
change: implement-r5-runtime-governance-batch-20260607
design-doc: openspec/changes/implement-r5-runtime-governance-batch-20260607/design.md
status: active
---

# Implementation Plan: R5 Runtime Governance Batch

## Critical Path

1. Foundation receipt/checker model.
2. User-level CLI sensitive-action receipt gates.
3. Delivery/harness R5 gates.
4. Spec Kit subordinate R5 gates.
5. Verification, archive, local-main integration.

## TDD Contract

For each slice, add or update a focused test first, run it to observe failure, implement the minimal checker/runtime change, rerun the focused test, then commit the plan slice.

## Commit Boundaries

One local commit per requested plan whenever practical. Tightly coupled foundation code may share helper implementation but documentation/status updates should keep each plan visible in the commit history.

## Remote Boundary

Do not push, create/update/merge GitLab MR, or sync GitHub in this batch unless a later user message explicitly names remote publication.
