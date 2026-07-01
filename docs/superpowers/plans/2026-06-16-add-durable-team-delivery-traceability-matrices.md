---
change: add-durable-team-delivery-traceability-matrices-20260616
design-doc: docs/superpowers/specs/2026-06-16-durable-team-delivery-traceability-design.md
base-ref: 46b8e38441b09a4ae1892d28e833b7a3c3d5466d
archived-with: 2026-06-16-add-durable-team-delivery-traceability-matrices-20260616
---

# Durable-Team Delivery Traceability Proof Surfaces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add bilingual proof surfaces and governed references for the durable-team documentation refresh.

**Architecture:** The change is docs-only. New proof surfaces map UR1 through UR4 to existing authority documents and OpenSpec specs while preserving raw-cache and runtime boundaries.

**Tech Stack:** Markdown, OpenSpec, repository document checkers, local-main-first validation.

archived-with: 2026-06-16-add-durable-team-delivery-traceability-matrices-20260616
---

## Task 1: Add proof surface documents

**Files:**
- Create: `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.md`
- Create: `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.zh-CN.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_source_traceability.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_source_traceability.zh-CN.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_process_group_contract.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_process_group_contract.zh-CN.md`

- [x] Step 1: Add the delivery matrix with UR1-UR4 rows and document target rows.
- [x] Step 2: Add the source traceability index with source run identity and evidence boundary.
- [x] Step 3: Add the process-group contract with Inputs / Tools and Techniques / Outputs.

## Task 2: Register and connect the proof surfaces

**Files:**
- Modify: `docs_bilingual/docs_registry.yaml`
- Modify: `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.md`
- Modify: `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.zh-CN.md`
- Modify: `openspec/specs/codex-product-lifecycle-document-governance/spec.md`
- Modify: `openspec/specs/codex-product-lifecycle-document-governance/spec.zh-CN.md`

- [x] Step 1: Register the new bilingual docs.
- [x] Step 2: Add stable spec requirements for delivery, traceability, and process-group proof surfaces.
- [x] Step 3: Add matching active delta specs under the OpenSpec change.

## Task 3: Refresh active corpus evidence references

**Files:** active durable-team and product-lifecycle docs under `docs_bilingual/`.

- [x] Step 1: Replace the prior 20260614 evidence boundary with `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` and `2026-06-15T17:33:52Z`.
- [x] Step 2: Add concise proof-surface handoff notes where the core corpus needs a current checkpoint.
- [x] Step 3: Keep archived OpenSpec history unchanged.

## Task 4: Validate and archive

- [ ] Step 1: Run OpenSpec strict validation for this change.
- [ ] Step 2: Run document pair, implementation-plan, name, mojibake, precommit, local gate, and local MR review checks.
- [ ] Step 3: Add verification reports and archive the OpenSpec change.
