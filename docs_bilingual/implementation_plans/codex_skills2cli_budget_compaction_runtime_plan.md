---
doc_id: codex_skills2cli_budget_compaction_runtime_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_skills2cli_budget_compaction_runtime_plan.md
translation: docs_bilingual/implementation_plans/codex_skills2cli_budget_compaction_runtime_plan.zh-CN.md
status: active
doc_class: implementation_plan
created_at: 2026-06-26
---

# Skills2CLI Budget and Compaction Runtime Plan

## Summary

This plan fixes the Codex skills-context-budget warning path exposed after long-thread compaction:

```text
Exceeded skills context budget of 2%. All skill descriptions were removed and 1111 additional skills were not included in the model-visible skills list.
```

The fix is local-main-first and split into two local integration packages:

1. Freeze this plan and integrate it into local `main`.
2. Implement the live runtime, checkers, and tests, then integrate that package into local `main`.

The runtime remains preview-first. It may diagnose, route, soft-load, and generate visibility candidates, but it must not automatically mutate user-level `config.toml`, plugin cache files, remote refs, or standalone skills.

## Current status

<!-- CURRENT_STATUS_START -->

- Phase A plan-freeze package is being prepared in local worktree `docs/skills2cli-budget-compaction-plan`.
- Phase B runtime implementation has not started yet.
- Remote publication is not authorized.

<!-- CURRENT_STATUS_END -->

## Task backlog

<!-- TASK_BACKLOG_START -->

- [x] Diagnose current budget-warning routing and skill-layer counts.
- [x] Freeze this implementation plan as the Phase A local integration package.
- [ ] Implement `core-dev.skills-budget-triage` routing metadata.
- [ ] Implement budget-warning intent detection and standalone skill-pressure reporting.
- [ ] Extend checkers/tests and integrate the runtime package into local `main`.

<!-- TASK_BACKLOG_END -->

## Evidence index

<!-- EVIDENCE_INDEX_START -->

- Baseline command: `python -X utf8 tools/skills2cli.py profile suggest --query "Codex compaction exceeded skills context budget additional skills removed" --json`.
- Baseline finding: `web-saas` currently ranks above `core-dev` for the budget-warning query.
- Baseline command: `python -X utf8 tools/skills2cli.py index --json`.
- Baseline finding: skills layer counts are `user=1009`, `plugin=364`, `repo=29`, and `system=5`.

<!-- EVIDENCE_INDEX_END -->

## Current evidence

- The command `skills2cli profile suggest --query "Codex compaction exceeded skills context budget additional skills removed" --json` currently ranks `web-saas` above `core-dev` because audit usage boost wins when no budget-specific scenario terms match.
- The command `skills2cli index --json` currently reports `1407` skills: `1009` from the user layer, `364` from plugins, `29` from the repository, and `5` from the system layer.
- Repeatedly applying the `core-dev` plugin profile is not sufficient. Plugin profile hard-load can reduce plugin surface, but the current budget pressure is dominated by standalone user-level skills and compaction-time model-visible skill injection.

## Design rules

- Budget, compaction, loader, and skills-surface warnings are Codex runtime/developer-workflow troubleshooting, not Web/SaaS work.
- These warnings must route to `core-dev` and a dedicated `core-dev.skills-budget-triage` task module.
- Audit usage evidence may boost candidates only after scenario routing and safety gates. It must not override explicit budget-warning intent.
- `full` remains explicit-only and troubleshooting-only. It must not become top-1 for ordinary warning triage.
- Standalone user skills are managed separately from plugin profiles. The runtime may generate a preview candidate for visibility reduction, but apply requires a later explicit, backed-up, reversible action.
- Skills/profile helper output is workflow context only. It is not native expert/subagent evidence.

## Runtime implementation

### Profile registry

Update the plugin-modules profile registry to add:

