---
change: refactor-general-template-plans-comet
status: archived
archived-with: openspec/changes/archive/2026-05-27-refactor-general-template-plans-comet
---

# General Template Plan Refactor Design

## Problem
Two Chinese implementation plans carried overlapping history, target-template facts, and live-session notes. Cold-start readers could not quickly distinguish the fuller `PythonProject_General` governance template from the local-only `PythonProject_General_2` template.

## Design Decision
Use a full Comet governance pass to split the documents by capability tier:

- `PythonProject_General` is the fuller reusable Codex/OpenSpec/Comet governance template. It may template optional oh-my-codex, native_omx, LangGraph compatibility source, MCP scope rules, launcher payload rules, and local/remote gate parity.
- `PythonProject_General_2` is the local-only template. It keeps local Git, OpenSpec, Superpowers governance, and native Codex subagents, and explicitly excludes remote CI/MR, oh-my-codex, native_omx, LangGraph durable backend, and `.omx/state/` runtime state.
- Comet is described only as OpenSpec + Superpowers governance. It is not native subagent evidence, a durable backend, or a replacement for OpenSpec.

## Document Shape
Each implementation plan becomes decision-complete for a future cold-start implementer: current state, non-goals, capability map, implementation sequence, verification commands, acceptance criteria, and rollback path. The documents avoid copying terminal mojibake, stale active-session facts, or current live state.

## Validation
The refactor is validated by UTF-8 clean writes, OpenSpec validation, implementation-plan checks, Comet/OpenSpec guard checks, local CI, and local MR review. No remote publication is part of this change.
