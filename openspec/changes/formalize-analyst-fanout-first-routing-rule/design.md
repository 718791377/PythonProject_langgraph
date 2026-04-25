## Context

The current user-level routing model already has strong role descriptions, phase-based thresholds, and explicit boundaries between leader-side native experts and durable worker lanes. What it does not yet make explicit is the sequencing rule for a very common class of task:

- the task is still in the bounded research, classification, or scoping stage
- the task has multiple parallel research faces
- the leader wants fast recall and clean fan-in before escalating to design, execution ordering, or final writing

Without an explicit rule, the router and the operator can drift into a mixed first round such as:

- `analyst`
- `architect`
- `planner`
- `writer`

That mixed first round is costly because it mixes four abstraction levels:

- definition
- architecture
- execution ordering
- document finalization

The result is higher fan-in cost, more overlap, and premature escalation into roles that should enter only after the first research round has been absorbed by the leader.

This design therefore focuses on one narrow change only:

- formalize an analyst-fanout-first rule for bounded multi-face research tasks

It does not redesign the durable-team model, backend-family rules, or specialist role catalog.

## Goals / Non-Goals

**Goals:**

- make the first research-round routing rule explicit for bounded multi-face research tasks
- prefer homogeneous `analyst` fan-out while the task is still primarily about definition, classification, scoping, or repository-grounded comparison
- delay escalation to `architect`, `planner`, or `writer` until the leader has completed a first research fan-in
- reflect that rule in generated routing-policy surfaces, generated leader instructions, and operator-facing documentation
- keep the rule understandable enough that an operator can explain why the router chose multiple `analyst` calls first

**Non-Goals:**

- changing the durable-team thresholds or backend-family model
- replacing `architect`, `planner`, or `writer` with `analyst` in all situations
- forcing same-role fan-out for design, execution, or documentation phases that are already clearly identified
- changing the managed specialist model defaults themselves
- introducing a new specialist role just for research fan-out orchestration

## Decisions

### Decision 1: Define a bounded “analyst-fanout-first” task class

The rule should not apply to all early-stage work. It should apply only when the current task is still primarily about:

- problem definition
- scoping
- classification
- repository-grounded comparison
- bounded research questions with multiple independent faces

The router should treat these as one task class and prefer homogeneous `analyst` fan-out first.

Alternative considered:

- treat every early-stage task as analyst-first by default

Rejected because:

- some early-stage tasks are already clearly architectural or planning-heavy
- overextending the rule would delay valid use of `architect` or `planner`

### Decision 2: Delay cross-role escalation until after the first leader fan-in

The first fan-out should prefer `analyst` only. The leader then absorbs the analyst outputs and explicitly decides whether the task has now become:

- an architecture question → escalate to `architect`
- an execution-ordering question → escalate to `planner`
- a final document-production question → escalate to `writer`

This keeps the first parallel round homogeneous and makes later role changes intentional.

Alternative considered:

- keep mixed first-round fan-out and rely on better prompts

Rejected because:

- the problem is not only prompt wording
- the main cost comes from mixing abstraction layers too early

### Decision 3: Encode the rule in routing policy, not only in prose

The rule should live in the same structured routing-policy model that already drives:

- generated leader instructions
- generated routing-policy inspection output
- generated playbook and leader profile wording

This avoids a split between:

- “what the docs say”
- and “what wrapped startup actually routes”

Alternative considered:

- document the rule only in an implementation plan or governance note

Rejected because:

- the operator-facing behavior would still drift
- later generated assets could continue to reflect older mixed-role heuristics

### Decision 4: Preserve existing specialist meanings and durable-team boundaries

This change must not reinterpret:

- `architect`
- `planner`
- `writer`
- durable worker lanes

It changes the sequencing rule for one task class, not the meaning of the roles themselves.

Alternative considered:

- redefine `architect` or `planner` as “advanced analyst” roles

Rejected because:

- it would blur current role boundaries
- it would create downstream confusion in both routing policy and operator documentation

### Decision 5: Keep observability simple and operator-facing

The generated routing-policy surface and leader instructions should explain this rule in plain operator language, for example:

- homogeneous analyst fan-out comes first for bounded multi-face research
- architecture, planning, or writing roles enter after the first research fan-in when the task has clearly changed type

This should stay visible in:

- generated routing policy
- generated leader profile
- generated playbook or quick-reference surfaces where appropriate

Alternative considered:

- keep the distinction implicit inside routing thresholds only

Rejected because:

- operators would see the behavior without seeing the reason
- later maintenance would be harder

## Risks / Trade-offs

- [Risk] The rule is applied too broadly and delays legitimate architectural routing.
  - Mitigation: limit it to bounded multi-face research tasks and keep explicit escalation triggers for architecture and planning.

- [Risk] Operators read “analyst-first” as “analyst-only”.
  - Mitigation: document the second-step escalation rule explicitly in routing policy and generated leader instructions.

- [Risk] Generated assets drift from routing logic again.
  - Mitigation: implement the rule inside the shared structured routing-policy model and verify generated outputs in tests.

- [Risk] Existing mixed-role examples in documents become inconsistent.
  - Mitigation: update the generated operator surfaces and any directly affected implementation-plan wording in the same change.

## Migration Plan

1. Update the structured routing-policy model to define the bounded analyst-fanout-first task class.
2. Update generated leader instructions and generated routing-policy inspection output to describe the rule.
3. Update generated operator-facing assets such as the leader profile and playbook so they explain when analyst fan-out comes first and when later escalation occurs.
4. Add or update tests that verify:
   - homogeneous analyst fan-out is preferred for bounded multi-face research
   - `architect`, `planner`, and `writer` are not pulled into the first round unless the task already clearly belongs to their layer
5. Preserve all durable-team thresholds, backend-family rules, and specialist model defaults unchanged.
6. If rollout introduces confusing operator behavior, rollback by reverting the routing-policy rule and regenerated assets together.

## Open Questions

- Should the routing-policy surface expose this as a named task class, or only as a narrative rule inside role-threshold explanations?
- Should the generated quick-reference card mention this explicitly, or is the playbook plus routing-policy output sufficient?
- Do any current mixed-role examples in user-level documentation need to be rewritten now, or can they be left until the next documentation sync pass?
