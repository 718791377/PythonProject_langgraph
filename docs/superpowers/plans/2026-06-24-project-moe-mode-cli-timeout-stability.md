# Project MOE Mode CLI Timeout Stability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize Project MOE GUI Mode CLI subprocess timeout behavior under full-suite Windows load.

**Architecture:** Keep timeout handling local to the two existing runner modules. Use one env var contract and bounded fallback behavior.

**Tech Stack:** Python stdlib, `unittest`, subprocess timeout handling, OpenSpec.

---

---
change: stabilize-project-moe-mode-cli-timeout-20260624
design-doc: docs/superpowers/specs/2026-06-24-project-moe-mode-cli-timeout-stability-design.md
base-ref: a471e993b05e0fe6b70530c6cfc1463230784406
---

## File Structure

- Modify `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`: add `DEFAULT_MODE_CLI_TIMEOUT_SECONDS`, `MODE_CLI_TIMEOUT_ENV`, and `mode_cli_timeout_seconds()`; use it in `run_cli()`.
- Modify `tools/project_moe_gui_toolchain/src/project_moe_gui/gui_shell.py`: add the same timeout helper and use it in `run_cli_json()`.
- Modify `test/project_moe_gui_toolchain.test.py`: add regression tests for explicit env override, default headroom, write/readback consistency, and the default GUI write/readback budget.
- Add `openspec/changes/stabilize-project-moe-mode-cli-timeout-20260624/`: record proposal, design, spec, tasks, and management evidence.

## Tasks

### Task 1: Prove configurable read timeout

- [x] Add `test_mode_cli_read_contract_timeout_is_configurable_for_loaded_hosts` to patch `project_moe_gui.toolchain.subprocess.run`, set `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS=45`, and assert `timeout == 45.0`.
- [x] Add `test_mode_cli_default_timeout_has_full_suite_headroom` to clear the env var and assert the default observed timeout is at least `45.0`.

### Task 2: Implement shared read timeout helper

- [x] Add `DEFAULT_MODE_CLI_TIMEOUT_SECONDS = 60.0` and `MODE_CLI_TIMEOUT_ENV = "PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS"` to `toolchain.py`.
- [x] Add `mode_cli_timeout_seconds()` to parse a positive float override and otherwise return the default.
- [x] Replace `timeout=20` in `toolchain.run_cli()` with `timeout=mode_cli_timeout_seconds()`.

### Task 3: Prove GUI write/readback consistency

- [x] Add `test_gui_write_readback_timeout_uses_shared_environment_budget` to patch `project_moe_gui.gui_shell.subprocess.run`, perform `execute_write_action_with_readback(...)`, and assert all write/readback subprocess calls use `45.0` when the environment override is set.
- [x] Add `test_gui_write_readback_default_timeout_has_full_suite_headroom` to prove the no-override GUI write/readback path uses the 60 second default instead of the old 20 second fallback.

### Task 4: Implement GUI shell timeout helper

- [x] Add the same constants and helper to `gui_shell.py`.
- [x] Replace `timeout=timeout` in `run_cli_json()` with `timeout=mode_cli_timeout_seconds(timeout)`.
- [x] Change GUI runner default timeout arguments to `None` so default write/readback paths use `DEFAULT_MODE_CLI_TIMEOUT_SECONDS` rather than the previous 20 second call-site fallback.

### Task 5: Verify and integrate

- [x] Run focused timeout tests.
- [x] Run the full Project MOE GUI toolchain test file.
- [x] Run OpenSpec validation, precommit update/archive review, repository guard, local gate, and local MR review.
- [x] Integrate through the local-main helper and stop before remote publication.
