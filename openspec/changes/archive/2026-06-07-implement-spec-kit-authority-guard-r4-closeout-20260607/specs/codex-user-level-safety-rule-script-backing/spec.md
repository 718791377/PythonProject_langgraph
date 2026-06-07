## ADDED Requirements

### Requirement: Spec Kit authority guard SHALL validate generated surfaces and subordinate dry-run receipts

The repository SHALL keep Spec Kit below Comet, OpenSpec, Superpowers, local-main-first gates, and remote-publication gates by enforcing generated-surface and runtime-receipt checks before any Spec Kit surface can be treated as repository evidence.

`tools/check_spec_kit_authority_guard.py` SHALL fail closed on `.specify/`, root `specs/`, generated `.codex/commands/*speckit*`, generated `.codex/skills/*speckit*`, generated `.github/prompts/*speckit*`, `/speckit.*`, `$speckit-*`, extension, preset, and workflow-output surfaces unless a separate active authority-migration plan explicitly owns the change. Any `specify init` or `specify self check` command evidence SHALL remain blocked subordinate command evidence unless that same authority-migration plan explicitly owns the command boundary.

The repository SHALL provide `tools/spec_kit_subordinate_runtime.py` as a dry-run-only subordinate helper. The helper SHALL only support `source-refresh`, `probe`, `plan-dry-run`, `init-dry-run`, and `self-check-dry-run`, SHALL reject live or apply mode names, SHALL NOT run live `specify`, SHALL NOT create `.specify/` or root `specs/`, and SHALL NOT write generated command, skill, prompt, extension, preset, or workflow-output surfaces.

Spec Kit subordinate runtime receipts SHALL include `dry_run_only=true`, `source_url`, `source_pin`, `authority_decision`, and `surface_status`. For R4, `authority_decision.decision` SHALL be only `blocked` or `subordinate`, SHALL record the winning authority layer, and SHALL preserve the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

#### Scenario: Generated Spec Kit command surface is blocked

- **WHEN** a changed or present repository path contains `.codex/commands/speckit.plan.md`
- **AND** no active Spec Kit authority-migration plan owns that generated command surface
- **THEN** `python tools/check_spec_kit_authority_guard.py --root . --json` SHALL fail

#### Scenario: Dry-run subordinate receipt is accepted

- **WHEN** `tools/spec_kit_subordinate_runtime.py probe --root <repo> --receipt-out <receipt>` writes a dry-run receipt
- **AND** the receipt records `authority_decision.decision=subordinate`, `dry_run_only=true`, source evidence, and complete surface status
- **THEN** `python tools/check_spec_kit_authority_guard.py --root <repo> --receipt <receipt> --json` SHALL pass

#### Scenario: Live or apply mode is rejected

- **WHEN** an operator requests `tools/spec_kit_subordinate_runtime.py apply-live --root <repo>`
- **THEN** the helper SHALL reject the mode before building a runtime payload
- **AND** it SHALL NOT run live Spec Kit commands or create generated Spec Kit surfaces
