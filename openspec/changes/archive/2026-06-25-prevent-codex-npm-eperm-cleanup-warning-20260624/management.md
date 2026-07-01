# Management: Prevent Codex npm EPERM Cleanup Warnings

## Open

- [x] Value and why are stated. Evidence: avoid ambiguous Codex update state caused by Windows `npm warn cleanup` / `EPERM` file-lock warnings.
- [x] Success criteria are measurable. Evidence: lock-risk updates block by default, cleanup warnings are classified, and leftover staging candidates are reported for manual cleanup.
- [x] Stakeholders, constraints, or operating boundaries are identified. Evidence: operator safety, existing Codex sessions, local-main-first publication boundary, no automatic process kill, no automatic staging deletion.

## Design

- [x] Delivery approach is tailored: predictive, agile, or hybrid. Evidence: extend the existing official update template and its focused PowerShell regression test surface.
- [x] Major risks and assumptions are recorded. Evidence: active Codex sessions cannot be safely killed from inside the updater; fake process inventory is required for deterministic tests.
- [x] Acceptance evidence path is defined. Evidence: focused PowerShell test, OpenSpec validate, precommit guard, OpenSpec guard, local gate, local MR review, guarded local-main integration.

## Build

- [x] Execution mode is selected. Evidence: Stage 2 used subagent-driven-development with leader-owned integration and a bounded test-engineer/verifier review loop.
- [x] Quality evidence is recorded: TDD, review, test, or equivalent. Evidence: focused fake npm/process-inventory regression tests cover blocking, override, unknown inventory, cleanup warning classification, and non-zero failure preservation.
- [x] Blockers are cleared or have an explicit decision. Evidence: Project MOE Mode CLI timeout blocker was fixed first; Stage A governance package and Stage B runtime package are both on local `main`.

## Verify

- [x] Variance from scope, design, and acceptance criteria is checked. Evidence: no automatic process kill or staging-directory deletion was added; implementation remains in `tools/codex-official-update-patch-replay-template.ps1` and tests.
- [x] Risk and change impact are assessed. Evidence: update behavior changes only before global npm mutation or when classifying successful npm cleanup warnings; non-zero install failures remain failures.
- [x] Control decision is recorded. Evidence: local-main-first integration is complete; remote publication remains unauthorized and was not performed.

## Archive

- [x] Value outcome is summarized. Evidence: local `main` now contains the fail-closed Windows Codex npm lock preflight and structured cleanup-warning reporting, preventing future ambiguous EPERM cleanup updates from being treated as unclassified success/failure noise.
- [x] Lessons learned or reusable guidance are recorded. Evidence: Windows npm updater code must treat live `codex.exe` locks as a pre-mutation risk; cleanup-warning classification must be gated on npm exit code `0`; stale `.codex-*` directories are manual cleanup candidates only.
- [x] Delta spec sync, verification evidence, and archive path are confirmed. Evidence: delta spec will sync through `comet-archive.sh`; verification report is `docs/superpowers/reports/2026-06-25-codex-npm-eperm-update-preflight-verification.md`; archive target is `openspec/changes/archive/2026-06-25-prevent-codex-npm-eperm-cleanup-warning-20260624/`.

## Monitoring Loop

- [x] Current facts are checked. Evidence: current local `main` is `84e8d624b964fe6a85032164183137937ee91e74`, ahead of `gitlab/main` and not behind; the Stage 2 runtime package is integrated locally and no remote publication was performed.
- [x] Continue, adjust, stop, or return decision is made. Evidence: continue to archive this completed change; no return to open/design/build/verify is required.
- [x] If return is needed, target_phase and rework_reason are recorded. Evidence: no return is needed; `.comet.yaml` keeps `target_phase: null` and `rework_reason: null`.
