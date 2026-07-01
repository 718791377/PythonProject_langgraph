---
doc_id: ten_to_twelve_layer_bridge
lang: en
doc_class: product_lifecycle
status: draft
canonical_path: docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.md
zh_cn_path: docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.zh-CN.md
---

# 10-To-12 Layer Bridge

This bridge explains why the research note and the white paper remain separate, how their layer models connect, and how to read in both directions without collapsing their responsibilities.

## Canonical Roles

- The research note owns the canonical 10-layer runtime/governance capability model.
- The white paper owns the canonical 12-layer product/business lifecycle narrative for the Codex CLI platform.
- This bridge owns only the mapping grammar between them.
- This bridge must not redefine the research model and must not replace the lifecycle stack.

## Relationship

- The research note uses a 10-layer runtime/governance decomposition to study what a solo-maintainable persistent team must do at execution time.
- The white paper uses the repository 12-layer product/business lifecycle to explain why the Codex CLI durable-team platform should exist and how it becomes governable.
- They should not be physically merged now because they have different audiences, review paths, and downstream references.

## Reading Modes

### Read 10 -> 12

Use this direction when a runtime finding needs lifecycle owners, documents, release gates, or platform-facing explanation.

Questions in this mode:

- Which lifecycle layer receives this runtime capability?
- Which document should own the resulting requirement?
- Which owner, metric, runbook, or release gate must be updated?

### Read 12 -> 10

Use this direction when a white-paper or lifecycle claim needs proof that the runtime can really support it.

Questions in this mode:

- Which runtime capability makes this lifecycle claim true?
- Which research-layer evidence must exist before the lifecycle claim is credible?
- Which runtime gaps block the lifecycle promise?

## 10 -> 12 Bridge Table

The table is a bridge-time aggregation. It does not replace the research note's canonical 10-layer runtime list; it groups adjacent runtime concerns so each concern can land in the appropriate 12-layer lifecycle document, owner, and gate.

| 10-layer research model | Primary 12-layer landing zones | Secondary 12-layer landing zones | Bridge rule |
| --- | --- | --- | --- |
| Interaction and execution | Product, Execution | Operations | Convert runtime interaction capability into product promises, execution workflow, operating runbooks, and safe user expectations |
| Team orchestration | Organization, Execution | Operations | Convert worker/leader coordination into responsibility domains, agent governance, escalation paths, and execution gates |
| Agent state persistence | Technical, Operations | Retrospective | Convert state fields into architecture contracts, recovery evidence, migration rules, and post-incident learning |
| Task-flow persistence | Technical, Execution | Operations | Convert workflow state into plan checkpoints, resumption rules, and governed execution handoffs |
| Memory and context | Cognitive Narrative, Technical | Operations, Retrospective | Convert memory capability into cold-start understanding, context-store design, retention policy, and learning feedback |
| Retrieval and knowledge | Growth, Technical | Metrics, Retrospective | Convert retrieval into knowledge reuse, source maps, quality evidence, and compounding learning loops |
| Quality and evaluation | Metrics, Execution | Retrospective | Convert evaluation into acceptance gates, regression checks, release criteria, and lessons learned |
| Security and governance | Organization, Technical | Operations | Convert security constraints into trust boundaries, ownership rules, operating controls, and approval discipline |
| Observability and audit | Metrics, Operations | Retrospective | Convert observability into guardrails, trace evidence, closure evidence, and learning assets |
| Control center and operator surface | Cognitive Narrative, Product, Organization | Operations | Convert operator surfaces into authority boundaries, recoverable workflows, incident handling, and command discipline |

## 12-Layer Receiving View

This table is the reverse view. Start from a lifecycle layer and ask which 10-layer runtime concerns usually feed it.

| 12-layer lifecycle layer | Usual incoming 10-layer concerns | Why this layer receives them |
| --- | --- | --- |
| 0. Cognitive Narrative | Memory/context; control center; auditability | The operator needs a stable story, a recoverable mental model, and visible authority surfaces |
| 1. Business | Interaction/execution; quality/evaluation; recovery cost | Business value depends on whether the platform reliably produces useful work at maintainable cost |
| 2. Market | Interaction/execution; quality/evaluation; observability/audit | Market positioning depends on visible capability, reliability, and trust evidence |
| 3. Strategy | Security/governance; team orchestration; persistence boundary | Strategy owns local-first posture, backend-family separation, and solo-maintainer control |
| 4. Metrics | Retrieval/knowledge; quality/evaluation; observability/audit | Metrics make runtime quality, cost, and evidence inspectable |
| 5. Product | Interaction/execution; control center; team orchestration | Product shape is the user-facing expression of execution capability and control design |
| 6. Technical | Agent state persistence; task-flow persistence; retrieval/storage; security | Architecture receives the runtime mechanisms and trust constraints |
| 7. Organization | Team orchestration; security/governance; control center | Ownership, role discipline, and authority boundaries belong here |
| 8. Execution | Interaction/execution; task-flow persistence; quality assurance | Delivery flow depends on coordination, checkpointing, and acceptance behavior |
| 9. Growth | Retrieval/knowledge; memory/context; evaluation | Growth comes from reuse, compounding knowledge, and measurable improvement |
| 10. Operations | Persistence; task-flow persistence; memory/context; observability; security | Operations owns recovery, incidents, runbooks, and day-two controls |
| 11. Retrospective | Memory/context; retrieval/knowledge; evaluation; audit | Retrospective turns runtime evidence into corrections and reusable learning |

