## Context

This is a documentation-only Comet tweak for the Project MOE Agent GUI toolchain plan. The target plan already records the core architecture, readiness gates, fixture evidence, and target-project repair lane. The current session also found an active ownership claim for the same target file, so the correct write surface is the existing `project-moe-agent-gui-toolchain-plan` worktree rather than a new worktree.

The current Windows shell does not expose `bash`, so Comet shell helpers such as `comet-state.sh` and `comet-guard.sh` cannot be executed directly. The fallback is to keep explicit OpenSpec artifacts and repository validation evidence rather than pretending script state transitions succeeded.

## Goals / Non-Goals

**Goals:**

- Update the plan so cold-start readers understand that the worktree was reused because ownership precheck found an active claim.
- Record that Comet was requested and used as the traceability layer for this small documentation tweak.
- Keep `status: draft` and explain why repository fixture readiness is not the same as real target-project GUI readiness.
- Preserve the local-main-first and remote-publication approval boundaries.

**Non-Goals:**

- No runtime implementation.
- No target-project mutation.
- No real GUI launch, installation, or control.
- No global/user-level Codex configuration change.
- No forced archive if Comet shell scripts remain unavailable.

## Decisions

- Use the existing claimed worktree instead of creating a new worktree, because the ownership precheck classified the target file as in-progress.
- Treat this as a Comet `tweak` rather than a full design/build wave, because the change is a single-document local optimization with no new capability, architecture, interface, dependency, or spec-level behavior.
- Use OpenSpec artifacts plus repository gates as the traceable fallback when `bash` is unavailable for Comet state scripts.
- Keep the plan in `draft`, because real target-project readiness and visible GUI/control evidence still have explicit gates.

## Risks / Trade-offs

- [Risk] Comet shell state is not machine-transitioned in this shell. → Mitigation: record the blocker and keep artifact files plus validation outputs as the evidence trail.
- [Risk] Readers may confuse fixture-level readiness with target-project readiness. → Mitigation: keep the warning in section 0 and section 13 explicit.
- [Risk] A duplicate future session may ignore the active claim. → Mitigation: add continuation wording that requires ownership precheck and reuse/classification of existing worktrees.

## Migration Plan

No migration is required. This is a documentation-only refresh. Rollback is a normal Git revert of the feature commit.

## Open Questions

- Whether future Comet use on Windows should install Git Bash or provide PowerShell-native state/guard wrappers is outside this tweak and should be handled by a separate change.
