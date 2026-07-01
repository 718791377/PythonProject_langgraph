---
doc_id: codex_cli_durable_team_agent_evaluation
doc_class: operations_package
status: active
package: codex
body_kind: agent_governance_body
generated_by: tools/generate_operations_package.py
lang: en
---

<!-- GENERATED_BY: tools/generate_operations_package.py; DO NOT EDIT BY HAND. -->

# Codex CLI Durable Team Agent Evaluation Body Document

## Purpose

Defines how the personal production command-line team system operates the agent-evaluation.md artifact inside the agent governance family with evidence gates, expert routing discipline, and approval boundaries.

## Authority Boundary

- Authority sources: team white paper, North Star, product lifecycle registers, PMI process-group contract, OpenSpec change, and local-first publication rules.
- This document operationalizes only this governed command-line team package.
- Codex owns execution truth for agents, OpenSpec, worktrees, durable state, validation gates, local-main evidence, rollback, and release boundaries.
- Codex remains an embedded execution capability inside a one-person company; it is not a peer business authority and must not redefine business truth.
- Any remote publication still requires explicit approval in the current user message.

## Lifecycle Placement

- Primary lifecycle layers: L7 Organization, L8 Execution
- Primary process groups: Planning, Executing, Monitoring and Controlling
- Owner surface: Agent Governance Office
- Document family: Agent governance; source list item: `agent-evaluation.md`.

## Tailoring Rules

Default tailoring mode: Full architecture. This choice must explain why it is not heavier or lighter and must keep escalation triggers visible.

| Mode | Use when | Lightweight scope |
| --- | --- | --- |
| Full architecture | Cross-stage, external-customer, revenue, compliance, security, publication, rollback, durable-state, shared-runtime, or multi-agent work. | Govern every affected risk layer end to end. |
| Whole-project lightweight | Private, reversible, low-risk exploration with no external commitment, durable-state impact, publication, sensitive data, or shared runtime. | The whole project may stay light while still recording owner, validation, rollback, and learning. |
| Phase-local lightweight | One discovery, metrics, growth, or retrospective phase is low risk inside a larger governed project. | Only that named phase is light; upstream and downstream gates stay explicit. |
| Module-level lightweight | One bounded document family, helper, prototype, or local module does not change trust, state, public API, CI, release, or shared runtime behavior. | Only that module is light; the surrounding project keeps its full boundary. |
| Hybrid architecture | Most real work, where low-risk phases can start light but production, customer, revenue, trust, durable-state, or release impact needs fuller control. | Critical layers are full; low-risk phases or modules stay light until escalation triggers fire. |

### Why this mode is not heavier or lighter

`agent-evaluation.md` uses the default mode because the agent governance family needs governed evidence, but a heavier mode is reserved for external commitment, sensitive information, shared state, or difficult recovery.

### Escalation triggers

Escalate to a heavier tailoring mode when scope, trust, compliance, revenue exposure, recovery difficulty, or cross-boundary coordination exceeds the assumptions recorded for the current mode. For `agent-evaluation.md`, also escalate when the owner cannot confirm evidence, validation is no longer repeatable, or outputs affect an external commitment.

## Inputs

- Current local workspace, OpenSpec state, registry state, validation gates, and Agent Governance Office owner constraints.
- The `agent-evaluation.md` document family, risk profile, dependencies, rollback path, or retirement path.
- Latest boundaries for expert routing, durable execution, and local-first evidence.

## Tools And Techniques

- Twelve-layer placement, RACI, agent gates, process-group I/T/O, and tailoring scorecard.
- Deterministic generator, checker, focused tests, local CI, local review, and rollback reference.
- Expert or durable lane handoff only when ownership is isolated, with leader-owned fan-in.

## Outputs

- Governed `Agent Evaluation` body document, zh-CN companion, and registry entry.
- Owner, tailoring mode, escalation triggers, validation path, and publication approval boundary record.
- Operating evidence for later implementation, verification, retrospective, or archive work.

## Process Group Operating Table

| Process group | Inputs | Tools And Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | source need, owner signal, scope boundary, first risk; document `agent-evaluation.md` | charter framing, stakeholder scan, tailoring pre-check | authorized operating slice, named owner, initial risk log |
| Planning | approved purpose, dependencies, constraints, acceptance target; document `agent-evaluation.md` | I/T/O planning, RACI mapping, validation design, rollback design | document plan, validation path, rollback boundary |
| Executing | approved slice, templates, evidence, local state; document `agent-evaluation.md` | controlled drafting, review, test, evidence capture | updated operating artifact, change evidence, handoff record |
| Monitoring and Controlling | active artifact, metrics, issues, review feedback; document `agent-evaluation.md` | quality checks, variance review, change control, gate rerun | issue log, decision record, gate evidence |
| Closing | accepted artifact, final evidence, residual risk; document `agent-evaluation.md` | closeout review, archive or registry sync, retrospective | final body doc, registry entry, lessons learned |

## Closeout And Registry

- Registry `doc_id` remains unique: `codex_cli_durable_team_agent_evaluation`.
- English primary `docs_bilingual/operations_packages/codex_cli_durable_team/agent-evaluation.md` and zh-CN companion `docs_bilingual/operations_packages/codex_cli_durable_team/agent-evaluation.zh-CN.md` stay paired.
- Closeout confirms owner, tailoring mode, escalation triggers, output evidence, and next-cycle input.
