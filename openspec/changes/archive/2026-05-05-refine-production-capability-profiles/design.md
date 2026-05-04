# Design

## Placement

The production plan receives a new dependency ownership subsection under tool reuse and a new abstract capability-profile subsection before concrete release-stage guidance. The concrete workload examples are intentionally kept in a separate reference file so the main plan remains stable and abstract.

## Runtime Boundary

The rule distinguishes three surfaces:

1. Codex CLI durable-team runtime: shared orchestration, checking, evaluation, recovery, and operator-control tooling.
2. Concrete business runtime: dependencies, state, and user-facing behavior owned by each business project.
3. Shared local model service: a local Llama deployment that may serve both surfaces only through provider adapters with separate policy, logging, and data boundaries.

## Capability Profiles

Capability profiles are horizontal classifications over the ten-layer framework. They are not an eleventh layer. A new workload should map to one or more profiles and inherit the required controls from those profiles.
