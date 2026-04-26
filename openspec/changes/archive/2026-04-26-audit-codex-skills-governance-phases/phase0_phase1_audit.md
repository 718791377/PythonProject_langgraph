# Phase 0/1 Audit Evidence

Date: 2026-04-25

Scope: local audit only for Phase 0 baseline inventory and Phase 1 governance policy / profile registry. No commit, push, MR update, user-level skill mutation, Vercel plugin disablement, or user-level `config.toml` mutation was performed.

## Phase 0: Baseline Inventory

### Artifacts

- `tools/inventory_codex_skills.py`: present.
- `docs_bilingual/governance/codex_skills_inventory_baseline.json`: present.

### Command

```powershell
python tools/inventory_codex_skills.py --root . --json
```

Result: exit code 0.

### Current inventory summary

- Total skills: 131
- Source layers:
  - plugin: 51
  - repo: 20
  - user: 60
- Suspected profiles:
  - browser: 21
  - core: 25
  - github: 11
  - openspec: 20
  - orchestration: 9
  - web: 45
- Duplicate name groups: 12

### Baseline comparison

The committed baseline reports the same high-level counts as the current run:

- Total skills: 131
- Source layers:
  - plugin: 51
  - repo: 20
  - user: 60
- Duplicate name groups: 12

The current output and baseline both include the required row fields:

- `name` - skill identifier captured from each scanned `SKILL.md` file.
- `description_length` - character count used to flag long skill descriptions.
- `source_layer` - inventory classification for repo, user, system, or plugin skill origin.
- `file_path` - concrete location of the scanned skill file.
- `duplicate_name_group` - grouping key for skills that share the same name.
- `suspected_profile` - inferred launcher profile bucket for routing analysis.
- `status_suggestion` - non-mutating recommendation such as report-only, investigate, or keep.

### Phase 0 verdict

Phase 0 is landed as an inventory and baseline reporting phase. The inventory reports counts, duplicates, description lengths, suspected profiles, and status suggestions. It does not delete, move, rename, or rewrite user-level skills, and this audit did not run it with `--output`.

Known findings remain visible rather than cleaned up:

- 10 OpenSpec nested duplicate candidates marked for investigation before cleanup.
- 29 user-level long-description candidates marked for post-inventory shortening.
- 51 plugin skills reported as plugin-managed / report-only.

## Phase 1: Governance Policy and Registry

### Artifacts

- `docs_bilingual/governance/codex_user_level_skills_governance_policy.md`: present.
- `docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md`: present.
- `docs_bilingual/governance/codex_skills_profiles.registry.yaml`: present.
- `docs_bilingual/docs_registry.yaml`: present.

### Profile registry checks

Required profiles are present:

- `core` - minimal default profile for routine repository work.
- `browser` - profile that preserves browser automation and Vercel-backed verification capability.
- `web` - profile for web application and deployment-oriented skill access.
- `github` - profile for GitHub-specific review and publication tooling.
- `full` - broad profile that keeps the complete installed skill surface visible.

Additional lifecycle profiles are present:

- `openspec` - lifecycle profile for OpenSpec artifact and governance work.
- `orchestration` - profile for native subagent, OMX, and LangGraph orchestration work.

Browser-capable project defaults are present:

- the browser-profile legacy application project: `[core, browser, orchestration]`
- `D:\PythonProject_CLIProxyAPI`: `[core, browser, orchestration]`

The registry declares `config_mutation: forbidden` and describes itself as not mutating user-level `config.toml`.

### Docs registry checks

`docs_bilingual/docs_registry.yaml` registers:

- `codex_user_level_skills_governance_and_profiles_plan` - implementation-plan registry entry for the skills governance rollout.
- `codex_user_level_skills_governance_policy` - governance-policy registry entry for skills lifecycle rules.

The current document governance checker treats `docs_registry.yaml` as a registry for bilingual Markdown governance documents. It does not currently require non-Markdown YAML data artifacts such as `codex_skills_profiles.registry.yaml` to be listed as standalone registry entries.

### Commands

```powershell
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
```

Results:

- `check_document_governance_rules.py`: exit code 0, `ok: true`, 0 errors, 0 warnings.
- `check_implementation_plan_rules.py`: exit code 0, `ok: true`, 0 errors, 0 warnings.

### Phase 1 verdict

Phase 1 is landed for the original implementation-plan acceptance path: the bilingual governance policy exists, the declarative profile registry exists, browser-capable project defaults are preserved, and the repository document / implementation-plan governance checks pass.

Nuance for follow-up: if future policy requires every non-Markdown registry artifact to appear in `docs_registry.yaml`, that should be added as a separate explicit governance-rule change. It is not enforced by the current Phase 1 checker.
