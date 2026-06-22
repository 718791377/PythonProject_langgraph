# Design: Skills2CLI Routing Contract Hardening

## Phase A boundary

Phase A is a plan-freeze package. It may update OpenSpec artifacts, the bilingual implementation plan, and local worktree receipts only. It must not change runtime code, `profiles.json`, helper scripts, checker logic, tests, user-level installed copies, `config.toml`, or plugin cache files.

## Phase B target

Phase B implements the frozen follow-up contract:

1. orthogonal schema fields for routing, activation, governance, and evidence scope;
2. first-class logical semantics for `profile.task_module` while keeping the on-disk nested registry layout;
3. fail-closed positive scenario quality checks for top-level profiles, scenario profiles, and task modules;
4. behavior tests proving `profile suggest` and `load_module` do not mutate `config.toml`, plugin cache, or apply profiles;
5. explicit eligibility gating for `full` so warning pressure and audit evidence can change order but cannot grant eligibility;
6. install artifact surface reporting for repo and installed `skills2cli.py`, `skills2cli_profile_registry_contract.py`, and `profiles.json`.

## Contract model

`load_policy` remains a compatibility field. New registry entries must additionally expose:

- `routing_scope`: `default_candidate`, `focused_candidate`, or `explicit_only`;
- `activation_scope`: `soft_load_only` or `top_level_hard_load_preview`;
- `governance_scope`: `cross_project`, `repo_local_only`, or `troubleshooting_only`;
- `evidence_scope`: `workflow_context_only`.

The checker must verify that the compatibility `load_policy` maps consistently to those orthogonal fields.

## Task-module identity

A task module's canonical logical ID is `qualified_name=<profile>.<task_module>`. The local `task_module` name is valid only within its owning top-level profile. Task modules are soft-load guidance only, cannot define independent `hard_load`, cannot be hard-load targets, and may inherit parent hints only when an explicit inheritance marker is present.

## Full-profile eligibility

`full` and the `troubleshooting` scenario are explicit-only. If `explicit_full_request=false`, `full` must be absent from the selected profile and appear only in `excluded_candidates` with an eligibility reason. If `explicit_full_request=true`, selection must include `why_full_selected` with one of: `explicit_all_plugins`, `explicit_broad_discovery`, or `explicit_missing_plugin_capability`.

## Safety and evidence

All suggestion and soft-load surfaces remain advisory. They must expose safety flags and behavior-level evidence that no profile apply happened, no config was changed, no plugin cache was changed, and no native expert evidence was produced. Remote publication remains outside this flow.
