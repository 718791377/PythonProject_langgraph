# Document Product Lifecycle Stage Map

## Why

The production durable-team plan now mixes several planning concepts that have different purposes: white paper, BRD, MRD, North Star plan, PRD, technical design, implementation plan, growth plan, and retrospective records. The repository needs a small durable reference that explains these documents and separates two workflows:

1. Building the Codex CLI personal production durable-team platform.
2. Using that platform inside later concrete projects.

Without this separation, future maintainers may put business-project documents into the platform plan, or treat the platform repository as the durable truth for consumer projects.

## What Changes

- Add a bilingual product and business document lifecycle reference.
- Add a bilingual Codex CLI durable-team platform-build lifecycle reference.
- Add a bilingual downstream project-consumption lifecycle reference.
- Add OpenSpec requirements that keep platform-build documentation separate from project-consumption documentation.

## Non-Goals

- Do not implement runtime behavior.
- Do not launch `native_omx`; this is the durable-team backend lane for worker-centric execution.
- Do not launch `langgraph`; this is the graph checkpoint and approval-gate backend lane.
- Do not write `.omx/state/`; this is the repo-local durable state directory.
- Do not modify user-level Codex configuration.
