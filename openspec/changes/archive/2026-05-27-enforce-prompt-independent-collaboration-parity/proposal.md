# Proposal: Enforce Prompt-Independent Collaboration Parity

## Why

The automatic orchestration plan now requires executable evidence that equivalent tasks route the same way whether or not the prompt repeats collaboration phrases. Durable and persistent team claims also need a single checker-backed evidenceguard so readiness, stale LangGraph state, skill invocation, timeout, or bare `.omx` directories cannot be reported as runtime completion evidence.

## What

- Add a checker for prompt-independent collaboration parity, cold-start read-order evidence, durable/persistent evidenceguard records, expert lifecycle audit events, and LangGraph state release.
- Add fixture pairs for document-update and multi-slice routing parity plus explicit `omx` and LangGraph threshold cases.
- Wire the checker into the OpenSpec guard, CI manifest, safety registry, governance docs, implementation plan, AGENTS.md, and stable OpenSpec spec.

## Impact

This is a local repository enforcement change. It does not launch a durable team, does not claim native expert execution, and does not publish to remotes.
