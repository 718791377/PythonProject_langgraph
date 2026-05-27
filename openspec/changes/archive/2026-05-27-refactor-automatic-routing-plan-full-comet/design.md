## Context

The target implementation plan has become the central active baseline for automatic collaboration routing. It already contains the major policy content, but the top-level framing still described the previous work as a Comet tweak, while the current user explicitly requested a full `/comet` refactor. The refactor must therefore make the workflow evidence complete without pretending that runtime enforcement changed.

The current Windows shell does not expose `bash`; Comet shell helper scripts are present, but cannot run. The design records that blocker and uses OpenSpec/Superpowers artifacts plus repository validation as fallback evidence.

## Design Decision

Use a documentation-only full Comet workflow:

1. Keep source-of-truth policy content intact.
2. Add a full Comet reading path and artifact map to the top of the Chinese plan.
3. Update the English companion with matching high-level full Comet framing.
4. Add a Phase 4 boundary note that says the full Comet refactor is traceability evidence only, not Phase 4 implementation.
5. Create the OpenSpec and Superpowers artifacts normally required by a full workflow.
6. Archive with `--skip-specs` after validation because the change does not introduce a durable product capability or runtime contract that should be promoted into stable OpenSpec specs.

## Alternatives Considered

### Option A: Tweak again

Rejected. The user explicitly asked for complete `/comet`, and the previous archived change was already a tweak.

### Option B: Rewrite the entire long plan from scratch

Rejected. A full rewrite would create a high diff risk and could accidentally alter already-completed Phase 0-3 conclusions. The safer design is a structural full-workflow refactor that preserves existing policy content while improving the authority map and evidence boundaries.

### Option C: Documentation-only full workflow with targeted structural edits

Selected. It satisfies the full Comet traceability requirement while keeping runtime and policy behavior unchanged.

## Risks and Mitigations

- Risk: readers treat the refactor as runtime evidence. Mitigation: repeat the documentation-only and non-evidence boundary in the target plans, OpenSpec artifacts, and verification report.
- Risk: bilingual drift increases. Mitigation: update the English companion with the same high-level framing even though the user named the Chinese file.
- Risk: shell helper transitions are overclaimed. Mitigation: record `bash_unavailable_in_current_windows_shell` and do not claim guard transitions ran.
- Risk: Phase 4 appears completed. Mitigation: keep Phase 4 status as `planned follow-up` and state that checkers/fixtures are not implemented by this change.

## Acceptance Criteria

- Target Chinese plan no longer describes this work as tweak-level.
- Full Comet artifact paths are visible in the plan.
- English companion includes the same high-level framing.
- OpenSpec status for the active change reaches complete before archive.
- Validation commands are run and their outcomes are recorded before commit.
