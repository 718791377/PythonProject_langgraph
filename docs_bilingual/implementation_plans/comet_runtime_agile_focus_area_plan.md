---
doc_id: comet_runtime_agile_focus_area_plan
lang: en
canonical: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
translation: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md
status: draft
doc_class: implementation_plan
---

# Comet Runtime Agile Focus-Area Implementation Plan

## Goal
Turn Comet runtime management from a linear phase label into an iterative control loop. The runtime keeps the five Comet phases, but Monitoring can return work from any current phase to any earlier phase that needs correction.

## Runtime Model

- [ ] Add a per-change `management.md` record with phase checklists.
- [ ] Extend `.comet.yaml` with `management_record`, `monitoring_status`, `control_decision`, `target_phase`, `rework_reason`, and `iteration_count`.
- [ ] Keep Monitoring as cross-cutting runtime behavior, not a sixth Comet phase.
- [ ] Support return transitions: `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify`.

## Phase Checklists

- [ ] Open: value, success criteria, stakeholders or constraints.
- [ ] Design: tailored delivery approach, risks and assumptions, acceptance evidence path.
- [ ] Build: execution mode, quality evidence, blockers cleared or decided.
- [ ] Verify: variance check, risk/change impact, control decision.
- [ ] Archive: value outcome, lessons learned, archive/sync evidence.
- [ ] Monitoring: facts checked, return decision made, target/reason recorded when returning.

## Implementation Slices

- [ ] Slice 1: initialize management state and record files.
- [ ] Slice 2: add hard phase checklist gates.
- [ ] Slice 3: add Monitoring return transitions and iteration tracking.
- [ ] Slice 4: update Comet skill instructions.
- [ ] Slice 5: update governance, OpenSpec specs, checker, and tests.

## Acceptance

- [ ] Missing required checklist items block forward transition.
- [ ] A return decision can move work back to Open, Design, Build, or Verify.
- [ ] Returning increments `iteration_count` and preserves `rework_reason`.
- [ ] Archive is blocked until closing evidence exists.
- [ ] No runtime field depends on the literal term `PMBOK8`.
