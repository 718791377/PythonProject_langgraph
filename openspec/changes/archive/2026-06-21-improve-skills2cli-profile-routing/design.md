# Design: Scenario-Based Skills2CLI Profile Routing

## Current state

`profiles.json` defines eight top-level modules and maps each directly to plugin bundles and skill-doc hints. This shape is useful for profile apply preview, but it cannot express why a profile should or should not match a user task.

## Target state

The registry becomes a layered routing source:

1. top-level profile: stable compatibility ID and broad scenario;
2. scenario profile: recommendation entry that resolves to canonical `target_profile`;
3. task module: focused capability block inside a profile;
4. hint layer: plugin family and `SKILL.md` references.

Profile IDs remain stable. New fields are additive so existing scripts can keep working while new scripts use richer metadata.

## Routing model

`skills2cli.py profile suggest` scores user text against `route_when` and task-module examples, applies `negative_examples` exclusions or penalties, uses audit evidence as advisory boost, and penalizes `full` unless the query explicitly asks for broad troubleshooting.

## Safety model

All routing output is advisory. `load_module.ps1` can soft-load top-level or nested modules. `set_plugin_profile.ps1` only previews/applies top-level profiles and fails closed for nested task modules.

## Compatibility

Existing calls such as `load_module.ps1 core-dev -Json` and `set_plugin_profile.ps1 core-dev -Json` must continue working. Nested calls such as `load_module.ps1 web-saas.mobile-app -Json` are new. Nested calls to `set_plugin_profile.ps1` must fail closed with a clear explanation.

## Compatibility refinement

Scenario profiles are recommendation entries only. They resolve to canonical `target_profile` IDs and task modules. They do not replace existing `modules`, and they are not valid hard-load targets.
