---
doc_id: codex_skills2cli_profile_routing_runtime_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.md
translation: docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.zh-CN.md
status: final
doc_class: implementation_plan
change: improve-skills2cli-profile-routing
created_at: 2026-06-21
archived-with: 2026-06-22-harden-skills2cli-profile-routing-followup
---

# Skills2CLI Scenario-Based Profile Routing Runtime Plan

> For agentic workers: use `subagent-driven-development` or a guarded durable-team lane after this plan is frozen. Keep the plan-freeze package and live runtime package as separate local-main integration packages. Profile apply is out of scope unless a later explicit apply receipt exists.

**Goal:** optimize Codex plugin skill management by adding a scenario-entry and task-module routing layer while preserving canonical `target_profile` hard-load semantics.

**Architecture:** Phase A freezes the OpenSpec contract and bilingual implementation plan. Phase B extends the plugin-modules registry, helper scripts, `skills2cli.py`, checkers, and tests. The runtime remains advisory: it can recommend soft-load and hard-load preview candidates, but it must not edit `config.toml`, plugin cache, or hard-load profiles.

**Tech Stack:** JSON profile registry, PowerShell plugin-module helpers, Python `skills2cli.py`, repository checkers, OpenSpec, local CI and local MR review.

---

## Current Status

<!-- CURRENT_STATUS_START -->

- Baseline Stage A plan-freeze package was integrated into local `main` at `3d08d6e`.
- Baseline Phase B runtime implementation was integrated into local `main` at `80ec3dd`.
- The baseline OpenSpec change is archived at `openspec/changes/archive/2026-06-21-improve-skills2cli-profile-routing/`.
- Follow-up Phase A plan-freeze package was integrated into local `main` at `6919f0b`.
- Follow-up Phase B runtime implementation has been integrated into local `main`: `cfd6376` contains runtime hardening, `e1844fb` repairs the archive ledger, `04b8686` archives the follow-up OpenSpec change, and `bf8b380` records user-level install-sync evidence.
- Follow-up change `harden-skills2cli-profile-routing-followup` is archived at `openspec/changes/archive/2026-06-22-harden-skills2cli-profile-routing-followup/` and its stable spec has been promoted under `openspec/specs/codex-user-level-plugin-modules-profile-helper/`.
- Runtime remains advisory and preview-only: no profile apply, no `config.toml` mutation, no plugin-cache edit, and no remote publication.
- User-level live runtime install artifacts were synchronized on 2026-06-22: `skills2cli.py`, `skills2cli_profile_registry_contract.py`, and `profiles.json` now match the repository source in the installed user-level `skills2cli` helper and the installed `plugin-modules` skill registry copy.
- Installed-artifact drift is currently clean: `tools/check_skills2cli_profile_routing.py --root . --json` reports `hash_equal=true` for `skills2cli.py`, the profile registry contract module, and `profiles.json`, including the installed `plugin-modules` registry copy.
- `codex_skills_usage_audit` evidence remains advisory input for recall/rerank only; it does not authorize profile apply.
- Remote publication is not authorized.

<!-- CURRENT_STATUS_END -->

## 1. Inputs and design principles

This plan uses three inputs:

1. The local reference video filename summary: improve Agent skill hit rate by writing scenario descriptions, layered routing, negative-sample boundaries, and recall/rerank.
2. The `codex_skills_usage_audit` evidence model: strong evidence supports routing and review, but does not authorize profile apply.
3. The current `target_profile` registry: `core-dev`, `web-saas`, `company-ops`, `market-research`, `customer-comms`, `creative-content`, `pyside6-gui`, and `full` remain compatible IDs.

## 1.1 Four-principle traceability matrix

| Principle | Frozen contract | OpenSpec surface | Phase B evidence target |
| --- | --- | --- | --- |
| Scenario-based descriptions | `scene_description` is primary and `scenario_description` remains a compatibility alias. | `Scenario-based profile routing metadata` requires positive scenario evidence for profiles, scenario profiles, and task modules. | Registry checker fails closed when scenario text plus `route_when` or `positive_examples` are missing. |
| Layered routing | Canonical profile -> scenario profile -> `profile.task_module` -> skill/plugin hints. | `Task modules provide layered routing` and `Scenario profiles resolve to canonical target profiles`. | `load_module.ps1` reports `entry_kind`, `target_profile`, and `task_module`; `skills2cli profile suggest` reports profile and module matches. |
| Negative-sample boundaries | Ordinary routes require negative examples and excluded-candidate evidence. | `Scenario-based profile routing metadata` and `Profile suggestion matrix covers ordinary profiles and explicit full troubleshooting`. | Suggest output reports negative-match or eligibility reasons; ordinary rows never select `full`. |
| Recall/rerank | Recall and rerank are separate; audit evidence can boost, warning pressure can penalize, but safety gates win. | `Recall/rerank is explainable and fail-closed`. | Suggest output reports sanitized rank factors and evidence source labels without raw transcripts or private paths. |

