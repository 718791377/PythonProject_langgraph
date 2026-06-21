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

- [ ] Value outcome recorded.
- [ ] Lessons learned recorded.
- [ ] Archive/sync evidence recorded after Stage B.

## Monitoring

- [x] Current facts: Phase B runtime now has scenario/task-module routing, former only-full plugins have non-full routes, and installed-copy drift is reported instead of silently trusted.
- [x] Return/no-return decision: continue.
