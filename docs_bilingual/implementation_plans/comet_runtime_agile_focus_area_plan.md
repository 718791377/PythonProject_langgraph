---
doc_id: comet_runtime_agile_focus_area_plan
lang: en
canonical: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
translation: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md
status: active
doc_class: implementation_plan
last_reviewed: 2026-05-27
---

# Comet Runtime Agile Focus-Area Implementation Plan

## Review Finding

The previous plan was not complete enough for execution. It was still marked `draft`, the Chinese companion contained mojibake, and the execution slices did not define enough runtime fields, gate rules, tests, rollback paths, or ownership boundaries. This version is the active implementation plan.

2026-05-27 granularity review: the plan now passes repository implementation-plan checks, but the slice-only backlog was still too coarse for an agentic worker to execute without rediscovering file ownership and test order. This revision keeps the five implementation slices and adds an explicit file map, readiness checklist, task-level backlog, command evidence, rollback rules, and local-integration sequence.

2026-05-27 completeness audit: the plan content and granularity are now implementation-ready. This audit adds no new runtime scope; it records that the active plan already contains five execution slices, Task A-E backlog items, file ownership, per-task test evidence, Chinese commit examples, local integration gates, acceptance criteria, and risk mitigations sufficient for a worker to execute without rediscovering the plan structure.

## Current Status

<!-- CURRENT_STATUS_START -->

- [x] Status: implemented-local runtime baseline; front matter and registry remain `active` because active Comet changes may still reference this implementation plan while they are in build or verification phases.
- [x] Historical evidence packages are externalized to keep routine reads lightweight.
- [x] Runtime scripts, guard/archive validators, skill instructions, policy/spec alignment, and targeted tests are present on local `main`.
- [x] 2026-06-07 closure verification records targeted Comet runtime and policy evidence; the full OpenSpec guard still reports an unrelated multi-session worktree hygiene blocker outside this plan's write set.

<!-- CURRENT_STATUS_END -->

## Objective

Upgrade Comet runtime governance from a one-way phase label into an adaptive management loop while preserving the five Comet phases:

`Open -> Design -> Build -> Verify -> Archive`

The runtime keeps the phase names, but it manages them as project-management focus areas:

- Open = Initiating
- Design = Planning
- Build = Executing
- Verify = Controlling
- Archive = Closing
- Monitoring = a cross-cutting control loop, not a sixth phase

The runtime must absorb PMBOK-style non-prescriptive management logic without requiring the literal text `PMBOK8` in runtime state, prompts, or script output.

Guard compatibility statement: Monitoring can return work from any current phase when evidence shows an earlier focus area is incomplete. The runtime must provide explicit return transitions and must not force a single waterfall pass.

## Non-Goals

- [ ] Do not replace Comet's five phases with a sixth phase.
- [ ] Do not turn the workflow into a large waterfall-only implementation.
- [ ] Do not make Monitoring a passive checklist-only review.
- [ ] Do not bypass OpenSpec artifacts for WHAT or Superpowers artifacts for HOW.
- [ ] Do not require runtime field names to contain PMP or PMBOK labels.

## Runtime Governance Principles

- [ ] Every phase must have explicit checklist evidence before a forward transition.
- [ ] Monitoring must run on every forward transition and can decide to continue, adjust the current phase, stop, or return to an earlier focus area.
- [ ] A return decision may target `open`, `design`, `build`, or `verify` when the current evidence shows that earlier work is incomplete.
- [ ] Return decisions must preserve the reason, target phase, and iteration count.
- [ ] The workflow should support agile or hybrid increments: small slices, fast feedback, and controlled rework.
- [ ] The control layer must keep OpenSpec as WHAT governance and Superpowers as HOW guidance.

## Runtime State Contract

`.comet.yaml` must include or preserve these fields:

