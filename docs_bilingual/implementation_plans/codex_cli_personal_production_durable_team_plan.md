---
doc_id: codex_cli_personal_production_durable_team_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md
translation_of: null
doc_class: implementation_plan
status: draft
---

# Codex CLI Personal Production Durable Team Plan

> Scope and document identity
>
> - This document is not a pure user-level authority index and not a single-repository task sheet.
> - It is a combined user-level plus project-level implementation plan for deploying a personal production durable team model that can be reused across all `PyCharm / Codex CLI` projects under the same machine, user account, and Codex home.
> - The user-level part describes shared control surfaces, shared runtime assets, shared role catalogs, and long-term contract direction.
> - The project-level part explains how each repository keeps its repo-local source, repo-local durable state, OpenSpec, project documents, tests, and exceptions.
> - Stable user-level rules belong in `docs_bilingual/governance/`. Structural multi-file repository work still belongs in OpenSpec.

## 1. Document Positioning And Goal

This plan defines, under the following baseline assumptions, how to build a production-grade durable team model for `Codex CLI` that is maintainable by one developer and reusable across all `PyCharm / Codex CLI` projects:

- `subagent` keeps its existing role
- `native_omx` keeps its existing role
- `langgraph` is treated as already close to a `fully realized LangGraph-native orchestration runtime`
- no new capability may break the stable three-lane operating model
- external tooling reuse is allowed, but only within existing repository safety boundaries and additive-only governance

This plan does not replace the white paper or the governance research canon:

- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` - concise strategic white paper for why the direction exists, target-state narrative, and the 12-layer lifecycle frame.
- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.md` - evidence-heavy production-capability research canon, including the 10-layer runtime capability core.

Document-layer role:

| Layer | Role of this document |
| --- | --- |
| User-level | Describe target-state contracts, shared control surfaces, and shared runtime behavior reused by all `PyCharm / Codex CLI` projects |
| Cross-project shared layer | Explain how shared launchers, support scripts, shared venvs, role catalogs, and helper artifacts work without hosting canonical durable state |
| Project-level | Explain how one repository keeps repo-local state, source, OpenSpec, documents, tests, and rollout ownership |

This plan exists to:

- map the governance research document's 10-layer production-capability core into the white paper and lifecycle documents' 12-layer product/business architecture for all `PyCharm / Codex CLI` projects
- explain how the user-level layer, cross-project shared layer, and project layer should each land under the baseline
- define what can be reused directly, what should only be borrowed by design, and what should stay out of the main stack
- explain how many projects can share one durable-team model while keeping project durable truth isolated
- explain how existing `experts / durable_team / persistent team` concepts fit into one unified control model without collapsing their differences
- provide a phased rollout path that does not break existing behavior

## 1.1 Lifecycle Alignment

This draft is the North Star and implementation-bridge plan for the strategy layer. It consumes the white paper and MRD:

- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` is the white paper; it explains why the direction exists.
- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md` is the MRD; it defines target project types, capability profiles, runtime-owner boundaries, and risk controls.

This plan outputs staged targets, lane boundaries, release slices, metrics, and non-goals for later PRD, architecture, test, release, rollback, adoption, and retrospective documents.

PMBOK8 value-delivery overlay for this draft:

- PMBOK 8th Edition is used as the primary overlay for value delivery, project canvas, performance-domain thinking, AI-era project governance, hybrid delivery, and tailoring.
- PMBOK 6th Edition and Process Groups are used only as execution support for inputs, tools and techniques, outputs, and closeout gates.
- PMBOK 7th Edition is used as the principles, value-delivery, performance-domain, and tailoring bridge.
- Agile Practice Guide is used for adaptive discovery, MVP slices, feedback loops, and small reversible releases.
- Program Management is used when multiple related initiatives need shared benefits, sequencing, or dependency alignment.
- Portfolio Management is used when value, capacity, risk, and release timing must be balanced across competing work.
- PMO Practice Guide is used as the pattern for governance services, enablement, oversight, and reusable operating standards.

This means each future release slice must describe not only the task list, but also the value increment, feedback point, validation path, rollback boundary, and operator consent boundary.

### 1.2 12-Layer Architecture Inventory Alignment

The older ten-layer runtime map in this plan is a historical decomposition for execution lanes. It is not the full document-governance model. The full product/business lifecycle model is now the 12-layer trunk: cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, and retrospective.

The Codex CLI personal production durable-team target uses this inventory: 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, and 12 recommended books. This is the platform target for reusable Codex orchestration mechanisms. The canonical count map is `docs_bilingual/product_lifecycle/codex_platform_inventory_map.md`.

The downstream personal production one-person-company target uses this larger inventory: 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and 12 minimal startup documents. This is a downstream business operating-system model and must not be treated as platform repo-local truth. The canonical count map is `docs_bilingual/product_lifecycle/one_person_company_inventory_map.md`.

### 1.3 Process-Group Execution Contract

Execution-facing plan sections use a PMI process-group style:

- Inputs: source documents, current state, constraints, risks, approvals, and upstream layer outputs.
- Tools and Techniques: OpenSpec, local-main-first gates, worktree isolation, native subagents, `native_omx`, LangGraph, checkers, reviews, tests, release and rollback planning.
- Outputs: approved plans, changed files, validation evidence, release evidence, archive evidence, lessons learned, and next-cycle inputs.

This contract applies before a durable team or graph lane is launched. A durable lane still requires a frozen plan plus at least two mostly independent execution slices.

### 1.4 Tailoring Contract

`docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md` defines when this North Star uses full architecture coverage and when a bounded phase or module may stay lightweight.

For this plan, full architecture coverage is required for affected scopes that change reusable orchestration behavior, native subagent routing, `native_omx`, LangGraph, worktree safety, OpenSpec governance, user-level launcher policy, skill/profile governance, local-main-first publication, shared templates, durable state, release safety, or cross-project adoption.

