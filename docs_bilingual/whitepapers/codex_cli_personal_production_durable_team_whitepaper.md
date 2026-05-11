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

This is an AI-era value-delivery system, not only a toolchain. The platform exists to help a solo maintainer keep value judgment, risk trade-offs, approvals, release responsibility, and learning loops inspectable while AI accelerates research, drafting, planning, and verification support.

- Native Codex remains the base layer.
- Native subagents remain leader-side expert bursts.
- `native_omx` is the worker-centric durable backend lane used after plan freeze and independent execution slices.
- `langgraph` is the graph-shaped checkpoint and approval lane used when graph phases, checkpoints, approval gates, or survivor queues are required.
- OpenSpec remains the repository governance and change-control surface.
- Repo-local durable state remains inside each project.

## 12-Layer Target Architecture

The white-paper target is not a generic multi-agent story. It is a governed Codex CLI platform architecture:

- 12 trunk layers keep the platform connected from narrative to retrospective learning.
- 4 virtual departments keep platform strategy/product, engineering/platform, agent governance, and growth/knowledge responsibilities separate.
- 24 responsibility domains, 18 cross-cutting modules, and 48 core documents define the minimum serious operating surface for a production-grade personal developer platform.
- 12 governed AI agents expand execution and review capacity, but the human operator and current main Codex leader session keep final authority.
- 12 recommended books provide the local management, product, engineering, organization, security, and learning reference base.

This inventory is intentionally smaller than the downstream one-person-company operating-system inventory. The Codex platform should build developer orchestration mechanisms; it should not absorb downstream customer, revenue, finance, legal, or operations truth.

## PMI Delivery Discipline

The platform narrative becomes actionable only when delivery follows a process-group discipline. Every release slice should identify Inputs, Tools and Techniques, and Outputs, then move through initiating, planning, executing, monitoring and controlling, and closing. This keeps AI-assisted delivery inspectable and prevents hidden automation from becoming approval authority.

## Architecture Tailoring Rule

The full platform architecture is used for the affected scope when work changes reusable orchestration behavior, native subagent routing, `native_omx`, LangGraph, worktree safety, OpenSpec governance, user-level launchers, skill/profile governance, local-main-first publication, shared templates, durable state, release safety, or cross-project adoption.

Lightweight treatment is allowed only for bounded low-risk phases or modules that are reversible and do not change runtime entrypoints, secrets, durable state, CI gates, release gates, or downstream project dependencies. The decision rule lives in `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md`.


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
