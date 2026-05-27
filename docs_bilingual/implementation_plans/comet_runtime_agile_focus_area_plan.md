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
- [ ] Update `.codex/skills/comet/scripts/comet-state.sh init` to create `management.md`.
- [ ] Populate new `.comet.yaml` management fields during init.
- [ ] Update `.codex/skills/comet/scripts/comet-yaml-validate.sh` to validate allowed values.
- [ ] Add or update fixtures for new change initialization.

Done when:
- [ ] New Comet changes include `.comet.yaml` fields and `management.md`.
- [ ] Existing changes can be validated without losing current metadata.
- [ ] Invalid enum values fail closed.

Tests:
- [ ] Initialization test for management record creation.
- [ ] YAML validation test for every allowed enum.
- [ ] Negative test for invalid enum and missing management record.

### Slice 2: Checklist Gate Enforcement

Scope:
- [ ] Add reusable checklist parsing to `comet-guard.sh` or a helper script.
- [ ] Require Open checklist before `open -> design`.
- [ ] Require Design checklist before `design -> build`.
- [ ] Require Build checklist before `build -> verify`.
- [ ] Require Verify checklist before `verify -> archive`.
- [ ] Require Archive checklist before archive completion.

Done when:
- [ ] Missing checklist items block the matching transition.
- [ ] Error output identifies the missing section and item.
- [ ] Existing non-management checks still run.

Tests:
- [ ] One passing fixture per phase.
- [ ] One failing fixture per phase.
- [ ] Regression test that previous guard constraints still apply.

### Slice 3: Monitoring Return Transitions

Scope:
- [ ] Add `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify` to `comet-state.sh transition`.
- [ ] Enforce matching `control_decision` and `target_phase`.
- [ ] Require non-null `rework_reason` for return decisions.
- [ ] Increment `iteration_count` on successful return.
- [ ] Preserve existing artifacts and paths during return.

Done when:
- [ ] Return transitions move `.comet.yaml phase` to the target phase.
- [ ] Return transitions fail closed on missing target or reason.
- [ ] Return loops can proceed forward again after checklist evidence is repaired.

Tests:
- [ ] Return to Open from Build.
- [ ] Return to Design from Verify.
- [ ] Return to Build from Verify.
- [ ] Return to Verify from Archive.
- [ ] Iteration count increments exactly once per return.

### Slice 4: Skill Instruction Integration

Scope:
- [ ] Update `comet-open` to require Open checklist evidence before leaving Open.
- [ ] Update `comet-design` to require Design checklist evidence before leaving Design.
- [ ] Update `comet-build` to require Build checklist evidence before leaving Build.
- [ ] Update `comet-verify` to record variance, risk/change impact, and return/no-return decision.
- [ ] Update `comet-archive` to require Closing checklist evidence.
- [ ] Update the root `comet` skill to explain adaptive Monitoring returns.

Done when:
- [ ] Skill instructions match script behavior.
- [ ] Skills state that Monitoring is cross-cutting and not a sixth phase.
- [ ] Skills route return decisions back to the correct phase instead of forcing waterfall progression.

Tests:
- [ ] Static text checks for required runtime fields.
- [ ] Static text checks for required return commands.
- [ ] Manual dry-run against a sample change.

### Slice 5: Policy, OpenSpec, and Checker Alignment

Scope:
- [ ] Update governance policy to describe Comet as an iterative control layer.
- [ ] Update OpenSpec specs with phase checklist and return-transition scenarios.
- [ ] Update `tools/run_openspec_guard.py` or related checkers to include runtime management rules.
- [ ] Register new tests in `tools/ci/ci_test_manifest.json` if needed.
- [ ] Keep `docs_bilingual` as English canonical plus Chinese companion.

Done when:
- [ ] Policy, spec, skills, scripts, and tests describe the same runtime behavior.
- [ ] The implementation plan checker passes.
- [ ] OpenSpec guard passes.

Tests:
- [ ] `python tools/check_implementation_plan_rules.py --root . --json` - verifies implementation plan registry, bilingual pairing, text health, and active-plan status.
- [ ] `python tools/run_openspec_guard.py --root .` - verifies OpenSpec, document governance, implementation-plan rules, and name clarity gates.
- [ ] Targeted Comet runtime unit tests.

## File Responsibility Map

