---
doc_id: codex_shared_local_model_assets_migration_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_shared_local_model_assets_migration_plan.md
translation_of: null
doc_class: implementation_plan
status: draft
---

# Shared Local Model Assets Migration Plan

## Scope

This plan describes how local llama and GGUF model assets can be moved under `D:\PythonProject_langgraph`, the orchestration repository that owns shared Codex CLI durable-team tooling, without making either `D:\PythonProject_langgraph` or `D:\PythonProject_OpenClaw` dirty by accident.

This plan is documentation and governance first. It does not move real GGUF files, start model servers, or modify OpenClaw.

## Goal

Centralize local model assets under an ignored local directory in `D:\PythonProject_langgraph`, while preserving the ability for OpenClaw and other consumer repositories to start or call those model services through explicit provider profiles.

Target model assets:

- `Qwen3.5-9B-Q4_K_M-GGUF` - local lightweight judgement and summarization model asset.
- `jina-embeddings-v5-text-small-retrieval-GGUF` - local embedding and retrieval model asset.

Recommended local roots:

- `D:\PythonProject_langgraph\.local\models\` - ignored local model asset directory for large model files.
- `D:\PythonProject_langgraph\.runtime\models\` - ignored local runtime model directory for temporary runtime assets.

## Non-Goals

- Do not commit GGUF files to ordinary Git.
- Do not rewrite Git history.
- Do not change `C:\Users\lenovo\.codex\config.toml`, the user-level Codex configuration file.
- Do not write `.omx/state/`, the repo-local durable state directory.
- Do not modify OpenClaw business or domain-agent state.
- Do not make local model providers durable backends, approval authorities, or routing selectors.

## Git Hygiene Rules

The repository should ignore local model assets and runtime caches:

```gitignore
.local/
.runtime/
*.gguf
*.GGUF
```

`git check-ignore -v`, the Git command that explains which ignore rule matched a path, should be used before copying large files.

`git status --short --branch`, the Git command that reports branch and dirty-work status, should be run before and after migration steps.

If a GGUF file is already tracked by Git, use a separate cleanup plan. The safe default is to back up the file, add ignore rules, run `git rm --cached` to remove it from the Git index while keeping the local file, then commit the index removal. Do not rewrite history in this migration slice.

## Ownership Split

`D:\PythonProject_langgraph`, the orchestration repository, owns:

- model asset directory conventions
- provider profile templates
- launcher templates
- health-check scripts
- adapter contracts
- Codex durable-team usage policy

`D:\PythonProject_OpenClaw`, the consumer domain-agent platform, owns:

- its own adapter or profile references
- its own business runtime configuration
- its own domain-agent state
- its own release validation

OpenClaw may start a shared model service if it uses an explicit provider profile and does not claim ownership of the model asset truth.

## Shared Versus Isolated

Allowed to share:

- GGUF model files
- local model server process definitions
- provider endpoint names
- provider profile IDs
- health checks
- checksum manifests

Forbidden to share:

- Codex durable-team state
- OpenClaw domain-agent state
- approval state
- recovery evidence
- customer data
- unredacted prompt or response logs
- `.omx/state/`, the repo-local durable state directory

## Provider Profiles

`local-judge-qwen` is a provider profile for `Qwen3.5-9B-Q4_K_M-GGUF`. It is advisory only and may be used for light judgement, bug triage, summary compression, and low-risk draft review.

`local-embed-jina` is a provider profile for `jina-embeddings-v5-text-small-retrieval-GGUF`. It may be used for local embeddings over documents, OpenSpec artifacts, plans, reports, and evidence.

Both profiles must stay behind provider adapters. A provider adapter is the bounded code layer that normalizes inputs, outputs, logging, health checks, and data boundaries for a model service.

## Environment Variable

`CODEX_LOCAL_MODEL_ROOT` is the environment variable for the shared local model root. It should normally point to:

```powershell
$env:CODEX_LOCAL_MODEL_ROOT="D:\PythonProject_langgraph\.local\models"
```

This variable lets OpenClaw or another consumer repository find the shared local model assets without hardcoding the path into tracked business code.

## Migration Phases

### Phase 0: Read-Only Inventory

Run `git status --short --branch`, the Git dirty-work check command, in both repositories.

Run `git ls-files`, the Git tracked-file listing command, to check whether any GGUF file is already tracked.

### Phase 1: Add Governance In The Orchestration Repository

In `D:\PythonProject_langgraph`, add or update ignore rules, provider policy, profile templates, health-check design, and this plan. Do not copy model files in the same commit.

### Phase 2: Copy Model Files Locally

Copy the model directories into `.local/models/`, the ignored local model root. After copying, run `git status --short --branch` and confirm that GGUF files do not appear as untracked work.

### Phase 3: Add Consumer Wiring In OpenClaw

In `D:\PythonProject_OpenClaw`, add only consumer wiring such as profile examples, adapter references, `.env.example`, and startup documentation. Do not copy model files into OpenClaw.

### Phase 4: Validate Both Repositories

Validate that Codex durable-team tooling and OpenClaw can discover the shared provider profiles, while both Git repositories remain clean after local-only model files are in place.

## Rollback

Rollback for documentation and scripts uses normal Git revert or branch deletion.

Rollback for local model files means deleting or moving files under `.local/models/`, the ignored local model root. Because those files are not tracked by Git, this operation must be done carefully and must not be scripted as part of an automatic repository cleanup.

## Acceptance Criteria

- The migration plan exists as an English ASCII primary and a UTF-8 Chinese companion.
- The local model provider policy exists and states that model services are shared but state is not shared.
- The repository ignore policy keeps GGUF files out of ordinary Git.
- The OpenSpec guard and document governance checks pass.
- No real GGUF files are moved by this documentation change.