## 2. Non-goals and safety boundaries

- Do not rename existing `target_profile` IDs in Phase B; add aliases and scenario metadata instead.
- Do not automatically apply any hard-load profile.
- Do not mutate `C:\Users\lenovo\.codex\config.toml`.
- Do not bulk-edit plugin cache files or vendor `SKILL.md` files.
- Do not make `full` a normal top-1 suggestion.
- Do not treat profile/helper invocation as native expert evidence.
- Do not push GitLab/GitHub in this implementation flow.

## 2.1 Unified safety boundary matrix

| Boundary | Allowed | Forbidden | Phase A evidence | Phase B enforcement target |
| --- | --- | --- | --- | --- |
| Advisory-only routing | Generate suggestions, soft-load guidance, and hard-load previews. | Apply a profile automatically. | Proposal/design/spec say no profile apply. | Output flags and fixture hashes prove no apply. |
| Config immutability | Read fixture or configured paths for drift reporting. | Mutate `C:\Users\lenovo\.codex\config.toml`. | Non-goal and management constraints. | No-auto-apply tests snapshot config before and after. |
| Plugin-cache immutability | Read metadata needed for reports. | Edit plugin cache or vendor `SKILL.md`. | Non-goal and management constraints. | No-auto-apply tests snapshot plugin-cache markers. |
| Remote-publication boundary | Local commits and local `main` integration after gates. | Push GitLab/GitHub, open/merge MR, or mutate remote refs. | This plan states remote publication is not authorized. | Publication helper remains unused unless a later user message names remote action. |
| `full` eligibility | Use `full` for explicit all-plugin troubleshooting. | Let broad ordinary tasks select `full` top-1. | Delta spec defines explicit-only gate. | Suggest matrix requires `excluded_candidates` when `explicit_full_request=false`. |
| Task-module activation | Soft-load `profile.task_module` guidance. | Treat task modules as hard-load targets. | Delta spec defines first-class soft-load-only identity. | `set_plugin_profile.ps1` rejects scenario/task-module inputs. |
| Expert-evidence boundary | Use skills/profile helpers as procedural context. | Treat skill/profile invocation as native subagent evidence. | Non-goal and management constraints. | Boundary checker and output flags preserve distinction. |
| Installed artifact drift | Report drift for installed helper artifacts. | Treat user-level installed copies as source of truth. | Delta spec names required artifact surface. | Checker reports repo and installed paths for `skills2cli.py`, contract module, and `profiles.json`. |

## 3. Target model

The registry must represent four layers:

1. **Canonical top-level profile** - the existing `target_profile` hard-load ID used by `set_plugin_profile.ps1` and audit candidates.
2. **Scenario profile** - a new recommendation entrypoint that resolves to a canonical `target_profile` and default task modules.
3. **Task module** - a task capability block inside a profile, such as `web-saas.mobile-app` or `core-dev.security-review`.
4. **Skill/plugin hints** - candidate plugin families and `SKILL.md` references that can be soft-loaded.

Every top-level profile and every task module must define:

- `scene_description` as the primary scenario description field, with `scenario_description` retained as a compatibility alias;
- positive routing examples or `route_when` terms;
- negative examples that exclude false matches;
- load policy: `default-candidate`, `hard-load-preview`, `soft-load`, `repo-local-only`, or `troubleshooting-only`;
- plugin hints and skill document hints when applicable;
- ranking signal notes explaining how audit evidence and warning pressure affect ordering.


## 3.1 Compatibility constraints

- `target_profile` in audit candidates and hard-load previews continues to mean an existing canonical profile ID.
- `scenario_profiles` is a new recommendation entry layer and does not replace canonical `modules`.
- `task_modules` may be embedded under a profile and resolved by runtime as `profile.task_module`.
- `set_plugin_profile.ps1` accepts only canonical top-level profiles; scenario or task-module input must fail closed.
- `load_module.ps1` may accept canonical profiles, scenario profiles, or `profile.task_module`, but the output must explicitly report `entry_kind`, `target_profile`, and `task_module`.

