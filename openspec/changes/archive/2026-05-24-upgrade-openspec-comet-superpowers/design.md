## Context

The user supplied a local video reference and `reference_files/2.md`, which points to the upstream Comet, OpenSpec, and Superpowers projects. The Comet README describes Comet as an OpenSpec + Superpowers dual-star development workflow: OpenSpec handles WHAT, Superpowers handles HOW, and Comet chains both into a five-phase automated pipeline.

This repository already owns user-level Codex orchestration governance, official OpenSpec bootstrap/update policy, generated OpenSpec skills, and checker-backed publication gates. It does not yet have a Comet/Superpowers workflow surface. The safe first step is therefore to make the Comet-style workflow explicit and checker-backed before any runtime installation or generated skill overwrite.

The local mp4 could not be fully transcribed in this session because no `OPENAI_API_KEY` was available for the transcribe skill and the local ffmpeg shim was not runnable from the sandbox. The design therefore uses the mp4 file name as topic evidence and uses `reference_files/2.md` plus upstream project READMEs for concrete behavior.

## Goals / Non-Goals

**Goals:**

- Define the repository's Comet-controlled OpenSpec + Superpowers workflow contract.
- Preserve OpenSpec as the WHAT layer and Superpowers as the HOW layer.
- Treat Comet as an additive control layer for phase dispatch, state, guards, resume, and evidence.
- Keep adoption repository-local and non-mutating until the operator explicitly approves installing or running Comet tooling.
- Add executable validation so the governance surface cannot silently drift.

**Non-Goals:**

- Do not install `@rpamis/comet` globally or locally in this change.
- Do not run `comet init`, overwrite `.codex/skills`, or install Superpowers plugin files in this change.
- Do not mutate user-level `C:\Users\lenovo\.codex\config.toml`.
- Do not modify consumer repositories outside `D:\PythonProject_langgraph`, generic project-root workspaces outside this repository, or their durable state.
- Do not change LangGraph or native_omx backend behavior.

## Decisions

### Decision 1: Add a governance policy before runtime adoption

Create `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md` and `.zh-CN.md` as the stable operator-facing policy for this workflow.

Rationale: Comet can install skills and scripts into platform directories. The repository needs an explicit boundary before allowing any install or overwrite action, especially because this repository already has generated OpenSpec skills and user-level orchestration policy.

Alternative considered: run `comet init` immediately. Rejected for this change because it would mutate generated skills or user-level/project-level assets before a write scope, rollback plan, and validation surface are defined.

### Decision 2: Use a new OpenSpec capability

Create a new capability `codex-user-level-comet-controlled-openspec-superpowers` instead of folding this into existing LangGraph, native_omx, or skills-governance specs.

Rationale: The Comet pattern is related to skills governance and OpenSpec archive evidence, but it is a distinct workflow-control contract. A dedicated capability keeps the WHAT/HOW/control-layer terms easy to find and prevents accidental backend-family mixing.

Alternative considered: modify only `codex-user-level-skills-governance-lifecycle`. Rejected because the workflow spans OpenSpec lifecycle, Superpowers methodology, state/resume, and archive evidence, not just skills inventory.

### Decision 3: Add a focused checker and guard wiring

Create `tools/check_openspec_comet_superpowers_policy.py` and extend the existing guard JSON unit test module. The checker validates:

- the bilingual policy files exist;
- the docs registry contains the governance entry;
- the English policy retains ASCII-only required boundary terms;
- the Chinese policy retains the corresponding Comet/OpenSpec/Superpowers workflow terms;
- the OpenSpec delta spec exists while the change is active, or the promoted stable spec exists after archive.

Rationale: The repository instruction surface requires durable safety boundaries to be backed by scripts where practical. A small checker is enough for this first governance upgrade and avoids depending on a live Comet runtime.

Alternative considered: rely only on document review. Rejected because the repository already guards governance surfaces with scripts.

### Decision 4: Keep Comet runtime installation as a future explicit adoption gate

The policy should name `@rpamis/comet`, `comet init`, `comet status`, `comet doctor`, and `comet update`, but it should not make those commands the default repository runtime yet.

Rationale: Comet is an external package and may write to platform skill directories. Future adoption should use a separate OpenSpec change with dry-run/preview evidence, a clear project-local versus user-level write plan, and rollback instructions.

Alternative considered: declare Comet the immediate default. Rejected because the repo has an existing official OpenSpec surface and no evidence yet that Comet-generated files are compatible with all local guard checks.

## Risks / Trade-offs

- [Risk] The change may look like a full Comet runtime installation even though it is only governance and validation. -> Mitigation: document non-goals and final status clearly.
- [Risk] The policy may duplicate existing OpenSpec official workflow policy. -> Mitigation: keep the new policy focused on Comet/OpenSpec/Superpowers layer mapping, not official OpenSpec command semantics.
- [Risk] A checker that searches for terms can become brittle. -> Mitigation: check only cold-start-critical boundary terms and file/registry presence.
- [Risk] Video details may contain additional behavior not captured in README. -> Mitigation: record the evidence boundary and leave runtime interaction details for a later video-transcription follow-up if needed.

## Migration Plan

1. Create the OpenSpec change artifacts and delta spec.
2. Add bilingual governance docs and registry entry.
3. Add the checker and focused test coverage.
4. Wire the checker into `tools/run_openspec_guard.py` and the guard JSON test.
5. Run targeted validation.

Rollback: remove the new docs, registry entry, checker, tests, guard step, manifest entry, and OpenSpec change directory.

## Open Questions

- Whether a later change should install `@rpamis/comet` and run `comet init` in project scope after a dry-run or throwaway-clone compatibility check.
- Whether the local video should be transcribed later and compared against the README-derived policy.
- Whether hotfix/tweak presets should be mapped onto this repository's local-main-first publication workflow in a future runtime adoption change.
