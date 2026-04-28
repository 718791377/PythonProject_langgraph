## Why

The current leader-side expert routing guidance is strong on role descriptions, but it does not yet make one important sequencing rule explicit: when a task is still in the bounded research or classification stage and has multiple parallel research faces, the first fan-out should prefer homogeneous `analyst` calls rather than prematurely mixing `architect`, `planner`, and `writer` in the same round. That gap increases fan-in cost, mixes abstraction levels too early, and makes role routing less predictable than it should be.

This change is needed now because the repository already has an explicit user-level routing policy, generated leader instructions, and reusable specialist roles. Without formalizing this rule, later changes can keep reintroducing mixed-role research fan-out patterns that are harder to integrate and harder to explain.

## What Changes

- Formalize an analyst-fanout-first rule for bounded multi-face research tasks.
- Require leader-side routing to prefer homogeneous `analyst` fan-out when the task is still primarily about definition, classification, scoping, or repository-grounded comparison.
- Delay escalation to `architect`, `planner`, or `writer` until the leader has already completed a first research fan-in and confirmed that the task has moved into design, execution ordering, or document-finalization work.
- Make generated routing-policy and leader-profile surfaces explain this sequencing rule explicitly so operators can understand why the router chose homogeneous analysts first.
- Keep the existing burst-role model, durable-team thresholds, and backend-family rules unchanged.

## Capabilities

### New Capabilities
- `codex-user-level-analyst-fanout-first-routing`: define the reusable role-routing rule that bounded multi-face research tasks should first fan out into homogeneous `analyst` calls before escalating into design, planning, or writing roles.

### Modified Capabilities
- `codex-user-level-team-mode-routing-thresholds`: add the analyst-fanout-first sequencing rule and clarify when `architect`, `planner`, and `writer` should enter only after an initial research fan-in.

## Impact

- affected user-level routing policy and generated leader instructions
- `tools/install-codex-user-level-team-mode.ps1` - installer source script that generates user-level team-mode routing assets
- generated `team-leader.toml` and routing-policy surfaces
- related user-level team-mode documentation and implementation plans
- tests that verify routing-policy wording and generated asset behavior