## 3.2 Phase boundary and package split

| Package | Allowed write scope | Forbidden scope | Exit condition |
| --- | --- | --- | --- |
| Follow-up Phase A plan-freeze | `openspec/changes/harden-skills2cli-profile-routing-followup/**`, this bilingual plan, local receipts. | Runtime code, `profiles.json`, helper scripts, checkers, tests, user-level installed copies, `config.toml`, plugin cache, remote refs. | Delta spec validates, plan matrices are present, pre-commit/archive review passes, local gate and local MR review pass, then local-main helper integrates the package. |
| Follow-up Phase B runtime hardening | Registry, runtime, helper scripts, checkers, tests, CI manifest, install-source metadata, and the same active OpenSpec change. | Profile apply, plugin-cache edits, `config.toml` edits, remote publication, unrelated worktrees. | Focused tests, representative suggestions, OpenSpec guard, local gate, local MR review pass; then archive the change and integrate into local `main`. |

Phase B may use a LangGraph durable checkpoint or persistent-team lane only after Phase A is frozen and at least two independent write slices are ready with explicit ownership. The main Codex CLI session remains the leader and owns fan-in.

## 4. Top-level profile matrix

| Existing ID | Scenario alias | Intended task modules |
| --- | --- | --- |
| `core-dev` | `repo-dev` | `repo-governance`, `code-review`, `security-review`, `openai-dev`, `docs-artifacts`, `browser-verification` |
| `web-saas` | `web-product` | `frontend-build`, `deploy-runtime`, `db-backend`, `payments`, `observability`, `mobile-app`, `design-implementation`, `browser-verification` |
| `company-ops` | `ops-knowledge` | `mail-calendar`, `docs-sheets-slides`, `knowledge-capture`, `crm-workflow`, `team-comms`, `meeting-intel`, `issue-planning` |
| `market-research` | `research-analysis` | `company-research`, `news-library`, `paper-citation`, `model-dataset-inspection`, `science-visuals`, `report-artifacts` |
| `customer-comms` | `customer-comms` | `messaging`, `email-delivery`, `support-comms`, `payment-comms` |
| `creative-content` | `design-media` | `design-generation`, `design-implementation`, `slides-docs`, `video-motion`, `brand-assets`, `media-assets` |
| `pyside6-gui` | `repo-local-gui` | `qt-gui-dev`, `gui-preview-apply`, `gui-packaging-preflight` |
| `full` | `troubleshooting` | no normal task modules; broad discovery only |

The Phase B registry must ensure the former only-`full` plugins have non-`full` task-module ownership:

- `BioRender` -> `market-research.science-visuals`;
- `ChatGPT Apps` -> `core-dev.openai-dev` or a `core-dev.chatgpt-apps` task module if needed;
- `Cloudinary` -> `creative-content.media-assets`;
- `Expo` -> `web-saas.mobile-app`;
- `Fireflies` -> `company-ops.meeting-intel`;
- `Linear` -> `company-ops.issue-planning`;
- `Temporal` -> `core-dev.workflow-orchestration` or `web-saas.workflow-orchestration` if implementation evidence favors web workflows.

## 5. Runtime behavior

`skills2cli.py profile suggest --query <text> --json` must:

1. score top-level profiles using scenario text and `route_when` terms;
2. exclude or penalize profiles whose `negative_examples` match;
3. score task modules within the retained profiles;
4. add advisory boosts from `codex_skills_usage_audit` strong evidence when available;
5. apply warning-pressure penalties to oversized or troubleshooting-only profiles;
6. return compact sanitized JSON with selected profile, task modules, excluded candidates, soft-load commands, optional hard-load preview command, and explanation strings.

`load_module.ps1` must accept both top-level modules and `profile.task_module` names. A task-module load returns only that module's hints when present.

`list_module.ps1` must show top-level modules and optionally nested task modules.

`set_plugin_profile.ps1` remains top-level only. If a task-module ID is supplied, it must fail closed with an explanation that task modules are soft-load guidance and that hard-load applies only to top-level profiles.

## 6. Checkers and tests

Add or extend a checker so the repository fails closed when:

