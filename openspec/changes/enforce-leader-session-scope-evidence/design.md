# Design: Leader session and scope evidence enforcement

## Context

Leader/session scope is a release-safety boundary. The current main Codex CLI session must remain the leader and release authority, while native experts, durable workers, skills, plugin profiles, and LangGraph nodes remain execution surfaces. Startup and first activation are activation checkpoints, not automatic durable-team launch events. Adoption decisions must target the current task flow, and legacy resumed sessions must remain compatibility-scoped.

## Decisions

1. Add `tools/check_leader_session_scope_evidence.py` with two modes:
   - repository mode checks policy surfaces, guard wiring, safety registry wiring, and local CI manifest wiring;
   - evidence mode checks saved traces, run summaries, or leader/scope notes.
2. Treat saved leader evidence as incomplete unless it includes the current main Codex CLI session, leader-owned fan-in, evidence labeling, and final integration or release recommendations.
3. Reject any unnegated claim that a separate persistent leader pane replaces or owns the main session.
4. Require startup or first activation evidence to cite an unmet or triggered durable-team threshold whenever durable-team state is reported.
5. Reject routing evidence that bases adoption on repository age or new/existing project status rather than task-flow scope.
6. Require legacy resumed session evidence to say compatibility-scoped and to preserve current repository governance plus capability-chain policy.
7. Require reload/restart/resume/continue/durable-state detection evidence to show an activation check rerun.

## Risks

- Text evidence checks can be conservative. Mitigation: repository mode is exact, and evidence mode uses stable marker phrases aligned with startup/governance policy.
- Some older transcripts may lack evidence labels. Mitigation: the checker is intended for accepted evidence; missing labels should force main-session takeover or regenerated run-summary evidence.

## Rollback

Revert the checker, test, guard/registry/manifest wiring, and policy/spec text updates. The implementation plan remains as historical context.
