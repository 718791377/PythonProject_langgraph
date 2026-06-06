# Design: Durable Smoke Adoption Runtime R4

The R4 runtime stays deliberately small. `run_durable_routing_smoke.py` executes a bounded local Python checker command, defaults to the existing durable routing smoke gate template checker, and writes one explicit receipt file. The helper validates that the command begins with Python, targets a repository `tools/check_*.py` script, and does not contain apply, durable-team, remote-publication, or LangGraph launch markers.

The receipt is evidence, not adoption. It records `runtime_stage=R4`, `stage=smoke-tested`, `routing_mode=read_only`, `state_write_policy=receipt_only`, bounded timeout release, a git-head rollback pointer, transcript hashes/excerpts, redaction status, and backend-family evidence. The fields `adoption_performed`, `durable_workflow_selected`, `durable_workflow_running`, `durable_workflow_adopted`, `mutation_allowed`, `user_level_state_mutated`, `durable_team_launched`, `omx_apply_performed`, `langgraph_thread_started`, and `remote_publication_authorized` must remain false.

`check_durable_routing_smoke_receipts.py` validates the receipt shape and fails closed against adoption claims, unbounded transcripts, raw sensitive data, timeout failures, missing rollback readiness, and backend evidence that claims selected/running/adopted state. The checker runs built-in positive and negative fixtures by default so the OpenSpec guard can validate the receipt contract without creating live durable state.

Apply-mode adoption, selected/running/adopted receipts, and live handoff receipts remain later Stage D work. This R4 slice gives those future helpers a safe precondition: smoke success can be proven without collapsing into adoption.
