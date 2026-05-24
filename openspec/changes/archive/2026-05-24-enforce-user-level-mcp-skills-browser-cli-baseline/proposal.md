# Proposal: enforce user-level MCP skills browser CLI baseline

## Why

The user-level MCP, skills, browser automation, and CLI harness governance plan is now execution-ready, but its first baseline slice must be script-backed before any helper can become active. Without a checker, future work could mark high-token or high-risk surfaces as default, omit authorization receipts, or record unsafe runtime evidence.

## What changes

- Add a repository checker for the user-level MCP/skills/browser/CLI baseline surfaces.
- Require the bilingual plan and OpenSpec surfaces to preserve token/risk priority, sensitive authorization receipt fields, update receipt fields, and evidence redaction rules.
- Register the checker in OpenSpec guard, CI manifest, and safety-rule backing registry.
- Add regression coverage for passing repository surfaces and fail-closed missing authorization/spec evidence.
- Update the implementation plan checklist to mark the first baseline items complete.

## Safety

The checker is read-only. It validates repository-owned documentation, OpenSpec specs, and guard registration only. It does not install user-level tools, inspect browser profiles, read secrets, call MCP endpoints, or mutate user-level runtime state.
