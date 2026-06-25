---
archived-with: 2026-06-25-prevent-codex-npm-eperm-cleanup-warning-20260624
translation_of: docs/superpowers/plans/2026-06-24-codex-npm-eperm-update-preflight.md
---
# Codex npm EPERM Update Preflight Implementation Plan (zh-CN companion)

> ?????????????????????????????????? Windows ???????????????????????????????????????????

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent recurring Windows `npm warn cleanup` / `EPERM` ambiguity during Codex official npm updates by adding a fail-closed lock preflight and structured cleanup-warning reporting.

**Architecture:** Extend the existing official update orchestration script instead of wrappers. The update template performs process-lock detection before global npm mutation, classifies cleanup warnings after npm output, and reports leftover staging candidates without deleting them.

**Tech Stack:** PowerShell 5+/7 compatible script, existing fake-command PowerShell regression test, OpenSpec validation, local-main-first integration helpers.

---

## File Structure

- Modify: `tools/codex-official-update-patch-replay-template.ps1`
  - Add parameters: `-AllowLockedCodexUpdate` and test-only fake process inventory support through an environment variable.
  - Add functions for npm root detection, `.codex-*` staging candidate discovery, process inventory, lock-risk evaluation, and npm cleanup-warning classification.
  - Add report fields: `windows_codex_lock_preflight` and `official_update_cleanup_warnings`.
  - Add generated checklist lines for preflight and manual cleanup.
- Modify: `test/codex-official-update-patch-replay-template.test.ps1`
  - Extend fake `npm.cmd` to simulate install success/failure and npm root output.
  - Add fake process inventory environment setup.
  - Assert lock-risk blocking, override, warning classification, and non-deletion of staging directories.
- No new CI manifest entry is required because `codex-official-update-patch-replay-template.test.ps1` is already registered.

## Tasks

### Task 1: Lock preflight report and blocking behavior

**Files:**
- Modify: `tools/codex-official-update-patch-replay-template.ps1`
- Modify: `test/codex-official-update-patch-replay-template.test.ps1`

- [ ] **Step 1: Write failing test for lock-risk blocking**

Add a fake process inventory environment variable in the test with one `codex` process and assert that `-Stage update` fails before fake npm install when no override is used.

Expected failure before implementation: the update stage currently invokes fake npm install instead of failing closed on the fake process.

- [ ] **Step 2: Implement preflight functions and report object**

Add production process enumeration with fake JSON override for tests. Match process names `codex`, `node`, or command/path evidence under the detected global npm `@openai/codex` tree. Return a `windows_codex_lock_preflight` object with `checked`, `lock_risk`, `matched_processes`, `leftover_staging_candidates`, and `recommended_action`.

- [ ] **Step 3: Block npm update before mutation**

Before the existing `Invoke-ExternalCommand` call for `npm install`, throw a clear error if Windows lock risk is detected and `-AllowLockedCodexUpdate` is not supplied. Preserve existing `ShouldProcess` behavior.

- [ ] **Step 4: Verify focused test**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\test\codex-official-update-patch-replay-template.test.ps1
```

Expected: test reaches the new blocking assertion and passes existing stage-gate assertions.

### Task 2: Cleanup warning classification and leftover staging reporting

**Files:**
- Modify: `tools/codex-official-update-patch-replay-template.ps1`
- Modify: `test/codex-official-update-patch-replay-template.test.ps1`

- [ ] **Step 1: Write failing tests for cleanup warning classification**

Make fake `npm.cmd install -g ...` emit `npm warn cleanup`, `EPERM`, `unlink ...codex.exe` and exit `0`. Assert `official_update_cleanup_warnings[0].type == windows_file_lock_eperm` and `official_update.exit_code == 0`.

Also simulate non-zero fake npm install with the same warning and assert the warning classifier does not convert the failed command into success.

- [ ] **Step 2: Implement classifier**

Add a function that inspects combined command output only after npm returns. If exit code is `0` and cleanup/EPERM/unlink/codex.exe markers are present, emit a `windows_file_lock_eperm` warning entry. If exit code is non-zero, preserve existing failure semantics.

- [ ] **Step 3: Report staging candidates without deleting them**

Discover `@openai/.codex-*` directories below the fake or real npm global root and list them in `windows_codex_lock_preflight.leftover_staging_candidates`. Do not call `Remove-Item`.

- [ ] **Step 4: Verify focused test**

Run the same PowerShell test. Assert the fake staging directory still exists after the template run.

### Task 3: Checklist guidance, OpenSpec validation, and local integration

**Files:**
- Modify: `tools/codex-official-update-patch-replay-template.ps1`
- Modify: `openspec/changes/prevent-codex-npm-eperm-cleanup-warning-20260624/tasks.md`
- Modify if needed: `openspec/changes/prevent-codex-npm-eperm-cleanup-warning-20260624/management.md`

- [ ] **Step 1: Update generated checklist text**

Add checklist lines requiring Windows lock preflight review before update and manual cleanup guidance after sessions exit.

- [ ] **Step 2: Mark Stage 2 tasks complete only after evidence exists**

Update the OpenSpec task checklist after focused tests and guard commands pass.

- [ ] **Step 3: Run verification**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\test\codex-official-update-patch-replay-template.test.ps1
python .\tools\run_openspec_guard.py --root .
.\tools\ci\local_gate.ps1 -Root . -StepTimeoutSeconds 3600
.\tools\ci\local_mr_review.ps1
```

Expected: all commands exit `0` with fresh output.

- [ ] **Step 4: Integrate local-main-first**

From the primary root, run the repository local-flow helper with explicit `--root`, `--worktree`, `--branch`, `--stage implementation`, `--implementation-plan`, and long local-gate timeout. Stop before remote publication.

## Self-Review Checklist

- Every added runtime behavior maps to an OpenSpec requirement.
- No task kills processes or deletes `.codex-*` staging directories.
- Non-zero npm update remains failed even when cleanup warnings are classifiable.
- Tests use fake npm/process inventory and do not inspect or mutate real global npm state.
- Local integration is performed from the primary root, not from inside the feature worktree.
