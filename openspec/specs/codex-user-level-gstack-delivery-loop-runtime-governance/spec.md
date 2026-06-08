# codex-user-level-gstack-delivery-loop-runtime-governance Specification

## Purpose
Define the stable repo-local governance boundary for the gstack delivery-loop runtime lane so R4 helper/checker behavior remains subordinate, advisory, read-only by default, and aligned with `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
## Requirements
### Requirement: gstack delivery-loop runtime SHALL remain subordinate and advisory

The repository SHALL keep gstack delivery-loop runtime surfaces subordinate to the authority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

Repo-local gstack helper output SHALL be advisory only. It SHALL NOT replace Comet control, OpenSpec WHAT authority, Superpowers HOW discipline, harness runtime-safety gates, local-main-first integration gates, or remote-publication approval gates.

#### Scenario: Delivery-loop dry-run remains advisory

- **WHEN** `python tools/gstack_codex_delivery_loop_runtime.py analyze --root . --json` or another dry-run action is invoked
- **THEN** the output SHALL include `authority_decision`, the machine-readable field that states which authority layer won and why
- **AND** the decision SHALL preserve the priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`
- **AND** the helper SHALL NOT claim controller takeover, browser launch, telemetry enablement, durable-state mutation, or remote publication

### Requirement: gstack R4 smoke receipts SHALL stay read-only and fixture-backed

The repository SHALL allow bounded gstack R4 smoke receipts only through an explicit receipt directory. The helper MAY accept a fixture/existing install receipt for a bounded help probe, but it SHALL NOT install or clone upstream gstack by itself.

Positive R4 smoke receipts SHALL remain read-only and SHALL include timeout release, rollback readiness, transcript redaction, and an `authority_decision` field. The `authority_decision` field is the machine-readable control decision that records the winning authority layer, the applied priority order, and the allow/block reason for the gstack lane. Missing install receipt evidence SHALL produce a blocked/not-smoke-tested receipt rather than a false positive.

#### Scenario: Missing install receipt yields blocked smoke evidence

- **WHEN** `python tools/gstack_codex_delivery_loop_runtime.py smoke --receipt-dir <dir> --json` runs without an install receipt
- **THEN** the helper SHALL write a blocked receipt
- **AND** the receipt SHALL remain `smoke_tested=false`
- **AND** the checker SHALL accept it only as honest blocked evidence, not as a positive smoke-tested result

#### Scenario: Positive smoke remains non-live evidence

- **WHEN** the helper runs smoke with a valid fixture/existing install receipt
- **THEN** the receipt SHALL be limited to bounded help/read-only evidence
- **AND** it SHALL NOT enable hooks, browser QA, telemetry, user-level state mutation, or active-candidate behavior

### Requirement: gstack governance checker SHALL fail closed on priority drift or live markers

The repository SHALL provide a gstack governance checker that validates bilingual plan markers, dry-run surfaces, smoke receipts, guard/CI wiring, and the authority order.

The checker SHALL fail closed when the priority order drifts, `authority_decision` is missing, smoke receipts claim live/write behavior, or required tests/guard steps are absent.

#### Scenario: Forbidden live markers are present

- **WHEN** a gstack smoke receipt or runtime output claims write, browser, telemetry, active-candidate, or remote-publication behavior
- **THEN** `python tools/check_gstack_codex_delivery_loop.py --root . --receipt-dir <dir> --json` SHALL fail closed
- **AND** the checker SHALL return sanitized blocker codes instead of treating the evidence as valid R4 behavior
