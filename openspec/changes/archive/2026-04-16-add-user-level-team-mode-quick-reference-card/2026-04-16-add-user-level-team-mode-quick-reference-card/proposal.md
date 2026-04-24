## Why

The current user-level playbook is thorough, but it is no longer minimal. Operators now have enough working capability that they also need a short, high-signal command card for the most common actions without scanning the full playbook each time.

## What Changes

- Add a user-level quick-reference card for the most common Codex / oh-my-codex team-mode commands and state checks.
- Keep the card focused on operator-frequency actions rather than full policy explanation.
- Cover the highest-frequency actions across:
  - mode and switch inspection
  - backend inspection
  - durable-state inspection
  - durable-state reconciliation preview and apply
  - native `omx` team launch or ops
  - LangGraph run, inspect, and resume
- Clarify which commands are read-only by default and which are mutating actions.
- Link the quick-reference card from the generated user-level playbook instead of treating it as a separate undocumented side file.

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-quick-reference-card`: a concise user-level operator command card for the most common team-mode, state, and cleanup workflows

### Modified Capabilities
- `codex-user-level-team-mode-team-entrypoints`: extend the generated user-level documentation layer so the playbook references a minimal quick-reference companion instead of forcing operators to rely on the full playbook for common commands

## Impact

- impact_scope:
  - generated user-level docs under `C:\Users\lenovo\.codex\docs`
  - installer-generated playbook and related user-level documentation assets
  - regression coverage for generated user-level documentation assets
- explicit_non_goals:
  - no new backend family
  - no change to current global switch values
  - no new routing thresholds
  - no replacement of the full playbook with a shorter document
  - no repository-specific operator guide
- rollout_sequence:
  - define the quick-reference card scope and allowed command categories
  - generate the quick-reference asset alongside the existing playbook
  - update the playbook to point to the quick-reference card
  - validate that the generated asset stays aligned with the actual installed user-level command surfaces
- rollback_plan:
  - revert the generated quick-reference asset and playbook linkage if it proves redundant or misleading
  - restore prior user-level documentation assets from installer backups if needed
- validation_path:
  - verify the generated quick-reference asset under `C:\Users\lenovo\.codex\docs`
  - verify that the listed commands match actual installed user-level scripts
  - run `openspec validate --all`
- mainline_classification:
  - existing mainline continuation
  - specifically a user-level operator-documentation and command-guidance refinement pass
