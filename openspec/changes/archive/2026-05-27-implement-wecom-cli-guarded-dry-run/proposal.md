# Change: Implement WeCom CLI Guarded Dry-Run Governance

## Why
The user-level MCP/skills/browser/CLI governance plan still listed `wecom-cli` as planned. Enterprise WeChat / WeCom / WXWork automation is sensitive because GUI attachment can expose messages, contacts, tokens, or human-owned desktop state.

## What Changes
- Add a repo-local `tools/wecom_cli_governance.py` guard.
- Add fixture tests for API/Webhook-first posture, GUI dry-run planning, missing-receipt fail-closed behavior, and valid-receipt dry-run dispatch eligibility.
- Register the test in the shared CI manifest and require it through the baseline checker.
- Update the bilingual implementation plan and stable specification to mark `wecom-cli` as implemented-local only, not active user-level automation.

## Impact
- No live `WXWork.exe` process is probed or controlled.
- No user-level Codex configuration is changed.
- No remote publication is performed.
