# Management: Harden Skills2CLI Profile Routing Follow-up

## Open / Initiating

- [x] Value and why are stated. Close expert-reviewed routing quality and safety gaps after the initial Skills2CLI profile-routing baseline.
- [x] Success criteria are measurable. Stage A freezes the contract; Stage B implements checker/runtime/test hardening; no remote publication or profile apply occurs.
- [x] Stakeholders, constraints, or operating boundaries are identified. Constraints: no `config.toml`, no plugin cache, no vendor `SKILL.md`, no remote mutation, and skills/profiles are not native expert evidence.

## Design / Planning

- [x] Delivery approach is tailored: predictive, agile, or hybrid. Two local-main packages were used: Stage A plan-freeze then Stage B runtime implementation.
- [x] Major risks and assumptions are recorded. Risks covered: field-only quality without behavior proof, `full` fallback inflation, apply-boundary drift, installed-copy drift.
- [x] Acceptance evidence path is defined. Evidence path: plan docs, delta spec, focused checker/test output, representative suggestions, OpenSpec guard, local gate, local MR review, completed claim.

## Build / Executing

- [x] Execution mode is selected. Main-session-led implementation with expert read-only fan-in, LangGraph durable checkpoint state, and worktree isolation.
- [x] Quality evidence is recorded: TDD, review, test, or equivalent. Fresh evidence includes `python test\skills2cli.test.py`, `python test\check_skills2cli_profile_routing.test.py`, `python test\check_plugin_modules_skill.test.py`, `python -X utf8 tools\check_plugin_modules_skill.py --root . --json`, `python -X utf8 tools\check_skills2cli_profile_routing.py --root . --json`, representative `skills2cli profile suggest` smokes, `python tools\run_openspec_guard.py --root . --tool codex --json`, and `python tools\check_precommit_update_archive.py --root . --json`.
- [x] Blockers are cleared or have an explicit decision. Prior expert timeout/stall is treated as non-evidence; main session took over implementation and verifier performed read-only review. No config/cache/vendor/remote mutation occurred.

## Verify / Controlling

- [x] Variance from scope, design, and acceptance criteria is checked. Scope diff is limited to profiles registry, Skills2CLI runtime/contract/checkers, plugin-modules helper scripts, and focused tests plus OpenSpec bookkeeping/archive.
- [x] Risk and change impact are assessed. `full` is explicit-only, advisory outputs remain no-auto-apply, installed-copy drift is reported instead of trusted, and hard-load remains top-level only.
- [x] Control decision is recorded. Continue to archive after clean local validation; stop at remote publication gate because no GitLab/GitHub publication was authorized.

## Archive / Closing

- [x] Value outcome is summarized. Skills2CLI routing now has scenario metadata, orthogonal scope checks, task-module identity, explicit `full` eligibility, installed-artifact drift reporting, and advisory no-apply evidence.
- [x] Lessons learned or reusable guidance are recorded. Keep profile suggestions as advisory/preview surfaces; never treat profile/skill routing as native expert evidence; report installed-copy drift before user-level install/apply.
- [x] Delta spec sync, verification evidence, and archive path are confirmed. Delta spec will be synced to `openspec/specs/codex-user-level-plugin-modules-profile-helper/spec.md`; archive target is `openspec/changes/archive/2026-06-22-harden-skills2cli-profile-routing-followup/`; verification report path is set in `.comet.yaml`.

## Monitoring Loop

- [x] Current facts are checked. Stage A is already integrated on local `main` at `6919f0b`; Phase B implementation is in worktree branch `implement-skills2cli-profile-routing-followup-runtime`.
- [x] Continue, adjust, stop, or return decision is made. Continue; no earlier phase return is required.
- [x] If return is needed, target_phase and rework_reason are recorded. `target_phase` means the Comet phase to re-enter, and `rework_reason` means the reason code for revisiting an earlier phase; not applicable here because `target_phase=null` and `rework_reason=null`.