- [ ] `.codex/skills/comet/scripts/comet-state.sh`: owns `.comet.yaml` default fields, transition events, Monitoring return transitions, and `iteration_count` mutation.
- [ ] `.codex/skills/comet/scripts/comet-guard.sh`: owns forward-transition gate checks, management checklist parsing, and fail-closed diagnostic output.
- [ ] `.codex/skills/comet/scripts/comet-yaml-validate.sh`: owns enum validation and cross-field invariants for `monitoring_status`, `control_decision`, `target_phase`, `rework_reason`, and `iteration_count`.
- [ ] `.codex/skills/comet/scripts/comet-archive.sh`: owns archive-time Closing evidence checks and the final Monitoring decision before archive completion.
- [ ] `.codex/skills/comet/SKILL.md` and `.codex/skills/comet-{open,design,build,verify,archive,hotfix,tweak}/SKILL.md`: own operator-facing workflow instructions and routing text.
- [ ] `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md` and `.zh-CN.md`: own user-facing governance language.
- [ ] `openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md` and `.zh-CN.md`: own stable WHAT requirements.
- [ ] `test/run_openspec_guard_json.test.py`: owns guard aggregation fixture coverage when a new checker or guard dependency is added.
- [ ] New targeted runtime tests, if needed, should be placed under `test/` with names that describe the checked runtime contract, then registered in `tools/ci/ci_test_manifest.json`.

## Definition of Ready Before Implementation

- [ ] The implementation branch or worktree starts from current local `main`.
- [ ] The active plan status remains `active` in `docs_bilingual/docs_registry.yaml`.
- [ ] English canonical and Chinese companion are both updated before any runtime script changes.
- [ ] The worker records whether the implementation is script-only, skill-only, or script-plus-skill.
- [ ] The worker identifies the exact transition being changed before editing a script.
- [ ] Each runtime behavior change has a matching test or checker update in the same commit.

## Task-Level Execution Backlog

### Task A: Add runtime-state bootstrap coverage

**Files:**
- Modify: `.codex/skills/comet/scripts/comet-state.sh`
- Modify: `.codex/skills/comet/scripts/comet-yaml-validate.sh`
- Test: add or extend `test/comet_runtime_management_flow.test.py`
- Register if new: `tools/ci/ci_test_manifest.json`

- [ ] Step A1: Write a failing test that initializes a sample change and asserts `.comet.yaml` contains `management_record`, `monitoring_status: clear`, `control_decision: continue`, `target_phase: null`, `rework_reason: null`, and `iteration_count: 0`.
- [ ] Step A2: Run `python test/comet_runtime_management_flow.test.py -k bootstrap` and confirm the failure is caused by missing management defaults, not by test setup.
- [ ] Step A3: Update `comet-state.sh` initialization so a new change writes the required fields and creates `openspec/changes/<name>/management.md` if absent.
- [ ] Step A4: Update `comet-yaml-validate.sh` so missing management fields and illegal enum values fail closed with field-specific messages.
- [ ] Step A5: Re-run the bootstrap test and `python tools/check_openspec_comet_superpowers_policy.py --root . --json`.
- [ ] Step A6: Commit with a Chinese message that means "initialize Comet management fields".

### Task B: Enforce phase checklist gates

**Files:**
- Modify: `.codex/skills/comet/scripts/comet-guard.sh`
- Test: add or extend `test/comet_runtime_management_flow.test.py`
- Register if new: `tools/ci/ci_test_manifest.json`

- [ ] Step B1: Write failing fixtures for unchecked Open, Design, Build, Verify, and Archive management sections.
- [ ] Step B2: Run the targeted guard tests and confirm each transition currently passes or fails for the wrong reason.
- [ ] Step B3: Add one reusable checklist parser in `comet-guard.sh`; do not duplicate per-phase parsing logic.
- [ ] Step B4: Wire `open -> design`, `design -> build`, `build -> verify`, `verify -> archive`, and archive completion to the parser.
- [ ] Step B5: Ensure diagnostic output names both the missing section and missing item.
- [ ] Step B6: Re-run targeted tests, then run `python tools/run_openspec_guard.py --root . --skip-validate --json` if the full guard would otherwise be blocked by unrelated local state.
- [ ] Step B7: Commit with a Chinese message that means "enforce phase management checklist gates".

### Task C: Implement Monitoring return transitions

