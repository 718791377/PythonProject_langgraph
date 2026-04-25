## Context

The user-level Codex persistent agent-team line already has these LangGraph-side pieces in place:

- additive durable backend integration under the Codex CLI leader model
- a seven-phase root graph
- bounded quality-gated loops
- reducer-aware fan-out and fan-in semantics
- replay, state-history inspection, and explicit recovery controls

What still remains shallow is the subgraph layer. The current implementation keeps a `SUBGRAPHS` map in Python, but that map is not yet a reusable library with stable contracts, handoff expectations, or active-subgraph projection. For a real persistent agent-team lane, subgraphs must become first-class durable objects rather than just labels attached to a role list.

## Goals / Non-Goals

**Goals:**

- define a reusable LangGraph subgraph library for the user-level persistent agent-team lane
- give each supported subgraph a stable identity and contract
- make research-to-planning and planning-to-execution handoffs explicit at the subgraph boundary
- persist active-subgraph identity in tracked LangGraph thread state
- expose subgraph-library inspection through user-level tooling and canonical state surfaces

**Non-Goals:**

- changing when LangGraph is selected as the effective durable backend
- replacing the seven-phase root graph with a subgraph-only runtime
- turning all specialist roles into always-on persistent workers
- introducing cloud deployment, LangSmith hosting, or external orchestration infrastructure
- redesigning loops, reducers, or replay and recovery controls beyond subgraph-aware integration points

## Decisions

### Decision 1: Keep the seven-phase root graph and make subgraphs reusable building blocks under it

The root graph already matches the durable-team development cadence. Replacing it would expand scope unnecessarily.

Instead, each phase-family will map to a reusable subgraph contract:

- `research`
- `planning`
- `execution`
- `verification`
- `adversarial-review`

Alternative considered:

- replace the root graph with one graph node per role
  - rejected because it would blur leader-owned routing with durable backend structure and over-persist bursty specialists

### Decision 2: Subgraph contracts must declare more than a role list

Each reusable subgraph should carry a stable contract that includes at least:

- `subgraph_id`
- `default_phase`
- `role_family`
- `roles`
- `input_artifacts`
- `output_artifacts`
- `fresh_context_boundary`
- `durable_worker_default`
- `read_only_default`

Alternative considered:

- keep only the existing `SUBGRAPHS = { name: [roles...] }`
  - rejected because it is not rich enough to support persistent-team handoff, inspection, or later graph reuse

### Decision 3: Research and implementation boundaries stay explicit at subgraph boundaries

The plan already requires research and implementation to stay separate. The subgraph library should formalize that boundary instead of weakening it.

Examples:

- `research` outputs a frozen implementation brief
- `planning` consumes that brief and produces plan-ready execution ownership
- `execution` consumes frozen plan inputs rather than the entire open-ended research context

Alternative considered:

- allow cross-subgraph reuse of full preceding context by default
  - rejected because it would dilute the existing fresh-context discipline

### Decision 4: The first rollout should expose subgraph inspection before deep execution semantics

The first implementation needs to make the library inspectable and durable before attempting full graph execution through every subgraph boundary.

That means the first rollout should support:

- stable contract definitions
- active-subgraph recording on tracked threads
- user-level inspection of available subgraphs and active-subgraph posture

Alternative considered:

- implement hidden internal subgraph contracts without exposing them
  - rejected because the user-level persistent-team lane requires inspectability and operator-facing clarity

### Decision 5: Add one additive subgraph-library helper surface instead of overloading every existing command

The current `inspect` surface should expose subgraph-related projection data, but a dedicated helper remains useful for operator-facing discovery and future tooling.

The minimal additive surface is:

- `omx-langgraph-subgraphs.ps1`

Alternative considered:

- force all subgraph inspection through `omx-langgraph-inspect.ps1` only
  - rejected because library inspection and thread inspection are related but not identical operator questions

## Risks / Trade-offs

- [Risk] Subgraph contracts may become too abstract and drift away from the current runtime. -> Mitigation: keep the first rollout tied to the already-supported five role families and current seven-phase root graph.
- [Risk] The library may look more complete than the actual execution semantics. -> Mitigation: distinguish clearly between reusable contract availability and deeper execution behavior still deferred to later changes.
- [Risk] Research/implementation boundaries could regress if subgraph reuse is too permissive. -> Mitigation: encode fresh-context boundaries directly in the subgraph contract.
- [Risk] Another helper surface may create command sprawl. -> Mitigation: keep the first rollout to one small inspection helper plus inspect-surface projection.

## Migration Plan

1. Add proposal, design, and spec artifacts for reusable subgraph contracts.
2. Extend the LangGraph Python contract layer with a richer subgraph library structure.
3. Record active-subgraph metadata in tracked thread state and expose it through inspect output.
4. Add a user-level LangGraph subgraph-library helper wrapper and generated playbook or quick-reference mentions.
5. Validate that the library remains additive, durable, and inspectable without disturbing existing replay, recovery, or reducer behavior.

Rollback strategy:

- revert the reusable subgraph contract and helper surfaces only
- keep the current root graph and previously delivered LangGraph durable behaviors intact

## Open Questions

- Should a later rollout allow root-graph execution to target a named reusable subgraph directly, or should subgraphs remain inspectable library contracts first?
- Should `verification` remain one reusable subgraph, or later split into `verification` and `security-verification` contracts if the current family becomes too broad?
