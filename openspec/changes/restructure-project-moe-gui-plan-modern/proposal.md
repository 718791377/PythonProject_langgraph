# Change: Restructure Project MOE GUI Toolchain Plan

## Why

The Project MOE Agent GUI implementation plan still used an older cumulative-document shape, while the newer Pi sidecar plan uses an executable-plan structure with explicit architecture, source-of-truth, contracts, gates, rollback, risks, and self-check sections. The mismatch makes the MOE plan harder to execute and easy to misread as a historical status log.

## What Changes

- Rewrite `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` into the newer executable-plan structure.
- Preserve the Project MOE-specific Phase 1/Phase 2, Ready/Bootstrap/Repair lanes, readiness gates, state contracts, target-project install model, rollback, and validation boundaries.
- Record this as a Comet/OpenSpec tweak because it is a single-document structural refresh with no runtime code or interface implementation change.

## Impact

- No runtime behavior changes.
- No remote publication.
- No target-project writes.
- Existing OpenSpec change `refresh-project-moe-gui-plan-comet` remains separate and completed with archive deferred because the current Windows shell cannot execute Comet bash scripts.