- [ ] `management_record`: path to the per-change management checklist, normally `openspec/changes/<name>/management.md`.
- [ ] `monitoring_status`: one of `clear`, `needs_decision`, or `blocked`.
- [ ] `control_decision`: one of `continue`, `adjust-current`, `return-open`, `return-design`, `return-build`, `return-verify`, or `stop`.
- [ ] `target_phase`: `null`, `open`, `design`, `build`, or `verify`.
- [ ] `rework_reason`: `null`, `scope-gap`, `planning-gap`, `execution-gap`, `verification-gap`, `value-gap`, `risk-change`, or `stakeholder-change`.
- [ ] `iteration_count`: integer count of Monitoring-driven return iterations.

### State Invariants

- [ ] Forward transitions require `monitoring_status=clear`.
- [ ] Forward transitions require `control_decision=continue`.
- [ ] `control_decision=return-*` requires a matching `target_phase`.
- [ ] `control_decision=return-*` requires a non-null `rework_reason`.
- [ ] `monitoring_status=blocked` cannot move forward.
- [ ] A return transition increments `iteration_count` exactly once.
- [ ] A return transition must not delete existing OpenSpec or Superpowers artifacts.

### Runtime Term Notes

- [ ] `control_decision`: field that means the Monitoring control choice; return values select a rework path instead of forward progress.
- [ ] `target_phase`: field that identifies the Comet phase reached by a Monitoring return transition.
- [ ] `rework_reason`: field that records why a return transition is required.
- [ ] `iteration_count`: field that counts successful Monitoring return events.
- [ ] `return-open`, `return-design`, `return-build`, and `return-verify`: `control_decision` field values that describe return paths back to Open, Design, Build, or Verify.
- [ ] `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify`: runtime transition events that move `.comet.yaml phase` to the selected return target.

## Management Record Template

Each active change must have `management.md` with these checklist sections. Scripts may match labels by section heading and checkbox state.

```markdown
# Comet Management Record

## Open / Initiating
- [ ] Value and why are stated.
- [ ] Success criteria are measurable.
- [ ] Stakeholders, constraints, or operating boundaries are identified.

## Design / Planning
- [ ] Delivery approach is tailored: predictive, agile, or hybrid.
- [ ] Major risks and assumptions are recorded.
- [ ] Acceptance evidence path is defined.

## Build / Executing
- [ ] Execution mode is selected.
- [ ] Quality evidence is recorded: TDD, review, test, or equivalent.
- [ ] Blockers are cleared or have an explicit decision.

## Verify / Controlling
- [ ] Variance from scope, design, and acceptance criteria is checked.
- [ ] Risk and change impact are assessed.
- [ ] Control decision is recorded.

## Archive / Closing
- [ ] Value outcome is summarized.
- [ ] Lessons learned or reusable guidance are recorded.
- [ ] Delta spec sync, verification evidence, and archive path are confirmed.

## Monitoring Loop
- [ ] Current facts are checked.
- [ ] Continue, adjust, stop, or return decision is made.
- [ ] If returning, target_phase and rework_reason are recorded.
```

## Phase Gate Matrix

| Transition | Required focus-area evidence | Monitoring requirement | Allowed outcomes |
| --- | --- | --- | --- |
| `open -> design` | Open checklist checked | Monitoring checked and `continue` | Continue, adjust Open, stop |
| `design -> build` | Design checklist checked | Monitoring checked and `continue` | Continue, return-open, adjust Design, stop |
| `build -> verify` | Build checklist checked | Monitoring checked and `continue` | Continue, return-open, return-design, adjust Build, stop |
| `verify -> archive` | Verify checklist checked | Monitoring checked and `continue` | Continue, return-open, return-design, return-build, adjust Verify, stop |
| `archive -> done` | Archive checklist checked | Monitoring checked and `continue` | Complete, return-open, return-design, return-build, return-verify, stop |

## Monitoring Return Semantics

- [ ] `monitor-return-open`: use when value, success criteria, stakeholder, scope, or constraints are incomplete.
- [ ] `monitor-return-design`: use when planning, architecture, risk, acceptance evidence, or delivery approach is incomplete.
- [ ] `monitor-return-build`: use when implementation, tests, quality evidence, or blocker handling is incomplete.
- [ ] `monitor-return-verify`: use when Archive or later review finds that verification evidence must be rerun or corrected.
- [ ] After any return, the target phase must be reworked and then pass its forward gate again.
- [ ] Return loops are expected adaptive behavior and must not be treated as workflow failure by default.