Use the five tailoring outcomes explicitly. Full architecture is required for affected platform orchestration, trust, durable-state, release-safety, or cross-project adoption scope. Whole-project lightweight is allowed only for private, reversible, low-risk work with no external users, money, sensitive data, shared runtime, or release commitment. Phase-local lightweight is allowed for bounded discovery, metrics, growth, or retrospective phases inside a larger governed project. Module-level lightweight is allowed for bounded documentation, research, local helper, or spike modules that do not change runtime entrypoints, durable state, secrets, CI gates, release gates, or downstream project dependencies. Hybrid is required when uncertainty remains high but later delivery may affect production, users, trust, revenue, compliance, runtime behavior, or release safety. If a lightweight module becomes shared infrastructure or production behavior, expand the affected layers before release.


## 2. Problem Statement And Design Drivers

Under this baseline, the real problem is no longer "can LangGraph be used?", but:

- how the three lanes keep stable long-term division of responsibility
- which durable truth belongs in `langgraph` and which remains in `native_omx`
- how `subagent` stays a leader-side burst-expert lane instead of drifting into a persistent worker role
- how a solo developer recovers from cold start, context loss, partial failure, approval blocking, and version change
- how memory, retrieval, regression, GUI, and security are added without creating a second hidden control surface

Fixed design drivers:

1. recovery before automation
2. clear control surfaces before execution complexity
3. additive-only before replacement refactors
4. manual-first before black-box automatic progression
5. solo long-term maintainability before platform-level complexity

## 3. Target Capabilities And Non-Goals

### 3.1 Target capabilities

This plan targets:

- a long-lived durable team model for `Codex CLI`
- `langgraph` as one graph-shaped durable orchestration backend
- `native_omx` as the worker-centric durable lane
- `subagent` as the leader-side expert-routing lane
- a repo-grounded landing map for the ten-layer framework
- clear introduction order and boundaries for memory, retrieval, regression, security, and GUI
- clear separation between what belongs to the user-level shared layer, the cross-project shared layer, and the project layer
- an operator model where most threads can be inspected, approved, recovered, and resumed without reading source code

### 3.2 Non-goals

This plan does not:

- redefine `langgraph` as a universal replacement for all three lanes
- redefine the burst-delegation semantics of `subagent`
- redefine the worker-centric durable semantics of `native_omx`
- demote the current main `Codex CLI` session into a new persistent leader pane
- introduce full heterogeneous persistent teams all at once
- make GUI the primary runtime too early
- rewrite existing durable truth in order to add memory or vector retrieval

### 3.3 10-To-12-Layer Framework Landing Map

The ten-layer framework is the research document's production-capability core, not the full product/business lifecycle. It remains visible in this plan so a cold-start maintainer can see how the runtime target decomposes, but the planning frame is now the 12-layer lifecycle defined in `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md`.

10-layer capability core:

| Layer | Production meaning | Landing rule in this plan |
| --- | --- | --- |
| 1. Persistence Core | Owns state, checkpoints, event history, execution position, and recovery semantics. | `.omx/state/` is the repo-local durable-state directory; it stores each repository's canonical durable truth and must not be shared as a user-level global state directory. |
| 2. Interaction and Execution Layer | Owns commands, events, tasks, executors, and local or remote execution. | `codex-ohmy` is the normal wrapped Codex launcher; `codex-raw` is the raw Codex bypass launcher; both must stay thin entrypoints over guarded scripts and documented commands. |
| 3. Team Orchestration Layer | Owns role assignment, task scheduling, parallel slicing, conflict convergence, and human intervention. | `subagent` is the leader-side burst expert lane; `native_omx` is the worker-centric durable execution lane; `langgraph` is the graph-shaped checkpoint and resume orchestration lane. |
| 4. Long-Term Memory Layer | Owns cross-session and cross-task facts, experience, rules, and artifact summaries. | Memory can enhance execution, but it must not become workflow truth, approval truth, or the only recovery source. |
| 5. Context Enhancement Layer | Owns retrieval, filtering, reranking, compression, injection, and context-budget governance. | Startup summaries, governance docs, OpenSpec artifacts, and bounded retrieval can improve context, but they must remain inspectable and budget-controlled. |
| 6. Vector Database and Retrieval Storage Layer | Owns vector indexing, tenant isolation, filtering, backup and restore, and lifecycle strategy. | Vector storage is optional and adapter-backed; it must not replace repo-local durable state or authoritative documents. |
| 7. Quality Assurance Layer | Owns runtime constraints, output validation, tool validation, approval gates, and acceptance gates. | Script controls, checkers, CI gates, and approval prompts must back important safety rules instead of relying only on prompt reminders. |
| 8. Evaluation and Regression Layer | Owns benchmark sets, experiment comparison, online evaluation, regression gates, and version comparison. | Regression fixtures and evaluation reports should be added after the durable core has observable status and rollback evidence. |
| 9. Security and Persistence Hardening Layer | Owns authorization, audit, secrets, data classification, encryption, tamper resistance, and recovery safety. | MCP scope, secret handling, permission boundaries, and state write scopes must fail closed when a cold-start session has no prior context. |
| 10. Local GUI Control Center | Lets the maintainer inspect state, approve actions, replay, intervene, and recover without reading source code directly. | GUI or dashboard work is observer-first and must come after read-only state inspection, recovery surfaces, and guarded action semantics. |

Derived release rule:

- R0 and R0.5 cover layers 1, 7, and 9 only at the minimum governance and read-only inspection level.
- R0.6 through R0.8 exercise layers 1 through 3 in small smoke/adoption gates without claiming the whole production target.
- R1.0 through R1.2 make layers 1 through 3 usable across projects while keeping layers 4 through 10 mostly guarded, optional, or observer-first.
- R2.0 slices complete the production target by adding durable memory, recovery hardening, graph-native orchestration, security hardening, performance tests, operator dashboard, maintenance strategy, and rollback evidence.

## 4. Layered Responsibilities Of The Three Lanes

### 4.1 `subagent`

Fixed role:

- leader-side bounded expert delegation
- main home for burst roles such as architect, planner, verifier, and researcher
- does not own team-level durable truth
- does not act as a long-lived persistent worker

### 4.2 `native_omx`

Fixed role:

- worker-centric durable execution lane
- owns worker lifecycle
- owns mailbox state
- owns worktree-scoped execution state
- owns worker team identity
- fits long-running execution, task distribution, and mostly homogeneous worker swarms
- must not be rewritten as a transitional capability

### 4.3 `langgraph`

Target role under this baseline:

