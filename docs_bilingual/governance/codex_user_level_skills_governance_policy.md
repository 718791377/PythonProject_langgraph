---
doc_id: codex_user_level_skills_governance_policy
lang: en
doc_class: governance
status: active
---

# Codex User-Level Skills Governance Policy

## 1. Purpose

This policy defines how user-level Codex skills, repository-local skills, plugin skills, and profile metadata are governed for the Codex orchestration line on this machine. The goal is to reduce startup skills context pressure without losing cross-project capabilities such as OpenSpec workflows, Codex orchestration governance, durable-team routing, LangGraph policy, browser automation, and verification.

This policy is declarative. It does not delete skills, disable plugins, or mutate `C:\Users\lenovo\.codex\config.toml`.

## 2. Authority Boundary

Use this boundary rule:

```text
shared runtime and policy: user-level
project facts and durable truth: repo-local
```

User-level policy may describe reusable skills, launch profiles, and shared runtime behavior. Repository-local state remains under the repository that owns it, including `openspec/changes/`, `openspec/specs/`, `.omx/state/`, `.omx/state/langgraph/`, repository task queues, memory summaries, CI state, and release state.

`D:\PythonProject_langgraph` is the source of truth for this governance policy and the related implementation plans. It must not move its repo-local durable state into a user-level shared runtime, and it must not treat its repo-local state as global state for other projects.

## 3. Skill Layer Model

Skills are governed in four primary layers:

1. `core_user`: user-level skills that are broadly useful, low context cost, and safe to load by default.
2. `profile_user`: user-level skills that are useful for a class of projects but should be enabled by profile or project policy.
3. `repo_local`: skills owned by a specific repository, such as repository OpenSpec skills. Repository-local skills must not leak repository facts or durable state into other repositories.
4. `plugin`: vendor or plugin supplied skills. Treat plugin skills as bundle-managed until the launcher supports fine-grained plugin-skill filtering.

Inventory tools may report more detailed source labels, but policy decisions map back to these four layers.

## 4. Placement Rules

Place a skill in the lowest authority layer that owns the behavior:

- Cross-project workflow instructions belong in user-level skills or user-level governance docs.
- Repository facts, active changes, and durable task state belong in the repository.
- OpenSpec workflow skills may exist in repositories that have OpenSpec initialized, but generated files must be treated as managed artifacts.
- Plugin skills remain under their plugin cache and should not be edited by repository changes.
- New skills with broad applicability should start as profile-gated unless they are clearly safe for `core`.

Do not bulk-edit skill descriptions before an inventory and governance check can measure the effect.

## 5. Profile Definitions

The profile registry is `docs_bilingual/governance/codex_skills_profiles.registry.yaml`.

Required profiles:

- `core`: always-on cross-project skills for skill management, diagnostics, planning, review, notes, worker/team protocol docs, general OpenSpec workflow, and Codex orchestration governance.
- `openspec`: OpenSpec workflow capability, including proposal, apply, verify, sync, archive, and refresh guidance when a repository uses OpenSpec.
- `orchestration`: Codex subagent, OMX, durable-team, LangGraph, routing, state, and recovery policy.
- `browser`: browser automation, browser MCP, Playwright, visual verification, web console testing, and agent-browser workflows.
- `web`: Vercel, Next.js, React, AI web app, frontend, and deployment work.
- `github`: GitHub issue and PR workflows only when they are active for the task.
- `full`: short-lived troubleshooting profile for broad skill discovery.

`full` is not a long-term default profile.

## 6. Project Defaults

Default profiles are declarative project policy, not an automatic launcher mutation:

| Project | Default profiles | Rule |
| --- | --- | --- |
| `D:\PythonProject_langgraph` | `core`, `openspec`, `orchestration` | Source of truth for Codex orchestration governance and implementation plans. |
| registry browser legacy application project | `core`, `browser`, `orchestration` | Browser automation is expected and must remain available. |
| `D:\PythonProject_CLIProxyAPI` | `core`, `browser`, `orchestration` | Browser or endpoint verification may be required and must remain available. |
| `D:\project` | `core` | Add browser or web only after repository evidence requires it. |
| future projects | `core` first | Add `browser`, `web`, `github`, or `full` only when project evidence requires it. |

## 7. Duplicate Skill Policy

Duplicate skill names are handled by scope and authority:

- Duplicate names inside the same governed layer are errors unless the registry declares a temporary exception for a managed generated artifact under active investigation.
- Cross-layer duplicates are warnings until the policy records a preferred source.
- Repository-local OpenSpec nested duplicates must not be deleted until OpenSpec regeneration and the OpenSpec guard are green in a clean clone.
- GitHub skill duplicates should prefer the plugin source when the GitHub plugin is the active workflow surface.
- Plugin duplicates are report-only unless the plugin manager or launcher exposes a supported filtering mechanism.

The current policy preference is:

- `gh-address-comments`: prefer plugin when GitHub review work is active.
- `gh-fix-ci`: prefer plugin when GitHub CI work is active.
- `openspec-*`: prefer repository-local generated OpenSpec skills for repository OpenSpec work until official generation behavior is verified.

## 8. Description Length Limits

Suggested limits for frontmatter `description` values:

- user-level skills: 180 English characters or 80 Chinese characters
- repository-local skills: 220 English characters or 100 Chinese characters
- plugin skills: report only; do not edit vendor or plugin files from a repository MR

Long descriptions should be shortened only after inventory output makes the change measurable and reviewable.

## 9. Plugin Handling Rules

Do not disable an entire plugin only to reduce context pressure when an active project depends on capabilities from that plugin.

For the Vercel plugin, browser projects must preserve access to these browser-oriented skills when available:

- `agent-browser` - Vercel plugin browser automation skill for agent-driven browser sessions.
- `agent-browser-verify` - Vercel plugin browser verification skill for checking browser behavior.
- `verification` - Vercel plugin full-story verification skill for acceptance and behavior checks.
- `investigation-mode` - Vercel plugin structured debugging workflow skill for browser or app investigations.

If partial plugin skill loading is not supported, keep the Vercel plugin available for `browser` and `web` profile projects instead of globally disabling it.

## 10. Safety Rules

- Do not delete user-level skills without a backup and explicit user approval.
- Do not disable the Vercel plugin when browser automation is required and no replacement is available.
- Do not move repository durable state into user-level locations.
- Do not automatically edit `C:\Users\lenovo\.codex\config.toml` from a repository MR.
- Do not treat historical `.omx/state` records as live activation selectors unless scoped selector policy permits it.

## 11. Publication Workflow

This repository uses GitLab as the authoritative review and merge surface:

1. Create a feature branch.
2. Push the feature branch to GitLab.
3. Open or update a GitLab MR.
4. Wait for the GitLab pipeline to pass.
5. Merge into GitLab `main`.
6. Sync that exact GitLab `main` commit directly to GitHub `main`.
7. Do not open GitHub PRs unless the user explicitly overrides this workflow.

## 12. Required Checks

Before concluding a skills governance MR, run at least:

```powershell
git diff --check
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/inventory_codex_skills.py --root . --json
```

When the governance check is in scope, also run:

```powershell
python tools/check_codex_skills_governance.py --root . --json
python -m pytest test/check_codex_skills_governance.test.py
```