## Implementation Slices

### Slice 1: State and Management Record Bootstrap

Scope:
- [x] Update `.codex/skills/comet/scripts/comet-state.sh init` to create `management.md`.
- [x] Populate new `.comet.yaml` management fields during init.
- [x] Update `.codex/skills/comet/scripts/comet-yaml-validate.sh` to validate allowed values.
- [x] Add or update fixtures for new change initialization.

Done when:
- [x] New Comet changes include `.comet.yaml` fields and `management.md`.
- [x] Existing changes can be validated without losing current metadata.
- [x] Invalid enum values fail closed.

Tests:
- [x] Initialization test for management record creation.
- [x] YAML validation test for every allowed enum.
- [x] Negative test for invalid enum and missing management record.

### Slice 2: Checklist Gate Enforcement

Scope:
- [x] Add reusable checklist parsing to `comet-guard.sh` or a helper script.
- [x] Require Open checklist before `open -> design`.
- [x] Require Design checklist before `design -> build`.
- [x] Require Build checklist before `build -> verify`.
- [x] Require Verify checklist before `verify -> archive`.
- [x] Require Archive checklist before archive completion.

Done when:
- [x] Missing checklist items block the matching transition.
- [x] Error output identifies the missing section and item.
- [x] Existing non-management checks still run.

Tests:
- [x] One passing fixture per phase.
- [x] One failing fixture per phase.
- [x] Regression test that previous guard constraints still apply.

### Slice 3: Monitoring Return Transitions

Scope:
- [x] Add `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify` to `comet-state.sh transition`.
- [x] Enforce matching `control_decision` and `target_phase`.
- [x] Require non-null `rework_reason` for return decisions.
- [x] Increment `iteration_count` on successful return.
- [x] Preserve existing artifacts and paths during return.

Done when:
- [x] Return transitions move `.comet.yaml phase` to the target phase.
- [x] Return transitions fail closed on missing target or reason.
- [x] Return loops can proceed forward again after checklist evidence is repaired.

Tests:
- [x] Return to Open from Build.
- [x] Return to Design from Verify.
- [x] Return to Build from Verify.
- [x] Return to Verify from Archive.
- [x] Iteration count increments exactly once per return.

### Slice 4: Skill Instruction Integration

Scope:
- [x] Update `comet-open` to require Open checklist evidence before leaving Open.
- [x] Update `comet-design` to require Design checklist evidence before leaving Design.
- [x] Update `comet-build` to require Build checklist evidence before leaving Build.
- [x] Update `comet-verify` to record variance, risk/change impact, and return/no-return decision.
- [x] Update `comet-archive` to require Closing checklist evidence.
- [x] Update the root `comet` skill to explain adaptive Monitoring returns.

Done when:
- [x] Skill instructions match script behavior.
- [x] Skills state that Monitoring is cross-cutting and not a sixth phase.
- [x] Skills route return decisions back to the correct phase instead of forcing waterfall progression.

Tests:
- [x] Static text checks for required runtime fields.
- [x] Static text checks for required return commands.
- [x] Manual dry-run against a sample change.

### Slice 5: Policy, OpenSpec, and Checker Alignment

Scope:
- [x] Update governance policy to describe Comet as an iterative control layer.
- [x] Update OpenSpec specs with phase checklist and return-transition scenarios.
- [x] Update `tools/run_openspec_guard.py` or related checkers to include runtime management rules.
- [x] Register new tests in `tools/ci/ci_test_manifest.json` if needed.
- [x] Keep `docs_bilingual` as English canonical plus Chinese companion.

Done when:
- [x] Policy, spec, skills, scripts, and tests describe the same runtime behavior.
- [x] The implementation plan checker passes.
- [x] Full OpenSpec guard status is recorded; current full-guard failure is unrelated multi-session worktree hygiene outside this plan's write set.

