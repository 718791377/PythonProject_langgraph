## Context

The previous `define-durable-routing-smoke-gate-release` change established R0.6 as the next read-only gate. The operator then asked whether the path to R2.0 can be split even more finely. This change records that finer release-train structure before any runtime smoke work begins.

## Goals / Non-Goals

**Goals:**

- Make R0.6 through R2.0 small enough that a future session can open one OpenSpec change per slice.
- Keep the immediate next work focused on R0.6.0 and R0.6.1.
- Keep the production durable-team plan as draft-only north-star material.
- Preserve the default read-only boundary until an operator explicitly authorizes mutation.

**Non-Goals:**

- Do not run durable routing helpers in apply mode.
- Do not start, stop, or reuse a durable team.
- Do not edit repo-local durable state.
- Do not archive this change until its docs/spec updates have landed through GitLab-first review.

## Decisions

1. Use subrelease labels such as R0.6.0 and R0.6.1.
   - Rationale: subrelease labels are easier for cold-start sessions to scope than a broad R0.6 label.

2. Treat each subrelease as one reviewed OpenSpec change by default.
   - Rationale: one small change per slice keeps GitLab MR review, validation, and rollback bounded.

3. Keep R2.0 split into readiness, memory, recovery, security, performance, dashboard, maintenance, and final-release slices.
   - Rationale: the production target is too broad to implement safely as one milestone.

## Risks / Trade-offs

- [Risk] More slices create more planning overhead. -> Mitigation: each slice should be small and mostly mechanical.
- [Risk] Release labels may drift from implementation reality. -> Mitigation: archive each slice through OpenSpec and keep startup summaries synchronized only after validation.
- [Risk] Future sessions may treat a roadmap entry as permission to mutate state. -> Mitigation: every slice keeps an explicit operator consent boundary.
