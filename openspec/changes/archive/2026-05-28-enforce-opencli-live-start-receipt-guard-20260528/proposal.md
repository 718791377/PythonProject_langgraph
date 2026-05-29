# Proposal: Enforce OpenCLI live-start receipt and owner evidence guard

## Why

The user-level MCP, skills, browser, and CLI governance plan still had an unchecked Task 5 item: live OpenCLI start requires install receipt and owner evidence. The existing repo-local OpenCLI guard checked target actions, on-demand mode, browser-owner leases, authorization receipts, and `--port auto` lease evidence, but it did not model the live-start preflight itself.

## What

- Extend `tools/opencli_governance.py` with a non-mutating `start` preflight command.
- Require a valid OpenCLI install/update receipt before live-start can proceed.
- Require active browser-owner lease evidence and sanitized `codex-port --port auto` lease evidence.
- Keep repo-local MVP behavior non-starting: when all evidence is present, fail closed with `live_start_not_implemented_repo_local_mvp`.
- Add unit tests for missing install receipt, missing owner evidence, and complete-evidence deferral.
- Promote the behavior into the stable user-level MCP/skills/browser/CLI governance spec.

## Non-goals

- Do not install, update, or start OpenCLI.
- Do not launch browsers or connect to browser targets.
- Do not mutate `C:\Users\lenovo\.codex`.
- Do not read cookies, execute JavaScript, click, type, navigate, or touch human-owned browser assets.
- Do not push remote branches or open remote MRs.

## Rollback

Rollback by reverting this local feature commit or resetting local `main` to the rollback ref created before integration. No user-level runtime state is changed.
