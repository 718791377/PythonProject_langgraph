## Context

The bilingual team-mode implementation plan has served as the main operator-facing roadmap for the Codex / oh-my-codex user-level workflow. Since that plan was drafted and iteratively refined, multiple capability batches have landed, been validated, and been archived, including controls, startup binding, routing thresholds, native Windows durable-team backend work, startup leader protocol, native-subagent boundaries, and LangGraph durable orchestration integration.

The current bottleneck is not implementation capability. The bottleneck is document drift. Parts of the implementation plan still describe already-landed behavior as planned, or still frame some additive surfaces as future direction when they are now materially present in the user-level installation. If left uncorrected, this weakens the plan as a canonical operator reference.

## Goals / Non-Goals

**Goals:**

- sync the bilingual plan pair with the current implementation state
- make the implemented/optional/future distinctions explicit and internally consistent
- keep the bilingual plan semantically aligned
- improve operator trust in the implementation plan as a canonical reality map

**Non-Goals:**

- rewriting the whole plan from scratch
- broad governance rewrites outside the team-mode line
- behavior changes unless the audit uncovers a true plan-to-runtime contradiction

## Decisions

### Decision 1: Treat the implementation plan as a canonical state map, not just a brainstorming document

The plan should not merely preserve ideas. It should accurately show:

- what is implemented now
- what is optional but available
- what is still future

### Decision 2: Sync based on actual generated assets and main specs, not on memory

The sync pass should use current generated user-level surfaces, main specs, and archived changes as evidence.

This avoids carrying forward outdated roadmap wording after implementation has already moved.

### Decision 3: Preserve optional future sections, but clearly label them as optional future layers

The plan should still keep optional future paths such as mixed persistent pane compose, but those sections must remain clearly outside the currently implemented default lane.

### Decision 4: Keep bilingual parity strict

The English and Chinese plan files should stay semantically aligned.

If one side has newer status wording than the other, the lagging side should be treated as incomplete.

## Risks / Trade-offs

- [Risk] A sync pass may accidentally turn the implementation plan into a changelog. → Mitigation: keep the plan high-signal and phase-oriented, not file-by-file.
- [Risk] Status language can drift again after later implementation work. → Mitigation: add an explicit doc-sync capability so this remains a recognized maintenance responsibility.
- [Risk] Optional future layers may be over-promoted. → Mitigation: preserve the default path vs optional path distinction explicitly.

## Migration Plan

1. Audit the bilingual plan against current installed and specified surfaces.
2. Update stale roadmap markers and operator-facing status wording.
3. Re-run OpenSpec validation.
4. Keep future implementation batches responsible for resync when they materially change the operator model.

## Open Questions

- Should the plan include a small “last validated against implementation on <date>” marker?
- Should future runtime-affecting changes be required to update the plan in the same change by policy?
