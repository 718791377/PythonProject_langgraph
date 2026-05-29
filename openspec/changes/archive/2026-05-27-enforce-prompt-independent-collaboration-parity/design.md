# Design: Collaboration Evidenceguard

The checker is intentionally repository-local and fixture-driven. Repository mode validates policy surfaces, safety-registry registration, guard wiring, and the required fixture set. Evidence mode validates one structured JSON case for use by future run summaries or saved activation artifacts.

The design keeps five evidence contracts together because they share the same failure mode: a final report may otherwise over-claim collaboration from prompts, plans, readiness, stale state, or partial lifecycle evidence. The checker does not replace existing specialized checkers; it adds an acceptance layer for the Phase 4 implementation plan.

No runtime team is started by this change. Durable/persistent team execution remains threshold-gated and must still provide active selector, manifest or LangGraph thread state, heartbeat, close, and leader absorption evidence before selected/running/complete claims are accepted.
