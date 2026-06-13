# Codex Platform Project Canvas

This canvas is a lightweight alignment artifact for the Codex CLI personal production durable-team platform. It is not a replacement for the white paper, MRD, implementation plan, OpenSpec, or release evidence. It follows the `Business Management/` synthesis by keeping the platform intentionally small, mechanism-driven, outcome-measured, and repo-local.

## Source And Process Boundary

The current canvas is derived from the `fresh-source-lifecycle-whitepaper-pmi-refresh-20260613` evidence boundary in `fresh_source_reading_evidence.md`. When this canvas authorizes execution, expand the affected lifecycle layer into Inputs, Tools and Techniques, and Outputs in the relevant OpenSpec change, implementation plan, or lifecycle document rather than treating the canvas itself as the whole delivery record.

## Purpose

Build a personal production-grade Codex CLI durable-team platform that lets one maintainer work across multiple repositories without losing context, mixing repo-local durable truth, or breaking native Codex.

## Value Hypothesis

If startup context, worktree ownership, OpenSpec governance, release gates, rollback evidence, and durable-lane selection are visible and script-backed, then a solo maintainer can use native Codex, `subagent`, `native_omx`, and `langgraph` more safely across projects.

## Stakeholders

- The user/operator who decides release timing and approval gates.
- The current main Codex session that acts as leader.
- Native `subagent` roles that provide bounded expert bursts.
- Optional durable lanes such as `native_omx` and `langgraph`.
- Downstream project maintainers and future cold-start sessions.

## Boundaries

- Native Codex remains the base layer.
- User-level helpers are install artifacts, not repo-local durable truth.
- Each downstream project keeps its own OpenSpec tree, Git history, release facts, and `.omx/state/` directory.
- The long-term production durable-team plan remains a draft until release slices are promoted through OpenSpec.

## First Value Increments

- Short startup summaries and read orders that let a cold-start session recover context.
- Checker-backed safety rules that do not rely on prompt reminders alone.
- Worktree and session-ownership rules that reduce multi-session collisions.
- Read-only state inspection before any durable team is launched.
- Release slices that preserve native Codex rollback paths.

## Risks

- Hidden automation can be mistaken for governance.
- Shared user-level helpers can be mistaken for shared durable truth.
- PMBOK-derived lifecycle language can become paperwork if it is not tailored.
- Downstream project facts can leak into the platform repository if boundaries are not enforced.

## Delivery Style

Use a hybrid delivery style:

- Predictive gates for runtime entrypoints, checkers, release evidence, rollback evidence, and repository governance.
- Adaptive discovery for unclear orchestration behavior, new templates, and project-consumption feedback.
- Small release slices for implementation, validation, and learning.

## Outcome Checks

A release slice is useful only if it improves at least one of these outcomes:

- cold-start continuation success;
- operator status clarity;
- cross-session coordination quality;
- repo-local durable-truth safety;
- native Codex compatibility and rollback confidence;
- downstream adoption safety and feedback quality.
