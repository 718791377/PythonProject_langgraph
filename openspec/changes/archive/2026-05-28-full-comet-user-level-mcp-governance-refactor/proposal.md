# Proposal: Full Comet refactor of user-level MCP/skills/browser/CLI governance plan

## Why

The Chinese implementation plan currently carries a Comet tweak framing even though the operator explicitly requested a complete `/comet` refactor. The document should reflect the complete Open -> Design -> Build -> Verify -> Archive flow so future user-level MCP, skills, browser, and CLI harness governance work has phase evidence, rollback boundaries, and archive/deferral rules.

## What

- Reframe `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` from tweak-only Comet wording to the full `/comet` phase model.
- Preserve the existing governance scope: `skills2cli`, `mcp2cli`, browser automation, `chrome-devtools-mcp`, CDP Bridge, OpenCLI, CLI-Anything, and `wecom-cli`.
- Add explicit Open/Design/Build/Verify/Archive evidence requirements, phase gates, implementation order, verification rules, and archive/deferral status expectations.
- Keep `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` as the local Codex governance fork reference for Pi/oh-my-pi sidecar matters.

## Non-goals

- Do not install or update user-level wrappers.
- Do not mutate `C:\Users\lenovo\.codex` runtime state.
- Do not push GitLab/GitHub or create remote MRs.
- Do not implement new live browser, MCP, OpenCLI, CLI-Anything, or WXWork behavior.

## Impact

- Primary documentation impact: one Chinese implementation plan.
- Governance evidence impact: this OpenSpec change, Superpowers design doc, Superpowers plan, and verification report.
- Runtime impact: none.

## Rollback

Rollback by reverting the local feature commit or resetting the feature branch to `ab5e1c1c3e2f9fd01dc5af5eb30e9d6c5267f802` before integration. No user-level runtime state is changed.
