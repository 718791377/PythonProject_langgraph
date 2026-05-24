## Why

The repository currently has official OpenSpec workflow governance, generated OpenSpec skills, and Codex orchestration policy, but it does not model the Comet pattern referenced by `reference_files/2.md`: a control layer that combines OpenSpec for WHAT and Superpowers for HOW.

This change upgrades the repository's OpenSpec governance target so future OpenSpec work can be treated as a Comet-controlled OpenSpec + Superpowers workflow: stateful, resumable, guarded, and evidence-driven rather than chat-only or markdown-only.

## What Changes

- Add a new OpenSpec capability for a Comet-controlled OpenSpec + Superpowers workflow.
- Add bilingual governance guidance describing OpenSpec as the WHAT layer, Superpowers as the HOW layer, and Comet as the control/state/guard layer.
- Add a repository checker and test coverage so the new governance surface remains registered and retains the core Comet/Superpowers boundary tokens.
- Wire the checker into the repository OpenSpec guard and the existing guard JSON test coverage.
- Keep the first upgrade as repository-local governance and validation only: no global `comet` installation, no user-level plugin mutation, and no automatic rewrite of consumer-project state outside this repository.

## Capabilities

### New Capabilities
- `codex-user-level-comet-controlled-openspec-superpowers`: Defines the repository contract for a Comet-style control layer over OpenSpec and Superpowers, including phase ownership, decoupled state, transition guards, resume behavior, and adoption boundaries.

### Modified Capabilities
- `codex-user-level-skills-governance-lifecycle`: Adds a checker-backed governance surface for the Comet/OpenSpec/Superpowers workflow so skills, profiles, and native subagents remain distinct.
- `codex-user-level-openspec-code-archive-evidence`: Keeps archive and verification evidence requirements aligned with the Comet-style verify-before-archive model.

## Impact

- Affected documentation: `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md`, its Chinese companion, and `docs_bilingual/docs_registry.yaml`.
- Affected validation: new `tools/check_openspec_comet_superpowers_policy.py`, `tools/run_openspec_guard.py`, and `test/run_openspec_guard_json.test.py`.
- Affected OpenSpec artifacts: this change directory and the new delta spec.
- Non-goals: do not install `@rpamis/comet`, do not run `comet init`, do not install or mutate Superpowers plugin files, do not change consumer repositories outside this repository, and do not merge LangGraph and native_omx backend semantics.

## Rollout and Validation

- Rollout sequence: define OpenSpec artifacts, add bilingual governance, add checker/test coverage, wire guard, run targeted validation.
- Rollback plan: remove the new governance doc pair, registry entry, checker/guard/test wiring, and this OpenSpec change if validation shows the policy does not fit the repository.
- Validation path: run the new checker, its unit test, document governance check, OpenSpec validation, and the relevant guard or precommit checks.
- Mainline classification: new bounded governance/tooling slice related to OpenSpec skills governance, not a continuation of the current LangGraph mainline.
