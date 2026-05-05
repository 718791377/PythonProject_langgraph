---
doc_id: codex_local_model_provider_policy
lang: en
canonical: docs_bilingual/governance/codex_local_model_provider_policy.md
translation_of: null
doc_class: governance
status: active
---

# Codex Local Model Provider Policy

## Purpose

This policy defines how local model services are shared by Codex CLI durable-team tooling and consumer repositories without sharing durable state, business data, approval authority, or routing truth.

## Provider, Not Truth

A local model provider is a model service endpoint behind a bounded adapter. It can generate text, embeddings, judgement summaries, or retrieval vectors. It must not become:

- durable truth
- approval authority
- backend routing selector
- persistent team identity
- project memory authority
- business runtime state

## Standard Provider Profiles

`local-judge-qwen` is the local lightweight judgement provider profile. It may use `Qwen3.5-9B-Q4_K_M-GGUF` for low-cost judgement, bug triage, summary compression, and evidence ordering.

`local-embed-jina` is the local embedding provider profile. It may use `jina-embeddings-v5-text-small-retrieval-GGUF` for local embeddings over documents, OpenSpec artifacts, implementation plans, reports, and evidence.

## Light Judge Strategy

`Light Judge` is a strategy, not a required dependency. It can be used for candidate bug triage, survivor-queue generation, low-cost quality gates, and inspect-summary hints.

`Light Judge` must not decide final approval, own durable state, launch persistent workers, or select durable backend families.

## Shared Service Boundary

`D:\PythonProject_langgraph` may centrally manage model assets, provider profile templates, health checks, and adapter contracts. OpenClaw and other consumer repositories may call or start the service through explicit profiles.

Shared service assets may include model files, endpoints, health checks, and checksums. Shared service assets must not include project durable state, OpenClaw domain-agent state, customer data, or unredacted prompt logs.

## Adapter Requirements

A provider adapter must define:

- `profile_id` - stable profile name used by scripts and docs.
- `model_asset` - model asset name or manifest reference.
- `health_check` - read-only check that reports whether the provider can answer.
- `allowed_use` - allowed use cases such as judgement or embeddings.
- `forbidden_use` - forbidden use cases such as approval authority or durable truth.
- `data_boundary` - statement of what logs, prompts, and outputs may be stored.

## Git And Runtime Rule

Real GGUF files should stay under ignored local roots such as `.local/models/` or `.runtime/models/`. Git should track manifests, checksums, docs, scripts, and templates, not large model binaries.

## Failure Rule

If a provider is unavailable, Codex durable-team tooling must fail closed or fall back to a documented non-provider path. It must not silently reinterpret provider unavailability as approval, readiness, or successful routing.
