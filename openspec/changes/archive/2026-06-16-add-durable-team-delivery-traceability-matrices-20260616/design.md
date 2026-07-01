# Design: Durable-Team Delivery, Traceability, And Process-Group Proof Surfaces

## Context

The fresh source run `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` was generated at `2026-06-15T17:33:52Z` and recorded 54 sources, 9,656 reading units, and 18,492,044 extracted characters. Tracked documents should cite aggregate and synthesized evidence only. Raw extraction text remains local ignored cache.

The previous corpus sync clarified the 10-layer runtime/governance capability core and the 12-layer product/business lifecycle planning frame. This slice adds proof surfaces so maintainers can audit delivery scope, evidence boundaries, and execution grammar without expanding every existing authority document.

## Decisions

1. Add three small proof surfaces instead of over-expanding the white paper, research note, plan, and playbook.
2. Keep authority split explicit: white paper owns strategic narrative, research note owns runtime/governance capability criteria, inventory maps own counts, PMI/lifecycle maps own tailoring and process-group grammar.
3. Use UR1 through UR4 as the stable cross-document user-requirement labels.
4. Keep all proof surfaces docs-only. They are evidence of documentation governance, not runtime implementation evidence.
5. Update stable OpenSpec specs manually and keep active delta specs as governed change evidence.

## File Scope

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.*` - maps UR1 through UR4 to deliverable documents, counts, and ownership evidence.
- `docs_bilingual/product_lifecycle/durable_team_source_traceability.*` - records the fresh source run identity, source counts, and tracked-versus-ignored evidence boundary.
- `docs_bilingual/product_lifecycle/durable_team_process_group_contract.*` - defines where Inputs / Tools and Techniques / Outputs grammar applies.
- active durable-team corpus docs that still cite the prior 20260614 evidence boundary
- `docs_bilingual/docs_registry.yaml` - registers the new bilingual proof surfaces for discovery.
- `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.*` - makes delivery-matrix and bridge requirements part of the stable durable-team plan contract.
- `openspec/specs/codex-product-lifecycle-document-governance/spec.*` - makes traceability and process-group proof requirements part of the stable document-governance contract.
- this OpenSpec change package and Superpowers evidence artifacts

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Proof surfaces are mistaken for runtime evidence | Repeat that docs are draft/documentation evidence only, not a running durable-team proof. |
| Raw cache becomes an authority dependency | State tracked versus ignored evidence in every new proof surface. |
| Whitepaper and research note roles collapse | Keep relationship and non-merge rules in traceability and delivery matrix docs. |
| Process-group vocabulary becomes heavy ceremony everywhere | Apply Inputs / Tools and Techniques / Outputs only to execution-facing layers, gates, and slices. |
| Chinese companion drift | Write bilingual pairs together and run pair/mojibake checks. |

## Acceptance Evidence

- New bilingual proof surfaces exist and are registered.
- Active docs reference `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` and `2026-06-15T17:33:52Z` as the current evidence boundary.
- Stable and delta OpenSpec requirements mention delivery, traceability, and process-group proof surfaces.
- Validation commands pass or record explicit follow-up blockers.
