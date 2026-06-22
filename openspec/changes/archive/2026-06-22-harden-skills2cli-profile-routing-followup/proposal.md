---
change_id: harden-skills2cli-profile-routing-followup
status: proposed
owner: codex
created_at: 2026-06-22
---

# Proposal: Harden Skills2CLI Profile Routing Follow-up

## Why

The previous `improve-skills2cli-profile-routing` change delivered the scenario-based profile routing baseline and archived the initial OpenSpec contract. Expert review of the landed baseline found that the runtime is useful but still needs stronger fail-closed evidence for routing quality and safety:

- positive scenario quality is described in the plan but is not fully fail-closed in the shared registry contract;
- `load_policy` mixes routing, activation, and governance semantics;
- `profile.task_module` is used as a stable logical identifier but is not yet documented as a first-class read-only routing ID;
- `full` is penalized but should be an explicit eligibility-gated troubleshooting profile;
- installed-copy drift currently focuses on `profiles.json` and should cover the full `skills2cli` artifact surface;
- no-auto-apply is represented by output flags but needs behavior-level evidence that config and plugin cache are not mutated.

## What Changes

- Freeze a follow-up contract before runtime edits.
- Add a Phase A acceptance matrix that maps scenario descriptions, layered routing, negative examples, and recall/rerank to fields, OpenSpec scenarios, and Phase B checkers.
- Define Phase A/Phase B separation so plan-freeze work cannot silently include runtime code, registry schema, helper script, checker, or install changes.
- Add a unified safety contract: local-main-first allowed, no remote publication, no `config.toml` mutation, no plugin cache/vendor `SKILL.md` mutation, and no profile apply without a later explicit apply receipt.
- Require Phase B to add orthogonal schema fields, first-class `profile.task_module` semantics, explicit `full` eligibility gating, full install artifact drift reporting, and behavior-level no-auto-apply tests.

## Out of Scope

- Remote publication, GitLab MR creation or merge, GitHub sync, or remote ref mutation.
- Editing `C:\Users\lenovo\.codex\config.toml`.
- Bulk-editing plugin cache or vendor `SKILL.md` files.
- Automatically applying any hard-load profile.
- Treating skills, profiles, or helper invocation as native subagent/expert evidence.
