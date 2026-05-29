# Automatic Routing Plan Full Comet Refactor Design

Change: `refactor-automatic-routing-plan-full-comet`
Status: implemented and archived with `openspec/changes/archive/2026-05-27-refactor-automatic-routing-plan-full-comet/`

## Context

The user requested a complete `/comet` refactor of `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` and a local Git commit. The previous pass was a Comet tweak, so this design upgrades the traceability level without changing runtime behavior.

## Selected Approach

Use a documentation-only full Comet workflow with targeted structural edits.

- Keep existing automatic orchestration policy content intact.
- Add full Comet framing, artifact paths, and evidence boundaries to the Chinese plan.
- Update the English companion with matching high-level framing to avoid bilingual drift.
- Create OpenSpec and Superpowers artifacts so future maintainers can audit why the refactor happened.
- Record `bash_unavailable_in_current_windows_shell` instead of claiming Comet shell guard transitions ran.

## Alternatives

1. Repeat a tweak-level cleanup. Rejected because the user requested complete `/comet`.
2. Rewrite the whole plan from scratch. Rejected because it would create avoidable policy-drift risk.
3. Targeted full-workflow documentation refactor. Selected because it satisfies traceability while preserving stable policy content.

## Scope

In scope:

- Chinese target implementation plan full Comet framing.
- English companion high-level alignment.
- OpenSpec proposal/design/tasks/delta spec.
- Superpowers design and implementation plan.
- Verification and archive evidence.

Out of scope:

- Phase 4 checker implementation.
- Runtime worker/team launch.
- User-level asset mutation.
- Local-main integration or remote publication.

## Acceptance

- The Chinese plan says this work is a full Comet documentation refactor, not a tweak.
- The plan identifies full Comet artifact paths.
- The English companion has matching high-level framing.
- Validation results are recorded before commit.
- The final report distinguishes documentation evidence from runtime evidence.

## Self-Review

- No placeholders remain.
- Runtime non-evidence boundary is explicit.
- Phase 4 remains planned follow-up.
- The design is small enough for a single implementation plan.
