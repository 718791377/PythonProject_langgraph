# Change: Enforce durable-team threshold trace wording

## Why
The active automatic orchestration plan requires startup and first activation traces to say which durable-team threshold was not met, or which threshold triggered a team launch. Existing policy text says durable teams are threshold-gated, but the script-backed checker does not yet enforce this first-activation threshold wording explicitly.

## What Changes
- Strengthen governance/spec surfaces so first activation traces must include durable-team threshold evidence.
- Extend the orchestration activation policy checker to require stable threshold snippets.
- Add regression coverage proving the checker fails when those snippets are absent.

## Impact
- Affects documentation/policy enforcement only.
- Does not launch durable teams or mutate `.omx/state`.
