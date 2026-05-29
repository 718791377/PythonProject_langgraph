---
change: refactor-general-template-plans-comet
design-doc: docs/superpowers/specs/2026-05-27-general-template-plan-refactor-design.md
base-ref: ab5e1c1
archived-with: openspec/changes/archive/2026-05-27-refactor-general-template-plans-comet
---

# General Template Plan Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans` for this single-slice documentation refactor; native subagent fan-out is unnecessary.

**Goal:** Refactor the two Chinese General template implementation plans so they are decision-complete, UTF-8 clean, and aligned with full Comet governance.

**Architecture:** Keep `PythonProject_General` and `PythonProject_General_2` as distinct capability tiers. Record durable reusable requirements in OpenSpec and use the two plan documents as the operator-facing implementation handoff.

**Tech Stack:** Markdown, OpenSpec, Comet governance artifacts, repository local CI scripts.

---

### Task 1: Establish Comet/OpenSpec evidence

**Files:**
- Create: `openspec/changes/archive/2026-05-27-refactor-general-template-plans-comet/` ? archived OpenSpec change evidence for this refactor.
- Create: `openspec/specs/codex-template-implementation-plan-governance/spec.md` ? stable reusable requirements for template implementation plans.
- Create: `docs/superpowers/specs/2026-05-27-general-template-plan-refactor-design.md` ? Superpowers design record for the Comet design phase.

- [x] Create the OpenSpec proposal, design, tasks, management, and delta spec artifacts.
- [x] Sync the reusable requirements into the stable OpenSpec spec.
- [x] Mark the Comet archive evidence as complete after verification.

### Task 2: Refactor the two target implementation plans

**Files:**
- Modify: `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md` ? fuller General template implementation plan.
- Modify: `docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.zh-CN.md` ? local-only General_2 implementation plan.

- [x] Replace stale chat-history and mojibake-prone prose with UTF-8 clean sections.
- [x] Preserve the capability-tier distinction between General and General_2.
- [x] State goals, non-goals, implementation sequence, validation commands, acceptance criteria, and rollback path.

### Task 3: Verify and commit locally

**Files:**
- Create: `docs/superpowers/verification/2026-05-27-general-template-plan-refactor-verification.md` ? verification report for the Comet verify phase.

- [x] Run targeted text-health and OpenSpec checks.
- [x] Run local CI and local MR review when the final tree is ready.
- [x] Commit the refactor to the local Git repository without remote publication.
