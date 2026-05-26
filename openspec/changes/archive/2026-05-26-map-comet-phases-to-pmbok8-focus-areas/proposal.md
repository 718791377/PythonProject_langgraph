## Why

The Comet/OpenSpec/Superpowers workflow policy mapped Comet phases to project-management focus areas, but that first pass was still mostly textual. The runtime must absorb the management logic: every phase needs explicit management evidence, and Monitoring must support adaptive or hybrid rework rather than a one-way waterfall.

The local PMBOK8 notes emphasize that focus areas recur, overlap, and can be tailored across predictive, adaptive, and hybrid work. In Comet terms, this means a later phase must be able to return to Open, Design, Build, or Verify when current evidence shows an earlier focus area is incomplete.

## What Changes

- Add a bilingual implementation plan for the iterative Comet runtime management loop.
- Extend `.comet.yaml` with management record, monitoring status, control decision, target phase, rework reason, and iteration count fields.
- Add `management.md` checklist evidence for Open, Design, Build, Verify, Archive, and Monitoring.
- Make Comet guards fail closed when required management checklist items are missing.
- Add Monitoring return transitions so a change can return to `open`, `design`, `build`, or `verify` with reason and iteration tracking.
- Update Comet skills, governance policy, OpenSpec capability, checker, and tests.

## Impact

- Affected runtime: `.codex/skills/comet/scripts/comet-state.sh`, `comet-guard.sh`, `comet-yaml-validate.sh`, and `comet-archive.sh`.
- Affected skills: project-local `.codex/skills/comet*` instructions.
- Affected documentation: governance policy and implementation plan under `docs_bilingual/`.
- Affected validation: policy checker, guard JSON fixture, and a runtime-management test/check surface.

## Validation

- Run the Comet/OpenSpec/Superpowers policy checker.
- Run OpenSpec validation.
- Run the focused guard JSON test and the new Comet runtime management test/checker.
- Run document governance and implementation-plan checks.
