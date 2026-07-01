---
doc_id: codex_platform_inventory_map
lang: en
doc_class: product_lifecycle
status: draft
canonical_path: docs_bilingual/product_lifecycle/codex_platform_inventory_map.md
zh_cn_path: docs_bilingual/product_lifecycle/codex_platform_inventory_map.zh-CN.md
---

# Codex Platform Inventory Map

This map is the concise canonical inventory for the target Codex platform architecture used by this repository.

## Fresh Source Evidence

This map uses the June 16 fresh extraction run `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` (`2026-06-15T17:33:52Z`) as its evidence boundary. Exact inventory counts come from the full-text read of `Business Management/Architecture note 1 - Codex CLI personal production durable team.md` (source `S0030`, 10,424 characters). Business Management sources explain operating principles; PMP sources provide process-group and tailoring discipline.

## Canonical Inventory

| Inventory element | Count | Canonical shape |
| --- | ---: | --- |
| Trunk layers | 12 | Cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, retrospective |
| Virtual departments | 4 | Strategy and Product Office; Engineering and Platform Office; Agent Governance Office; Growth and Knowledge Office |
| Responsibility domains | 24 | Six domains per department |
| Cross-cutting modules | 18 | Finance, operations, engineering, organization, legal, security, knowledge, risk, productivity, agent, data, trust, toolchain, SLA, asset, research, channel, exit |
| Core documents | 48 | Eight six-document families |
| Governed AI agents | 12 | Research, PM, Architect, Code, Review, Test, Security, DevOps, Data, Docs, Ops, Risk |
| Recommended books | 12 | Product, engineering, operating-system, security, and delivery references |

## Source-Family Rationale

| Source family | Role in this map | Why it is authoritative here |
| --- | --- | --- |
| Fresh architecture-note extraction under `.omx/state/langgraph/extraction/` | Exact inventory counts and named structures | The local architecture note for the Codex CLI durable-team target defines the 12 layer, 4 department, 24 domain, 18 module, 48 document, 12 agent, and 12 book shape |
| Business-management sources | Operating principles | They justify intentional smallness, product discovery, architecture boundaries, delivery quality, team topology, metrics discipline, trust, and reusable operating mechanisms |
| PMP sources | Process-group operating gate | They provide the Initiating, Planning, Executing, Monitoring and Controlling, and Closing gate discipline used to operate each layer and release slice |
| Existing lifecycle docs in `docs_bilingual/product_lifecycle/` | Repository wording and boundary alignment | They connect this inventory to platform-build lifecycle, downstream-consumption boundaries, and local governance language already used in the repo |

## 12 Trunk Layers

| # | Layer | Primary question | Primary owner surface |
| ---: | --- | --- | --- |
| 0 | Cognitive narrative | Why should the platform exist | Vision and thesis |
| 1 | Business | Why is it worth maintaining | Business model and pricing |
| 2 | Market | Which developers and teams need it | User segments and market map |
| 3 | Strategy | What to do first and what to refuse | Strategy and product boundary |
| 4 | Metrics | What evidence changes decisions | North Star, metrics, tracking |
| 5 | Product | Which operator workflows are exposed | PRD and CLI UX |
| 6 | Technical | How the platform stays safe and evolvable | Architecture and ADRs |
| 7 | Organization | Who owns decisions and permissions | Role map and operating rhythm |
| 8 | Execution | How work ships and rolls back | Delivery plan and definition of done |
| 9 | Growth | How adoption compounds | Growth model and trust surface |
| 10 | Operations | How support and runtime health stay stable | Support playbook and changelog |
| 11 | Retrospective | How lessons become durable | Decision log and postmortem |

## 4 Departments and 24 Domains

### Strategy and Product Office

1. CEO and strategy owner
2. Chief of staff
3. Business model owner
4. Finance owner
5. Market intelligence
6. Customer research

### Engineering and Platform Office

7. Product strategy
8. PM and PRD owner
9. CLI and UX owner
10. Metrics owner
11. CTO and architect
12. Engineering manager

### Agent Governance Office

13. Code quality owner
14. DevOps owner
15. Platform and toolchain owner
16. Security owner
17. Privacy and data protection owner
18. Data governance owner

### Growth and Knowledge Office

19. Agent governance owner
20. Agent evaluation owner
21. Docs owner
22. Support owner
23. Brand and trust owner
24. Knowledge and review owner

## 18 Cross-Cutting Modules

| Module group | Modules |
| --- | --- |
| Core operating control | Finance, operations, engineering management, organization design, legal and compliance, security |
| Durable learning control | Knowledge management, risk management, personal productivity, AI agent governance, data governance, brand trust |
| Scale and boundary control | Toolchain governance, SLA governance, asset and IP governance, user-research governance, channel governance, exit governance |

## 48 Core Documents

The fresh architecture note fixes the target at 48 core documents. This canonical map normalizes that target into eight six-document families so the count stays exact and operable.