- graph-native persistent-team kernel
- owns checkpoint-native orchestration state
- owns thread phase
- owns approval state
- owns replay and recovery provenance
- owns frozen implementation brief artifacts
- owns survivor queue artifacts
- serves as one graph-shaped durable backend family
- remains additive rather than a replacement for the entire product line

### 4.4 Long-term relationship among the three lanes

The stable relationship should remain:

- `subagent` = expert routing plus leader-side burst collaboration
- `native_omx` = worker-centric durable execution
- `langgraph` = graph-shaped durable orchestration

They are complementary, not replacement lanes.

## 5. Tool Reuse And Shared Constraints

### 5.1 Reuse principles

External tool reuse is allowed only when:

- the external tool does not become a new authoritative control surface
- the external tool does not become a new durable truth source
- the external tool does not silently alter lane boundaries
- the external tool attaches to the existing orchestration line rather than redefining it
- every reuse passes through a bounded adapter with explicit input, output, and side-effect boundaries

### 5.2 Shared dependency and runtime ownership

`D:\PythonProject_langgraph` - the current orchestration repository and source-of-truth for shared Codex CLI durable-team tooling, adapters, checkers, and installer logic.

This repository may centrally manage dependency declarations, installation scripts, wrappers, and adapter contracts for the Codex CLI durable-team control surface. The actual third-party runtime outputs should stay in ignored local runtime directories such as `.runtime/`, `.venv-tools/`, or `.toolchains/`; those directories are machine-local dependency caches or virtual environments, not source-of-truth project files.

Default rule:

- Third-party dependencies for evaluation, GUI control, queues, embeddings, vector retrieval, dashboarding, and recovery tooling are for each development project's Codex CLI durable-team runtime only.
- These dependencies must not be mixed into concrete business runtime dependencies by default.
- A concrete business project that needs the same library name must declare, install, test, package, and release its own business dependency in that project's repository.
- Shared durable-team wrappers may call into a business repository only through explicit adapters, profiles, and release gates.

Narrow model-service exception:

- A local Llama deployment is a local model service that may be shared by both the Codex CLI durable-team runtime and concrete business runtimes.
- The shared local model service must be reached through provider adapters and provider profiles.
- Provider adapters must separate policy, logging, permissions, prompts, secrets, customer data, business state, and durable-team state.
- The local model service must not become durable truth for either side.

`PySide6` boundary:

- `PySide6` in this plan means the Codex CLI durable-team local GUI control center. It is an operator tool for inspecting runs, approvals, recovery candidates, regression results, helper state, and template state.
- A concrete business project may also use `PySide6`, but that is a separate business GUI. Its dependencies, packaging, state, user interface, and release rules belong to the business project, not to this durable-team control center.
- The two GUI surfaces must not share runtime state, approval state, customer data, or release artifacts.

### 5.3 Recommended tool reuse
#### Strongly recommended

- `SQLite` - layer: persistence kernel
  - layer: persistence kernel
  - use: `run index`, `thread index`, `event ledger`, `approval ledger`, `audit ledger`, `artifact index`

- `promptfoo` - layer: evaluation and regression
  - layer: evaluation and regression
  - use: offline eval, CI regression, red team, version comparison

- `QMD` - layer: context enhancement
  - layer: context enhancement
  - use: local authority or spec or docs first-lookup sidecar

#### Conditionally recommended

- `jina-embeddings` - layer: context enhancement / vector retrieval
  - layer: context enhancement / vector retrieval
  - use: optional embedding provider
  - constraint: must remain behind a provider adapter

- `PySide6` - layer: local GUI control center
  - layer: local GUI control center
  - use: observer-first / guarded-actions desktop control center

- `Redis` - layer: interaction / execution / team orchestration
  - layer: interaction / execution / team orchestration
  - use: presence, short-lived queues, locks, Pub/Sub
  - constraint: must not become the only durable truth

#### Design inspiration only, not mainline dependencies

- `ClawTeam-OpenClaw` - borrow swarm, worktree, mailbox, and product-model ideas only
  - borrow swarm, worktree, mailbox, and product-model ideas only

- `OpenViking` - borrow context database, session archiving, and memory-extraction boundaries only
  - borrow context database, session archiving, and memory-extraction boundaries only

- `lossless-claw-enhanced` - borrow context compaction and CJK-aware summarization ideas only
  - borrow context compaction and CJK-aware summarization ideas only

#### Not part of the mainline

- `Light Judge` - keep only the light-judge strategy idea, not the external dependency
  - keep only the light-judge strategy idea, not the external dependency

- `memory-lancedb-pro-skill` - treat as reference material, not production infrastructure
  - treat as reference material, not production infrastructure

### 5.4 Abstract business capability profiles

Business capability profiles are horizontal workload classifications over the ten-layer framework. They are not an eleventh layer and they are not concrete business names. A new workload should map to one or more profiles before implementation starts.

| Capability profile | Universal purpose | Main ten-layer demand |
| --- | --- | --- |
| Interactive frontend product delivery | Deliver user-facing frontend, mini-app, web, or app surfaces with testable release boundaries. | Layers 2, 3, 7, 8, and 9. |
| Generated media asset pipeline | Manage generated images, video, audio, prompts, parameters, asset selection, and downstream approval. | Layers 1, 4, 5, 7, and 9. |
| Platform content operations | Govern content generation, scheduling, publication, receipt capture, retry, and audit. | Layers 1, 2, 7, 8, 9, and optional layer 10. |
| Customer message automation with human handoff | Govern automated customer replies, sensitive-content handling, human takeover, and audit. | Layers 1, 4, 5, 7, 9, and optional layer 10. |
| External domain-agent runtime governance | Govern domain-agent profiles, knowledge updates, regression tests, release gates, logs, and recovery when the final user-facing agent runtime lives outside Codex CLI. | Layers 1, 3, 4, 5, 7, 8, and 9. |
| Knowledge retrieval and citation workflows | Govern retrieval, citation, evidence chains, summary quality, and hallucination checks. | Layers 4, 5, 6, 7, and 8. |
| Professional tool teaching and guided operation | Govern step-by-step operation help, screenshots, case libraries, error recovery, and risk notices. | Layers 2, 4, 5, 7, and optional layer 10. |
| Solo business operations management | Govern projects, customers, sales, delivery, cost summaries, and review cycles for a solo operator. | Layers 1, 3, 4, 7, and optional layer 10. |
| High-risk decision support | Govern decisions that require simulation, approval, audit, rollback, or stop-loss behavior before execution. | Layers 1, 7, 8, 9, and optional layer 10. |
| Layout-sensitive document transformation | Govern extraction, replacement, rendering, human review, and layout regression for formatted documents. | Layers 1, 2, 5, 7, and 8. |
| Structured proposal and compliance document delivery | Govern template libraries, source collection, section generation, citations, compliance checks, approvals, and delivery records. | Layers 1, 4, 5, 7, 8, and 9. |
| Template and project bootstrap lifecycle | Govern new-computer bootstrap, project template initialization, existing-project update, backups, and checker verification. | Layers 1, 2, 7, and 9. |

