# Design: LangGraph State Release Runtime R4

## Context

The current LangGraph evidence checker rejects completed work that remains in active statuses such as `running`. Runtime code can create, resume, inspect, recover, and enrich thread state, but it does not yet provide an operator-facing helper that records the release event and updates the thread to a non-active state.

## Goals

- Provide a single bounded release command for `close`, `release`, and `handoff` actions.
- Persist release receipts in repo-local LangGraph state rather than transient chat context.
- Preserve rollback or restore notes so release mistakes are recoverable without silently switching backend families.
- Keep backend-family handoff explicit by recording handoff target and reason.
- Keep the current Codex leader and seven-phase LangGraph shell unchanged.

## Non-Goals

- Do not implement a new durable backend family.
- Do not mutate remote publication state.
- Do not delete thread, checkpoint, history, interrupt, brief, or survivor artifacts.
- Do not automatically switch to `native_omx`; handoff records only make a later explicit switch safe.

## Decisions

### Decision 1: Add a release receipt under the existing LangGraph store tree

Receipts live under `.omx/state/langgraph/store/releases/` because they are durable thread evidence, not activation selectors and not shared user-level state.

### Decision 2: Use one helper for close, release, and handoff

The command records the same common fields for every action and adds handoff fields only for backend-family handoff. This keeps release evidence consistent while preserving action-specific semantics.

### Decision 3: Keep rollback evidence as text, not automatic state rewrite

The helper records rollback or restore guidance but does not rewind thread state. Explicit recovery remains the bounded recovery mechanism.

## Validation Plan

1. Add a failing runtime test for the missing release helper command.
2. Implement the helper and receipt path.
3. Verify close and handoff receipts through status/inspect output.
4. Run targeted LangGraph state-release tests and repository gates.
