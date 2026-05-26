## Context

The repository's Comet policy separates OpenSpec as WHAT, Superpowers as HOW, and Comet as CONTROL. The PMBOK8 cache under `PMP/PMP_MD/` says the familiar process groups return as focus areas that recur, overlap, and are tailored across predictive, adaptive, and hybrid delivery.

The runtime design therefore should not create a giant waterfall implementation ceremony. It should keep the five Comet phases as a simple state machine while adding a cross-cutting Monitoring control loop that can return to any earlier phase when evidence changes.

## Decisions

1. Preserve `Open -> Design -> Build -> Verify -> Archive` as the forward phase chain.
2. Add per-change `management.md` checklist evidence instead of relying only on prose in proposal/design/tasks.
3. Add `.comet.yaml` fields for `management_record`, `monitoring_status`, `control_decision`, `target_phase`, `rework_reason`, and `iteration_count`.
4. Treat `control_decision=continue` as the only normal forward decision. `adjust-current`, `return-*`, `stop`, or `blocked` states prevent forward transition until resolved.
5. Implement return events as explicit state transitions: `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify`.
6. Keep runtime field names neutral; the runtime implements management behavior and does not depend on a literal `PMBOK8` field.

## Runtime Behavior

- On `comet-state init`, create `.comet.yaml` and `management.md` together.
- On each guard, require the current phase checklist and Monitoring forward-readiness checklist.
- When a later phase discovers earlier evidence is weak, write `control_decision=return-<phase>`, `target_phase=<phase>`, and a non-null `rework_reason`; then use the matching `monitor-return-*` event.
- A return transition sets `phase` to the target phase, increments `iteration_count`, preserves `rework_reason`, clears `target_phase`, and resets Monitoring to `continue/clear` for the next iteration.
- Archive checks Closing evidence before moving the change into archive history.

## Risks / Trade-offs

- Hard checklist gates can feel heavier for tiny changes. Hotfix/tweak flows still use the same minimum evidence, but the evidence can be concise.
- Bash runtime tests cannot execute on Windows environments without `bash`; therefore the repository checker also verifies script and skill surfaces statically.

## Rollback

Revert the runtime script changes, remove the implementation plan registry entry and plan files, remove the added OpenSpec requirement, and restore the policy checker/test fixture to the prior mapping-only behavior.
