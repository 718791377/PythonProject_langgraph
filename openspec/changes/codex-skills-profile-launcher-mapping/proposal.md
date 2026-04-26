## Why

The skills governance plan now has inventory, policy, governance checks, and safe-cleanup reporting. The remaining Phase 4 gap is a launcher-facing profile mapping that tells future user-level launchers which profile should load which skill groups without mutating user-level configuration or disabling plugin capabilities.

This change lands Phase 4 as a repository-governed, non-mutating profile-to-launcher mapping and validation surface. It documents the intended aliases and checks that the mapping preserves browser/web capabilities while keeping the default profile smaller.

## What Changes

- Add a declarative `launcher_mapping` section to the Codex skills profiles registry.
- Add bilingual governance documentation for the profile-to-launcher mapping.
- Add a validation script that checks the mapping against the profile registry.
- Validate that:
  - `core`, `browser`, `web`, `github`, and `full` profile launcher aliases are declared,
  - launcher integration remains document-only / future-optional until an explicit launcher install change exists,
  - no repository change mutates user-level `config.toml`,
  - browser profile projects keep browser automation capabilities,
  - Vercel plugin capabilities remain preserved for browser and web profiles.
- Do not install or edit user-level launcher wrappers in this change.
- No **BREAKING** changes are intended.

## Capabilities

### New Capabilities

- `codex-skills-profile-launcher-mapping`: Defines the declarative profile-to-launcher mapping and validation behavior for Phase 4 of Codex skills governance.

### Modified Capabilities

- None. This introduces a new Phase 4 mapping surface rather than changing existing archived specs.

## Impact

- Affected documentation:
  - `docs_bilingual/governance/codex_skills_profile_launcher_mapping.md` - English profile launcher mapping governance document.
  - `docs_bilingual/governance/codex_skills_profile_launcher_mapping.zh-CN.md` - Chinese profile launcher mapping governance document.
  - `docs_bilingual/docs_registry.yaml` - bilingual documentation registry entry.
- Affected registry:
  - `docs_bilingual/governance/codex_skills_profiles.registry.yaml` - profiles registry launcher mapping metadata.
- Affected tooling and tests:
  - `tools/check_codex_skills_profile_launcher_mapping.py` - JSON-emitting launcher mapping checker.
  - `test/check_codex_skills_profile_launcher_mapping.test.py` - fixture tests for launcher mapping validation.
- User-level installed files are out of scope and must not be changed.

## Impact Scope

This is a repository-local Phase 4 mapping and validation change for the Codex user-level skills governance plan. It documents and checks launcher integration metadata but does not install launcher aliases.

## Explicit Non-Goals

- Do not edit `C:\Users\lenovo\.codex\config.toml`.
- Do not edit generated wrappers under `C:\Users\lenovo\.codex\bin\`.
- Do not disable Vercel or any plugin bundle.
- Do not delete, move, or edit user-level skills.
- Do not implement fine-grained plugin-skill loading in this change.
- Do not create GitHub PRs.

## Rollout Sequence

1. Create this OpenSpec change and validate the Phase 4 contract.
2. Add the declarative launcher mapping to the profiles registry.
3. Add bilingual governance documentation.
4. Add a validation script and tests.
5. Run local validation and OpenSpec guard.
6. Publish through GitLab-first workflow.

## Rollback Plan

- Before merge, rollback is deleting this feature branch or reverting local changes.
- After merge, rollback is reverting the registry mapping, documentation, checker, tests, and OpenSpec change.
- No user-level launcher or config rollback is needed because this change does not mutate installed user-level files.

## Validation Path

Minimum validation:

```powershell
git diff --check
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/check_codex_skills_governance.py --root . --json
python tools/check_codex_skills_profile_launcher_mapping.py --root . --json
python test/check_codex_skills_profile_launcher_mapping.test.py
openspec status --change "codex-skills-profile-launcher-mapping"
openspec validate "codex-skills-profile-launcher-mapping" --strict
python tools/run_openspec_guard.py --root . --tool codex --json
```

## Mainline Classification

This is a continuation of the Codex user-level skills governance and profiles implementation plan. It is a cross-mainline governance/control-surface change, not a new LangGraph-deepening mainline.
