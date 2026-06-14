---
doc_id: north_star_plan
lang: en
canonical: docs_bilingual/north_star_plan.md
translation_of: null
doc_class: north_star_plan
status: draft
---

# North Star Plan: Codex CLI Personal Production Durable-Team Platform

## Document Identity

This is the metrics-layer North Star plan for the Codex CLI personal production durable-team platform. It translates the white-paper narrative, MRD requirements, and product-lifecycle inventory maps into measurable direction. It is not runtime evidence that a durable or persistent team is currently running.

Fresh source evidence for this refresh comes from ignored extraction artifacts generated at `2026-06-14T10:48:53Z` under `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614/`: `fresh_source_manifest.json`, `fresh_source_synthesis.json`, and the local raw `fresh_source_items.jsonl`. The extraction covers 54 sources: 31 Business Management sources, 23 PMP sources, 31 PDFs / 9,280 pages, 9 EPUBs / 362 spine items, 14 Markdown full-text files, and 18,492,044 extracted text characters. The tracked document records synthesis only; source text, per-unit extraction streams, and extraction logs remain uncommitted.

## Primary North Star Metric

**Safe cold-start continuation success rate**: the percentage of new or resumed Codex sessions that can continue a project task without repeated user explanation, cross-project state leakage, false durable-team claims, unsafe Git/worktree action, or unverified completion claims.

## Input Metrics

| Input metric | Why it matters | Example evidence |
| --- | --- | --- |
| Startup context recovery rate | A new session must find the right read order and current mainline | Startup summaries, `AGENTS.md`, docs registry |
| Routing evidence completeness | Experts, `native_omx`, and LangGraph must be selected or rejected for concrete reasons | Routing trace with phase, backend readiness, thresholds, blockers |
| Durable-state isolation quality | Shared user-level helpers must not become cross-project durable truth | Repo-local `.omx/state/`, selector status, state-status output |
| Plan-freeze quality | Durable team execution should start only after the target and slices are clear | Frozen plan, scope, owner map, validation, rollback boundary |
| Validation freshness | Completion claims require recent evidence | Local gates, OpenSpec guard, diff review, test output |

## Guardrail Metrics

- Zero false claims that a durable or persistent team ran without selector, manifest, heartbeat, worker record, or closed-agent evidence.
- Zero use of an outdated extraction cache as the source of truth when the task requires fresh reading.
- Zero unauthorized remote publication, protected-branch mutation, or cross-project Git commit.
- Zero mixing of Codex platform durable state with downstream business runtime truth.

## Target Architecture Inventory

| Target | Inventory | Authority boundary |
| --- | --- | --- |
| Codex CLI personal production durable team | 12 trunk layers + 4 virtual departments + 24 responsibility domains + 18 cross-cutting modules + 48 core documents + 12 governed AI agents + 12 recommended books | This repository owns platform governance, helper source, docs, checkers, templates, and repo-local platform durable state |
| Personal production one-person company | 12 trunk layers + 5 virtual departments + 30 responsibility domains + 20 cross-cutting modules + 60 core documents + 15 governed AI agents + 15 recommended books + 12 minimal startup documents | Downstream repositories own customer evidence, revenue, finance, legal, support, release, durable state, and lessons learned |

## Process-Group Operating Model

Layer-level I/T/O authority remains in `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md`; PMI overlay and tailoring authority remain in `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` and `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md`. This North Star plan owns metric direction, decision thresholds, and evidence cadence.

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | White paper, MRD, source-synthesis evidence, startup pain, routing failures, durable-state risks | Value framing, stakeholder/owner mapping, non-goal review, risk framing | North Star metric, guardrails, scope boundary, initial risks |
| Planning | North Star metric, input metrics, lifecycle maps, PMI tailoring rules, current capability state | Metric decomposition, threshold design, tailoring, release-slice planning, validation design | Input-metric plan, decision thresholds, release-slice metrics, validation plan |
| Executing | Approved plan, worktree ownership, docs/templates/checkers, extraction evidence | Documentation updates, checker updates, expert fan-out when eligible, local validation | Updated docs, templates, checkers, release evidence, changed-path list |
| Monitoring and Controlling | Current metrics, routing evidence, selectors, gates, review findings, issue logs | Diff review, OpenSpec guard, local CI, durable evidence checks, change control | Accepted changes, defects, deferred risks, rollback readiness, routing corrections |
| Closing | Accepted artifacts, validation output, archive candidates, lessons | Closeout review, docs registry/spec sync, retrospective, next-cycle triage | Stable docs, archived change or deferral, lessons learned, next increment |

## Decision Thresholds

- Use the full platform architecture when a change affects orchestration, subagent routing, `native_omx`, LangGraph, worktree safety, OpenSpec governance, launchers, checkers, release safety, or cross-project templates.
- Allow whole-project lightweight only for low-risk private spikes or local notes with no external users, money, trust boundary, sensitive data, shared runtime entrypoint, durable-state change, or release commitment.
- Use phase-local or module-level lightweight when a bounded slice is low risk and reversible, while adjacent high-risk phases or modules stay on the full architecture path.
- Use hybrid when discovery is still needed but eventual delivery may affect users, trust, revenue, compliance, runtime behavior, or release safety.
