# Design: Durable-team threshold trace evidence

## Context

Activation traces already carry `durable_workflow`, `persistent_team`, and `why` fields. The trace-evidence validator already checks required fields, capability-chain consistency, lane vocabulary, missing-reminder reasons, and expert-timeout evidence labels.

The missing enforcement gap is that lane vocabulary alone is not enough. A trace can say `persistent_team=not_needed` or `persistent_team=running` while the `why` field omits the threshold evidence that justifies the decision.

## Decisions

- Keep the implementation inside `tools/check_orchestration_trace_evidence.py` instead of adding a new script, because this rule applies to saved activation trace evidence rather than repository policy surfaces.
- Require threshold evidence in the `why` field, not merely somewhere else in the trace. Field names such as `phase=execute-parallel` must not accidentally satisfy the triggered-threshold rule.
- Treat `not_needed` as requiring an unmet-threshold marker such as `threshold_not_met:no_frozen_plan` or `threshold_not_met:single_execution_slice`.
- Treat `blocked` as requiring a named blocker or unmet-threshold marker such as `blocked:preflight_failed` or `threshold_not_met:no_frozen_plan`.
- Treat `selected` and `running` as requiring triggered-threshold evidence such as `triggered_threshold:frozen_plan_with_2+_independent_slices`, a frozen-plan plus independent-slices phrase, or stabilization/blocking-issues trigger language.
- Keep accepted marker lists bilingual where this repository already uses Chinese operator traces.

## Risks

- Overly strict matching can reject legitimate local wording. Mitigation: accept stable ASCII tokens and common English/Chinese phrases; recommend `threshold_not_met:*`, `blocked:*`, and `triggered_threshold:*` in traces.
- Overly broad matching can accept phase names as evidence. Mitigation: check only `why` for threshold markers.
- Existing saved examples may need clearer `why` labels. Mitigation: the change only affects validation of saved trace evidence and gives actionable error messages.

## Rollout

1. Add checker logic and focused unit tests.
2. Update governance and stable OpenSpec text.
3. Validate and archive before local main integration.