**Files:**
- Modify: `.codex/skills/comet/scripts/comet-state.sh`
- Modify: `.codex/skills/comet/scripts/comet-yaml-validate.sh`
- Test: add or extend `test/comet_runtime_management_flow.test.py`

- [ ] Step C1: Write failing tests for `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify`.
- [ ] Step C2: Add negative tests where `target_phase` is missing, `control_decision` does not match the event, `rework_reason` is `null`, or `iteration_count` is non-numeric.
- [ ] Step C3: Implement a single return helper in `comet-state.sh` that maps return events to target phases and preserves existing artifact paths.
- [ ] Step C4: Increment `iteration_count` exactly once per successful return event.
- [ ] Step C5: Re-run targeted tests twice to confirm repeated returns increment from `0` to `1` to `2` without resetting other fields.
- [ ] Step C6: Commit with a Chinese message that means "support Monitoring return transitions".

### Task D: Align Comet skill instructions

**Files:**
- Modify: `.codex/skills/comet/SKILL.md`
- Modify: `.codex/skills/comet-open/SKILL.md`
- Modify: `.codex/skills/comet-design/SKILL.md`
- Modify: `.codex/skills/comet-build/SKILL.md`
- Modify: `.codex/skills/comet-verify/SKILL.md`
- Modify: `.codex/skills/comet-archive/SKILL.md`
- Modify if preset behavior changes: `.codex/skills/comet-hotfix/SKILL.md`, `.codex/skills/comet-tweak/SKILL.md`

- [ ] Step D1: Add instruction text that Monitoring is a cross-cutting control loop, not a sixth phase.
- [ ] Step D2: Add per-phase exit requirements that point to the matching management checklist section.
- [ ] Step D3: Add return routing instructions so `return-open`, `return-design`, `return-build`, and `return-verify` route to the corresponding Comet phase instead of forcing forward progression.
- [ ] Step D4: Run `python tools/check_openspec_comet_superpowers_policy.py --root . --json` and confirm all skill terms remain present.
- [ ] Step D5: Commit with a Chinese message that means "align Comet management return instructions".

### Task E: Align policy, specs, checker coverage, and integration gates

**Files:**
- Modify: `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md`
- Modify: `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md`
- Modify: `openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md`
- Modify: `openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.zh-CN.md`
- Modify if checker terms change: `tools/check_openspec_comet_superpowers_policy.py`
- Modify if guard steps change: `tools/run_openspec_guard.py` and `test/run_openspec_guard_json.test.py`
- Register tests: `tools/ci/ci_test_manifest.json`

- [ ] Step E1: Update the English policy first, then update the Chinese companion with the same governance meaning.
- [ ] Step E2: Update stable OpenSpec requirements for checklist evidence, Monitoring return transitions, and non-waterfall adaptive execution.
- [ ] Step E3: If a new checker is introduced, add it to `tools/run_openspec_guard.py` and mirror it in `test/run_openspec_guard_json.test.py` fixture steps.
- [ ] Step E4: Run `python tools/check_implementation_plan_rules.py --root . --json`.
- [ ] Step E5: Run `python tools/check_openspec_comet_superpowers_policy.py --root . --json`.
- [ ] Step E6: Run `python tools/run_openspec_guard.py --root . --json` or record the exact known local-state blocker if the guard is blocked by unrelated worktree hygiene.
- [ ] Step E7: Commit with a Chinese message that means "sync Comet agile management focus areas".

## Local Integration Sequence

