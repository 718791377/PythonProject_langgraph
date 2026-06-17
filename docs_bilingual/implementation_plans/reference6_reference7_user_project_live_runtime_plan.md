---
doc_id: reference6_reference7_user_project_live_runtime_plan
lang: en
doc_class: implementation_plan
status: active
---

# Reference 6/7 User-Level And Project-Level Live Runtime Plan

## Goal

Implement `reference_files/6.md` and `reference_files/7.md` as governed user-level and project-template capability surfaces, update `D:/PythonProject_General` and `D:/PythonProject_General_2`, and keep all work inside the conflict order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

The raw `reference_files/7.md` file remains ignored. The committed structured authority for that file is `docs_bilingual/reference_manifests/reference7_capability_sources.json`.

## Current Status

<!-- CURRENT_STATUS_START -->

- 2026-06-17: Reference 6 has existing runtime/checker/test surfaces and must be revalidated in this rollout.
- 2026-06-17: Reference 7 was reread as a non-empty ignored input and converted into a committed structured manifest.
- 2026-06-17: User requirement update: every non-Codex upstream, not only Claude Code-only upstreams, must be forked or adapted into a Codex project surface before Codex live-executed status can be claimed.

- 2026-06-17: Reference 7 runtime/checker/test surfaces are implemented; 25/25 capabilities are `R6 live-executed` only through Codex adapter/fork surfaces, with raw upstream live-executed evidence rejected.
- 2026-06-17: User-level Codex adapters were applied with hash-redacted receipts; General commit `0000634` and General_2 commit `2d07680` carry the template sync evidence.
- 2026-06-18: Final current-state audit revalidated Reference 6 user-level install/smoke receipts, Reference 7 user-level live-executed receipts, template sync, and local main integration; remote publication remains not authorized.

<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [x] Capture Reference 6 status and keep the existing Reference 6 checker in scope.
- [x] Convert ignored `reference_files/7.md` into committed structured manifest `docs_bilingual/reference_manifests/reference7_capability_sources.json`.
- [x] Freeze the hard rule that every non-Codex upstream requires a Codex fork/adapter before live-executed status.
- [x] Merge this plan package into local `main`.
- [x] Implement Reference 7 runtime, checker, tests, user-level adapters, and receipts.
- [x] Sync `D:/PythonProject_General` active templates and `D:/PythonProject_General_2` inert templates.
- [x] Run source, user-level, and template gates; merge implementation to local `main` and stop before remote publication.

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

| Evidence item | Expected path or command | Status |
| --- | --- | --- |
| Plan registration | `docs_bilingual/docs_registry.yaml` | included in this plan package |
| Reference 7 structured manifest | `docs_bilingual/reference_manifests/reference7_capability_sources.json` | included in this plan package |
| Reference 6 checker | `python tools/check_reference6_capability_install.py --root . --json` | must remain passing |
| Plan guard | `python tools/run_openspec_guard.py --root . --json` | required before local merge |
| Reference 7 runtime/checker | `tools/reference7_capability_install.py`, `tools/check_reference7_capability_install.py` | implemented and registered |
| General sync | `D:/PythonProject_General` local gate | passed on synced main at `0000634` |
| General_2 sync | `D:/PythonProject_General_2` local gate | passed on synced main at `2d07680` |
| Reference 7 live evidence | `python tools/check_reference7_capability_install.py --root . --codex-home C:/Users/lenovo/.codex --require-user-level-installed --require-smoke-tested --require-live-executed --general-root D:/PythonProject_General --general2-root D:/PythonProject_General_2 --require-template-sync --json` | passed on 2026-06-18; 25/25 live-executed through Codex adapter/fork surfaces |

<!-- EVIDENCE_INDEX_END -->

## Non-Codex upstream hard rule

All upstream projects that are not already Codex-native must be forked or adapted into a Codex project surface before Codex completion can be claimed. This applies to every non-Codex project: Claude Code projects, generic CLI tools, desktop apps, MCP servers, skill packs, templates, and other agent frameworks.

Allowed counted Codex surfaces:

- Codex `SKILL.md` under the user-level skill directory or a project template.
- Codex native agent TOML with top-level `name`, `description`, and `developer_instructions`.
- Codex runtime wrapper/checker with hash-redacted receipts.
- Codex project-template adapter that is active in `D:/PythonProject_General` or inert/opt-in in `D:/PythonProject_General_2`.

Disallowed completion evidence:

- Raw upstream install only.
- `.claude/agents`, Claude hooks, non-Codex agent configs, desktop product install, MCP server install, or generic CLI install without a Codex adapter.
- Live-executed claims without checker-backed receipt and smoke evidence.

## Reference 6 status

Reference 6 already has repository runtime/checker/test surfaces:

- `tools/reference6_capability_install.py` - Reference 6 command-line runtime entrypoint.
- `tools/reference6_capability_install/manifest.json` - Reference 6 source and layer manifest.
- `tools/check_reference6_capability_install.py` - Reference 6 repository/user-level surface checker.
- `test/reference6_capability_install.test.py` - Reference 6 unit and receipt regression tests.
- `docs_bilingual/implementation_plans/reference6_user_project_capability_install_plan.md` - existing Reference 6 implementation plan.

Fresh validation in this rollout must re-run the Reference 6 checker. Known external-service blockers are explicit user actions: set `MINERU_API_KEY` for MinerU live service smoke, and optionally set `BROWSERBASE_API_KEY` plus `BROWSERBASE_PROJECT_ID` for Browserbase service smoke.

## Reference 7 structured source set

- `https://opc-skills.ft07.com/#install` - id `opc-skills-site`, family `opc`, target `user_level`, adapter `codex_skill_family_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-orchestrator` - id `opc-orchestrator`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-resource-audit` - id `opc-resource-audit`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-niche-positioning` - id `opc-niche-positioning`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-value-proposition` - id `opc-value-proposition`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-business-model-design` - id `opc-business-model-design`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-mvp-designer` - id `opc-mvp-designer`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-conversion-loop` - id `opc-conversion-loop`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-asset-ops` - id `opc-asset-ops`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/easychen/opc-methodology/skills/opc-dashboard-review` - id `opc-dashboard-review`, family `opc`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/msitarzewski/agency-agents` - id `agency-agents`, family `agent-pack`, target `user_level`, adapter `codex_agent_pack_adapter`.
- `https://github.com/alchaincyf/nuwa-skill` - id `nuwa-skill`, family `skill`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/golutra/golutra` - id `golutra`, family `cli-desktop-orchestrator`, target `project_template_general_2`, adapter `codex_template_inert_adapter`.
- `https://github.com/DeepExperience/MMSkills` - id `mmskills`, family `visual-agent-skill`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/Yuan1z0825/nature-skills` - id `nature-skills`, family `skill-collection`, target `user_level`, adapter `codex_skill_collection_adapter`.
- `https://github.com/Imbad0202/academic-research-skills` - id `academic-research-skills`, family `research-skill`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/Agents365-ai/drawio-skill` - id `drawio-skill`, family `diagram-skill`, target `user_level`, adapter `codex_skill_adapter`.
- `https://github.com/nexu-io/html-video` - id `html-video`, family `node-cli`, target `project_template_general`, adapter `codex_runtime_wrapper_adapter`.
- `https://github.com/nexu-io/nexu` - id `nexu`, family `cli-agent-bridge`, target `project_template_general_2`, adapter `codex_template_inert_adapter`.
- `https://github.com/nexu-io/html-anything` - id `html-anything-ref7`, family `duplicate-reference6`, target `project_template_general`, adapter `dedupe_to_reference6_codex_adapter`.
- `https://github.com/nexu-io/open-design` - id `open-design-ref7`, family `duplicate-reference6`, target `project_template_general`, adapter `dedupe_to_reference6_codex_adapter`.
- `https://github.com/safishamsi/graphify` - id `graphify`, family `code-graph-tool`, target `project_template_general`, adapter `codex_runtime_wrapper_adapter`.
- `https://github.com/pixel-cellar/Claude-Code-Game-Studios` - id `claude-code-game-studios-pixel-cellar`, family `game-template`, target `project_template_general_2`, adapter `codex_template_inert_adapter`.
- `https://github.com/Donchitos/Claude-Code-Game-Studios` - id `claude-code-game-studios-donchitos`, family `game-template`, target `project_template_general_2`, adapter `codex_template_inert_adapter`.
- `https://github.com/colbymchenry/codegraph` - id `codegraph`, family `code-graph-cli-mcp`, target `project_template_general`, adapter `codex_runtime_wrapper_adapter`.