Concrete workload examples belong in Appendix A of `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md`, which is the MRD that maps examples to abstract profiles. The production durable-team plan should stay abstract so future business names do not rewrite the architecture.
## 6. Control Surface For Codex CLI

The minimum operator control surface for a solo developer must answer:

1. what runs or threads are currently active?
2. what is blocked, and why?
3. what approvals are pending, and what is the next executable action?
4. where did the latest failure happen, and what durable evidence exists around it?
5. how can the operator pause, approve, reject, resume, or recover without reading source code?

Recommended minimum control surface:

- CLI-first unified entry
- loopback control API
- `inspect summary` - operator surface for viewing the current durable run and state summary.
- `approval surface` - operator surface for pending approvals and recorded approval decisions.
- `recovery surface` - operator surface for resume, replay, redrive, and manual recovery actions.
- replay / time-travel entry
- a small cost / concurrency / backlog board

## 7. Production Durable Team Model

In this plan, a production durable team is not "more always-on agents". It is:

- one leader session
- a set of leader-side burst experts
- one worker-centric durable lane
- one graph-centric durable lane
- one unified inspect / approval / audit / recovery contract

The model must define:

- `role assignment` - team-model concern for mapping work to explicit roles.
- `ownership` - team-model concern for making file, task, and decision authority explicit.
- `parallel slice planning` - team-model concern for splitting work into safe concurrent execution slices.
- `convergence` - team-model concern for merging parallel outputs into one coherent state.
- `conflict detection` - team-model concern for finding incompatible edits or task outcomes early.
- `approval wait` - team-model concern for durable human gates that can survive interruption.
- `manual takeover` - team-model concern for operator intervention in an in-flight durable task.
- `failure branch recovery` - team-model concern for retrying or redriving only the failed path.

Recommended default:

- `subagent` continues to serve architect / planner / researcher / verifier
- `native_omx` continues to serve mostly homogeneous durable workers
- `langgraph` continues to own team phase graph, interrupt graph, approval graph, and recovery graph
- `mixed compose opt-in` remains an advanced explicit mode only

### 7.1 How many `PyCharm / Codex CLI` projects can share one model

This plan is not about each repository inventing its own persistent-team model. It is about many `PyCharm / Codex CLI` projects on the same machine, user account, and Codex home sharing one personal production durable-team model.

Shared approach:

- **shared user-level control surface**
  - shared launchers
  - shared capability switches
  - shared expert-routing semantics
  - shared inspect / approval / recovery / replay operator model

- **shared cross-project runtime substrate**
  - shared venvs
  - shared support scripts
  - shared role catalog
  - shared helper artifacts
  - shared schemas and templates

- **isolated project-level durable truth**
  - each project keeps its own repo-local source
  - each project keeps its own repo-local `.omx/state/`
  - each project keeps its own OpenSpec, project docs, tests, artifacts, and reports

Shared:

- tools
- rules
- control-surface semantics
- role catalogs
- shared runtime substrate

Isolated:

- canonical durable state
- repo-local source
- repo-local OpenSpec changes
- project memory, project artifacts, and project recovery evidence

Permanent rules:

- one durable task has one explicit `repo_root`
- one durable task uses one durable backend family
- the user-level shared layer must not host any single project's canonical durable state

### 7.2 Unified management of `experts / durable_team / persistent team`

These three terms must stay layered:

- `experts` - leader-side burst experts
  - leader-side burst experts
  - a staffing and invocation concept, not persistent workers
  - examples: `analyst / architect / planner / writer / verifier`

- `durable_team` - execution objects within a durable backend family
  - execution objects within a durable backend family
  - in `native_omx`, closer to a tracked worker swarm
  - in `langgraph`, closer to a tracked durable thread or graph execution posture

- `persistent team` - the product-level operating model
  - the product-level operating model
  - not a third backend and not a third state root
  - means: `leader session + burst experts + durable lane + unified inspect / approval / recovery contract`

Unification should happen at the operator-facing contract layer:

- unified inspect / status / run surface
- unified approval surface
- unified recovery surface
- unified audit and identity model

Recommended long-term handling:

- `experts` go into the user-level routing catalog, not durable truth
- `durable_team` goes into backend-specific execution state and is exposed through unified inspect summaries
- `persistent team` stays as the top-level operating model organizing user-level targets and project-level handoff

### 7.3 Safety controls must combine scripts and prompts

The production-grade persistent team cannot depend on the model remembering a long prompt after context grows.

Every system-level, user-level, or project-level safety boundary must therefore use both layers:

- script control - executable checks, generated helper logic, guarded state transitions, or CI gates that fail closed for a cold-start model with no prior conversation context.
- prompt reminder - startup-summary and implementation-plan text that explains the rule, the reason for the script guard, and the recovery procedure when the reminder appears forgotten; `AGENTS.md` is a recovery reread target, not the literal canary prompt source.

Minimum production requirement:

- `experts` routing must have script-visible thresholds or checker evidence before it is described as automatic.
- `durable_team` launch must be guarded by frozen-plan and independent-slice checks rather than by prompt memory alone.
- `persistent team` state must be scoped by repository and backend family in executable helpers, not only in prose.
- publication, cleanup, state mutation, and cross-project activation must have a script gate or an explicit documented gap.
- a user-level aggregate safety-boundary checker must verify that every registered safety rule has a script control, a prompt reminder, and an implementation status, or else report it as a tracked gap.

