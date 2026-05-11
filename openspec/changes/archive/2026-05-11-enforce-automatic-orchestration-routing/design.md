## Design

This change is intentionally checker-first. It does not add a new orchestration runtime; it makes the existing runtime policy harder to forget by pairing prompt reminders with executable repository checks.

The enforcement surface has three layers:

1. Prompt/policy surfaces: `AGENTS.md`, startup summaries, and the new governance policy.
2. Stable OpenSpec surfaces: activation policy, routing thresholds, capability switches, and automatic team routing.
3. Script control: `tools/check_orchestration_activation_policy.py`, called from `tools/run_openspec_guard.py` and registered in the safety-rule registry.

Runtime adoption still remains threshold-gated. `backend_default=langgraph` and `backend_ready=true` mean LangGraph is the default ready durable backend; they do not imply persistent team is already running.
