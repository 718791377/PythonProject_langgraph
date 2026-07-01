---
change: add-durable-team-delivery-traceability-matrices-20260616
status: draft
archived-with: 2026-06-16-add-durable-team-delivery-traceability-matrices-20260616
status: final
---

# Design: Durable-Team Delivery And Traceability Proof Surfaces

## Goal

Add three compact proof surfaces for the durable-team corpus: delivery matrix, source traceability, and process-group contract.

## Approach

The proof surfaces sit beside existing authority documents. They do not replace the white paper, research note, inventory maps, PMI map, implementation plan, playbook, or OpenSpec specs. They make the refresh auditable by mapping user requirements UR1 through UR4 to files, evidence boundaries, bridge rules, and process-group gates.

## Decisions

- Use table-heavy documents so cold-start maintainers can scan the update quickly.
- Treat `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` as the current source evidence boundary.
- Keep raw extraction streams out of Git.
- Keep the white paper and research note physically separate.
- Use Inputs / Tools and Techniques / Outputs only for execution-facing gates, layers, and release slices.

## File Ownership

- Delivery matrix: `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.*`
- Source traceability: `docs_bilingual/product_lifecycle/durable_team_source_traceability.*`
- Process-group contract: `docs_bilingual/product_lifecycle/durable_team_process_group_contract.*`
- Governance links: docs registry plus durable-team and lifecycle OpenSpec specs.

## Acceptance

- The new files are bilingual pairs.
- English primary files are ASCII-only.
- The proof surfaces cite aggregate evidence only.
- OpenSpec validation and document checks pass before archive.