- [ ] Keep the feature worktree clean before integration: `git status --short` returns no paths.
- [ ] Run the local MR review gate against the pre-change base: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef <base-sha> -HeadRef HEAD -Json`.
- [ ] Fast-forward or merge the feature branch into local `main` only after local checks pass.
- [ ] Do not push remote unless the user explicitly asks for remote publication.
- [ ] Preserve the branch until the user decides whether to publish or clean it up.

## Completion Review Checklist

- [ ] Every scope item has a matching task-level step.
- [ ] Every runtime field has bootstrap, validation, and at least one negative test.
- [ ] Every forward transition has both a passing and failing checklist fixture.
- [ ] Every Monitoring return event has success, missing-target, missing-reason, and iteration-count evidence.
- [ ] English and Chinese documents are semantically aligned.
- [ ] All commits use Chinese messages.

## Acceptance Criteria

- [ ] A missing Open checklist blocks the transition to Design.
- [ ] A missing Design checklist blocks the transition to Build.
- [ ] A missing Build checklist blocks the transition to Verify.
- [ ] A missing Verify checklist blocks the transition to Archive.
- [ ] A missing Archive checklist blocks archive completion.
- [ ] Monitoring can return from Build to Open for unclear scope.
- [ ] Monitoring can return from Verify to Design for a planning or acceptance gap.
- [ ] Monitoring can return from Archive to Verify for insufficient verification evidence.
- [ ] Return decisions preserve `target_phase`, `rework_reason`, and `iteration_count`.
- [ ] Runtime still exposes only the five Comet phases.
- [ ] Runtime output does not require the literal term `PMBOK8`.

## Evidence to Preserve

- [ ] Updated plan pair: English canonical and Chinese companion.
- [ ] Updated registry entry with `status: active`.
- [ ] Script diffs for state, guard, archive, and validation helpers.
- [ ] Skill instruction diffs for all Comet phase skills.
- [ ] Test output and checker output.
- [ ] Archive or closeout note after implementation is complete.

## Risks and Mitigations

- [ ] Risk: checklist parsing becomes brittle. Mitigation: centralize required item labels and test missing-item output.
- [ ] Risk: return loops hide real failure. Mitigation: require `rework_reason` and increment `iteration_count`.
- [ ] Risk: users mistake Monitoring for a sixth phase. Mitigation: keep Monitoring as transition evidence only.
- [ ] Risk: docs and runtime drift. Mitigation: checker coverage plus paired updates to skills, scripts, and specs.

## 2026-05-27 Runtime Evidence Batch

- [x] Governance-order package is recorded before non-document runtime execution.
- [x] This batch is classified as script-plus-test implementation, not a new OpenSpec scope.
- [x] No derived `openspec/` or `docs/` update is required for this batch because the active stable spec and governance policy already require management checklist evidence, Monitoring return transitions, and runtime field validation.
- [x] Expected runtime files: `.codex/skills/comet/scripts/comet-state.sh`, `.codex/skills/comet/scripts/comet-guard.sh`, and `.codex/skills/comet/scripts/comet-yaml-validate.sh`.
- [x] Expected evidence files: `test/comet_runtime_management_flow.test.py` and `tools/ci/ci_test_manifest.json`.
- [x] Acceptance evidence must include targeted Comet runtime tests, the OpenSpec Comet/Superpowers policy checker, implementation-plan rules, pre-commit update/archive review, local CI, and local MR review.

## 2026-05-27 Local Execution Governance Package

- [x] This local execution range starts with this `docs_bilingual` package before runtime script and test changes.
- [x] Scope: tighten Comet runtime Monitoring gates for forward transitions, guard diagnostics, archive closing labels, and checker fixtures.
- [x] No derived `openspec/` or `docs/` update is needed in this package because the stable policy and spec already define the management focus-area contract.
- [x] The next commit may modify runtime scripts, targeted tests, and the Comet/Superpowers policy checker fixture only.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-27 Skill Instruction Alignment Governance Package

- [x] This execution range starts with this `docs_bilingual` package before changing Comet skill instruction files.
- [x] Scope: align operator-facing Comet phase skills with the already implemented management checklist gates, Monitoring return transitions, and non-waterfall adaptive routing.
- [x] This batch is classified as skill-plus-checker implementation; it does not change runtime state-machine behavior.
- [x] No derived `openspec/` or `docs/` update is needed because the stable policy and spec already require checklist evidence, Monitoring return transitions, and adaptive/hybrid control.
- [x] Expected skill files: `.codex/skills/comet-open/SKILL.md`, `.codex/skills/comet-design/SKILL.md`, `.codex/skills/comet-build/SKILL.md`, `.codex/skills/comet-verify/SKILL.md`, `.codex/skills/comet-archive/SKILL.md`, `.codex/skills/comet-hotfix/SKILL.md`, and `.codex/skills/comet-tweak/SKILL.md`.
- [x] Expected checker evidence: `tools/check_openspec_comet_superpowers_policy.py` and `test/run_openspec_guard_json.test.py` if aggregate guard fixture output changes.
- [x] Acceptance evidence must include the Comet/Superpowers policy checker, implementation-plan rules, targeted guard fixture tests, pre-commit update/archive review, local CI, and local MR review.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.
