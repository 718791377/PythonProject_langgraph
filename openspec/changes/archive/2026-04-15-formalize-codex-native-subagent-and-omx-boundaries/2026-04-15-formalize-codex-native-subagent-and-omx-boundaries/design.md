## Context

The Codex user-level team-mode line already has archived implementation batches for controls, startup binding, team entrypoints, routing thresholds, burst-review roles, automatic durable-team routing, native Windows backend, worker breakaway lifecycle, startup leader protocol, and provider pacing. The current repository plan documents were then tightened further to describe native Codex subagents as an official explicit-spawn capability, to distinguish wrapped leader-side routing from raw Codex defaults, and to define stricter boundaries for custom agent TOMLs, concurrency limits, and write-heavy fan-out.

The current bottleneck is no longer runtime capability. The bottleneck is contract clarity across the reusable spec layer. Existing common specs cover controls, startup posture, and routing thresholds, but they do not yet formalize:

- native Codex subagents as an explicit leader-orchestrated base capability
- the layered relationship between native Codex subagents and durable `omx team`
- the layered locations for reusable user-level agent TOMLs versus repository-scoped agent TOMLs
- the minimum standalone custom-agent schema used by this workflow
- the requirement that `agents.max_threads` and `agents.max_depth` stay explicit and inspectable
- the rule that write-heavy parallelism needs stronger ownership and integration boundaries than read-heavy fan-out

Stakeholders:

- user-level installer and wrapper maintainers
- routing-policy and startup-layer maintainers
- operator playbook and documentation maintainers
- future repositories that reuse the same Codex / oh-my-codex user-level workflow

## Goals / Non-Goals

**Goals:**

- promote the updated native-subagent rules from plan prose into reusable OpenSpec requirements
- prevent future wrappers, playbooks, and generated assets from misdescribing raw Codex as automatically spawning subagents by default
- formalize additive control surfaces for native-subagent limits and custom-agent placement
- formalize the routing-policy distinction between safe read-heavy fan-out and gated write-heavy multi-agent execution
- keep the native Codex base layer, wrapped native-routed mode, and enhanced OMX mode semantically distinct

**Non-Goals:**

- implementing a new durable-team backend or worker lifecycle mechanism
- introducing a mixed persistent-pane default
- replacing the native Codex executable or changing OpenClaw runtime configuration
- turning this change into a general multi-agent framework evaluation effort
- forcing immediate runtime behavior changes before the contract and validation surfaces are in place

## Decisions

### Decision 1: Add one new capability for native-subagent boundaries instead of overloading existing specs

We will add `codex-user-level-team-mode-native-subagent-boundaries` as a new reusable capability.

Why:

- the missing concerns are cross-cutting but conceptually coherent
- they span semantics, configuration boundaries, concurrency limits, execution-safety rules, and terminology
- forcing all of that into `controls` or `routing-thresholds` would blur the distinction between operator controls and native-subagent contract rules

Alternative considered:

- only add delta requirements to `controls` and `routing-thresholds`
- rejected because the resulting contract would stay fragmented and harder to reuse in future repositories

### Decision 2: Keep control-surface changes additive

We will extend `codex-user-level-team-mode-controls` only where the user-level control surface itself changes, mainly by requiring a managed native-subagent limit surface and keeping the generated assets additive.

Why:

- P0 already established the additive-control pattern
- limit management belongs to the control surface, not to startup or worker execution
- this preserves the native Codex base-layer safety boundary

Alternative considered:

- place `agents.max_threads` and `agents.max_depth` entirely inside routing policy or leader instructions
- rejected because limits must also be operator-visible and inspectable outside the live session

### Decision 3: Treat automatic expert routing as a leader-side overlay over explicit native spawning

We will extend `codex-user-level-team-mode-routing-thresholds` to say that automatic expert-role routing is a leader-side routing policy layered over native Codex subagents, not a statement about raw Codex defaults.

Why:

- this matches the researched product boundary
- it keeps wrapped behavior honest and inspectable
- it prevents future generated assets from implying that raw Codex always auto-spawns roles

Alternative considered:

- move this clarification into startup-only specs
- rejected because the concern is not only first-turn startup posture; it is the reusable routing model itself

### Decision 4: Use layered agent-TOML placement rules instead of one global location

We will formalize a layered rule:

- reusable cross-repository roles live under user-level Codex home
- repository-specific roles live under `<repo>/.codex/agents/`
- standalone custom-agent TOMLs must declare `name`, `description`, and `developer_instructions`

Why:

- this preserves reuse without collapsing repository-specific behavior into one global bucket
- it matches how current operator expectations and plan docs already distinguish global versus per-repository concerns

Alternative considered:

- standardize only on user-level agent files
- rejected because repository-local specialization is part of the native Codex configuration surface

### Decision 5: Make write-heavy parallelism a stricter gate than read-heavy fan-out

The native-subagent contract will explicitly prefer read-heavy or tightly bounded fan-out and gate write-heavy multi-agent execution behind:

- ownership isolation
- hotspot serialization rules
- leader-owned final integration

Why:

- this matches both the product research and the long-running-agent methodology
- it gives future routing and orchestration work a stable safety boundary

Alternative considered:

- treat all multi-agent parallelism as equivalent once a task is split
- rejected because it would under-specify merge-conflict and integration risk

## Risks / Trade-offs

- [Risk] The new capability may overlap semantically with existing controls and routing specs. → Mitigation: keep the new capability focused on native-subagent contract rules and keep asset-generation changes in `controls` and policy semantics in `routing-thresholds`.
- [Risk] Operators may expect `codex-subagent-limits.ps1` to be a broad configuration writer. → Mitigation: specify that the surface must at least be inspectable; if writing is supported, it remains bounded and additive.
- [Risk] The terminology rules may look documentation-only and drift from runtime behavior. → Mitigation: bind generated leader and playbook assets to the same contract and validate them through spec-backed acceptance criteria.
- [Risk] Write-heavy gating may slow down future multi-writer experiments. → Mitigation: make the rule explicit so experiments can opt in only after ownership isolation is formalized rather than by accidental drift.

## Migration Plan

1. Add the proposal, design, and spec deltas that formalize the native-subagent contract.
2. In a later implementation step, update the installer, generated controls, and generated routing or playbook assets to match the new requirements.
3. Validate wrapped native-routed startup, pure single-agent startup, limit-surface generation, and generated guidance across at least one test repository.
4. If implementation of the managed limit surface proves unstable, keep the inspection path and defer managed writes without relaxing the new contract requirements.

Rollback:

- revert only the additive installer outputs, generated docs, and routing-policy surfaces touched by implementation
- preserve the native Codex base layer unchanged
- preserve archived P0-P7 behavior that is not directly modified by this contract-tightening change

## Open Questions

- Should the managed limit surface write directly into Codex config, or remain inspection-first until wider operator validation is complete?
- Should the repository-local `.codex/agents/` guidance include precedence rules when a role name exists at both user and repository scope?
- Should the terminology boundary for `OpenHands` versus archived `OpenDevin` remain only in operator docs, or also be added to generated help text?
