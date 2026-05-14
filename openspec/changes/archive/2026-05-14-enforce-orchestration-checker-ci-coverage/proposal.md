---
change_id: enforce-orchestration-checker-ci-coverage
status: proposed
---

# Enforce orchestration checker CI coverage

## Why

Some automatic orchestration enforcement checkers and their tests already exist, but not every checker/test is wired into the shared local/remote gate. This leaves gaps where policy surfaces mention script-backed enforcement while the shared CI path does not execute the corresponding checker or unit tests.

## What changes

- Add the missing orchestration checker unit tests to `tools/ci/ci_test_manifest.json`.
- Run the no-input capability-switch checker from `tools/run_openspec_guard.py`.
- Update the safety-rule registry so capability-chain guard linkage is explicit.
- Make official OpenSpec verification output UTF-8-safe when pending changes emit non-ASCII validation symbols.

## Scope

In scope: guard/test wiring and registry evidence for existing checkers.
Out of scope: changing routing policy semantics, launching durable teams, or modifying user-level runtime state.
