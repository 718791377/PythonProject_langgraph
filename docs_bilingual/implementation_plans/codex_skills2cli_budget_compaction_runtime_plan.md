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

The runtime remains preview-first. It may diagnose, route, soft-load, and generate visibility candidates. It may only apply or restore standalone user-skill visibility when both `--apply` and `--operator-confirmation` are present. It must not mutate user-level `config.toml`, plugin cache files, or remote refs.

## Current status

<!-- CURRENT_STATUS_START -->

- Phase A plan-freeze package was integrated into local `main` at `d9b467b`.
- Guard hotfix `b654410` is the current local `main` baseline for this runtime package.
- Phase B runtime implementation is complete in this package: `core-dev.skills-budget-triage` metadata, budget-warning intent detection, standalone user-skill pressure reporting, checker coverage, and focused tests are updated together.
- Phase B proved diagnosis and routing, but did not by itself eliminate the post-compaction warning because the dominant pressure source is still standalone user-level skills.
- Phase C is now required for the original goal: add `skills2cli visibility plan/apply/restore/status` so standalone user skills can be moved out of the startup-visible loader root into a receipt-backed user-level state library, then restored exactly from the receipt.
- The runtime remains safe by default: `profile suggest` and `visibility plan/status` are read-only; `visibility apply/restore` require both `--apply` and `--operator-confirmation`; no `config.toml` mutation, no plugin-cache edit, and no remote publication.
- Final local-main integration evidence is recorded by the local-main-first helper through the completed claim, rollback ref, and post-merge gate result.

<!-- CURRENT_STATUS_END -->

## Task backlog

<!-- TASK_BACKLOG_START -->

- [x] Diagnose current budget-warning routing and skill-layer counts.
- [x] Freeze this implementation plan as the Phase A local integration package.
- [x] Implement `core-dev.skills-budget-triage` routing metadata.
- [x] Implement budget-warning intent detection and standalone skill-pressure reporting.
- [x] Extend checkers/tests and integrate the runtime package into local `main`.
- [ ] Implement Phase C `skills2cli visibility` commands for reversible standalone user-skill reduction.
- [ ] Install the updated user-level `skills2cli` wrapper and apply a receipt-backed `core-dev` visibility reduction.
- [ ] Restart or fresh-launch Codex to verify the startup/compaction skills-budget warning is gone or materially reduced.

<!-- TASK_BACKLOG_END -->

## Evidence index

<!-- EVIDENCE_INDEX_START -->

- Baseline command: `python -X utf8 tools/skills2cli.py profile suggest --query "Codex compaction exceeded skills context budget additional skills removed" --json`.
- Baseline finding: `web-saas` ranked above `core-dev` for the budget-warning query before this runtime package.
- Baseline command: `python -X utf8 tools/skills2cli.py index --json`.
- Baseline finding: skills layer counts were `user=1009`, `plugin=364`, `repo=29`, and `system=5`.
- Runtime smoke: `python -X utf8 tools/skills2cli.py profile suggest --query "Exceeded skills context budget of 2%. All skill descriptions were removed and 1111 additional skills were not included in the model-visible skills list." --json` selects `core-dev` with scenario profile `skills-budget-triage`, task module `core-dev.skills-budget-triage`, and `user_layer_pressure=true`.
- Runtime smoke: `python -X utf8 tools/skills2cli.py profile suggest --query "<Chinese compacted-context phrase> skills context budget <Chinese over-limit phrase> 1111 additional skills" --json` selects `core-dev.skills-budget-triage` and remains preview-only.
- Warning audit evidence: `python -X utf8 tools/skills2cli.py audit warnings --since 2026-06-25 --limit 20 --json` reports budget-warning pressure and current frontmatter compatibility without raw skill bodies or raw log paths.
- Checker evidence: `python -X utf8 tools/check_skills2cli_profile_routing.py --root . --json` passes and reports installed user-level artifact drift instead of treating installed copies as current.
- Focused tests: `python -X utf8 tools/ci/run_python_tests.py --root . --pattern skills2cli.test.py` passes 27 tests; `python -X utf8 tools/ci/run_python_tests.py --root . --pattern check_skills2cli_profile_routing.test.py` passes 10 tests.
- Repository guard: `python -X utf8 tools/run_openspec_guard.py --root . --json` passes after using a long enough timeout window; the earlier 120-second timeout was not treated as success evidence.
- Phase C preview: `python -X utf8 tools/skills2cli.py visibility plan --profile core-dev --max-visible-user-skills 80 --codex-home C:\Users\lenovo\.codex --root . --json` reports `active_user_skill_count=1009`, `hidden_user_skill_count=929`, and `expected_active_user_skill_count_after_apply=80` without mutating config or plugin cache; here `active_user_skill_count` means currently visible standalone user-level skill groups before apply, `hidden_user_skill_count` means groups planned for receipt-backed hiding, and `expected_active_user_skill_count_after_apply` means the projected visible user-skill group count after applying the reversible plan.
- Phase C focused test evidence: `python -X utf8 tools/ci/run_python_tests.py --root . --pattern skills2cli.test.py` covers preview-only visibility planning plus receipt-backed apply/restore in a temporary Codex home.

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
- Standalone user skills are managed separately from plugin profiles. The runtime may generate a preview candidate for visibility reduction. Apply requires an explicit, receipt-first, reversible action, and restore must stay inside the managed `CODEX_HOME/skills/` and `CODEX_HOME/state/skills2cli/visibility-disabled/` path boundary.
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

