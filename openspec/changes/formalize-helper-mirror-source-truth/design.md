## Context

The current user-level helper mirror model installs scripts under the user Codex home so multiple projects can call the same helper surface. That is useful for daily work, but it creates a naming risk: a generated helper can be mistaken for the authoritative implementation source or for a global durable-state root.

The active implementation plan now defines MR5 as the slice that makes this boundary explicit. `tools/install-codex-user-level-team-mode.ps1` is the repository source script that generates helper scripts. `codex-durable-state-status.ps1` is one generated helper and should expose the boundary because it is the canonical read-only durable-state inspection entrypoint.

## Goals / Non-Goals

**Goals:**

- Add machine-readable helper mirror provenance to generated durable-state status output.
- Keep the provenance read-only and independent of any `.omx/state/` mutation.
- Make the metadata clear enough for a cold-start model to identify repository source, generated helper status, and repo-local durable truth.
- Add regression tests for the new fields.

**Non-Goals:**

- Do not install or refresh real user-level helpers in this MR.
- Do not modify `C:\Users\lenovo\.codex\config.toml`.
- Do not delete or rewrite any consumer repository `.omx/state/` directory.
- Do not start native OMX, LangGraph, or durable teams.

## Decisions

- Expose a `helper_mirror_source_of_truth` object in `codex-durable-state-status.ps1` JSON output. Rationale: the durable-state status helper is the canonical cold-start inspection surface, so the provenance must be visible there without requiring a separate command.
- Include the same object in the routing policy contract where practical. Rationale: routing policy already explains operator and repository authority boundaries.
- Use stable strings instead of absolute source checkout paths. Rationale: installed helpers are shared across repositories; absolute paths can be stale or machine-specific, while repository-relative source names and state-scope rules stay stable.
- Add tests at installer level. Rationale: generated helper content is produced by the installer script, so the regression must verify the generated output, not only the source text.

## Risks / Trade-offs

- Risk: adding another status field could confuse scripts that assume a fixed output shape. Mitigation: add a new field without renaming or removing existing fields.
- Risk: provenance wording could be treated as policy only. Mitigation: enforce it through tests against generated helper output.
- Risk: helper metadata could imply this repository owns other project state. Mitigation: explicitly state that consumer projects keep independent repo-local `.omx/state/` truth.

## Migration Plan

- Add source code and tests in this repository.
- Merge through GitLab-first MR.
- Future installer runs will regenerate the user-level helper with the new metadata.
- Reverting the MR removes the metadata without touching durable state.

## Open Questions

- Whether future MR6 should require all generated helper wrappers, not just durable-state status, to expose a shared provenance header or JSON object.
