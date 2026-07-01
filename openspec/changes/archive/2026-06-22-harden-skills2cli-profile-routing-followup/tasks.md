# Tasks: Harden Skills2CLI Profile Routing Follow-up

## Stage A: freeze follow-up contract

- [x] Create the OpenSpec follow-up change for routing hardening.
- [x] Add delta requirements for orthogonal schema fields, task-module identity, positive scenario quality, explicit `full` eligibility, no-auto-apply behavior evidence, install artifact surface reporting, and recall/rerank fail-closed behavior.
- [x] Update the bilingual implementation plan with a four-principle traceability matrix, Phase A acceptance matrix, Phase A/Phase B boundary, unified safety contract, and Phase B execution slices.
- [x] Validate the Stage A plan-freeze package and commit it on the local feature branch.
- [x] Integrate the Stage A plan-freeze package into local `main` and clean the worktree/branch.

## Stage B: implement runtime hardening

- [x] Extend `profiles.json` with orthogonal schema fields, explicit task-module identity fields, positive examples where missing, safety fields, and `full` explicit-only eligibility metadata.
- [x] Update `skills2cli_profile_registry_contract.py` to validate positive scenario quality, orthogonal field mappings, `scene_description` compatibility, task-module identity, explicit `full` eligibility terms, and install artifact surface paths.
- [x] Update `skills2cli.py profile suggest` so eligibility and ordering are separated, `full` requires explicit eligibility, negative-example evidence is visible, and no-auto-apply behavior evidence is emitted.
- [x] Update plugin-modules helper checks so `load_module` remains soft-load only and `set_plugin_profile` rejects scenario/task-module hard-load targets.
- [x] Extend `check_skills2cli_profile_routing.py`, `check_plugin_modules_skill.py`, focused tests, and CI manifest coverage.
- [x] Validate Stage B with focused tests, representative suggestions, OpenSpec guard, local gate, and local MR review.
- [x] Archive this OpenSpec change after Stage B validation and integrate the runtime package into local `main`.
