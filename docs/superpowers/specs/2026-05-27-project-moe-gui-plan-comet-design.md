# Project MOE GUI Plan Full Comet Refactor Design

## Context

The Project MOE Agent GUI plan is a long-lived implementation plan. A previous pass aligned it with the newer executable-plan style, and the initial slice formalized the work as a full Comet/OpenSpec change. This continuation adds one bounded toolchain behavior: guarded uninstall `--apply`.

## Design Goals

- Make the target plan readable as an executable implementation plan without requiring chat history.
- Preserve Project MOE-specific boundaries instead of copying Pi sidecar runtime assumptions.
- Keep target project readiness, GUI runtime implementation and remote publication as separate states.
- Record Windows Comet bash unavailability honestly.
- Align with the Comet runtime plan's management-record, phase-gate, Monitoring-return, and evidence-retention semantics.
- Allow uninstall apply only for manifest-owned, allowlisted, hash-verified GUI artifacts while preserving private project surfaces.

## Selected Structure

The plan uses the same structural family as `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`:

- frontmatter with status/readiness/change metadata;
- review conclusion and status interpretation;
- relationship model and source-of-truth table;
- goals/non-goals;
- architecture and usage;
- install artifact and manifest contract;
- Phase 1 CLI and Phase 2 GUI contracts;
- JSON state model;
- readiness lanes;
- ordered implementation slices, item-level checkboxes, file ownership, and local integration order;
- verification plan, related-doc rules, risk table and self-checks.

## Acceptance Criteria

- The target plan has no ambiguous claim that a target project is GUI-ready.
- The target plan names the current Comet change.
- Management record, phase gates, Monitoring return semantics and evidence retention are explicit.
- Chinese paired support artifacts are valid UTF-8 Chinese instead of mojibake or question-mark placeholders.
- The OpenSpec change validates.
- The precommit update/archive gate accepts the explicit archive deferral.
- Targeted toolchain tests prove guarded uninstall apply deletes only verified managed artifacts and fails closed on out-of-allowlist manifest entries.
- The local MR review passes after commit.

## Guarded Uninstall Boundary

- `--apply` may delete only the fixed Project MOE GUI managed-artifact allowlist.
- Every non-manifest managed file must retain a matching manifest hash before deletion.
- Directory entries, paths outside the allowlist, missing hashes, and hash mismatches block the apply before deletion.
- `MOE.md`, `.codex/agents/*.toml`, and `.omx/state` remain protected and are not uninstall targets.
- This continuation does not install dependencies, adapt a real target project, or publish remote refs.
