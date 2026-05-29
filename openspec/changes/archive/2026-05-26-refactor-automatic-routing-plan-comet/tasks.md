## 1. Comet Artifact Setup

- [x] 1.1 Create lightweight OpenSpec change `refactor-automatic-routing-plan-comet` for the Comet-requested documentation refactor.
- [x] 1.2 Record proposal, design, minimal delta spec, and `.comet.yaml` fallback state because the current Windows shell cannot execute Comet `bash` scripts.

## 2. Plan Refactor

- [x] 2.1 Refactor `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` with reading map, Comet traceability, and Phase 4 summary.
- [x] 2.2 Preserve the completion/planned-follow-up/runtime-evidence boundaries.

## 3. Verification

- [x] 3.1 Run `git diff --check` and `openspec validate --all`.
- [x] 3.2 Run startup/canary/precommit/OpenSpec guard checks.
- [x] 3.3 Run local gate and local MR review, then commit locally on the feature branch.
