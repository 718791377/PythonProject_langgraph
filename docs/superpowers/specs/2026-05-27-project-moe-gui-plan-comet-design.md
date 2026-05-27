# Project MOE GUI Plan Full Comet Refactor Design

## Context

The Project MOE Agent GUI plan is a long-lived implementation plan. A previous pass aligned it with the newer executable-plan style, but this pass formalizes the work as a full Comet/OpenSpec change with explicit state, management checklist, delta spec and archive deferral.

## Design Goals

- Make the target plan readable as an executable implementation plan without requiring chat history.
- Preserve Project MOE-specific boundaries instead of copying Pi sidecar runtime assumptions.
- Keep target project readiness, GUI runtime implementation and remote publication as separate states.
- Record Windows Comet bash unavailability honestly.

## Selected Structure

The plan uses the same structural family as `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`:

- frontmatter with status/readiness/change metadata;
- review conclusion and status interpretation;
- relationship model and source-of-truth table;
- goals/non-goals;
- architecture and usage;
- install artifact and manifest contract;
- Phase 1 CLI and Phase 2 GUI contracts;
- JSON state model;
- readiness lanes;
- ordered implementation checklist;
- verification plan, related-doc rules, risk table and self-checks.

## Acceptance Criteria

- The target plan has no ambiguous claim that a target project is GUI-ready.
- The target plan names the current Comet change.
- The OpenSpec change validates.
- The precommit update/archive gate accepts the explicit archive deferral.
- The local MR review passes after commit.
