# Design: Project MOE GUI Plan Structure Refresh

## Decision

Use the newer Pi sidecar implementation-plan structure as the organizing pattern, not as a content source. The MOE plan keeps its own domain content and becomes easier to implement by making each contract and gate explicit.

## Target Structure

1. Review conclusion
2. Relationship model and naming boundary
3. Goals and non-goals
4. Runtime architecture
5. Codex / GUI / target-project usage
6. Repo-local source of truth
7. Target-project install artifacts and receipt
8. Phase 1 CLI / readiness contract
9. Phase 2 PySide6 GUI contract
10. JSON contract and state model
11. Safety, privacy, rollback, and uninstall
12. Ready / Bootstrap / Repair lane gates
13. Implementation task breakdown
14. Verification plan
15. Governance and companion document updates
16. Risks and default decisions
17. Self-check checklist
18. References

## Constraints

- Keep `status: draft`; this is not a claim that all runtime capability is complete.
- Add `plan_readiness` metadata to distinguish structural readiness from runtime completion.
- Preserve Project MOE boundaries: repo-local agent TOML, target-project private prompt source, no cross-project default scan, no direct JSON edits from GUI, no remote publication without explicit approval.
- Current Windows shell lacks bash, so Comet state scripts are not claimed as executed.