## Added 12-Layer Context

The 12-layer lifecycle adds business-facing trunks that the 10-layer runtime research does not own directly: cognitive narrative, business, market, strategy, metrics, product, organization, execution, growth, operations, and retrospective learning. Cognitive narrative, business, market, and growth are the most visible additions beyond the runtime capability model. They are not a replacement for runtime capability analysis; they are the larger frame in which runtime capability becomes a platform.

## Bridge Execution Grammar

Use this process-group style whenever a 10-layer runtime finding is converted into 12-layer lifecycle work, or whenever a 12-layer claim needs 10-layer runtime proof.

### Inputs

- The research-note layer, capability gap, source evidence, maturity finding, or runtime risk being bridged.
- The lifecycle-layer claim, product statement, operating rule, or retrospective conclusion being checked.
- The target lifecycle mode: Codex CLI durable-team platform or downstream one-person-company operating system.
- Fresh-source evidence boundary, inventory-count authority, affected layer owners, and current OpenSpec or delivery state.
- Constraints from security, durable state, operator authority, release safety, budget, and downstream project ownership.

### Tools And Techniques

- Bridge-time aggregation: group adjacent runtime concerns without renaming the canonical research model.
- Receiving-view lookup: choose which 12-layer lifecycle layers receive the runtime finding.
- Reverse-proof lookup: choose which 10-layer concerns must be cited to prove a lifecycle claim.
- Authority split review: keep runtime capability authority in the research note, narrative authority in the white paper, count authority in the inventory maps, PMI authority in the PMI reference map, and execution grammar in the lifecycle documents.
- Tailoring review: decide whether the result needs full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid governance.
- I/T/O expansion: if the bridged result drives execution, expand it into Inputs, Tools and Techniques, and Outputs in the receiving lifecycle document or OpenSpec change.

### Outputs

- A named 12-layer landing zone for the runtime finding.
- A named 10-layer proof path for the lifecycle claim.
- Updated lifecycle, white-paper, research-note, North Star, or OpenSpec references without merging their responsibilities.
- A tailoring decision and execution grammar for the affected scope.
- Traceable evidence showing which model is being used and which document owns the result.

## Governance Rule

Use the 10-layer model when evaluating runtime capability completeness, state, orchestration, memory, auditability, and operator control. Use the 12-layer model when deciding whether the platform or a downstream one-person company has enough narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, and retrospective evidence. If a document cites both, state which model is being used, which lifecycle layer receives the result, and which research-layer proof supports it.

Count authority remains in `codex_platform_inventory_map.md` and `one_person_company_inventory_map.md`. Runtime capability authority remains in `solo_maintainable_production_persistent_team_research.md`. Narrative authority remains in `codex_cli_personal_production_durable_team_whitepaper.md`. This bridge owns only the mapping between those authorities.

## Stage B Embedded Governance Closeout

This Stage B closeout makes the nested relationship explicit: the one-person company owns business truth, and embedded Codex owns governed execution truth. Embedded Codex is not a peer business authority and must not redefine business truth.

- Shared boundary: business truth defines customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, and business learning; execution truth defines agents, OpenSpec, worktrees, durable state, validation gates, local-main evidence, rollback, and release boundaries.
- Tailoring modes: full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid are all scoped choices. Tailoring does not delete the twelve-layer mental model; it only changes how much evidence and ceremony is required for the chosen project, phase, module, or release slice.
- Bridge rule: the 10-layer runtime capability view is an implementation projection of the 12-layer lifecycle view. The bridge prevents runtime convenience from overriding lifecycle authority.

### Inputs

- Current business intent, execution evidence, registry entry, tailoring decision, and local-main / remote-publication boundary.
- Business truth inputs when customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, or business learning are affected.
- Execution truth inputs when agent routing, OpenSpec, worktree isolation, durable state, validation, rollback, or release boundaries are affected.

### Tools And Techniques

- Apply the shared truth-boundary map before selecting full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid mode.
- Use process-group I/T/O, RACI ownership, evidence traceability, validation gates, and escalation triggers instead of deleting layers.
- Route mixed changes through both the business gate and the Codex execution gate before local-main integration or remote publication.

### Outputs

- A scoped governance mode, updated evidence trail, linked registry entry, and explicit owner for business truth, execution truth, or mixed truth.
- A closeout decision that either stays lightweight in the declared scope, escalates to fuller architecture, or stops at the publication gate until human approval.