The startup layer should also include a context-retention canary, but the literal canary prompt text is project-level and startup-summary-owned. It belongs only in each repository's `project_startup_summary.*` pair, not in `AGENTS.md`, user-level startup summaries, implementation plans, generated wrappers, or launcher payloads. The current canary convention is:

- startup summaries define the literal prompt for full assistant responses in their repository, unless a higher-priority system or developer instruction prevents it.
- missing canary text after startup-summary reading is treated as possible context-loss evidence.
- recovery is to rerun the cold-start read order from `AGENTS.md` and `docs_bilingual/project_startup_summary.*`, then reread only the files needed to continue safely.

The user-level canary capability should be a checker, not a prompt injector. When it receives transcript or response text, it should verify the startup-summary-defined canary and emit the recovery instruction above when the canary is absent. Without transcript or response input, it should only verify that the current project declares the canary in `project_startup_summary.*` and does not duplicate the literal prompt in other active instruction surfaces.

## 8. State, Memory, And Artifact Persistence

### 8.1 Durable truth layering

Required layers:

- `canonical durable state` - primary repo-local truth for durable task progress and recovery.
- `artifact state` - persistent record of generated outputs, references, and artifact identities.
- `memory state` - persistent record of short-term and long-term memory used by orchestration.
- `retrieval substrate` - storage and indexing layer that supports governed retrieval and context enhancement.
- `derived inspect projection` - read-only status view derived from canonical state, artifacts, and memory.

These must not be collapsed into one vague "memory" or one dashboard feed.

### 8.2 Recommended persistence split

#### `langgraph`

Primary responsibility:

- checkpoint-native orchestration state
- thread phase
- approval state
- replay / recovery provenance
- frozen implementation brief
- survivor queue

#### `native_omx`

Primary responsibility:

- worker lifecycle
- mailbox state
- worktree-scoped execution state
- worker team identity

#### `SQLite`

Recommended shared durability substrate for:

- run index
- thread index
- event ledger
- approval ledger
- audit ledger
- artifact index
- memory metadata
- retrieval metadata

#### File system

Continue to store:

- artifacts
- reports
- exported logs
- checkpoint visualization sidecars
- cached summaries

### 8.3 Memory and retrieval boundaries

Explicit categories:

- `procedural memory` - memory category for prompts, policies, rules, and skills.
- `short-term thread memory` - memory category for active thread state, message history, and checkpoints.
- `semantic long-term memory` - memory category for durable facts, preferences, and organizational rules.
- `episodic memory` - memory category for examples, trajectories, and reusable experience.
- `document knowledge base` - memory category for indexed documents used by retrieval and RAG.

Hard rules:

- thread state is not long-term memory
- long-term memory must not carry workflow recovery semantics
- vector stores remain retrieval substrate only, never canonical durable state

### 8.4 Capturing and reusing lessons learned

This section is not about whether retrospectives should exist. It is about making sure that past failures, proven techniques, and later corrections become reusable input instead of relying on human memory alone.

Working definition:

- lessons learned are not a raw event log
- they are reusable constraints, decision criteria, defaults, and anti-patterns extracted from past runs, design work, implementation, failure, and recovery
- their goal is to reduce repeated trial-and-error, repeated rework, and future drift

#### 8.4.1 What belongs in lessons learned

Worth capturing:

- repeated problems
- issues that affect recovery, stability, cost, approval, or maintainability
- issues with confirmed handling patterns
- issues that can be promoted into rules, checks, defaults, or tests

Usually not worth long-term capture:

- one-off environment noise
- emotional description only
- observations with no reasoned cause or handling
- one-time manual details that cannot be reused

#### 8.4.2 How to classify lessons learned

Recommended organization:

- object type plus five supporting axes

Important object types:

| Object type | Typical content | Success captures | Failure captures |
| --- | --- | --- | --- |
| Project-level | long-term direction, product-line boundaries, governance model | stable principles, defaults, narratives | systemic risks, drift sources, forbidden anti-patterns |
| Mainline / change | mainlines, OpenSpec changes, migration waves | standard sequence, gates, rollback points | stuck phases, prerequisite gaps, wrong decomposition |
| Branch / experiment | canary, shadow, one-off experiments | low-cost high-signal experiment methods | non-representative experiments, invalid conclusions |
| Plan / architecture | lane split, state model, backend choice | when to choose which lane | couplings that hurt recovery or compatibility |
| Rollout | order, migration strategy, compatibility strategy | correct rollout order and shadow validation | rollout patterns that cause contamination or irreversible upgrades |
| Implementation path | which layer to change first | stable fix order | wrong-layer fixes |
| Tool call | CLI calls, script calls, env constraints | stable command templates | long command, encoding, permission, path, and idempotency failures |
| Skill usage | when to use analyst / planner / verifier / writer | stable skill-selection patterns | skill misuse that inflates complexity |
| Prompt / instruction | briefs, developer instructions, task prompts | effective prompt templates | overlong, conflicting, or mixed-state prompt anti-patterns |
| Interface / contract | CLI params, state fields, resume contracts | stable I/O and version fields | hidden fields, compatibility breakage, state collapse |
| Rule / governance | additive-only, manual-first, and similar rules | rules worth enforcing long-term | vague or dangerous rules |
| User / operator habit | recurrent usage and misuse patterns | healthy operator habits | recurring misuse that should be absorbed by the product |

Recommended supporting axes:

- granularity
- time horizon
- reuse scope
- degree of structure
- actionability

#### 8.4.3 Where lessons should live

Do not ask only "should this be kept?" Ask "which layer should own it?"

Rules:

- lessons learned should not be written directly into canonical durable state
- canonical durable state owns runtime truth, not long prose
- lessons should normally be split into raw evidence, attribution, and reusable rule layers

Recommended landing places:

| Content layer | Location | Meaning |
| --- | --- | --- |
| Raw evidence | `reports`, `exported logs`, incident notes, change records | what happened |
| Current-mainline summary | current implementation plan, current OpenSpec design or tasks | only the summary, constraints, and action items needed now |
| Long-term repository rules | `docs_bilingual/governance/`, operator playbook, long-term policy docs | cross-mainline stable rules and anti-patterns |
| Tool / skill / prompt / interface-specific lessons | tool docs, skill docs, prompt templates, interface contracts, tests | lessons stay with the true owner |
| Search and index metadata | `SQLite` | labels, references, metadata, not full lesson bodies |
| Long-term retrievable cases | experience ledger, topic note, case doc | cold-start and retrieval support |

