---
doc_id: reference6_reference7_user_project_live_runtime_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/reference6_reference7_user_project_live_runtime_plan.md
---

# Reference 6/7 用户级与项目级 Live Runtime 计划

## 目标

This zh-CN companion records the same controlled plan as the English primary: implement `reference_files/6.md` and `reference_files/7.md`, update `D:/PythonProject_General` and `D:/PythonProject_General_2`, and obey `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

The raw `reference_files/7.md` stays ignored. The committed structured manifest is `docs_bilingual/reference_manifests/reference7_capability_sources.json`.

## 当前状态

<!-- CURRENT_STATUS_START -->

- 2026-06-17: Reference 6 already has runtime/checker/test surfaces and must be revalidated.
- 2026-06-17: Reference 7 was reread and converted into a committed structured manifest.
- 2026-06-17: User requirement update: all non-Codex upstream projects require a Codex fork/adapter before Codex live-executed status, not only Claude Code-only projects.

- 2026-06-17: Reference 7 runtime/checker/test surfaces are implemented; 25/25 capabilities are `R6 live-executed` only through Codex adapter/fork surfaces, with raw upstream live-executed evidence rejected.
- 2026-06-17: User-level Codex adapters were applied with hash-redacted receipts; General commit `0000634` and General_2 commit `2d07680` carry the template sync evidence.
- 2026-06-18: Final current-state audit revalidated Reference 6 user-level install/smoke receipts, Reference 7 user-level live-executed receipts, template sync, and local main integration; remote publication remains not authorized.

<!-- CURRENT_STATUS_END -->

## 任务 Backlog

<!-- TASK_BACKLOG_START -->

- [x] Capture Reference 6 status and keep the existing Reference 6 checker in scope.
- [x] Convert ignored `reference_files/7.md` into committed structured manifest `docs_bilingual/reference_manifests/reference7_capability_sources.json`.
- [x] Freeze the hard rule that every non-Codex upstream requires a Codex fork/adapter before live-executed status.
- [x] Merge this plan package into local `main`.
- [x] Implement Reference 7 runtime, checker, tests, user-level adapters, and receipts.
- [x] Sync `D:/PythonProject_General` active templates and `D:/PythonProject_General_2` inert templates.
- [x] Run source, user-level, and template gates; merge implementation to local `main` and stop before remote publication.

<!-- TASK_BACKLOG_END -->

## 证据索引

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

## 非 Codex upstream 硬规则

All upstream projects that are not already Codex-native must be forked or adapted into a Codex project surface before Codex completion can be claimed. This covers Claude Code projects, generic CLI tools, desktop apps, MCP servers, skill packs, templates, and other agent frameworks.

Counted Codex surfaces are Codex `SKILL.md`, Codex native agent TOML with `name`/`description`/`developer_instructions`, Codex runtime wrapper/checker with redacted receipts, or Codex template adapters in General/General_2.

Raw upstream install only, raw upstream install, `.claude/agents`, Claude hooks, non-Codex agent config, desktop install, MCP install, or generic CLI install without a Codex adapter is not completion evidence.

## Reference 6 status

Reference 6 source surfaces remain `tools/reference6_capability_install.py`, `tools/reference6_capability_install/manifest.json`, `tools/check_reference6_capability_install.py`, `test/reference6_capability_install.test.py`, and the existing Reference 6 implementation plan.

External live smoke user actions are explicit: `setx MINERU_API_KEY <secret-value>` for MinerU service smoke, and optional Browserbase keys for Browserbase full live smoke.

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

## 分层决策

- User-level: Codex skills, Codex agent adapters, wrappers, registry, smoke scripts, and receipts under the user Codex home.
- `D:/PythonProject_General`: active reusable templates/checkers/examples.
- `D:/PythonProject_General_2`: inert opt-in samples for heavy or risky surfaces.
- Source repository: runtime/checker/manifest/test/policy source of truth only.

## API key 与 config 策略

Reuse only Codex `env_key` / `env_key_name_only` names and environment presence booleans. Never copy secret values. Missing keys must produce blocker receipts with fill command, redacted verification command, and resume step. Receipts must use human-checkable labels plus hashes instead of raw private paths.

## 多阶段协同顺序

1. Freeze this bilingual plan and manifest, then merge the plan package into local `main`.
2. Implement Reference 7 runtime/checker/test with guarded apply flags.
3. Generate Codex adapter/fork surfaces for every Reference 7 source.
4. Re-run Reference 6 checks.
5. Sync General active templates and General_2 inert templates.
6. Run gates, merge implementation to local `main`, and stop at the remote-publication gate.

After plan freeze and two or more independent execution slices, durable-team adoption is allowed. Provider timeout or 503 is non-evidence and must not be counted as expert output.

## Runtime/checker requirements

Reference 7 runtime must support `plan`, `apply`, `check`, and `smoke`. Reference 7 checker must validate manifest, plan markers, registry/guard/CI registration, Codex adapter rule, user-level receipts, and template sync markers. Each capability must keep `requires_codex_adapter_before_live_executed=true` and `raw_upstream_live_executed_allowed=false` unless it is an explicit Reference 6 dedupe that reuses Codex-side Reference 6 evidence.

## 验证门禁

- Plan phase: `python tools/check_precommit_update_archive.py --root . --json`, `python tools/run_openspec_guard.py --root . --json`, and document-pair checks.
- Implementation phase: Reference 6 checker, Reference 7 checker, Reference 7 tests, OpenSpec guard, local gate, and local MR review.
- Template phase: local gates in `D:/PythonProject_General` and `D:/PythonProject_General_2`.

## 完成标准

- Plan commit is merged into local `main` before implementation starts.
- Implementation commit is merged into local `main` after gates pass.
- User-level Reference 7 Codex adapters and receipts are generated or explicit user-action blockers are recorded.
- General and General_2 are updated, clean, and locally validated.
- No remote publication is performed unless the current user message explicitly names that remote action.
