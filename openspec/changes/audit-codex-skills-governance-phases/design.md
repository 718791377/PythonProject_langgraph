## Context

This change is a governance correction around the Codex user-level skills governance and profiles work. Phase 0 and Phase 1 artifacts are already merged on `main`, while a follow-up Phase 2 guard integration exists in GitLab MR !6 and must remain untouched until this OpenSpec change defines the review path.

Current state:

- Phase 0 inventory exists through `tools/inventory_codex_skills.py` and `docs_bilingual/governance/codex_skills_inventory_baseline.json`.
- Phase 1 policy and registry exist through the bilingual skills governance policy, `codex_skills_profiles.registry.yaml`, and the docs registry entry.
- Phase 2 has a governance check script and tests merged, but guard/CI integration should be treated as pending normalization because MR !6 was opened before this OpenSpec change existed.
- Phase 3 cleanup is not implemented and must remain deferred until OpenSpec duplicate generation behavior is verified in a clean clone.

Constraints:

- Do not edit user-level skills under `C:\Users\lenovo\.codex\skills`.
- Do not edit plugin cache content or disable the Vercel plugin.
- Do not mutate `C:\Users\lenovo\.codex\config.toml`.
- Do not merge, close, force-push, or otherwise mutate MR !6 during this OpenSpec audit.
- Keep repository-local facts and durable state scoped to this repository.
- Keep GitLab as the review and merge surface; GitHub remains a post-merge sync target only.

Stakeholders:

- The local Codex operator, who needs predictable cold-start routing with lower skills context pressure.
- Browser-profile projects that rely on browser automation and must not lose Vercel/browser verification capabilities.
- Future implementation sessions that need clear OpenSpec-governed phase gates before cleanup or launcher integration.

## Goals / Non-Goals

**Goals:**

- Reconstruct an OpenSpec-governed lifecycle around the already-started skills governance work.
- Audit Phase 0 and Phase 1 against the implementation plan before accepting further changes.
- Define Phase 2 as a gated step that can either supersede or reuse MR !6 only after explicit user approval.
- Encode Phase 3 cleanup as deferred work with evidence requirements rather than immediate deletion.
- Preserve browser automation, OpenSpec, orchestration, durable team, and LangGraph capability surfaces while reducing context-budget pressure through policy and profile metadata.
- Make validation evidence explicit and repeatable.

**Non-Goals:**

- No user-level skill deletion, move, rename, or description rewrite.
- No plugin disablement, especially no Vercel plugin disablement for browser or web profile projects.
- No automatic launcher or `config.toml` mutation.
- No direct merge, close, or update of MR !6.
- No Phase 3 OpenSpec duplicate cleanup in this change.
- No GitHub PR workflow for this repository.

## Decisions

### Decision 1: Treat this as a cross-mainline governance correction, not a new implementation wave

The work repairs process discipline around skills governance rather than adding a new runtime feature. It should therefore produce OpenSpec artifacts that define audit and continuation gates before any further implementation.

Alternatives considered:

- Continue from MR !6 directly: rejected because it repeats the same process issue and bypasses OpenSpec review.
- Revert the merged Phase 0/1 work immediately: rejected because the merged artifacts pass local checks and can be audited without destructive rollback.

### Decision 2: Audit Phase 0/1 before normalizing Phase 2

Phase 0/1 already changed repository source of truth. The safest next step is to verify existence, registry consistency, inventory counts, duplicate reporting, and safety constraints before deciding what to do with Phase 2 guard integration.

Alternatives considered:

- Start with Phase 2 guard integration: rejected because it could codify an unreviewed baseline.
- Start with Phase 3 cleanup: rejected because cleanup is destructive and requires separate evidence.

### Decision 3: Keep MR !6 as a frozen external candidate

MR !6 should remain open but untouched while this change is authored. Its contents may later be adopted, superseded, or closed, but only after the OpenSpec artifacts define requirements and tasks and the user explicitly approves the action.

Alternatives considered:

- Close MR !6 now: rejected because the user explicitly asked to keep it.
- Merge MR !6 now: rejected because the user explicitly stopped publishing and asked for OpenSpec governance first.

