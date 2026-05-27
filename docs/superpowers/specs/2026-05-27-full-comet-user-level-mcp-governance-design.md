---
change: full-comet-user-level-mcp-governance-refactor
status: implemented
created_at: 2026-05-27
---

# Full Comet User-Level MCP/Skills/Browser/CLI Governance Design

## Context

The existing Chinese governance plan already covers user-level `skills2cli`, `mcp2cli`, browser automation, `chrome-devtools-mcp`, CDP Bridge, OpenCLI, CLI-Anything, and `wecom-cli` boundaries. The gap is that its Comet framing still says the plan is a lightweight tweak, which conflicts with the operator's explicit full `/comet` request.

## Design alternatives

1. **Minimal metadata edit.** Change only frontmatter from tweak to full. This is fast but leaves section-level evidence inconsistent.
2. **Full document phase refactor.** Update frontmatter, Section 0.1, implementation split, implementation order, and verification plan to use complete Comet phases. This is the selected approach because it gives future sessions executable evidence.
3. **Runtime implementation expansion.** Implement wrappers or user-level installs now. This is rejected because it expands beyond a document-governance refactor and would need separate OpenSpec slices.

## Selected approach

Use a documentation-only full Comet refactor. The document keeps existing lane scope and readiness gates, but every lane is now framed through Open, Design, Build, Verify, and Archive evidence. The change does not alter user-level runtime state.

## Boundaries

- Repo source of truth stays in this repository.
- User-level installed artifacts remain future install outputs with receipts.
- Pi/oh-my-pi sidecar details remain governed by `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`.
- No remote publication is performed by this change.

## Verification design

Verification is evidence-based: target document diff, OpenSpec validation, implementation-plan rules, MCP/skills/browser/CLI baseline checker, precommit update/archive review, aggregate OpenSpec guard, local gate, and local MR review.
