# Restore Production Durable-Team Ten-Layer Framework

## Why

The draft production durable-team implementation plan still references the white paper ten-layer model, but the detailed landing map is no longer visible in the plan itself. A cold-start maintainer must be able to see the ten layers directly in the plan before deciding which release slice is safe to implement next.

## What Changes

- Restore a dedicated ten-layer framework landing-map section in the English ASCII implementation plan.
- Restore the matching UTF-8 Chinese companion section with the same constraints and release interpretation.
- Keep the production durable-team plan in `status: draft`; this restoration is documentation only and does not claim runtime implementation.

## Non-Goals

- Do not implement any durable runtime behavior.
- Do not launch `native_omx` or `langgraph`.
- Do not write `.omx/state/`.
- Do not modify user-level Codex configuration.