- a top-level profile lacks scenario description, route terms, negative examples, ranking signals, or task modules;
- a task module lacks positive examples, negative examples, load policy, plugin hints, or routing explanation fields;
- a known plugin is reachable only through `full` without an explicit allowlist reason;
- ordinary profile suggestion returns `full` as top-1;
- user-level installed plugin-modules registry differs from repo source without reporting the drift;
- the profile suggestion output omits explanation, soft/hard boundary, or excluded-candidate evidence;
- the installed `skills2cli` wrapper passes `--help` but cannot run a real `profile suggest` smoke, including when the shared profile-routing contract module is required from the installed helper directory;
- the output sets `mutates_config`, `edits_plugin_cache`, or `profile_apply_performed` to true;
- the output treats skill/profile routing as native expert or native subagent evidence;
- paired `mcp2cli` risk-profile / receipt gates are bypassed when direct MCP handoff language is present.

Representative routing tests must cover:

- GitLab CI repair plus security review -> `core-dev` with `code-review` and `security-review`;
- Expo mobile build plus Sentry observability -> `web-saas` with `mobile-app` and `observability`;
- Twilio WhatsApp customer notice -> `customer-comms` with `messaging`;
- meeting notes and CRM follow-up -> `company-ops` with `meeting-intel` or `crm-workflow`;
- BioRender scientific figure -> `market-research.science-visuals`;
- Cloudinary asset pipeline -> `creative-content.media-assets`;
- unknown broad troubleshooting request -> no automatic `full` top-1 unless the query clearly asks for troubleshooting all plugins.

## 7. Phase A tasks

<!-- TASK_BACKLOG_START -->

- [x] Create this bilingual implementation plan.
- [x] Create the OpenSpec change `improve-skills2cli-profile-routing`.
- [x] Add a delta spec for profile routing, task modules, negative examples, recall/rerank output, and safety boundaries.
- [x] Update `codex_skills_usage_audit_plan.md` and `.zh-CN.md` to link audit evidence to advisory routing/rerank only.
- [x] Register the bilingual plan in `docs_bilingual/docs_registry.yaml`.
- [x] Run plan-level validation and commit the plan-freeze package.
- [x] Integrate Phase A into local `main` and clean the worktree/branch through the local-main-first helper.

## 7.1 Follow-up Phase A acceptance matrix

| Acceptance item | Required evidence before local commit | Owner phase | Status |
| --- | --- | --- | --- |
| Follow-up OpenSpec change exists | Proposal, design, tasks, management, `.openspec.yaml`, `.comet.yaml`, and bilingual companions exist under `harden-skills2cli-profile-routing-followup`. | Phase A | Required |
| Delta spec is non-empty and strict-valid | `openspec validate harden-skills2cli-profile-routing-followup --strict` passes. | Phase A | Required |
| Four principles are traceable | Section 1.1 maps scenario description, layered routing, negative boundaries, and recall/rerank to OpenSpec requirements and Phase B evidence. | Phase A | Required |
| Safety contract is unified | Section 2.1 lists allowed/forbidden behavior and checker targets. | Phase A | Required |
| Phase A and B are separated | Section 3.2 states plan-freeze-only scope and forbids runtime edits in Phase A. | Phase A | Required |
| Audit linkage remains advisory | Current status and safety sections state audit evidence does not authorize profile apply. | Phase A | Required |
| Local commit readiness | `check_precommit_update_archive.py`, `run_openspec_guard.py`, local gate, and local MR review pass before local `main` integration. | Phase A | Required |

## 8. Phase B tasks

- [x] Extend `profiles.json` with scenario metadata and task modules while preserving existing profile IDs.
- [x] Extend plugin-modules scripts for nested `profile.task_module` soft-load and top-level-only hard-load.
- [x] Add `skills2cli.py profile suggest` with positive/negative/rerank evidence and compact sanitized output.
- [x] Add checker and tests for schema, only-`full` coverage, no ordinary `full` top-1, and installed-copy drift reporting.
- [x] Update CI manifest and guard registrations if new checker/test files require registration.
- [x] Validate Phase B with checker, representative suggestions, OpenSpec guard, local gate, and local MR review.
- [x] Archive the OpenSpec change after runtime validation passes and prepare the package for local-main-first helper integration.

<!-- TASK_BACKLOG_END -->

## 9. Acceptance criteria

