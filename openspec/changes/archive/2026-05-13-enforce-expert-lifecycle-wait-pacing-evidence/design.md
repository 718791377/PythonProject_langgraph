# Design: Expert lifecycle, wait, and pacing evidence checker

## Decision

Add a focused saved-evidence checker instead of changing live subagent runtime behavior in this slice. The checker validates text artifacts that summarize expert lifecycle and wait behavior, which is the lowest-risk enforcement layer for the current plan phase.

## Rules enforced

1. Completed expert results must show either closure after absorption or an explicit preserved-thread reason.
2. Wait claims must show bounded windows and a total wait bound; indefinite or silent waiting is always rejected.
3. Liveness or stall language must show a concrete action such as inspect, redirect, respawn, durable handoff, or main-session takeover.
4. Provider pacing must be labeled as backpressure and must not be cited as a reason to disable orchestration.

## Integration

`tools/check_orchestration_activation_policy.py` remains the guard entrypoint that verifies policy surfaces and checker availability. The new checker also has a direct CLI so run summaries or transcript snippets can be validated independently. This avoids touching the CI manifest or global OpenSpec guard in this slice while still making the policy checker aware of the new executable control.

## Safety

The checker is read-only. It does not launch experts, wait on agents, change `.omx/state/`, or alter user-level capability switches.
