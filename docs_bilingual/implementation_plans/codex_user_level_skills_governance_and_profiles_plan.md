---
doc_id: codex_user_level_skills_governance_and_profiles_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-04-25
---

# Codex User-Level Skills Governance and Profiles Implementation Plan

> Cold-start contract: this file is self-contained. A fresh Codex session with no prior chat context can implement it by reading this document, `AGENTS.md`, `docs_bilingual/project_startup_summary.md`, and the two currently active implementation plans:
>
> - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
> - `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md`
>
> The long-range target plan remains `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md`, currently draft. Do not treat that draft as already implemented.

## 1. Goal

Create a maintainable skills governance and profile system for a single user-level Codex installation that supports multiple projects on the same machine:

- `D:\PythonProject_langgraph` - primary repository for Codex orchestration governance and implementation plans.
- `D:\PythonProject_OpenClaw` - consumer project that may need browser automation and profile preservation.
- `D:\PythonProject_CLIProxyAPI` - consumer project that may need browser or endpoint verification.
- `D:\project` - lightweight consumer project that should start with the core profile only.
- future repositories opened through `codex-ohmy`

The system must reduce skills context-budget pressure without removing useful cross-project capabilities such as browser automation, OpenSpec workflows, Codex orchestration governance, durable-team routing, and LangGraph workflow support.

## 2. Current Problem

The current startup loads too many skill descriptions into the model context.

Observed local shape as of 2026-04-25:

- about 131 `SKILL.md` files
- about 60 user-level skills
- about 20 repository OpenSpec skills
- about 51 plugin skills
- Vercel plugin contributes about 47 skills
- duplicate skill names include `openspec-*`, `gh-fix-ci`, and `gh-address-comments`

This causes warnings like:

```text
Exceeded skills context budget of 2%.
Loaded skill descriptions were truncated.
```

This is not a fatal runtime error, but it reduces automatic skill-routing accuracy and bloats startup context.

## 3. Core Design Decision

Do not optimize by blindly disabling whole capability families.

Instead, split skills into four layers:

1. **Core user-level skills**
   - always useful across projects
   - low context cost
   - safe to load by default

2. **Profile-gated user-level skills**
   - useful for a class of projects, but not every project
   - enabled by launch profile or project policy

3. **Repository-local skills**
   - owned by a specific repository
   - must not leak repository facts or durable state into other repositories

4. **Plugin skills**
   - supplied by enabled plugins
   - must be treated as bundles unless the launcher gains fine-grained plugin-skill filtering

## 4. Cross-Project Capability Rule

The following are not exclusive to `D:\PythonProject_langgraph`:

- OpenSpec official workflows
- Codex orchestration governance
- durable team routing policy
- LangGraph durable orchestration policy
- browser automation and verification

However, facts and state remain repository-local:

- `openspec/changes/` - repository-local directory for active and proposed OpenSpec changes.
- `openspec/specs/` - repository-local directory for stable OpenSpec specifications.
- `.omx/state/` - repository-local durable state directory for OMX workflows.
- `.omx/state/langgraph/` - repository-local durable state directory for LangGraph workflows.
- repository task queues
- repository memory summaries
- repository CI and release state

Use this rule:

```text
shared runtime and policy: user-level
project facts and durable truth: repo-local
```

## 5. Required Profiles

Implement or document these profiles. If direct launcher profile support is not yet available, implement this first as registry metadata and project policy; do not mutate `config.toml` automatically.

### 5.1 `core`

Default profile for non-web work.

Must include:

- skill management and diagnostics
- planning and review
- note/memory helpers
- worker/team protocol docs
- OpenSpec general workflow capability
- Codex orchestration governance capability

Must not require Vercel/Next.js-specific skills.

### 5.2 `browser`

Default add-on for projects that need browser automation, including:

- `D:\PythonProject_OpenClaw` - browser-oriented consumer project that should keep browser automation skills available.
- `D:\PythonProject_CLIProxyAPI` - endpoint and browser verification consumer project that should keep browser skills available.
- any project with browser UI verification, browser MCP, Playwright, or web-console testing

Must preserve access to browser-oriented Vercel plugin skills when available:

- `agent-browser` - Vercel plugin skill for agent-driven browser automation sessions.
- `agent-browser-verify` - Vercel plugin skill for browser behavior verification.
- `verification` - Vercel plugin skill for full-story acceptance and behavior checks.
- `investigation-mode` - Vercel plugin skill for structured browser or app debugging.

If the Vercel plugin cannot be partially loaded, keep the plugin available for browser profile projects rather than globally disabling it.

### 5.3 `web`

