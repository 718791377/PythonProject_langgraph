# Project MOE Mode CLI Timeout Stability Design

Status: active
Change: stabilize-project-moe-mode-cli-timeout-20260624

## Problem

Full Project MOE GUI test execution can exceed the previous hard-coded 20 second Mode CLI subprocess timeout on loaded Windows hosts even when focused reruns pass. The false timeout blocks unrelated local-main integrations.

## Approach

Use a bounded 60 second default and a local environment override named `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS`. Apply the same calculation in the shared toolchain read runner and GUI shell write/readback runner.

## Acceptance Evidence

- Tests observe explicit env override in `toolchain.run_cli()`.
- Tests observe default budget headroom in `toolchain.run_cli()`.
- Tests observe every GUI write/readback subprocess call using the same explicit env budget.
- Full Project MOE GUI toolchain test file passes.
