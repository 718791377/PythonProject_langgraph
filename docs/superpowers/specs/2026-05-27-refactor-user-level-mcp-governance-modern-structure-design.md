---
change: refactor-user-level-mcp-governance-modern-structure
status: implemented
created_at: 2026-05-27
---

# Modern Structure Design for User-Level MCP/Skills/Browser/CLI Governance

## Context

The target plan needs to align with the newer plan family represented by the Pi sidecar plan and the Comet runtime agile focus-area plan. The refactor is structural and must preserve all governance markers required by repository checkers.

## Selected approach

Use a complete Comet documentation refactor. Rebuild the bilingual plan pair around relationship boundaries, runtime architecture, repo-local source of truth, receipts, state contracts, management record, phase gates, slices, task backlog, local integration, acceptance, evidence, rollback, and risks.

## Rejected alternatives

- Metadata-only update: insufficient because the body would still be legacy-shaped.
- Runtime implementation: out of scope and unsafe without lane-specific OpenSpec changes and user-level receipts.
- Remote publication: out of scope for local documentation integration.

## Verification design

Run the document pair checker, implementation-plan checker, MCP/skills/browser/CLI baseline checker, precommit update/archive review, OpenSpec guard, local gate, and local MR review.
