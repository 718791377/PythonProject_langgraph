# Design: Enforce OpenCLI live-start receipt guard

## Problem

Task 5 in the user-level MCP/skills/browser/CLI governance plan requires live starts to have install receipt and owner evidence. OpenCLI already had target-action gates, but no repo-local live-start preflight.

## Decision

Add `opencli_governance.py start` as a non-mutating preflight:

- require `--port auto` plus sanitized codex-port lease evidence;
- require active browser-owner lease evidence for the target and session;
- require OpenCLI install/update receipt evidence;
- return `live_start_not_implemented_repo_local_mvp` after complete evidence because repo-local code must not start OpenCLI.

## Safety

The guard never installs OpenCLI, starts OpenCLI, launches browsers, connects to browser targets, reads cookies, executes JavaScript, clicks, types, navigates, or mutates user-level Codex configuration.

## Acceptance

Acceptance is unit-test evidence plus OpenSpec guard, local gate, local MR review, and local-main integration.