### Decision 4: Model Phase 3 cleanup as evidence-gated future work

OpenSpec nested duplicate skills are known but must not be deleted until official OpenSpec generation behavior is verified through regeneration and guard checks in a clean clone. The current change can specify that requirement but must not perform the cleanup.

Alternatives considered:

- Delete nested duplicates from this change: rejected because the implementation plan requires clean-clone verification first.
- Ignore duplicates entirely: rejected because inventory and governance checks need to preserve duplicate visibility.

### Decision 5: Keep validation local until artifacts are reviewed

Because the current workspace contains unrelated local drafts, this change should use local checks for artifact drafting and defer any publish/merge/sync operation until the user approves a reviewed OpenSpec-backed branch.

Alternatives considered:

- Push every artifact as soon as it is written: rejected because the user explicitly objected to direct PR/MR creation.
- Run `--require-clean-git` in this dirty workspace: rejected because unrelated drafts would contaminate the result.

## Risks / Trade-offs

- [Risk] Existing Phase 0/1 artifacts may contain gaps despite passing current checks. -> Mitigation: tasks must include a plan-to-artifact audit matrix and explicit command evidence.
- [Risk] MR !6 may drift from the OpenSpec-approved Phase 2 requirements. -> Mitigation: treat it as a frozen candidate and decide later whether to supersede or reuse it.
- [Risk] Warning-only user skill description limits may hide future context-budget pressure. -> Mitigation: keep warnings visible and defer description edits to a separate approved phase.
- [Risk] OpenSpec duplicate cleanup may look easy but remove officially generated files. -> Mitigation: require `openspec init`, `openspec update`, file comparison, and clean-clone guard before any cleanup.
- [Risk] Local unrelated drafts can pollute validation. -> Mitigation: use targeted local checks for drafting and clean temporary clone validation when `--require-clean-git` is needed.
- [Risk] Browser or web projects may lose automation capabilities if plugin filtering is over-aggressive. -> Mitigation: preserve Vercel plugin availability for browser/web profiles until fine-grained filtering exists.

## Migration Plan

1. Complete OpenSpec artifacts for this change: proposal, spec, design, and tasks.
2. Run a Phase 0/1 audit against the merged `main` artifacts without modifying user-level skills or plugins.
3. Decide, with user approval, whether Phase 2 should:
   - reuse MR !6,
   - close MR !6 and replace it with a new OpenSpec-backed branch, or
   - defer guard integration entirely.
4. Keep Phase 3 cleanup as a separate future change unless clean-clone evidence is produced and approved.
5. Only after explicit user approval, use GitLab-first publication for any repository changes.

Rollback strategy:

- Before publication, rollback is deleting or editing this local OpenSpec change.
- If later implementation is published and fails, revert only the repository-local branch or MR involved; do not touch user-level skills or plugins.
- If MR !6 is superseded, close it with a pointer to the OpenSpec-backed replacement rather than force-updating it silently.

## Observability and Failure Classification

Validation output should distinguish:

- `error`: missing required repository artifact, same-layer duplicate not covered by policy, unknown profile tag, broken docs registry, or failed OpenSpec validation.
- `warning`: known user-level long descriptions, known OpenSpec generated duplicate candidates, plugin bundle limitations, or Vercel bulk load.
- `deferred`: Phase 3 cleanup candidates that require clean-clone OpenSpec regeneration evidence.

User-visible failure handling:

- If audit checks fail, report the exact file and phase gate that failed.
- If a warning is expected by policy, keep it visible but do not block Phase 0/1 acceptance.
- If a cleanup candidate lacks clean-clone evidence, block cleanup and leave the skill files unchanged.

## Open Questions

- Should MR !6 be reused after this OpenSpec change is complete, or should it be closed and replaced by a new branch?
- Should user-level long description warnings remain warning-only until launcher profile filtering exists, or should a later change introduce stricter per-profile budgets?
- Should the inventory baseline artifact remain a full JSON snapshot, or should future baselines use a smaller summary artifact plus generated full report outside the docs tree?
- Should the eventual Phase 3 cleanup proposal include only OpenSpec nested duplicates, or also preferred-source decisions for GitHub duplicate skills?
