# Tasks

## 1. OpenSpec Artifacts

- [x] 1.1 Create `proposal.md`, the OpenSpec proposal for the traceable evidence intake pipeline.
- [x] 1.2 Create `design.md`, the OpenSpec design for PDF page evidence, HTML evidence, external tool inventory, knowledge boundaries, and tool maintenance boundaries.
- [x] 1.3 Create `specs/codex-product-lifecycle-document-governance/spec.md`, the delta spec for local-reference reading claims, knowledge-base boundaries, and tool inventory.

## 2. Implementation Plan

- [x] 2.1 Add `docs_bilingual/implementation_plans/evidence_intake_pipeline_workflow_plan.md`, the English ASCII implementation plan.
- [x] 2.2 Add `docs_bilingual/implementation_plans/evidence_intake_pipeline_workflow_plan.zh-CN.md`, the UTF-8 Chinese companion plan.
- [x] 2.3 Register the plan pair in `docs_bilingual/docs_registry.yaml`, the repository document registry.
- [x] 2.4 Add `docs_bilingual/implementation_plans/evidence_intake_pipeline_run_summary.md`, the English ASCII local run summary.
- [x] 2.5 Add `docs_bilingual/implementation_plans/evidence_intake_pipeline_run_summary.zh-CN.md`, the UTF-8 Chinese local run summary.

## 3. Tooling

- [x] 3.1 Add `tools/evidence_intake_pipeline.py`, the local PDF/HTML extraction and external-tool inventory script.
- [x] 3.2 Add fixture-based tests for text quality metrics, HTML visible-text extraction, and inventory classification.
- [x] 3.3 Ensure extraction output defaults to `.local/evidence/local_reference/`, an ignored local evidence directory.

## 4. Local Evidence Run

- [x] 4.1 Run the pipeline against the available local reference directory and write ignored local evidence under `.local/`.
- [x] 4.2 Run the inventory mode against an external local project and write ignored local evidence under `.local/`.
- [x] 4.3 Summarize results without committing extracted copyrighted or private reference text.

## 5. Validation

- [x] 5.1 Run `python test/evidence_intake_pipeline.test.py`, the unit test command for the pipeline.
- [x] 5.2 Run `openspec validate add-evidence-intake-pipeline`, the OpenSpec validation command for this change.
- [x] 5.3 Run `openspec validate --all`, the OpenSpec validation command for all specs and changes.
- [x] 5.4 Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`, the repository guard command.
- [x] 5.5 Run `git diff --check`, the whitespace validation command.
