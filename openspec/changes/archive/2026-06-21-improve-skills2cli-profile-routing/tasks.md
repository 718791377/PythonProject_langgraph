# Tasks: Improve Skills2CLI Profile Routing

## Stage A: Freeze plan

- [x] Create the bilingual implementation plan for scenario-based profile routing.
- [x] Create this OpenSpec change with proposal, design, tasks, and delta spec.
- [x] Link the skills usage audit plan to advisory routing/rerank only.
- [x] Register the new bilingual plan in the docs registry.
- [x] Validate and commit the Stage A plan-freeze package.
- [x] Integrate the Stage A plan-freeze package into local `main`.

## Stage B: Implement live runtime

- [x] Extend `profiles.json` with scenario metadata, negative examples, ranking signals, and task modules.
- [x] Extend plugin-modules scripts for `profile.task_module` soft-load and top-level-only hard-load.
- [x] Add `skills2cli.py profile suggest` with explainable recall/rerank output.
- [x] Add checker and tests for schema, only-`full` coverage, `full` fallback discipline, and installed-copy drift reporting.
- [x] Validate runtime behavior with representative suggestions, OpenSpec guard, local CI, and local MR review.
- [x] Archive this OpenSpec change after Stage B validation and prepare the runtime package for local-main-first helper integration.