## Layering decision

- User-level: Codex skill adapters, Codex agent-pack adapters, adapter registry, smoke wrappers, and receipts under the user Codex home. Native Codex binaries and core config files must not be patched.
- `D:/PythonProject_General`: active reusable template/checker/examples for safe adapters and runtime wrappers.
- `D:/PythonProject_General_2`: inert upgrade samples for heavy, risky, GUI, external-account, or non-Codex-native surfaces.
- Source repository: runtime/checker/manifest/test/policy source of truth only.

## API key and config policy

- Prefer the same environment-key shape as Codex `config.toml`.
- Reuse only `env_key` names and environment presence booleans; never copy secret values.
- Missing keys must produce a blocker receipt with fill command, redacted verification command, and resume step.
- Receipts must use human-checkable labels plus hashes, not raw private paths.

## Multi-stage collaboration order

1. Freeze this bilingual plan and the committed Reference 7 structured manifest, then merge the plan package into local `main`.
2. Implement the Reference 7 runtime/checker/test as a repository-owned source of truth. The runtime may write user-level install artifacts only with explicit `--apply --operator-confirmation` flags.
3. Generate Codex adapter/fork surfaces for each Reference 7 source. For every upstream whose native project shape is not Codex, the adapter must be the counted artifact.
4. Re-run Reference 6 checks.
5. Sync `D:/PythonProject_General` with active reusable Reference 7 template/checker/examples and sync `D:/PythonProject_General_2` with inert opt-in samples for heavy or risky surfaces.
6. Run source, user-level, General, and General_2 gates; integrate local `main`; stop at the remote-publication gate.

After the plan is frozen and at least two independent slices exist, durable-team adoption is allowed. Initial implementation slices are: user-level Codex adapters, source runtime/checker/test, General active templates, General_2 inert templates, and external credential blocker receipts. If native subagents or durable backend calls fail, their timeout or provider error is non-evidence; continue with leader-owned work and record the blocker.

## Runtime/checker requirements

- Add a Reference 7 runtime with `plan`, `apply`, `check`, and `smoke` actions.
- Add a Reference 7 checker that validates manifest, plan markers, registry/guard/CI registration, Codex adapter rule, user-level receipts, and template sync markers.
- Every capability record must include `requires_codex_adapter_before_live_executed=true` and `raw_upstream_live_executed_allowed=false`, unless it is an explicit dedupe to Reference 6 and still reuses Codex-side Reference 6 evidence.
- `R6 live-executed` is valid only when the Codex adapter/fork surface exists and the safe smoke result passes. Heavy external actions may remain `R6 blocked` only with complete blocker instructions.

## Verification gates

- Plan phase: `python tools/check_precommit_update_archive.py --root . --json`, `python tools/run_openspec_guard.py --root . --json`, and relevant document-pair checks.
- Implementation phase: Reference 6 checker, Reference 7 checker, Reference 7 tests, `python tools/run_openspec_guard.py --root . --json`, `tools/ci/local_gate.ps1`, and `tools/ci/local_mr_review.ps1`.
- Template phase: local gates in both `D:/PythonProject_General` and `D:/PythonProject_General_2` after syncing template files.

## Completion criteria

Current audit status: complete locally as of the 2026-06-18 verification pass; remote publication remains closed until an explicit remote action is requested.

- Plan commit is merged into local `main` before implementation starts.
- Implementation commit is merged into local `main` after gates pass.
- User-level Reference 7 Codex adapters and receipts are generated or explicit user-action blockers are recorded.
- General and General_2 are updated, clean, and locally validated.
- No remote publication is performed unless the current user message explicitly names that remote action.

Implementation marker: `env_key_name_only` config reuse is required.
