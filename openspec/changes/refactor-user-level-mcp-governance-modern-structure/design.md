# Design: Modern structure for user-level MCP/skills/browser/CLI governance

## Summary

This design converts the target plan from a lane-by-lane legacy checklist into the newer implementation-plan structure used by the Pi sidecar and Comet runtime plans. The refactor is documentation-only and keeps all existing governance semantics intact.

## Selected structure

1. Review verdict.
2. Relationship model and naming boundary.
3. Goals and non-goals.
4. Runtime architecture and Codex usage model.
5. Repo-local source of truth.
6. User-level artifacts and receipt contracts.
7. Token/risk, port, authorization, update, and redaction governance.
8. Capability lane contracts for `skills2cli`, `mcp2cli`, browser automation, `chrome-devtools-mcp`, CDP Bridge, OpenCLI, CLI-Anything, and `wecom-cli`.
9. Comet runtime state, management record, phase gates, and monitoring returns.
10. Implementation slices, task-level backlog, local integration order, acceptance criteria, evidence, rollback, and risks.

## Decisions

- Preserve implementation-state truth: repo-local helpers and guards may be implemented, but user-level lanes remain inactive until wrapper, smoke, receipt, and rollback evidence exist.
- Keep Pi sidecar details delegated to `pi_plugin_codex_user_level_sidecar_plan.*`.
- Keep Comet runtime governance explicit so future slices can decide whether to proceed, return to an earlier phase, defer archive, or open a new change.
- Keep local-main-first and remote publication out of this change.

## Risks and mitigations

- Risk: structural rewrite may drop old required markers. Mitigation: keep explicit checker markers and run the baseline checker.
- Risk: broad plan could imply runtime installation. Mitigation: restate non-goals and readiness gates.
- Risk: previous completed active OpenSpec changes remain active. Mitigation: this change carries explicit archive deferral and leaves broader archive cleanup to a separate integration decision.

## Acceptance

- The bilingual plan pair follows the newer Pi sidecar / Comet runtime structure.
- Existing lane semantics and checker markers remain present.
- OpenSpec validation, baseline checker, document pair policy, precommit archive review, OpenSpec guard, local gate, and local MR review pass.