### Visibility reduction

Add standalone visibility reporting and receipt-backed reduction:

- Count and summarize user-level standalone skills.
- Classify likely always-on core skills versus profile/task-specific skills.
- `visibility plan` and `visibility status` are read-only and must not modify the file system.
- `visibility apply` moves non-kept standalone user skill directories from `CODEX_HOME/skills/` into `CODEX_HOME/state/skills2cli/visibility-disabled/<receipt>/skills/` only when both `--apply` and `--operator-confirmation` are present.
- `visibility apply` writes a receipt with planned items before the first move, then refreshes the receipt after each successful move, so a crash window still leaves rollback evidence for moved directories.
- `visibility restore` moves directories back from the recorded receipt only when both `--apply` and `--operator-confirmation` are present.
- `visibility restore` validates the receipt path, source, destination, and top-level skill directory against the managed path boundary before moving anything; forged receipts must not move plugin cache, `config.toml`, or arbitrary paths.
- Receipt JSON is the rollback contract; helper output remains compact and path-redacted.

### Checkers and tests

Extend checker coverage so that:

- Chinese and English budget-warning queries select `core-dev` top-1.
- The selected result includes `skills-budget-triage` task-module evidence.
- `web-saas` is not top-1 for skills budget or compaction warnings.
- `full` is excluded unless explicitly requested.
- User-layer skill pressure is reported when the user layer dominates total skills.
- No profile suggestion command mutates config or plugin cache.
- `visibility apply/restore` require both the explicit apply flag and operator confirmation.
- Forged or out-of-scope receipts are rejected without moving plugin cache, `config.toml`, or other unmanaged paths.

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
python -X utf8 tools/skills2cli.py visibility plan --profile core-dev --max-visible-user-skills 80 --json
python -X utf8 tools/skills2cli.py visibility apply --profile core-dev --max-visible-user-skills 80 --apply --operator-confirmation --json
python -X utf8 tools/skills2cli.py visibility restore --receipt <receipt_id> --apply --operator-confirmation --json
python -X utf8 tools/check_skills2cli_profile_routing.py --root . --json
python -X utf8 tools/run_openspec_guard.py --root .
powershell -NoProfile -File tools/ci/local_gate.ps1
powershell -NoProfile -File tools/ci/local_mr_review.ps1
```

Acceptance criteria:

- Budget/compaction warning queries select `core-dev` top-1.
- Selected output includes a budget-triage scenario or task module.
- Layer counts expose user-level standalone skills as the dominant pressure source.
- Runtime remains preview/advisory-only unless a later explicit apply command is used; explicit apply must be receipt-backed, restorable, and leave `config.toml` plus plugin cache untouched.
- Local `main` receives both Phase A and Phase B packages after gates pass.

## Non-goals

- No GitLab/GitHub push, MR, merge, or sync.
- No plugin-cache bulk edit.
- No automatic `config.toml` mutation.
- No deletion of user-level standalone skills. Phase C may move standalone user skill directories out of the startup-visible root only through receipt-backed `visibility apply`, and must support exact restore.
- No claim that profile helpers are native expert evidence.
