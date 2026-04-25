## Context

The existing user-level team-mode line already defines:

- `Codex CLI` as leader
- additive LangGraph backend support
- repo-local thread identity and checkpoints
- a seven-phase durable flow
- backend-aware routing and inspectable state surfaces

What remains missing is execution logic inside the LangGraph lane that behaves like a graph instead of a persisted one-pass phase runner.

## Goals / Non-Goals

**Goals:**

- make LangGraph execution graph-native for user-level durable tasks
- support conditional edges driven by structured gate verdicts
- support bounded quality-gated loops before final acceptance
- keep loop state inspectable and resumable
- preserve the current backend-selection and leader-control model

**Non-Goals:**

- redesigning backend-family policy
- changing user-level selector defaults
- making all phases loop-capable by default
- replacing bursty expert roles with always-on persistent workers
- introducing replay, reducer merge, or reusable subgraph scope in this change

## Decisions

### Decision 1: Gate verdicts drive conditional edges

Each gated node returns a structured verdict such as:

- `accept`
- `revise`
- `escalate`
- `halt`
- `needs_human`

Conditional edges use that verdict to select the next node.

### Decision 2: Only selected flows become loop-capable in the first rollout

The first rollout supports loops only in the highest-value areas:

- implementation quality loop: `execute -> verify -> revise -> execute`
- review quality loop: `draft -> review -> revise -> review`
- stabilization retry loop: `stabilize -> verify-accept -> stabilize`

Other phases remain single-pass unless they clearly need loop semantics later.

### Decision 3: Loops are bounded and explicit

Each loop carries persisted control data:

- `active_loop`
- `iteration_count`
- `iteration_budget`
- `last_gate_verdict`
- `last_gate_reason`
- `entered_at`
- `stop_reason`

This prevents silent infinite churn and keeps resume behavior deterministic.

### Decision 4: Quality gates consume explicit acceptance inputs

Each loop evaluates against explicit acceptance inputs already available from the frozen brief or phase-local contract:

- required outcomes
- unresolved blockers
- validation failures
- severity thresholds
- human approval requirements

The graph loops only when the gate contract says work is incomplete but still viable.

### Decision 5: Inspectable state exposes loop progress as projection data

The canonical inspectable durable-state surface keeps the existing shared cross-backend contract. LangGraph-specific loop progress is exposed as projection data rather than as a change to the shared summary field set.

## Risks / Trade-offs

- [Risk] Loop behavior can create opaque retries. -> Mitigation: expose iteration, verdict, and stop reason explicitly through inspectable state.
- [Risk] Over-general loop abstractions can delay delivery. -> Mitigation: keep the first rollout narrow and support only the highest-value loop families.
- [Risk] Gate contracts that are too loose will create churn. -> Mitigation: prefer explicit accept or revise criteria tied to validation and blockers.
- [Risk] Budget exhaustion could be mistaken for acceptance. -> Mitigation: require an explicit exhaustion stop reason and do not fall through to success.

## Migration Plan

1. Add proposal, design, and delta spec contracts for graph-native quality-gated loops.
2. Extend the LangGraph backend contract with structured verdict routing and loop persistence.
3. Add LangGraph-specific loop projection data to the inspectable durable-state surface.
4. Validate review, execution, and operator-interrupt loop paths.
5. Keep existing non-looping LangGraph behavior available until loop-capable execution is proven stable.

## Open Questions

- Should the first rollout support operator-tunable iteration budgets or only fixed defaults?
- Should repeated `needs_human` verdicts count toward the same loop budget as automated revise paths?
- Should stabilization retry loops ship in the first rollout or only after review and execution loops are stable?