Tests:
- [x] `python tools/check_implementation_plan_rules.py --root . --json` - verifies implementation plan registry, bilingual pairing, text health, and active-plan status.
- [x] `python tools/run_openspec_guard.py --root . --skip-validate --json` - was run and currently reports an unrelated multi-session worktree hygiene blocker outside this plan's write set.
- [x] Targeted Comet runtime unit tests.

## File Responsibility Map

- [x] `.codex/skills/comet/scripts/comet-state.sh`: owns `.comet.yaml` default fields, transition events, Monitoring return transitions, and `iteration_count` mutation.
- [x] `.codex/skills/comet/scripts/comet-guard.sh`: owns forward-transition gate checks, management checklist parsing, and fail-closed diagnostic output.
- [x] `.codex/skills/comet/scripts/comet-yaml-validate.sh`: owns enum validation and cross-field invariants for `monitoring_status`, `control_decision`, `target_phase`, `rework_reason`, and `iteration_count`.
- [x] `.codex/skills/comet/scripts/comet-archive.sh`: owns archive-time Closing evidence checks and the final Monitoring decision before archive completion.
- [x] `.codex/skills/comet/SKILL.md` and `.codex/skills/comet-{open,design,build,verify,archive,hotfix,tweak}/SKILL.md`: own operator-facing workflow instructions and routing text.
- [x] `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md` and `.zh-CN.md`: own user-facing governance language.
- [x] `openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md` and `.zh-CN.md`: own stable WHAT requirements.
- [x] `test/run_openspec_guard_json.test.py`: owns guard aggregation fixture coverage when a new checker or guard dependency is added.
- [x] New targeted runtime tests, if needed, should be placed under `test/` with names that describe the checked runtime contract, then registered in `tools/ci/ci_test_manifest.json`.

## Definition of Ready Before Implementation

- [x] The implementation branch or worktree starts from current local `main`.
- [x] The active plan status remains `active` in `docs_bilingual/docs_registry.yaml`.
- [x] English canonical and Chinese companion are both updated before any runtime script changes.
- [x] The worker records whether the implementation is script-only, skill-only, or script-plus-skill.
- [x] The worker identifies the exact transition being changed before editing a script.
- [x] Each runtime behavior change has a matching test or checker update in the same commit.

## Task-Level Execution Backlog

<!-- TASK_BACKLOG_START -->

### Task A: Add runtime-state bootstrap coverage

**Files:**
- Modify: `.codex/skills/comet/scripts/comet-state.sh`
- Modify: `.codex/skills/comet/scripts/comet-yaml-validate.sh`
- Test: add or extend `test/comet_runtime_management_flow.test.py`
- Register if new: `tools/ci/ci_test_manifest.json`

- [x] Step A1: Write a failing test that initializes a sample change and asserts `.comet.yaml` contains `management_record`, `monitoring_status: clear`, `control_decision: continue`, `target_phase: null`, `rework_reason: null`, and `iteration_count: 0`.
- [x] Step A2: Run `python test/comet_runtime_management_flow.test.py -k bootstrap` and confirm the failure is caused by missing management defaults, not by test setup.
- [x] Step A3: Update `comet-state.sh` initialization so a new change writes the required fields and creates `openspec/changes/<name>/management.md` if absent.
- [x] Step A4: Update `comet-yaml-validate.sh` so missing management fields and illegal enum values fail closed with field-specific messages.
- [x] Step A5: Re-run the bootstrap test and `python tools/check_openspec_comet_superpowers_policy.py --root . --json`.
- [x] Step A6: Commit with a Chinese message that means "initialize Comet management fields".

### Task B: Enforce phase checklist gates

**Files:**
- Modify: `.codex/skills/comet/scripts/comet-guard.sh`
- Test: add or extend `test/comet_runtime_management_flow.test.py`
- Register if new: `tools/ci/ci_test_manifest.json`

