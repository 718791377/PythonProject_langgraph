# Automatic Routing Plan Full Comet Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for inline execution. This plan is documentation-only and uses a single isolated feature worktree; no durable/persistent team is selected because the task has one serialized document-maintenance slice.

**Goal:** Refactor the automatic orchestration routing enforcement plan through a full `/comet` documentation workflow and commit the result locally.

**Architecture:** Keep the existing policy baseline intact while adding full Comet traceability at the document and workflow-artifact layers. OpenSpec owns the WHAT artifacts; Superpowers owns the HOW artifacts; repository validation owns acceptance evidence.

**Tech Stack:** Markdown, OpenSpec CLI, PowerShell, Python repository checkers, local CI scripts.

---

## File Structure

- Modify: `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` - primary Chinese target plan.
- Modify: `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md` - English companion high-level alignment.
- Create: `openspec/changes/refactor-automatic-routing-plan-full-comet/proposal.md` - change motivation and scope.
- Create: `openspec/changes/refactor-automatic-routing-plan-full-comet/design.md` - design decisions and alternatives.
- Create: `openspec/changes/refactor-automatic-routing-plan-full-comet/tasks.md` - completion checklist.
- Create: `openspec/changes/refactor-automatic-routing-plan-full-comet/specs/automatic-orchestration-plan-doc-refactor/spec.md` - delta requirements.
- Create: `openspec/changes/refactor-automatic-routing-plan-full-comet/management.md` - Comet management checklist.
- Create: `openspec/changes/refactor-automatic-routing-plan-full-comet/verification.md` - verification report.
- Create: `docs/superpowers/specs/2026-05-27-automatic-routing-plan-full-comet-refactor-design.md` - Superpowers design doc.
- Create: `docs/superpowers/plans/2026-05-27-automatic-routing-plan-full-comet-refactor.md` - this implementation plan.

## Task 1: OpenSpec and Superpowers Artifacts

- [x] Create the full OpenSpec change directory and `.openspec.yaml`.
- [x] Write `proposal.md`, `design.md`, `tasks.md`, `management.md`, and `verification.md`.
- [x] Write the delta spec under `specs/automatic-orchestration-plan-doc-refactor/spec.md`.
- [x] Write the Superpowers design document and this implementation plan.

## Task 2: Document Refactor

- [x] Update the Chinese plan frontmatter version/date.
- [x] Replace the previous tweak note with a full Comet refactor reading path and artifact map.
- [x] Add the Phase 4 boundary note that this refactor is not runtime evidence.
- [x] Update the English companion with matching high-level framing and cold-start/full-Comet notes.

## Task 3: Verification

- [x] Run `git diff --check` and record the result in `verification.md`.
- [x] Run `openspec validate --all` and record the result.
- [x] Run startup/mojibake and canary guards and record the result.
- [x] Run precommit/archive guard and OpenSpec guard and record the result.
- [x] Run local gate and record the result.

## Task 4: Archive and Commit

- [x] Archive the change with `openspec archive refactor-automatic-routing-plan-full-comet --skip-specs --yes` after validation.
- [ ] Commit locally on `docs/refactor-automatic-routing-plan-comet` with a Chinese commit message.
- [ ] Run local MR review after the commit and report the result.

## Self-Review

- Spec coverage: all acceptance criteria map to Tasks 1-4.
- Placeholder scan: no `TBD` or unspecified implementation steps remain.
- Scope check: this is a single documentation-maintenance change, so it does not need decomposition.
