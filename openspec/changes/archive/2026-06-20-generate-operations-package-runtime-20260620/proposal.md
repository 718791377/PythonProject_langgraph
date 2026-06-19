---
change_id: generate-operations-package-runtime-20260620
status: proposed
owner: codex
created_at: 2026-06-20
---

# Proposal: Generate Operations Packages And Runtime

## Why

The Codex CLI personal production durable-team corpus and the personal production one-person-company operations corpus already define their white papers, North Stars, inventory maps, lifecycle rules, PMI overlays, and tailoring principles. They still need an operational package layer that turns those canonical inventories into governed, checkable, bilingual files and a repeatable live runtime for generating and validating the package.

The user explicitly requires a two-stage local-main-first delivery: freeze the plan first, integrate it into local `main`, then implement the live runtime from the frozen plan and integrate that runtime into local `main`.

## What Changes

- Freeze a bilingual implementation plan for operations-package generation and runtime delivery.
- Add an OpenSpec delta requirement covering operations-package generation, tailoring decisions, process-group I/T/O, bilingual registry coverage, and local-main-first staging.
- Define Stage B runtime scope before runtime edits begin: a deterministic generator, a checker, tests, registry updates, and generated bilingual operations-package documents.
- Require all execution-facing flows in generated or checked documents to expose `Inputs`, `Tools And Techniques`, and `Outputs` sections, with Chinese companions using equivalent localized headings.
- Require explicit tailoring rules for full, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid architecture modes.
- Keep remote publication out of scope unless the user later explicitly requests remote publication.

## Out of Scope

- Re-reading raw Business Management or PMP source libraries in Stage B; this change operationalizes the already refreshed corpus.
- Remote GitLab/GitHub publication, GitLab MR creation/update/merge, GitHub sync, or remote ref mutation.
- Replacing the existing white papers, North Stars, or inventory maps as authority sources.