- [x] Step B1: Write failing fixtures for unchecked Open, Design, Build, Verify, and Archive management sections.
- [x] Step B2: Run the targeted guard tests and confirm each transition currently passes or fails for the wrong reason.
- [x] Step B3: Add one reusable checklist parser in `comet-guard.sh`; do not duplicate per-phase parsing logic.
- [x] Step B4: Wire `open -> design`, `design -> build`, `build -> verify`, `verify -> archive`, and archive completion to the parser.
- [x] Step B5: Ensure diagnostic output names both the missing section and missing item.
- [x] Step B6: Re-run targeted tests, then run `python tools/run_openspec_guard.py --root . --skip-validate --json` if the full guard would otherwise be blocked by unrelated local state.
- [x] Step B7: Commit with a Chinese message that means "enforce phase management checklist gates".

### Task C: Implement Monitoring return transitions

**Files:**
- Modify: `.codex/skills/comet/scripts/comet-state.sh`
- Modify: `.codex/skills/comet/scripts/comet-yaml-validate.sh`
- Test: add or extend `test/comet_runtime_management_flow.test.py`

- [x] Step C1: Write failing tests for `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify`.
- [x] Step C2: Add negative tests where `target_phase` is missing, `control_decision` does not match the event, `rework_reason` is `null`, or `iteration_count` is non-numeric.
- [x] Step C3: Implement a single return helper in `comet-state.sh` that maps return events to target phases and preserves existing artifact paths.
- [x] Step C4: Increment `iteration_count` exactly once per successful return event.
- [x] Step C5: Re-run targeted tests twice to confirm repeated returns increment from `0` to `1` to `2` without resetting other fields.
- [x] Step C6: Commit with a Chinese message that means "support Monitoring return transitions".

### Task D: Align Comet skill instructions

**Files:**
- Modify: `.codex/skills/comet/SKILL.md`
- Modify: `.codex/skills/comet-open/SKILL.md`
- Modify: `.codex/skills/comet-design/SKILL.md`
- Modify: `.codex/skills/comet-build/SKILL.md`
- Modify: `.codex/skills/comet-verify/SKILL.md`
- Modify: `.codex/skills/comet-archive/SKILL.md`
- Modify if preset behavior changes: `.codex/skills/comet-hotfix/SKILL.md`, `.codex/skills/comet-tweak/SKILL.md`

- [x] Step D1: Add instruction text that Monitoring is a cross-cutting control loop, not a sixth phase.
- [x] Step D2: Add per-phase exit requirements that point to the matching management checklist section.
- [x] Step D3: Add return routing instructions so `return-open`, `return-design`, `return-build`, and `return-verify` route to the corresponding Comet phase instead of forcing forward progression.
- [x] Step D4: Run `python tools/check_openspec_comet_superpowers_policy.py --root . --json` and confirm all skill terms remain present.
- [x] Step D5: Commit with a Chinese message that means "align Comet management return instructions".

### Task E: Align policy, specs, checker coverage, and integration gates

**Files:**
- Modify: `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md`
- Modify: `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md`
- Modify: `openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md`
- Modify: `openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.zh-CN.md`
- Modify if checker terms change: `tools/check_openspec_comet_superpowers_policy.py`
- Modify if guard steps change: `tools/run_openspec_guard.py` and `test/run_openspec_guard_json.test.py`
- Register tests: `tools/ci/ci_test_manifest.json`

- [x] Step E1: Update the English policy first, then update the Chinese companion with the same governance meaning.
- [x] Step E2: Update stable OpenSpec requirements for checklist evidence, Monitoring return transitions, and non-waterfall adaptive execution.
- [x] Step E3: If a new checker is introduced, add it to `tools/run_openspec_guard.py` and mirror it in `test/run_openspec_guard_json.test.py` fixture steps.
- [x] Step E4: Run `python tools/check_implementation_plan_rules.py --root . --json`.
- [x] Step E5: Run `python tools/check_openspec_comet_superpowers_policy.py --root . --json`.
- [x] Step E6: Run `python tools/run_openspec_guard.py --root . --json` or record the exact known local-state blocker if the guard is blocked by unrelated worktree hygiene.
- [x] Step E7: Commit with a Chinese message that means "sync Comet agile management focus areas".

