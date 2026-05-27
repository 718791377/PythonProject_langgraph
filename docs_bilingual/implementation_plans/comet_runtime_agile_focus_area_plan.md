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
