# Design: Spec Kit Authority Guard R4 Closeout

## Current State

The repository already has a dry-run subordinate runtime helper and a fail-closed Spec Kit authority guard. Focused tests cover generated surfaces, safe references, and basic receipt validation. The remaining gap is not a new runtime lane, but the final R4 closeout contract: the helper, guard, stable spec, and registry still need to agree on the exact conflict-priority string and the stable safety-rule requirement.

## Decision

Keep the runtime scope unchanged and dry-run only.

- The exact conflict order becomes `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- `authority_decision.priority_order` is now part of the required receipt contract.
- The stable safety-rule spec records the requirement so future cold-start sessions do not rely only on plan text.
- The script-backing registry records both the checker and the dry-run runtime helper as the executable controls for this rule.
- `spec_kit_authority_guard_plan` remains the owning implementation plan; the subordinate adapter plan remains companion guidance.

## Safety Notes

- No live Spec Kit command runs.
- No `.specify/`, root `specs/`, slash-command, skill-surface, extension, preset, or workflow-output generation is allowed.
- The runtime helper still emits receipts only.
- Local integration remains subject to local-main-first validation and the remote-publication gate.

## Verification Focus

- Runtime receipts must include the exact priority order.
- The guard must reject receipts that omit or change that order.
- Stable spec and registry must both reflect the same rule.
- Implementation-plan and governance wording must align with the strict priority order.