<!-- TASK_BACKLOG_END -->

## Local Integration Sequence

- [ ] Keep the feature worktree clean before integration: `git status --short` returns no paths.
- [ ] Run the local MR review gate against the pre-change base: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef <base-sha> -HeadRef HEAD -Json`.
- [ ] Fast-forward or merge the feature branch into local `main` only after local checks pass.
- [ ] Do not push remote unless the user explicitly asks for remote publication.
- [ ] Preserve the branch until the user decides whether to publish or clean it up.

## Completion Review Checklist

- [x] Every scope item has a matching task-level step.
- [x] Every runtime field has bootstrap, validation, and at least one negative test.
- [x] Every forward transition has both a passing and failing checklist fixture.
- [x] Every Monitoring return event has success, missing-target, missing-reason, and iteration-count evidence.
- [x] English and Chinese documents are semantically aligned.
- [x] All commits use Chinese messages.

## Acceptance Criteria

- [x] A missing Open checklist blocks the transition to Design.
- [x] A missing Design checklist blocks the transition to Build.
- [x] A missing Build checklist blocks the transition to Verify.
- [x] A missing Verify checklist blocks the transition to Archive.
- [x] A missing Archive checklist blocks archive completion.
- [x] Monitoring can return from Build to Open for unclear scope.
- [x] Monitoring can return from Verify to Design for a planning or acceptance gap.
- [x] Monitoring can return from Archive to Verify for insufficient verification evidence.
- [x] Return decisions preserve `target_phase`, `rework_reason`, and `iteration_count`.
- [x] Runtime still exposes only the five Comet phases.
- [x] Runtime output does not require the literal term `PMBOK8`.

## Evidence to Preserve

- [x] Updated plan pair: English canonical and Chinese companion.
- [x] Updated registry entry with `status: active`.
- [x] Script diffs for state, guard, archive, and validation helpers.
- [x] Skill instruction diffs for all Comet phase skills.
- [x] Test output and checker output.
- [x] Archive or closeout note after implementation is complete.

## Risks and Mitigations

- [ ] Risk: checklist parsing becomes brittle. Mitigation: centralize required item labels and test missing-item output.
- [ ] Risk: return loops hide real failure. Mitigation: require `rework_reason` and increment `iteration_count`.
- [ ] Risk: users mistake Monitoring for a sixth phase. Mitigation: keep Monitoring as transition evidence only.
- [ ] Risk: docs and runtime drift. Mitigation: checker coverage plus paired updates to skills, scripts, and specs.

## Completed Evidence Index

<!-- EVIDENCE_INDEX_START -->

Each completed package is indexed here; full evidence is preserved in the external report rather than appended to this implementation plan.

- [x] 2026-05-27 Runtime Evidence Batch: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-27 Local Execution Governance Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-27 Skill Instruction Alignment Governance Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-27 Skill Instruction Alignment Evidence: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-27 Root Comet Controller Routing Governance Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-27 Runtime Test Evidence Governance Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-27 Monitoring Decision Gate Evidence Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-28 UTF-8 Management Label Evidence Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-28 Management Record Validation Evidence Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-28 YAML Enum Validation Evidence Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-28 YAML Path Validation Evidence Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-28 Verification Report Path Validation Evidence Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.
- [x] 2026-05-28 Artifact Path Safety Validation Evidence Package: completed; evidence: `docs/superpowers/reports/2026-05-28-comet-runtime-agile-focus-area-evidence-index.md`.

- [x] 2026-06-07 Implementation Closure Verification: completed; evidence: `python test/comet_runtime_management_flow.test.py`, `python tools/check_openspec_comet_superpowers_policy.py --root . --json`, and `python tools/check_implementation_plan_rules.py --root . --json`; full `python tools/run_openspec_guard.py --root . --skip-validate --json` is currently blocked by unrelated multi-session worktree hygiene residue rather than Comet runtime content.

<!-- EVIDENCE_INDEX_END -->
