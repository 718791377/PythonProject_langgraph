# Management: Prevent Codex npm EPERM Cleanup Warnings

## Open

- [x] Value and why checked: avoid ambiguous Codex update state caused by Windows file-lock cleanup warnings.
- [x] Success criteria checked: update path blocks lock-risk updates by default, classifies cleanup warnings, and reports manual cleanup without killing processes.
- [x] Stakeholders/constraints checked: operator safety, existing Codex sessions, local-main-first publication boundary, no wrapper mutation.

## Design

- [x] Delivery tailoring checked: use existing official update template and its PowerShell test surface.
- [x] Risks/assumptions checked: active Codex sessions cannot be safely killed from inside the updater; fake process inventory is required for deterministic tests.
- [x] Acceptance evidence path checked: OpenSpec validation, focused PowerShell test, repository guard, local gate, local MR review.

## Build

- [x] Execution mode checked: subagent-driven-development after freeze; implementation may split into runtime and test slices.
- [x] Quality evidence checked: TDD for warning classification and lock preflight behavior.
- [x] Blocker decision checked: if durable-team adoption is unavailable, main session continues with bounded native experts.

## Verify

- [x] Variance review checked: no automatic process kill or staging-directory deletion in v1.
- [x] Risk/change impact checked: update behavior changes only when the script is about to mutate global npm packages on Windows.
- [x] Control decision checked: continue through local-main-first integration, stop before remote publication.

## Archive

- [ ] Value outcome checked after runtime package lands.
- [ ] Lessons learned recorded after validation.
- [ ] Archive/sync evidence recorded when this change is archived.

## Monitoring

- [x] Current facts recorded: `@openai/codex` EPERM cleanup warning was observed with active Codex/Node processes and a `.codex-*` leftover.
- [x] Return/no-return decision: no return needed; the frozen design matches the current problem and repo entrypoint.
