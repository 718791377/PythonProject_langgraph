# Comet Management Record (zh-CN companion)

## Open / Initiating
- [x] Value / why is stated for the archive package.
- [x] Success criteria are stated for removing the completed change from the active OpenSpec set.
- [x] Stakeholders and constraints are identified for local-main-first integration.

## Design / Planning
- [x] Delivery tailoring is recorded for a documentation-only archive package.
- [x] Risks and assumptions are recorded, including the stable-spec sync skip decision.
- [x] Acceptance evidence path is defined through repository checkers and local gates.

## Build / Executing
- [x] Execution mode is selected: `executing-plans` in an isolated worktree.
- [x] Quality evidence is recorded through OpenSpec validation, archive review, local gate, and local MR review.
- [x] Current blockers are cleared or serialized before local `main` integration.

## Verify / Controlling
- [x] Variance review is complete.
- [x] Risk/change impact is assessed.
- [x] Control decision is `continue`; this means verification evidence supports archive progress and no earlier Comet phase return is needed.

## Archive / Closing
- [x] Value outcome is summarized.
  - Outcome: the completed structure-refactor change is removed from the active OpenSpec set and retained under the dated archive path.
- [x] Lessons learned or reusable guidance are recorded.
  - Lesson: do not overwrite the current stable MCP/skills/browser/CLI specification with an older narrow delta when the stable spec already carries broader current coverage.
- [x] Delta spec sync, verification evidence, and archive path are confirmed.
  - Stable-spec sync decision: skipped, because `openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md` already preserves broader current MCP/skills/browser/CLI governance requirements.
  - Verification evidence: the Phase 7 archive package refreshes OpenSpec validation, precommit archive review, local gate, and local MR review before local `main` integration.
  - Archive path: `openspec/changes/archive/2026-06-03-refactor-user-level-mcp-governance-modern-structure/`.

## Monitoring Loop
- [x] Current phase facts are checked.
- [x] Continue, adjust, stop, or return decision is made.
- [x] No return is required for this documentation-only archive; `monitoring_status=clear` means the monitoring loop has no blocked or undecided return work, and `control_decision=continue` means the archive may proceed without returning to an earlier Comet phase.
