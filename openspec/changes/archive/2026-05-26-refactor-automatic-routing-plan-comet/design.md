## Context

This is a documentation-only Comet tweak. The target plan is already the active baseline for automatic collaboration routing, but the latest follow-up notes make the document hard to scan: current completion evidence, Phase 4 planned work, evidence contracts, task list, risks, and acceptance criteria are all present but not clearly separated for cold-start readers.

The current Windows shell does not expose `bash`, so Comet shell helpers such as `comet-state.sh` and `comet-guard.sh` cannot be executed directly. The fallback is to keep explicit OpenSpec artifacts, `.comet.yaml` state with a blocker note, and repository validation evidence instead of claiming script transitions succeeded.

## Goals / Non-Goals

**Goals:**

- Add an explicit reading map and Comet refactor note near the top of the plan.
- Clarify that Phase 0-3 are complete while Phase 4 remains a planned follow-up.
- Make Phase 4 easier to implement by summarizing its future change id, checker set, evidence contracts, and non-evidence boundaries before the detailed tasks.
- Preserve UTF-8 content and avoid copying mojibake from terminal rendering.

**Non-Goals:**

- No runtime implementation.
- No new checker, fixture, or CI wiring.
- No stable governance policy rewrite.
- No local-main integration or remote publication.

## Decisions

- Use Comet `tweak` because the change is a bounded single-document refactor with no new capability, architecture, interface, or dependency.
- Keep the existing Phase 4 implementation package as planned follow-up, not current runtime evidence.
- Record Comet helper unavailability as a blocker rather than pretending shell state transitions ran.
- Keep local validation as the acceptance surface for this feature branch.

## Risks / Trade-offs

- [Risk] Readers may mistake a documentation refactor for Phase 4 implementation. -> Mitigation: state that no runtime checker or durable team evidence is added by this tweak.
- [Risk] The large document can still contain repeated historical sections. -> Mitigation: add an authoritative reading map and status matrix instead of deleting historical evidence during a small tweak.
- [Risk] Terminal mojibake can be copied into the file. -> Mitigation: read/write with explicit UTF-8 and run mojibake/startup guards.

## Migration Plan

No migration is required. Rollback is a normal Git revert of the feature-branch commit.

## Open Questions

- Whether to later rewrite the English companion into the same structure is outside this tweak and should be handled by a separate change if needed.