Add-on for Vercel, Next.js, React, AI web app, frontend, or deployment work.

May include:

- `nextjs` - Next.js framework guidance skill for App Router and related web work.
- `react-best-practices` - React review skill for TSX best-practice checks.
- `shadcn` - shadcn/ui component installation and usage guidance skill.
- `ai-sdk` - Vercel AI SDK guidance skill for AI application development.
- `ai-gateway` - Vercel AI Gateway configuration and routing guidance skill.
- `vercel-cli` - Vercel CLI guidance skill for deployment and project management.
- `vercel-api` - Vercel app and REST API guidance skill.
- `deployments-cicd` - Vercel deployment and CI/CD guidance skill.
- `env-vars` - Vercel environment variable configuration guidance skill.
- `observability` - Vercel observability guidance skill for logs, drains, and monitoring.
- `vercel-functions` - Vercel Functions guidance skill for serverless runtime behavior.
- `vercel-storage` - Vercel storage guidance skill for Blob, Edge Config, and related storage.

### 5.4 `github`

Add-on only when GitHub issue/PR workflows are active.

For this repository, GitHub is normally a post-merge sync target, not the review surface.

Do not open GitHub PRs by default. Use GitLab MRs first, then sync merged `main` to GitHub.

### 5.5 `full`

Temporary troubleshooting profile.

Allowed only for short sessions where broad plugin discovery matters more than context budget.

## 6. Project Defaults

Record these defaults in the registry or policy file:

| Project | Default profiles | Notes |
| --- | --- | --- |
| `D:\PythonProject_langgraph` | `core`, `openspec`, `orchestration` | Source of truth for Codex orchestration governance and implementation plans. |
| `D:\PythonProject_OpenClaw` | `core`, `browser`, `orchestration` | Browser automation is expected. Keep browser verification capability available. |
| `D:\PythonProject_CLIProxyAPI` | `core`, `browser`, `orchestration` | Browser or endpoint verification may be required. |
| `D:\project` | `core`, plus discovered project profile | Detect web/browser needs from repository contents before enabling web profile. |
| future projects | `core` first | Add `browser`, `web`, `github`, or `full` only when project evidence requires it. |

## 7. Implementation Artifacts

Implement this plan through small GitLab MRs. Do not make one large unreviewable change.

### 7.1 Add a skills governance policy

Create:

- `docs_bilingual/governance/codex_user_level_skills_governance_policy.md` - English governance policy for user-level skills, profiles, and authority boundaries.
- `docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md` - Chinese companion for the user-level skills governance policy.

The policy must define:

- skill layer model
- placement rules
- profile definitions
- project defaults
- duplicate-skill policy
- description-length limits
- plugin handling rules
- user-level versus repo-local authority
- local-main-first publication workflow

Register both files in `docs_bilingual/docs_registry.yaml`.

### 7.2 Add a skills inventory report tool

Create:

- `tools/inventory_codex_skills.py` - inventory script that reports user, repository, and plugin Codex skills.

The tool must:

- scan user-level skills under `%USERPROFILE%\.codex\skills`
- scan repo-level skills under `.codex/skills`
- optionally scan plugin skills under `%USERPROFILE%\.codex\plugins\cache`
- parse `SKILL.md` frontmatter
- output JSON with:
  - name
  - description length
  - source layer
  - file path
  - duplicate name group
  - suspected profile
  - status suggestion

Required command:

```powershell
python tools/inventory_codex_skills.py --root . --json
```

### 7.3 Add a skills governance check

Create:

- `tools/check_codex_skills_governance.py` - governance check script for duplicate skills, description limits, and registry consistency.
- `test/check_codex_skills_governance.test.py` - test coverage for the skills governance check script.

The check must fail on:

- duplicate skill names inside the same layer
- user-level skill descriptions longer than the configured limit
- repo-level skill descriptions longer than the configured limit
- missing governance registry entry
- unknown profile labels in the registry

The check should warn, not fail, on:

- duplicate names across user/plugin layers when the policy explicitly marks one as preferred
- plugin bundles that cannot be partially loaded
- known Vercel plugin bulk load

Required command:

```powershell
python tools/check_codex_skills_governance.py --root . --json
```

### 7.4 Add a project skills profile registry

Create:

- `docs_bilingual/governance/codex_skills_profiles.registry.yaml` - YAML registry that declares supported skills profiles and project defaults.

Minimum schema:

