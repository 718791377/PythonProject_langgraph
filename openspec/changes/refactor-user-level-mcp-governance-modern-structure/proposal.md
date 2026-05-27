# Proposal: Refactor user-level MCP/skills/browser/CLI governance plan to the modern structure

## Why

The target implementation plan already has complete Comet metadata, but its body still reads like an older long checklist. The operator asked to refactor it to the newer structure used by the Pi sidecar plan and the Comet runtime agile focus-area plan. The document should therefore expose relationship boundaries, runtime architecture, repo-local source of truth, receipts, state contracts, management records, phase gates, implementation slices, task backlog, local integration order, acceptance criteria, evidence, and risks in a consistent order.

## What

- Reorganize the Chinese plan into the modern implementation-plan structure used by `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` and `comet_runtime_agile_focus_area_plan.zh-CN.md`.
- Synchronize the English companion with the same structure.
- Preserve existing governance content for `skills2cli`, `mcp2cli`, browser automation, `chrome-devtools-mcp`, CDP Bridge, OpenCLI, CLI-Anything, `wecom-cli`, token/risk priority, port registry, authorization receipts, update receipts, and readiness gates.
- Add explicit Comet runtime state contract, management record template, phase gate matrix, monitoring return semantics, implementation slices, task backlog, and evidence checklist.

## Non-goals

- Do not implement or install user-level wrappers.
- Do not modify `C:\Users\lenovo\.codex` runtime state.
- Do not change live MCP, browser, OpenCLI, CLI-Anything, or WXWork behavior.
- Do not push to GitLab or GitHub.

## Impact

- Documentation-only refactor of the bilingual plan pair.
- New OpenSpec and Superpowers evidence for the complete Comet workflow.
- No runtime side effects.

## Rollback

Rollback by reverting the local feature commit or resetting the feature branch to `{base}` before local integration. User-level runtime state is not changed.
