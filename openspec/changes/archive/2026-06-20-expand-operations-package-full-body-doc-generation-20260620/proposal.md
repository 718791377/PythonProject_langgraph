---
change_id: expand-operations-package-full-body-doc-generation-20260620
status: proposed
owner: codex
created_at: 2026-06-20
---

# Proposal: Expand Operations Packages To Full Body Document Generation

## Why

The current operations-package runtime proves deterministic package generation, checkers, registry coverage, tailoring language, and process-group Inputs / Tools And Techniques / Outputs. It still generates only the governance and register layer around the two operating systems. The user now requires the next package to generate the actual full-body operating documents:

- Codex CLI personal production durable team: 48 core body documents, each with an English primary and zh-CN companion.
- Personal production one-person-company operations: 60 core body documents, each with an English primary and zh-CN companion.

The numbers 48 and 60 must therefore become generated body-document counts, not only numbers shown in a register.

## What Changes

- Freeze a bilingual implementation plan for full-body operations-package generation.
- Add OpenSpec delta requirements that define 48/60 as real generated body-document counts.
- Require generated body documents to live under `docs_bilingual/operations_packages/` and remain separate from the earlier governance/register layer.
- Require every execution-facing body document to contain Inputs, Tools And Techniques, and Outputs sections; Chinese companions must use localized equivalents.
- Require every body document to include explicit tailoring guidance for full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid architecture.
- Require registry coverage for every generated body document pair.
- Keep Stage A and Stage B as two separate local-main integrations.

## Out of Scope

- Remote publication, GitLab MR creation/update/merge, GitHub sync, or any remote ref mutation.
- Re-reading or re-extracting raw PDF, EPUB, or Markdown source libraries during Stage B.
- Replacing the already created white papers, North Stars, inventory maps, or governance/register package documents.
- Modifying LangGraph durable orchestration, launchers, `.omx/state/`, or unrelated governance scripts.