- `profiles.json` contains `scene_description` plus `scenario_description` compatibility fields and task modules for all non-`full` profiles.
- Every known plugin has a non-`full` route or an explicit allowlist reason.
- `skills2cli.py profile suggest --query ... --json` returns deterministic, sanitized, explainable recommendations, including profile-level `plugin_hints` and `skill_doc_hints` plus focused task-module hints.
- `full` is not top-1 for ordinary user tasks.
- Profile suggestion remains advisory and never applies config.
- `skills2cli` focused tests, `mcp2cli` risk/receipt tests, agent/skill/profile boundary tests, and strict user-level install/smoke checks are part of the final runtime validation set.
- User-level `skills2cli` installation copies every Python module required by the facade, including `skills2cli_profile_registry_contract.py`; install metadata and checker output expose that support file so simulated and live `profile suggest` smokes fail closed if the dependency is missing.
- The shared registry contract module is the only Python source for canonical profile IDs, required routing fields, registry/installed-copy paths, `scene_description` compatibility accessors, profile/task hint accessors, plugin coverage collection, and explicit `full` troubleshooting trigger terms.
- The checker-backed routing matrix proves that normal task queries for every ordinary top-level profile do not select `full`, while explicit English and Chinese all-plugin troubleshooting queries may select `full`; every matrix row must keep `mutates_config=false`, `edits_plugin_cache=false`, `profile_apply_performed=false`, and `approval_required_for_apply=true`.
- `check_skills2cli_profile_routing.py --json` emits UTF-8 JSON bytes so Chinese matrix rows remain decodable on Windows, and checker smoke cases remain black-box boundary tests rather than duplicated runtime scoring logic.
- Local OpenSpec validation, repository guard, local CI, and local MR review pass before local `main` integration.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- `docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.md` - Stage A frozen implementation plan and runtime validation contract.
- `docs_bilingual/docs_registry.yaml` - active bilingual plan registry entry.
- `openspec/changes/archive/2026-06-21-improve-skills2cli-profile-routing/` - archived OpenSpec change containing proposal, design, tasks, management record, and delta spec.
- `openspec/changes/archive/2026-06-22-harden-skills2cli-profile-routing-followup/` - archived follow-up OpenSpec change and promoted stable-spec evidence for the hardened routing runtime.
- `docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md` - advisory audit input linkage; profile apply remains unauthorized.
- Stage A validation evidence: `openspec validate improve-skills2cli-profile-routing --strict`, `tools/run_openspec_guard.py --root . --tool codex --json`, `tools/check_precommit_update_archive.py --root . --json`, and `tools/check_worktree_task_receipt.py --root . --json` passed before the plan-freeze commit.
- Closeout evidence: focused unit tests for `skills2cli`, `check_skills2cli_profile_routing`, and `check_plugin_modules_skill` cover `scene_description` compatibility and profile-level hints; full gates are rerun before local-main integration.
- Contract hardening package `harden-skills2cli-profile-routing-contract-20260622` centralizes the Python-side registry path, canonical profile IDs, required fields, scene/legacy-description accessor, hint accessor, plugin coverage collector, and explicit `full` trigger aliases in `tools/skills2cli_profile_registry_contract.py`; runtime scoring and checker black-box smokes remain separate, and the user-level installer now copies that contract module beside installed `skills2cli.py`.
- The profile-suggest checker now records a matrix covering ordinary `core-dev`, browser automation, `web-saas`, `customer-comms`, `company-ops`, `market-research`, `creative-content`, `pyside6-gui`, and explicit English/Chinese `full` troubleshooting queries, while preserving preview-only safety flags.

- Live runtime install sync evidence on 2026-06-22: `tools/install_user_level_mcp_skills_cli.py apply --apply --operator-confirmation --skip-upstream-skill-install --json` refreshed the user-level `skills2cli` install artifacts without installing upstream skills, editing `config.toml`, editing plugin cache, or applying a profile.
- Live plugin-modules install sync evidence on 2026-06-22: `tools/install-plugin-modules-skill.ps1 -Force` refreshed the installed `plugin-modules` skill registry copy while preserving advisory-only profile routing semantics.
- Live install smoke evidence on 2026-06-22: `tools/install_user_level_mcp_skills_cli.py check --require-installed --smoke --json` returned `ok=true`, `skills2cli_profile_registry_contract=true`, and a passing `skills2cli_profile_suggest` smoke.
- Drift-clean runtime evidence on 2026-06-22: `tools/check_skills2cli_profile_routing.py --root . --json` returned `ok=true`, no warnings, and no installed-artifact drift for `skills2cli.py`, `skills2cli_profile_registry_contract.py`, or `profiles.json`; `tools/check_plugin_modules_skill.py --root . --json` also returned `ok=true`.
<!-- EVIDENCE_INDEX_END -->
