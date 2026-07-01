---
doc_id: codex_cli_personal_production_durable_team_minimum_startup_documents
lang: en
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md
zh_cn_path: docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.zh-CN.md
---
# Codex CLI Personal Production Durable Team Minimum Startup Documents

## Purpose

This document defines the minimum embedded platform-governance start set for a Codex CLI personal production durable team inside a one-person-company project. It is not a business-startup list. It starts the embedded execution capability for agents, worktrees, durable state, validation gates, release gates, evidence, rollback, and review.

## Canonical 12-Document Startup Order

1. `thesis.md` - Explain why the embedded Codex platform-governance capability exists and what it refuses to own.
2. `architecture.md` - Define execution architecture, worktree boundaries, durable state, and authority boundaries.
3. `agent-governance.md` - Define what agents may do, draft, escalate, or never decide.
4. `agent-role-map.md` - Map agent roles to operating responsibilities and evidence expectations.
5. `agent-permissions.md` - Define tool, data, approval, and human-review permissions.
6. `delivery-plan.md` - Define how Codex work moves through planning, validation gates, release gates, and local-main evidence.
7. `observability.md` - Define runtime, repo, worktree, and agent evidence signals.
8. `risk-register.md` - Record platform, business, and mixed operating risks with scoped ownership.
9. `human-review-checklist.md` - Define human review before customer commitments, release gates, and irreversible actions.
10. `decision-log.md` - Record decisions with scope, truth owner, evidence source, decision right, and linked docs.
11. `backup-restore.md` - Define recovery for repo, runtime, durable state evidence, and rollback paths.
12. `monthly-review.md` - Drive recurring platform and business learning review.

## Process Group Usage

### Inputs

- Frozen one-person-company business boundary and current project scope.
- Repository state, worktree state, durable state, local-main status, and rollback evidence.
- Agent role catalog, permission matrix, validation gate expectations, and human-review rules.

### Tools And Techniques

- Read the 12 documents in the exact order above before assigning Codex execution truth.
- Apply local-main-first checks before any local integration.
- Use human review for customer commitments, contract promises, release approvals, financial commitments, and any mixed matter.
- Keep Codex execution truth separate from business truth while linking shared ledgers.

### Outputs

- A ready embedded Codex platform-governance baseline.
- A scoped decision log, risk register, human-review record, backup and restore path, and monthly review cadence.
- Evidence that the Codex team can operate without taking over customers, revenue, contracts, legal facts, or cashflow truth.

## Tailoring Note

Use the full 12-document set when the project changes customer-facing behavior, revenue, compliance, code, agents, runtime, durable state, or release boundaries. For a very small internal experiment, keep the order but complete a lighter entry in each document or ledger. Do not delete a document from the sequence; reduce the depth of the entry and record why the lighter path is safe.