- `core-dev.skills-budget-triage` - task module for skills budget and compaction warning triage, with route terms such as:
  - `skills context budget` - canonical English budget-warning phrase.
  - `Exceeded skills context budget` - Codex warning prefix.
  - `All skill descriptions were removed` - description-removal warning phrase.
  - `additional skills were not included` - omitted-skills warning phrase.
  - `compaction` - long-thread context compaction trigger.
  - `context compacted` - compacted-session trigger.
  - `skill descriptions removed` - compact loader symptom.
  - Chinese compacted-context phrase - represented in tests by Unicode codepoints rather than literal non-ASCII text.
  - Chinese skill-budget phrase - represented in tests by Unicode codepoints rather than literal non-ASCII text.
  - Chinese skill-context-budget phrase - represented in tests by Unicode codepoints rather than literal non-ASCII text.
- `skills-budget-triage` - scenario profile targeting `core-dev` with `soft-load` semantics.
- Unrelated-profile negative examples - prevent budget-warning text from routing to `web-saas`, `company-ops`, `market-research`, `customer-comms`, or `creative-content`.

### `skills2cli.py`

Extend profile suggestion and audit output so that:

- Budget/compaction warning queries are detected before audit boost is applied.
- Detected budget-warning intent forces or strongly gates routing to `core-dev` / `core-dev.skills-budget-triage`.
- Result JSON reports `budget_warning_intent`, layer counts, and standalone user-skill pressure.
- If `core-dev` hard-load preview is already `changed=false`, the message explains that repeating plugin-profile apply is not the primary fix.
- Output still reports `mutates_config=false`, `profile_apply_performed=false`, `edits_plugin_cache=false`, and no raw skill bodies.

### Visibility preview

Add preview-only standalone visibility reporting:

- Count and summarize user-level standalone skills.
- Classify likely always-on core skills versus profile/task-specific skills.
- Emit candidate actions in JSON/Markdown without modifying the file system.
- Require a future explicit apply receipt before changing any user-level skill visibility mechanism.

### Checkers and tests

Extend checker coverage so that:

- Chinese and English budget-warning queries select `core-dev` top-1.
- The selected result includes `skills-budget-triage` task-module evidence.
- `web-saas` is not top-1 for skills budget or compaction warnings.
- `full` is excluded unless explicitly requested.
- User-layer skill pressure is reported when the user layer dominates total skills.
- No profile suggestion command mutates config or plugin cache.

## Collaboration and execution

- Phase A is a plan-freeze package and can be executed by the main session with read-only expert review when available.
- Phase B is multi-slice implementation and should use the smallest available collaboration surface:
  - Profile registry updates.
  - `skills2cli.py` routing/audit/runtime output.
  - Checker/test updates.
  - Integration verification.
- If native expert spawning is blocked or unavailable, record the blocker and continue in the main session. Do not treat timeout or missing expert output as valid evidence.
- Durable team launch is allowed only after this plan is frozen and at least two independent write slices exist. One backend family should be used at a time.

## Test plan

Run at minimum:

```powershell
python -X utf8 tools/skills2cli.py profile suggest --query "Codex compaction exceeded skills context budget additional skills removed" --json
python -X utf8 tools/skills2cli.py profile suggest --query "Codex compaction exceeded skills context budget additional skills removed" --json
python -X utf8 tools/skills2cli.py audit warnings --since 2026-06-25 --limit 20 --json
python -X utf8 tools/check_skills2cli_profile_routing.py --root . --json
python -X utf8 tools/run_openspec_guard.py --root .
powershell -NoProfile -File tools/ci/local_gate.ps1
powershell -NoProfile -File tools/ci/local_mr_review.ps1
```

Acceptance criteria:

- Budget/compaction warning queries select `core-dev` top-1.
- Selected output includes a budget-triage scenario or task module.
- Layer counts expose user-level standalone skills as the dominant pressure source.
- Runtime remains preview/advisory-only unless a later explicit apply command is used.
- Local `main` receives both Phase A and Phase B packages after gates pass.

## Non-goals

- No GitLab/GitHub push, MR, merge, or sync.
- No plugin-cache bulk edit.
- No automatic `config.toml` mutation.
- No deletion, moving, or disabling of user-level standalone skills during this implementation.
- No claim that profile helpers are native expert evidence.
