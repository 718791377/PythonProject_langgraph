---
doc_id: codex_skills_profile_launcher_mapping
lang: en
doc_class: governance
status: active
---

# Codex Skills Profile Launcher Mapping

## 1. Purpose

This document defines the repository-governed mapping from Codex skills profiles to future launcher surfaces.

The mapping is declarative. It does not install launcher aliases, edit user-level wrappers, edit user-level `config.toml`, disable plugins, or mutate skills.

## 2. Authority Boundary

The source of truth is:

- profile definitions: `docs_bilingual/governance/codex_skills_profiles.registry.yaml`
- launcher payload safety: `docs_bilingual/governance/user_level_launcher_payload_policy.md`
- publication workflow: GitLab-first repository workflow

Installed user-level wrappers are deployment artifacts. They are not changed by this mapping document.

## 3. Current State

The stable command remains `codex-ohmy`.

Profile-specific aliases are future optional names, not installed commands in this change:

- `codex-ohmy-core` - future optional reduced-scope default launcher alias.
- `codex-ohmy-browser` - future optional browser automation launcher alias.
- `codex-ohmy-web` - future optional web and deployment launcher alias.
- `codex-ohmy-github` - future optional GitHub workflow launcher alias.
- `codex-ohmy-full` - future optional troubleshooting launcher alias.

Future launcher work may implement physical aliases, a `--profile` flag, or both. Until then, the registry mapping is policy metadata and validation input.

## 4. Profile Mapping

| Profile | Future alias | Purpose | Plugin rule |
| --- | --- | --- | --- |
| `core` | `codex-ohmy-core` | Reduced default profile for non-web Codex work. | Does not require Vercel or broad plugin discovery. |
| `browser` | `codex-ohmy-browser` | Browser automation and visual verification. | Preserve Vercel browser skills until fine-grained filtering exists. |
| `web` | `codex-ohmy-web` | Web, frontend, Vercel, Next.js, and deployment work. | Preserve Vercel bundle behavior until fine-grained filtering exists. |
| `github` | `codex-ohmy-github` | GitHub issue and PR work when active. | Enable GitHub workflow surfaces only for active GitHub tasks. |
| `full` | `codex-ohmy-full` | Temporary troubleshooting and broad discovery. | Not a long-term default. |

## 5. Safety Rules

- Do not mutate `C:\Users\lenovo\.codex\config.toml` from a repository MR.
- Do not edit generated user-level wrappers as part of this mapping.
- Do not disable the Vercel plugin to reduce context pressure.
- Do not edit plugin cache files.
- Do not delete or rewrite user-level skills.
- Keep browser-profile projects able to use browser automation and visual verification.
- Keep web-profile projects able to use Vercel, Next.js, frontend, and deployment skills.

## 6. Validation

Run:

```powershell
python tools/check_codex_skills_profile_launcher_mapping.py --root . --json
```

The checker validates that:

- every required profile has a launcher mapping entry,
- every mapped profile exists in the profiles registry,
- aliases are marked as future optional or temporary,
- `core` is the reduced default,
- `full` is temporary and not the default,
- browser and web mappings preserve Vercel/plugin capability,
- config and wrapper mutation are forbidden.

## 7. Future Implementation Rule

A later launcher implementation change must start with its own OpenSpec change.

That future change must decide whether to expose:

- physical aliases,
- a `--profile` flag,
- both aliases and a flag.

It must also respect the launcher payload policy: large startup instructions must be file-backed, not passed inline through long command arguments.
