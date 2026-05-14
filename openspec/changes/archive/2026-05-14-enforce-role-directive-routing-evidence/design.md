# Design: Role routing directive evidence enforcement

## Context

Hard routing directives and role selection are high-impact orchestration decisions. They must not depend only on prompt reminders, because stale sessions can otherwise treat `omx` or `LangGraph` as optional and can add unnecessary roles without a trigger.

## Decisions

1. Add `tools/check_role_routing_directive_evidence.py` with two modes:
   - repository mode checks policy surfaces, guard wiring, and safety registry wiring;
   - evidence mode checks saved traces, run summaries, or role-routing notes.
2. Treat explicit `omx`/`LangGraph` language as requiring either selected/running adoption or a named blocker/unmet threshold.
3. Treat threshold-satisfied language as requiring actual selected/running adoption, not explanation-only mode.
4. Treat selected role names as requiring trigger evidence.
5. Treat bounded multi-face research as analyst-first, with architect/planner/writer disallowed in the first round unless analyst fan-in is explicitly recorded.

## Risks

- Text evidence checks can be conservative. Mitigation: repository mode is exact, while evidence mode only fails when relevant markers appear.
- Role-trigger vocabulary can evolve. Mitigation: keep role trigger markers small and stable, and extend the checker as new evidence formats appear.

## Rollback

Revert the checker, test, guard/registry/manifest wiring, and policy/spec text updates. The implementation plan remains as historical context.
