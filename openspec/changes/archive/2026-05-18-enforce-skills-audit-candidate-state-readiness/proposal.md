# Proposal: enforce Skills audit candidate-state readiness

## Why

The Skills usage audit candidate gate already required a 30-day window, reviewed summary, source-report paths, and an explicit target profile. However, a manually invoked gate could still be given a structurally valid report whose `audit_state.state` was not actually candidate-ready, such as `ready-for-summary` or `closed-no-change`. That could make an unreviewed or no-change audit look like a usable profile-apply candidate preview.

## What changes

- Define candidate-ready audit states as `summary-reviewed`, `apply-candidate`, and `closed-with-candidate`.
- Block candidate generation for `planned`, `paused`, `running`, `ready-for-summary`, `closed-no-change`, missing, or otherwise not-ready audit states.
- Expose the accepted ready-state set in the candidate gate result.
- Add regression coverage for not-ready, no-change, and closed-with-candidate states.
- Update the bilingual Skills usage audit plan and stable lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load state, remote refs, or live plugin state.