The stable pattern is:

1. keep raw cases at the evidence and report layer
2. summarize what matters for the current mainline in the current implementation plan
3. promote only validated long-term rules into governance docs, tool docs, tests, or defaults

#### 8.4.4 From archived lesson to executable action

Three stable promotions:

- convert to a constraint
- convert to a checklist item
- convert to a default operating pattern

Maintenance rules:

- only archive lessons that already affect implementation-path choice
- update original entries instead of duplicating near-identical ones
- mark outdated lessons as historical reference only
- review at the end of each mainline whether a new lesson deserves promotion into rule, test, or default behavior

#### 8.4.5 Example: where the `codex-ohmy` "command line too long" failure belongs

Example:

> `PS D:\PythonProject_langgraph> codex-ohmy`
> `The command line is too long.`

This is first a tool-call failure, but the reusable lesson is:

- launcher and control-surface entrypoints should not carry large inline prompt or instruction payloads
- long instructions should be file-backed, state-backed, or passed by short reference

Recommended three-layer storage:

1. **raw event**
   - incident note, logs, report, or change record
2. **current-mainline summary**
   - current implementation plan summary and rollout reminder
3. **long-term rule**
   - launcher / control-surface contract docs, defaults, and tests

This example should be classified mainly as:

- tool-call failure
- launcher / interface-contract lesson
- Windows CLI limit lesson in control-surface design

Promote it into two long-term defaults:

- default entrypoints should stay short and expose only necessary parameters
- stable context should move into config files, argument files, state files, or repo-local state instead of being concatenated into command lines

## 9. Scheduling, Switching, And Upgrade Path

### 9.1 Backend-family rules

Permanent rules:

- one durable task or run uses one backend family
- `native_omx` and `langgraph` can coexist in the same product line
- `subagent` is never a durable backend family

### 9.2 Switching rules

Recommended policy:

- early read-context / freeze-plan: leader plus `subagent`
- worker-heavy execution: `native_omx`
- graph-shaped long-running phased execution: `langgraph`
- unhealthy lane: explicit downgrade, not silent drift

### 9.3 Upgrade path

Recommended order:

1. fix the stable three-lane narrative
2. solidify the graph-native durable-thread contract in `langgraph`
3. unify control plane, approval, and recovery into one shared surface
4. only then add memory, context, vector, and GUI enhancements

## 10. Repository Structure And Landing Points

Recommended structure:

