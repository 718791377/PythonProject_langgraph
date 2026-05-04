# Refine Production Capability Profiles

## Why

The draft personal production durable-team plan needs a clearer boundary between reusable Codex CLI durable-team tooling and concrete business runtimes. It also needs an abstract capability-profile model so future workloads can be assessed against the ten-layer framework without embedding concrete business names in the production plan.

## What Changes

- Add a shared dependency and runtime ownership rule to the draft production durable-team plan.
- Clarify that third-party dependencies such as evaluation, GUI, queue, embedding, and vector-store runtimes belong to the Codex CLI durable-team control surface by default, not to concrete business runtimes.
- Preserve a narrow exception for local Llama model deployments when used through provider adapters with separate logs, permissions, and data boundaries.
- Add abstract business capability profiles that map workload classes to the ten-layer framework without naming concrete businesses in the plan.
- Add a separate bilingual reference table for concrete workload examples and their abstract capability-profile mapping.

## Non-Goals

- Do not implement durable runtime behavior.
- Do not launch `native_omx` or `langgraph`.
- Do not write `.omx/state/`.
- Do not modify user-level Codex configuration.
- Do not move concrete business project dependencies into this repository.