```yaml
version: 1
profiles:
  core:
    description: Always-on cross-project Codex skills.
  browser:
    description: Browser automation and visual verification skills.
  web:
    description: Vercel, Next.js, React, AI web app, and deployment skills.
  github:
    description: GitHub issue and PR workflow skills.
  full:
    description: Temporary broad discovery profile.
projects:
  D:\PythonProject_langgraph:
    profiles: [core, openspec, orchestration]
  D:\PythonProject_OpenClaw:
    profiles: [core, browser, orchestration]
  D:\PythonProject_CLIProxyAPI:
    profiles: [core, browser, orchestration]
  D:\project:
    profiles: [core]
```

The registry must be declarative. Do not make it mutate user-level `config.toml` by itself.

### 7.5 Normalize OpenSpec skill duplication

Investigate why `.codex/skills/openspec-*` contains nested duplicate `openspec-*/SKILL.md` files.

Before deleting anything:

1. Run `openspec init --tools codex --force`.
2. Run `openspec update --force`.
3. Compare regenerated files.
4. Confirm whether nested copies are official OpenSpec 1.3.1 output or migration residue.
5. Only remove duplicates if `tools/run_openspec_guard.py --root . --tool codex --refresh-managed-files --require-clean-git --json` stays green in a clean clone.

### 7.6 Shorten descriptions only after registry exists

Do not bulk-edit descriptions first.

First create the inventory and governance checks so description changes are measured and reviewable.

Suggested limits:

- user-level `description`: 180 English characters or 80 Chinese characters
- repo-level `description`: 220 English characters or 100 Chinese characters
- plugin descriptions: report only; do not edit vendor/plugin files

## 8. Phased Execution

### Phase 0: Baseline inventory

Deliverables:

- inventory script
- JSON output artifact
- no skill deletion
- no plugin disablement

Acceptance:

```powershell
python tools/inventory_codex_skills.py --root . --json
```

must report current counts and duplicates.

### Phase 1: Governance policy and registry

Deliverables:

- governance policy EN/ZH
- profiles registry YAML
- docs registry update

Acceptance:

```powershell
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
```

must pass.

### Phase 2: Governance check

Deliverables:

- governance check script
- tests
- CI integration if stable

Acceptance:

```powershell
python tools/check_codex_skills_governance.py --root . --json
python -m pytest test/check_codex_skills_governance.test.py
```

must pass.

### Phase 3: Safe cleanup proposal

Deliverables:

- generated report identifying duplicates
- OpenSpec duplicate investigation result
- preferred source decisions for duplicate GitHub skills
- no destructive user-level cleanup without explicit user approval

Acceptance:

- no browser capability loss for `D:\PythonProject_OpenClaw`
- no browser capability loss for `D:\PythonProject_CLIProxyAPI`
- OpenSpec guard remains green

### Phase 4: Profile launcher integration

Deliverables:

- documented profile-to-launcher mapping
- optional future launcher support such as `codex-ohmy-core`, `codex-ohmy-browser`, `codex-ohmy-web`, `codex-ohmy-full`

Acceptance:

- default sessions load fewer skills
- browser projects can still use browser verification
- web projects can still opt into Vercel/Next.js skills

## 9. Safety Rules

1. Do not delete user-level skills without a backup and explicit user approval.
2. Do not disable the entire Vercel plugin if the project needs browser automation and no replacement is installed.
3. Do not move repo-local durable state into user-level locations.
4. Do not make GitHub PRs by default for this repository.
5. Do not mutate `C:\Users\lenovo\.codex\config.toml` in a repository MR.
6. Do not treat `D:\PythonProject_langgraph` repo-local state as global state for other projects.
7. Do not adopt historical `.omx/state` records as live activation selectors unless the scoped selector policy explicitly permits it.

## 10. Verification Commands

Run before every MR conclusion:

```powershell
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/run_openspec_guard.py --root . --tool codex --refresh-managed-files --require-clean-git --json
git diff --check
```

Because `run_openspec_guard.py --require-clean-git` is sensitive to local untracked scratch files, run it in a clean temporary clone when necessary.

## 11. Publication Workflow

Follow the repository publication rule:

1. Create a feature branch.
2. Push to GitLab.
3. Open or update a GitLab MR.
4. Wait for GitLab pipeline success.
5. Merge to GitLab `main`.
6. Sync GitLab `main` directly to GitHub `main`.
7. Do not open a GitHub PR unless explicitly requested.

## 12. Done Definition

This plan is complete when:

- skills inventory exists and is repeatable
- skills governance policy exists in EN/ZH
- project profile registry exists
- governance checks are automated
- duplicate and long-description issues are reported with clear severity
- no cross-project browser capability is lost
- future skills have a documented placement and lifecycle rule
- a cold-start Codex session can read this plan and know exactly which files to create, which commands to run, and which safety boundaries not to cross
