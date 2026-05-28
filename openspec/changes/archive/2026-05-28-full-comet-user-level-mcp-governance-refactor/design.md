# Design: Full Comet governance-plan framing

## Summary

This change treats the target document as a complete `/comet` governance plan rather than a tweak shortcut. The design preserves the plan's existing lane coverage while making phase gates explicit enough for future implementation slices to be audited without relying on chat context.

## Decisions

1. **Full Comet over tweak wording.** The frontmatter and Section 0.1 use `full` and `open-design-build-verify-archive` so the document no longer implies that design and planning can be skipped.
2. **Evidence-first phase gates.** Section 16 defines Open, Design, Build, Verify, and Archive gates with evidence and return behavior.
3. **No runtime expansion.** This refactor is documentation/governance only. Actual helper installs and live automation remain separate OpenSpec changes.
4. **Pi sidecar stays referenced, not absorbed.** Pi/oh-my-pi details remain in `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`; this document references it only as a local Codex governance fork source.

## Risks and mitigations

- Risk: the document could overstate implementation maturity. Mitigation: preserve planned/implemented-local/installed-user-level/smoke-tested/active/rollback-ready state gates and keep unfinished lanes unchecked.
- Risk: full Comet artifacts add process weight to a document-only change. Mitigation: keep the OpenSpec delta narrow and avoid user-level runtime mutations.
- Risk: archive sync could overwrite the large stable spec if misused. Mitigation: this change records archive readiness/deferral rather than running unsafe manual archive sync without a merge-aware archive path.

## Acceptance

- The target document no longer says the plan is a Comet tweak.
- The target document includes full Comet phase gates and verification expectations.
- Local implementation-plan and baseline checkers pass.
- OpenSpec validation and repository guard pass.
