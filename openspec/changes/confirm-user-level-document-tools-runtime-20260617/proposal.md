---
change_id: confirm-user-level-document-tools-runtime-20260617
status: proposed
owner: codex
created_at: 2026-06-17
---

# Proposal: Confirm User-Level Document Tool Runtime

## Why

The previous reusable document/PDF/vector tooling promotion moved the shared source surfaces into `D:\PythonProject_langgraph`, but the current checkout still needs an explicit follow-up confirmation package before live runtime fixes are implemented. Current evidence shows three remaining runtime-confirmation gaps:

- the repository-local Poppler cache under `.local/user_level_document_tools/` is not present yet;
- three document-pipeline PowerShell scripts currently fail parser checks;
- `D:\project` still contains old tool copies and unrelated dirty files, so it must be treated as a guarded source/consumer project rather than an unprotected implementation location.

## What Changes

- Freeze Stage 1 as a documentation-and-governance confirmation package only; do not claim live runtime completion.
- Record Stage 2 live runtime backlog for Poppler local cache confirmation under `.local/user_level_document_tools/`, document-pipeline PowerShell parser/runtime confirmation, and vector/retrieval framework smoke confirmation.
- Confirm `D:\PythonProject_langgraph\tools\user_level_document_tools` as the shared source/runtime-confirmation home and `D:\project` as guarded source/consumer evidence only.
- State that Poppler `.local` cache remains untracked and real vector data/indexes are not migrated into shared source.
- Require dirty-file protection for `D:\project` before any consumer-side cleanup or comparison work.

## Out of Scope

- Remote publication, GitLab MR creation/merge, or GitHub sync.
- Moving `D:\project` business data, protected source material, guard rules, or live vector indexes into this repository.
- Migrating vector databases, embeddings, JSONL corpora, or other live retrieval data from `D:\project`.
- Cleaning unrelated dirty files in `D:\project`.
- Rewriting archived OpenSpec history or historical implementation plans solely to replace old path names.
