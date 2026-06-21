---
doc_id: codex_skills2cli_profile_routing_runtime_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.md
translation: docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.zh-CN.md
status: active
doc_class: implementation_plan
change: improve-skills2cli-profile-routing
created_at: 2026-06-21
---

# Skills2CLI Scenario-Based Profile Routing Runtime Plan

> For agentic workers: use `subagent-driven-development` or a guarded durable-team lane after this plan is frozen. Keep the plan-freeze package and live runtime package as separate local-main integration packages. Profile apply is out of scope unless a later explicit apply receipt exists.

**Goal:** optimize Codex plugin skill management by adding a scenario-entry and task-module routing layer while preserving canonical `target_profile` hard-load semantics.

**Architecture:** Phase A freezes the OpenSpec contract and bilingual implementation plan. Phase B extends the plugin-modules registry, helper scripts, `skills2cli.py`, checkers, and tests. The runtime remains advisory: it can recommend soft-load and hard-load preview candidates, but it must not edit `config.toml`, plugin cache, or hard-load profiles.

**Tech Stack:** JSON profile registry, PowerShell plugin-module helpers, Python `skills2cli.py`, repository checkers, OpenSpec, local CI and local MR review.

---

## Current Status

<!-- CURRENT_STATUS_START -->

- Stage A plan-freeze package is integrated into local `main` at `3d08d6e`.
- Phase B runtime implementation is complete and committed on `implement-skills2cli-profile-routing-runtime-20260621`.
- Implemented runtime surfaces include scenario profiles, task modules, advisory `skills2cli profile suggest`, plugin-modules soft-load scripts, checker/test coverage, installed-wrapper profile-suggest smoke, and OpenSpec guard registration.
- Completed verification: representative routing smokes, focused tests, full Python unittest manifest, OpenSpec guard, local CI, and local MR review.
- Remaining closeout is local-main-first helper integration, post-merge validation, completed-claim/rollback evidence, and safe feature worktree cleanup; remote publication remains unauthorized.
- Remote publication is not authorized.

<!-- CURRENT_STATUS_END -->

## 1. Inputs and design principles

This plan uses three inputs:

1. The local reference video filename summary: improve Agent skill hit rate by writing scenario descriptions, layered routing, negative-sample boundaries, and recall/rerank.
2. The `codex_skills_usage_audit` evidence model: strong evidence supports routing and review, but does not authorize profile apply.
3. The current `target_profile` registry: `core-dev`, `web-saas`, `company-ops`, `market-research`, `customer-comms`, `creative-content`, `pyside6-gui`, and `full` remain compatible IDs.

## 2. Non-goals and safety boundaries

- Do not rename existing `target_profile` IDs in Phase B; add aliases and scenario metadata instead.
- Do not automatically apply any hard-load profile.
- Do not mutate `C:\Users\lenovo\.codex\config.toml`.
- Do not bulk-edit plugin cache files or vendor `SKILL.md` files.
- Do not make `full` a normal top-1 suggestion.
- Do not treat profile/helper invocation as native expert evidence.
- Do not push GitLab/GitHub in this implementation flow.

## 3. Target model

The registry must represent four layers:

1. **Canonical top-level profile** - the existing `target_profile` hard-load ID used by `set_plugin_profile.ps1` and audit candidates.
2. **Scenario profile** - a new recommendation entrypoint that resolves to a canonical `target_profile` and default task modules.
3. **Task module** - a task capability block inside a profile, such as `web-saas.mobile-app` or `core-dev.security-review`.
4. **Skill/plugin hints** - candidate plugin families and `SKILL.md` references that can be soft-loaded.

Every top-level profile and every task module must define:

- scenario description;
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
- the installed `skills2cli` wrapper passes `--help` but cannot run a real `profile suggest` smoke;
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

- `profiles.json` contains scenario fields and task modules for all non-`full` profiles.
- Every known plugin has a non-`full` route or an explicit allowlist reason.
- `skills2cli.py profile suggest --query ... --json` returns deterministic, sanitized, explainable recommendations.
- `full` is not top-1 for ordinary user tasks.
- Profile suggestion remains advisory and never applies config.
- `skills2cli` focused tests, `mcp2cli` risk/receipt tests, agent/skill/profile boundary tests, and strict user-level install/smoke checks are part of the final runtime validation set.
- Local OpenSpec validation, repository guard, local CI, and local MR review pass before local `main` integration.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- `docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.md` - Stage A frozen implementation plan and runtime validation contract.
- `docs_bilingual/docs_registry.yaml` - active bilingual plan registry entry.
- `openspec/changes/archive/2026-06-21-improve-skills2cli-profile-routing/` - archived OpenSpec change containing proposal, design, tasks, management record, and delta spec.
- `docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md` - advisory audit input linkage; profile apply remains unauthorized.
- Stage A validation evidence: `openspec validate improve-skills2cli-profile-routing --strict`, `tools/run_openspec_guard.py --root . --tool codex --json`, `tools/check_precommit_update_archive.py --root . --json`, and `tools/check_worktree_task_receipt.py --root . --json` passed before the plan-freeze commit.

<!-- EVIDENCE_INDEX_END -->
