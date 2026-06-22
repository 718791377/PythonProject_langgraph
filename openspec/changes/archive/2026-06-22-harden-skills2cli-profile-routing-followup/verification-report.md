# Verification Report: Harden Skills2CLI Profile Routing Follow-up

## Scope

Stage B implements the frozen Skills2CLI profile routing hardening package locally only. No profile apply, config.toml mutation, plugin cache edit, vendor SKILL.md edit, GitLab push, GitLab MR, or GitHub sync is part of this verification.

## Fresh verification evidence

- `python test\skills2cli.test.py` - pass, 16 tests.
- `python test\check_skills2cli_profile_routing.test.py` - pass, 8 tests.
- `python test\check_plugin_modules_skill.test.py` - pass, 15 tests.
- `python -X utf8 tools\check_plugin_modules_skill.py --root . --json` - pass, `ok=true`, `errors=0`.
- `python -X utf8 tools\check_skills2cli_profile_routing.py --root . --json` - pass, `ok=true`, `errors=0`; expected warning reports installed user-level drift.
- Representative `skills2cli profile suggest` smokes show focused top profile recommendations for GitLab CI/security, Expo/Sentry, Twilio WhatsApp, and explicit-only `full` for all-plugin troubleshooting.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools\skill_sources\plugin-modules\scripts\load_module.ps1 web-saas.mobile-app -Json` - emits soft-load task-module guidance with no mutation flags.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools\skill_sources\plugin-modules\scripts\set_plugin_profile.ps1 web-saas.mobile-app -Json` - rejects nested hard-load with preview/soft-load guidance and no mutation flags.
- `openspec validate harden-skills2cli-profile-routing-followup --strict` - pass.
- `python tools\run_openspec_guard.py --root . --tool codex --json` - pass, `77/77` steps.
- `python tools\check_precommit_update_archive.py --root . --json` - pass, `ok=true`.

## Acceptance mapping

- Scenario-based profile routing metadata: covered by registry fields and `check_skills2cli_profile_routing.py` / `check_plugin_modules_skill.py`.
- Task-module identity: covered by `qualified_name` and focused tests for missing/wrong identity.
- Hard-load top-level only: covered by `set_plugin_profile.ps1` nested rejection smoke.
- Advisory suggestion: covered by `skills2cli.py profile suggest` mutation flags and tests.
- Known plugin non-full coverage: checker reports `known_plugins=37` and `non_full_plugin_coverage=37`.
- Shared contract: `skills2cli_profile_registry_contract.py` centralizes schema/path/accessors and installed artifact surfaces.
- Explicit `full`: ordinary queries exclude `full`; explicit all-plugin troubleshooting selects `full` with `why_full_selected`.
- UTF-8 stable checker JSON: Chinese full troubleshooting row is included and JSON-decodable in checker matrix.
- Installed artifact drift: checker reports `skills2cli.py`, `skills2cli_profile_registry_contract.py`, and `profiles.json` drift surfaces.

## Decision

Proceed to archive and local-main integration after local gate and local MR review pass. Stop at the remote-publication approval gate.
