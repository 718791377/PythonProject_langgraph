---
doc_id: codex_cli_personal_production_durable_team_whitepaper
lang: en
canonical: docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md
translation_of: null
doc_class: whitepaper
status: draft
---

# White Paper: Codex CLI Personal Production Durable Team

## Purpose

This white paper answers why a solo maintainer who works across multiple repositories needs a personal production durable team for Codex CLI. It is the cognitive-narrative document for the platform, not an implementation task list.

## Problem Narrative

A single chat session is useful for local work, but it is not enough as the only production control surface when work must survive context loss, restarts, multi-session collisions, release gates, rollback, and cross-project adoption.

The structural failures are prompt-only safety rules, dirty worktrees, unclear helper-source truth, shared-runtime state leakage, and premature durable-team launch before plan freeze.

## New Paradigm

The target is a layered Codex CLI production system:

- Native Codex remains the base layer.
- Native subagents remain leader-side expert bursts.
- `native_omx` is the worker-centric durable backend lane used after plan freeze and independent execution slices.
- `langgraph` is the graph-shaped checkpoint and approval lane used when graph phases, checkpoints, approval gates, or survivor queues are required.
- OpenSpec remains the repository governance and change-control surface.
- Repo-local durable state remains inside each project.

## Key Assumptions

- Recovery, inspection, and rollback are more important than hidden automation.
- User-level helpers are useful only when they stay thin and do not become durable truth.
- Each repository must keep its own source, OpenSpec artifacts, tests, release state, and durable facts.
- Local model providers are advisory services, not approval authorities or durable backend selectors.

## Non-Goals

- Do not replace native Codex CLI.
- Do not treat oh-my-codex as a Codex replacement.
- Do not put repo-local durable truth into a user-level virtual environment or helper mirror.
- Do not launch durable teams for read-only inventory, boundary-freeze work, or single-slice tasks.
- Do not mix downstream business runtime dependencies with Codex CLI durable-team dependencies unless the downstream project explicitly owns them.

## Downstream Documents

- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md` is the MRD; it defines target project types, capability profiles, runtime-owner boundaries, and risk controls.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` is the North Star and implementation-bridge plan; it turns this narrative into staged targets, metrics, lanes, and release slices.
- `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md` is the lifecycle reference; it defines how white papers, MRDs, North Star plans, PRDs, technical designs, release plans, and retrospectives relate.
