# codex-user-level-response-density-runtime Specification

## Purpose
TBD - created by archiving change implement-stop-slop-caveman-response-density-r4. Update Purpose after archive.
## Requirements
### Requirement: Stop-Slop/Caveman response density runtime SHALL be guarded and local
The repository SHALL provide a repo-local Stop-Slop/Caveman response density checker and runtime without installing upstream tools, mutating user-level configuration, enabling hooks, or activating always-on compression.

#### Scenario: Analyze reports diagnostics without mutation
- **WHEN** the operator runs the response-density runtime in analyze mode on explicit text or a file
- **THEN** the runtime SHALL return JSON diagnostics
- **AND** it SHALL NOT rewrite or write input.

#### Scenario: Rewrite preserves protected spans
- **WHEN** the operator runs rewrite dry-run or confirmed apply on explicit input
- **THEN** the runtime SHALL preserve code fences, inline code, URLs, paths, CLI arguments, schema keys, OpenSpec/evidence/blocker tokens, `Routing trace`, and `Updated Plan`
- **AND** dry-run SHALL NOT write files
- **AND** apply SHALL require operator confirmation.

#### Scenario: R4 smoke evidence stays bounded
- **WHEN** R4 smoke evidence is recorded or checked
- **THEN** missing R3 install evidence SHALL produce blocked/non-smoke-tested evidence
- **AND** only safe help, status, or dry-run rewrite smoke receipts with timeout release, rollback readiness, and redaction evidence SHALL count as positive smoke-tested evidence
- **AND** write, live, sensitive, user-level mutation, raw private path, or secret markers SHALL fail closed.