- user-level shared layer
- `C:\Users\lenovo\.codex\` - shared launchers, support scripts, role catalogs, helper artifacts, shared runtime, and shared switches
  - shared launchers, support scripts, role catalogs, helper artifacts, shared runtime, and shared switches

- cross-project shared runtime layer
  - shared venvs, shared helper mirrors, reusable templates
  - may be shared across projects, but must not host any single project's canonical durable state

- `docs_bilingual/governance/` - long-term method and governance boundaries
  - long-term method and governance boundaries
- `docs_bilingual/implementation_plans/` - target-state implementation plans
  - target-state implementation plans
- `openspec/` - proposal / design / spec / tasks
  - proposal / design / spec / tasks
- `.omx/state/` - repo-local durable state
  - repo-local durable state
- `.omx/plans/` - support plans, convergence artifacts, coordination results
  - support plans, convergence artifacts, coordination results
- `tools/` - adapters, control helpers, eval helpers, GUI launchers
  - adapters, control helpers, eval helpers, GUI launchers

As a historical external OpenClaw reference only, do not scatter future mainline implementation back into `D:\PythonProject_OpenClaw`.

In short:

- the user-level layer owns "how all projects share the model"
- the project layer owns "how this repository carries the model"

The two must cooperate, but they must not collapse into one state surface.

## 11. Runtime Boundaries And Compatibility Rules

These boundaries must remain stable:

- the leader session does not get demoted
- `subagent` does not become a persistent worker
- `native_omx` does not get rewritten as a legacy backend
- `langgraph` does not swallow the whole runtime
- `oh-my-codex` remains a workflow / control layer on top of Codex

Backward-compatible objects:

- `inspect/status/run surface` - compatibility object for the operator-facing run status view.
- `shared durable-state summary contract` - compatibility object for a common summary schema across backend families.
- `artifact identity` - compatibility object for stable artifact references across backends.
- `approval identity` - compatibility object for stable approval references across backends.
- `recovery pointer identity` - compatibility object for stable resume, replay, or redrive pointers.
- `backend-family selection semantics` - compatibility object for preserving explicit native_omx versus langgraph selection.

## 12. Failure Recovery, Observability, And Troubleshooting

Minimum observability:

- active / blocked / failed runs
- current phase / current node / current backend family
- pending approvals
- recovery posture
- artifact presence
- worker team status
- cost / concurrency / backlog

Recovery actions must stay distinct:

- resume
- replay
- redrive
- time-travel
- update-state recovery
- manual takeover

Do not collapse them into one vague `recover` button.

## 13. Validation, Testing, And Acceptance Gates

Minimum acceptance:

- narrative is consistent and no longer describes LangGraph as a still-future MVP lane
- the three lanes have stable responsibility boundaries
- inspect / approval / recovery share one surface
- high-risk actions have audit and guarded actions
- safety-critical prompt reminders have matching script controls or an explicit tracked gap, verified by a user-level aggregate safety-boundary checker
- startup context-retention canary behavior is documented in project-level `project_startup_summary.*`; `AGENTS.md` remains a recovery reread target and must not contain the literal canary prompt, while a user-level canary checker can report the cold-start reread recovery procedure when transcript evidence is available
- a regression gate exists
- at least one cold-start recovery drill exists
- at least one failure-branch redrive drill exists
- at least one approval-wait / approval-reject drill exists

Recommended tooling:

- `promptfoo` for regression and evaluation
- repo-local smoke / replay tests for state and recovery

## 14. Phased Delivery Order

### 14.0 Release train overlay for smaller delivery slices

This draft must be delivered through smaller release slices instead of one long implementation wave.

Release rules:

- Each release slice must identify the value increment it delivers, the feedback point that will prove whether the increment helped, and the rollback boundary that keeps native Codex and existing projects safe.
- This draft stays `status: draft` until a specific release slice is promoted through OpenSpec.
- Each release slice must have its own target repository, phase, task scope, validation path, rollback path, and operator consent boundary.
- A release slice may update this draft, but it must not claim the whole production durable-team target is implemented.
- One subrelease should normally map to one OpenSpec change and one GitLab MR.
- Runtime exercises begin only after the R0.6 template and checker slices are in place.
- Production marking for launcher or installer slices also requires the R0.6.1 Codex native rollback gate, which proves native Codex, raw bypass, wrapper smoke, config sentinel, and rollback evidence before release.

Detailed release ladder:

| Release | Meaning | Implementation posture |
| --- | --- | --- |
| `R0 Governance Baseline` | Startup, OpenSpec, worktree, session ownership, MCP scope, and safety-rule script backing. | Mostly implemented baseline. |
| `R0.5 Inspectable Durable State` | Read-only durable state status, selector safety, and helper mirror source-of-truth. | Mostly implemented baseline. |
| `R0.6.0 Gate Template` | Template for future smoke/adoption gate changes and their required fields. | Next safe planning slice. |
| `R0.6.1 Gate Field Checker And Codex Native Rollback Gate` | Checker-backed enforcement for required gate fields plus native Codex, raw bypass, wrapper, config sentinel, and rollback evidence. | Current safe script-backed slice. |
| `R0.6.2 Read-Only State Sampling` | Status-only sampling for one target repository. | Future read-only slice. |
| `R0.6.3 Dry-Run Routing Decision` | No-team, native_omx, or langgraph decision explanation without apply mode. | Future dry-run slice. |
| `R0.6.4 Expected-Result Fixture` | Regression fixture for the expected dry-run decision. | Future test slice. |
| `R0.6.5 Cross-Project Read-Only Review` | Consumer-project review that proves repo-local truth does not leak. | Future cross-project slice. |
| `R0.7.0 Low-Risk Target Selection` | First native_omx target repository and task selection. | Future reviewed slice. |
| `R0.7.1 Native OMX Dry-Run Stability` | Stable native_omx plan before apply mode. | Future dry-run slice. |
| `R0.7.2 Explicit Apply Consent` | Exact consent record before `-Apply`. | Future consent slice. |
| `R0.7.3 Lifecycle Record Check` | Launch, reuse, shutdown, and tracked-record evidence. | Future lifecycle slice. |
| `R0.7.4 Restart Recovery Check` | Cold-start inspection of native_omx state. | Future recovery slice. |
| `R0.7.5 Native OMX Closeout Archive` | Evidence archive and residue cleanup for native_omx adoption. | Future closeout slice. |
| `R0.8.0 Graph-Shaped Task Selection` | LangGraph target task with checkpoint, approval, frozen brief, or survivor-queue signal. | Future reviewed slice. |
| `R0.8.1 Checkpoint Smoke` | Save and resume evidence for langgraph state. | Future smoke slice. |
| `R0.8.2 Approval Gate Smoke` | Pause and approval evidence for operator decisions. | Future smoke slice. |
| `R0.8.3 Frozen Brief Smoke` | Research-to-implementation frozen brief evidence. | Future handoff slice. |
| `R0.8.4 Survivor Queue Smoke` | Bug-review survivor queue evidence. | Future triage slice. |
| `R0.8.5 LangGraph Closeout Archive` | Evidence archive without making langgraph default for unrelated tasks. | Future closeout slice. |
| `R0.9 Lane Arbitration` | Conflict rules for native_omx, langgraph, and no durable team. | Future arbitration release. |
| `R1.0 Personal Durable Team MVP` | First single-user, multi-project usable MVP. | Future MVP. |
| `R1.1 Multi-Project Consumer Rollout` | Rollout to consumer repositories while preserving repo-local durable truth. | Future rollout. |
| `R1.2 Operational Hardening` | Logging, MCP scope, config sentinel, helper mirror, cleanup, and rollback hardening. | Future hardening release. |
| `R2.0.0 Production Readiness Standard` | Production acceptance criteria and release gates. | Future production slice. |
| `R2.0.1 Durable Memory Model` | Memory boundaries, retention, and replay policy. | Future production slice. |
| `R2.0.2 Crash Recovery` | Safe inspection and resume after interruption. | Future production slice. |
| `R2.0.3 Graph-Native Orchestration` | Graph-native orchestration where graph-shaped execution is warranted. | Future production slice. |
| `R2.0.4 Security And Secrets Boundary` | Credentials, permissions, and untrusted-input protection. | Future production slice. |
| `R2.0.5 Performance And Concurrency Test` | Worker count, provider pacing, and long-running stability tests. | Future production slice. |
| `R2.0.6 Operator Dashboard` | Clear operator-facing status and control surface. | Future production slice. |
| `R2.0.7 Multi-Project Maintenance Strategy` | Long-term maintenance across repositories. | Future production slice. |
| `R2.0.8 Production Release And Rollback` | Formal release only after rollback evidence exists. | Final production slice. |

### 14.1 Stage 0: Narrative And Governance Alignment

Goal:

- align the target-state baseline with repository narrative

Preconditions:

- none

Exit conditions:

- startup summary, plans, and OpenSpec status narrative agree
- three-lane long-term division of responsibility agrees everywhere

### 14.2 Stage 1: Durable-Kernel Contracting

Goal:

- lock down the production-grade durable-thread contract for the `langgraph` lane

Focus:

- checkpoint / event envelope / migration compatibility
- approval / recovery provenance
- shared durable summary

Exit condition:

- threads are inspectable, resumable, recoverable, and compatibility-checkable

### 14.3 Stage 2: Unified Interaction And Execution Semantics

Goal:

- unify the action layer across CLI, PowerShell, and control API

Focus:

- unified Intent / Command / Event / Task / Approval / Artifact semantics
- unified pause / resume / reject / recover semantics

Exit condition:

- operators can understand and operate all three lanes with one mental model

### 14.4 Stage 3: Productized Team Orchestration Layer

Goal:

- make the default persistent-team model explicit

Focus:

- hybrid-by-default
- homogeneous durable workers
- mixed compose as explicit opt-in
- ownership / converge / escalation semantics

Exit condition:

- parallel execution, convergence, and manual escalation all have clear ownership

### 14.5 Stage 4: Quality Gates, Regression Gates, Security Hardening

Goal:

- add runtime and regression gates before expanding automation further

Focus:

- runtime QA gate
- `promptfoo` regression
- approval / audit / secret / policy hardening

Exit condition:

- high-risk actions cannot bypass gates
- regressions can be compared and quantified

### 14.6 Stage 5: Memory, Context Enhancement, And Vector Layer

Goal:

- add memory and retrieval enhancements only after the durable core is stable

Focus:

- structured memory store
- QMD local lookup
- optional embedding provider
- optional vector substrate

Exit condition:

- memory does not pollute state
- retrieval does not replace durable truth

### 14.7 Stage 6: Local GUI Control Center

Goal:

- provide an observer-first / guarded-actions-only operator surface

Focus:

- PySide6 desktop shell
- inspect / approval / recovery / replay / cost panels
- GUI and CLI sharing one action contract

Exit condition:

- a solo developer can recover most active threads without reading source

## 15. Risks, Anti-Patterns, And Non-Drift Rules

Most dangerous drift directions:

- rewriting LangGraph as a total replacement layer
- silently turning `subagent` into persistent workers
- downgrading `native_omx` into an old backend
- treating long-term memory as workflow state
- treating the vector layer as durable truth
- building a heavy GUI before recovery surfaces exist
- expanding automation without regression gates
- turning GUI into a second true control plane

Permanent rules:

- additive-only
- observer-first
- guarded-actions-only
- leader-owned final integration
- one durable task, one backend family

## 16. Relationship To OpenSpec And Governance Documents

This plan sits:

- below the white paper
- before concrete OpenSpec change work
- at the bridge layer between startup docs, governance docs, and implementation plans

Authority split:

| Authority layer | Main responsibility |
| --- | --- |
| White paper | overall method, target-state narrative, and 12-layer product/business lifecycle frame |
| Governance research canon | evidence-heavy production-capability research and the 10-layer runtime capability core that feeds the 12-layer frame |
| `docs_bilingual/governance/` | stable user-level rules, shared runtime policy, long-term boundaries |
| This implementation plan | shared user-level plus project-level implementation shape, multi-project reuse, repository handoff |
| OpenSpec proposal / design / spec / tasks | structural implementation changes, migration steps, task decomposition, acceptance |

This plan is responsible for:

- explaining the target architecture shared across all `PyCharm / Codex CLI` projects
- explaining the split among the user-level layer, the cross-project shared layer, and the project layer
- explaining how the current repository carries that shared model
- explaining rollout order
- explaining tooling-reuse boundaries

This plan does not replace:

- the white paper's overall method
- governance authority
- OpenSpec proposal / design / spec / tasks

Any multi-file change that touches the following should enter an OpenSpec mainline:

- control surface
- approval surface
- recovery surface
- memory surface
- vector surface
- GUI surface

## 17. Current Mainline And Next Increment Queue

Recommended next mainlines under this baseline:

1. `sync-langgraph-production-grade-narrative-and-status` - proposed follow-up mainline for aligning narrative and status with production-grade goals.
2. `stabilize-langgraph-runtime-contracts-for-solo-production-operations` - proposed follow-up mainline for hardening runtime contracts for solo operation.
3. `unify-operator-control-surfaces-for-inspect-approval-recovery` - proposed follow-up mainline for one inspect, approval, and recovery surface.
4. `add-runtime-quality-regression-and-security-gates` - proposed follow-up mainline for quality, regression, and security gates.
5. `extend-memory-and-context-governance-after-core-stabilizes` - proposed follow-up mainline for adding governed memory and context after core stability.
6. `add-minimal-local-gui-control-center-after-operator-surface-stabilizes` - proposed follow-up mainline for a minimal local GUI after operator surfaces stabilize.

Priority judgment:

- fix narrative and recovery surfaces first
- control surfaces and regression gates next
- GUI and vector layers last

## 18. Current Decisions

Fixed decisions at this stage:

- `subagent` remains the leader-side expert lane
- `native_omx` remains the worker-centric durable lane
- `langgraph` remains the graph-native persistent-team kernel
- `SQLite` is the preferred durable metadata / audit substrate
- `QMD` is the preferred local lookup sidecar
- `promptfoo` is the preferred regression / eval harness
- `PySide6` remains the later control-center implementation choice
- `Redis` and `jina-embeddings` are introduced only when clearly needed
- `ClawTeam-OpenClaw`, `OpenViking`, and `lossless-claw-enhanced` remain design references only
- `Light Judge` and `memory-lancedb-pro-skill` do not enter mainline dependencies

## 20. Release Playbook And Shared Local Model Providers

This draft remains the north-star target. Concrete implementation MUST use the smaller playbook and migration documents below instead of claiming this full draft is already implemented.

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_playbook.md` - release-slice playbook that turns the draft target into cold-start executable slices with scope, evidence, validation, and rollback.
- `docs_bilingual/implementation_plans/codex_shared_local_model_assets_migration_plan.md` - migration plan for centrally managing ignored local llama and GGUF assets under the orchestration repository without creating dirty Git work.
- `docs_bilingual/governance/codex_local_model_provider_policy.md` - governance policy for treating local model services as providers rather than durable truth, approval authority, or backend selectors.

Local model provider profiles are advisory service profiles only:

- `local-judge-qwen` - provider profile for low-cost judgement, summary compression, candidate bug triage, and inspect-summary hints using `Qwen3.5-9B-Q4_K_M-GGUF`.
- `local-embed-jina` - provider profile for local embeddings and retrieval over documents, OpenSpec artifacts, implementation plans, reports, and evidence using `jina-embeddings-v5-text-small-retrieval-GGUF`.

`Light Judge` remains a strategy. It MAY help generate survivor queues or triage candidate findings, but it MUST NOT approve work, own durable state, choose backend families, or replace verifier evidence.

`CODEX_LOCAL_MODEL_ROOT` is the environment variable for the shared local model root. It should point to an ignored local path such as `D:\PythonProject_langgraph\.local\models` and must not be used as a durable-state root.
