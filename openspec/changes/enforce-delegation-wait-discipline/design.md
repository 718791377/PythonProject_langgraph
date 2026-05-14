# Design: Delegation wait discipline evidence enforcement

## Overview

Add a repository checker that validates two layers:

1. Repository policy surfaces must explicitly connect delegation/wait discipline to script-backed enforcement.
2. Saved run summaries or worker briefs can be checked as evidence when a session uses native experts, workers, or `wait_agent`.

The checker is intentionally text-pattern based because the evidence sources are operator-facing traces, run summaries, and worker briefs rather than a single structured event stream.

## Checker behavior

`tools/check_delegation_wait_discipline_evidence.py` supports:

- `--root <path> --json`: repository surface check for docs/spec/guard/registry wiring.
- `--evidence <path> --json`: evidence-file check for actual delegation/wait wording.

Evidence validation:

- if delegation is present, require:
  - an immediate critical-path local task or leader-local work statement;
  - concrete/bounded/self-contained/materially-advancing sidecar wording;
  - duplicate-work prevention or non-overlapping ownership wording;
- if code-changing worker delegation is present, require:
  - file/module ownership or disjoint write-set wording;
  - a "not alone in the codebase / do not revert others" instruction;
  - changed-path reporting expectation;
- if `wait_agent` or equivalent wait wording is present, require:
  - bounded wait/critical-path blocker or equivalent "blocked until result" wording;
  - meaningful non-overlapping leader work, or a clear statement that the next step is blocked;
  - no indefinite/silent/reflexive wait wording.

## Guard integration

The OpenSpec guard runs repository-surface mode. Evidence-file mode remains a reusable local checker for run summaries and future artifacts; it is covered by unit tests and referenced by policy/spec text.

## Alternatives considered

- Extending `check_expert_lifecycle_wait_pacing_evidence.py`: rejected because lifecycle closure and delegation design are related but separate evidence concerns.
- Runtime-only enforcement: rejected because this repository currently needs prompt surfaces plus script controls that fail closed on saved evidence and policy drift.

## Risks

- Text-pattern checks can false-positive or false-negative. Mitigation: keep the marker set broad, bilingual, and focused on required evidence categories rather than exact phrasing.
- Overly strict evidence requirements could discourage useful expert use. Mitigation: repository-surface mode is required by guard; evidence mode is invoked when saved delegation/wait evidence exists.