| Document family | Count | Canonical documents |
| --- | ---: | --- |
| Strategy and business | 6 | `vision.md`, `thesis.md`, `business-model.md`, `pricing.md`, `unit-economics.md`, `strategy.md` |
| Market and product | 6 | `user-segments.md`, `market-map.md`, `research-repository.md`, `product-strategy.md`, `prd.md`, `cli-ux.md` |
| Metrics and data | 6 | `metrics.md`, `north-star.md`, `tracking-plan.md`, `data-dictionary.md`, `data-quality-checklist.md`, `experiment-log.md` |
| Engineering and platform | 6 | `architecture.md`, `adr.md`, `module-boundaries.md`, `tech-stack.md`, `delivery-plan.md`, `observability.md` |
| Security and risk | 6 | `security-policy.md`, `access-control.md`, `privacy-policy.md`, `incident-response.md`, `risk-register.md`, `backup-restore.md` |
| Agent governance | 6 | `agent-role-map.md`, `agent-permissions.md`, `agent-governance.md`, `human-review-checklist.md`, `agent-evaluation.md`, `agent-failure-modes.md` |
| Growth and operations | 6 | `growth-model.md`, `docs-plan.md`, `support-playbook.md`, `faq.md`, `trust-page.md`, `changelog.md` |
| Retrospective and knowledge | 6 | `decision-log.md`, `weekly-review.md`, `monthly-review.md`, `postmortem.md`, `learning-log.md`, `template-library.md` |

## 12 Governed AI Agents

| Agent | Main lane | Human gate |
| --- | --- | --- |
| Research Agent | Research and evidence gathering | Strategy interpretation |
| PM Agent | PRD and acceptance drafting | Scope and priority |
| Architect Agent | ADR and boundary drafting | Final architecture decision |
| Code Agent | Implementation and refactor | Merge approval |
| Review Agent | Review findings and release warnings | Accept or reject release |
| Test Agent | Test authoring and regression checks | Test deletion and release signoff |
| Security Agent | Security review and dependency checks | Permission and production changes |
| DevOps Agent | CI, deployment, and observability drafts | Production deployment |
| Data Agent | Metrics analysis and dashboard drafts | Metric definition changes |
| Docs Agent | README, FAQ, and lifecycle docs | Public commitments |
| Ops Agent | Triage, summaries, and operational reviews | User-facing responses |
| Risk Agent | Risk, compliance, and license review | Legal and policy release |

## 12 Recommended Books

1. Scaling People
2. Working Backwards
3. High Output Management
4. INSPIRED
5. Product Operations
6. Team Topologies
7. Accelerate
8. Shape Up
9. Lean Analytics
10. Designing Data-Intensive Applications
11. Secure by Design
12. The Staff Engineer's Path


## Layer-Level Inputs, Tools And Techniques, Outputs

Every one of the 12 trunk layers can run lightweight or full, but execution-facing work must still be expressible as Inputs, Tools and Techniques, and Outputs.

| Layer group | Inputs | Tools And Techniques | Outputs |
| --- | --- | --- | --- |
| 0-2 Narrative, business, market | User problem, source evidence, stakeholder signal, market/adoption assumptions | Strategy diagnosis, PR/FAQ, interview synthesis, positioning, initiating gate | White paper update, business boundary, market/adoption hypothesis, initial risks |
| 3-5 Strategy, metrics, product | North Star, OKRs, lifecycle tailoring decision, opportunity evidence | Guiding-policy design, OMTM/guardrail design, product discovery, planning gate | Strategy plan, metrics contract, PRD or release-slice brief, acceptance criteria |
| 6-8 Technical, organization, execution | Architecture constraints, role/agent map, implementation plan, worktree ownership | Architecture review, threat/risk review, OpenSpec, subagent/durable-team threshold check, executing gate | Technical design, ownership matrix, committed changes, validation evidence |
| 9-11 Growth, operations, retrospective | Release evidence, usage/adoption signals, incidents, lessons learned | Monitoring and controlling, portfolio review, PMO-style governance service, closing gate | Release notes, operating runbook, retrospective, archive and next-cycle decision |

## Process-Group Operating Gate

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Candidate layer, document family, module, agent surface, value hypothesis, scope boundary | Target-inventory mapping, owner identification, non-goal check, durable-state boundary check | Purpose, value hypothesis, owner, scope boundary, initial risk |
| Planning | Initiation output, dependencies, acceptance criteria, risk profile, human-vs-agent boundary | I/T/O planning, release slicing, validation design, rollback design, role-boundary review | Acceptance criteria, dependency map, risk response, validation path, human-vs-agent boundary |
| Executing | Approved slice, source evidence, templates, worktree state, role ownership | Controlled drafting or implementation, review, testing, doc update, expert/durable-lane handoff when eligible | Drafted artifact, controlled change set, validation work, changed-path evidence |
| Monitoring and Controlling | Active change set, metrics, issues, review findings, gate output | Local gate, OpenSpec guard, diff review, issue triage, change control, rollback readiness check | Metrics, issue log, review findings, local-gate evidence, rollback readiness |
| Closing | Accepted artifacts, validation evidence, archive candidates, lessons | Archive/sync, release note update, retrospective, next-cycle triage | Final document or policy, archive record, lessons learned, next-cycle input |

## Use Rule

Use this map when a platform change must show where it lands in the target architecture. A non-trivial slice should name at least one affected layer, one department, one responsibility domain, one module group, one core document family, and any governed-agent boundary that changes.

## Stage B Embedded Governance Closeout

This Stage B closeout makes the nested relationship explicit: the one-person company owns business truth, and embedded Codex owns governed execution truth. Embedded Codex is not a peer business authority and must not redefine business truth.

- Codex boundary: Codex owns execution truth for agents, OpenSpec, worktrees, durable state, validation gates, local-main evidence, rollback, and release boundaries, while consuming business intent from the one-person company.
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
