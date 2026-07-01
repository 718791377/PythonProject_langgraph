# Management: Improve Skills2CLI Profile Routing

## Open

- [x] Value and why recorded in proposal.
- [x] Success criteria recorded in implementation plan.
- [x] Constraints recorded: advisory-only, no config apply, no plugin-cache edits, no remote publication.

## Design

- [x] Delivery tailoring recorded: two local-main packages, Phase A then Phase B.
- [x] Risks and assumptions recorded in plan.
- [x] Acceptance evidence paths recorded in plan and tasks.

## Build

- [x] Execution mode selected: subagent-driven-development / guarded local-main-first flow.
- [x] Quality evidence collected for Stage A plan freeze: OpenSpec validate, repository guard, precommit update/archive, worktree receipt, and UTF-8 checks passed.
- [x] Stage B focused evidence collected: py_compile, plugin-modules checker, skills2cli profile-routing checker, user-level mcp/skills CLI install checker, focused tests, representative profile suggestions, and OpenSpec guard passed.
- [x] No current blocker requiring user decision.

## Verify

- [x] Stage A variance review completed: verifier findings on layer consistency and bilingual audit linkage were applied before amend.
- [x] Stage B variance review completed: installed-wrapper smoke was upgraded from help-only to real `skills2cli profile suggest`; user-level registry copy drift remains report-only until explicit apply/install authorization.
- [x] Stage A risk/change impact reviewed: runtime mutation, profile apply, plugin cache edits, user-level config edits, and remote publication remain out of scope.
- [x] Stage B risk/change impact reviewed: `profile suggest` and `load_module.ps1` remain advisory, `set_plugin_profile.ps1` rejects scenario/task-module hard-load, and output flags `mutates_config=false`, `edits_plugin_cache=false`, and `profile_apply_performed=false`.
- [x] Control decision: continue.

## Archive

- [x] Value outcome recorded: Phase A and Phase B are integrated in local `main`; closeout adds `scene_description` compatibility, profile-level hints, and archive evidence so the runtime is explainable and checker-backed.
- [x] Lessons learned recorded: keep user-facing field names explicit (`scene_description`) while preserving previous consumer compatibility (`scenario_description`); profile-level outputs should carry hints even when task modules also provide focused hints.
- [x] Archive/sync evidence recorded after Stage B: OpenSpec archive exists under this directory, stable spec is updated, local `main` contains Stage A `3d08d6e`, Phase B `80ec3dd`, and audit rerank closeout `d72aee7`; remote publication remains unauthorized.

## Monitoring

- [x] Current facts: Phase B runtime now has scenario/task-module routing, former only-full plugins have non-full routes, and installed-copy drift is reported instead of silently trusted.
- [x] Return/no-return decision: continue.
