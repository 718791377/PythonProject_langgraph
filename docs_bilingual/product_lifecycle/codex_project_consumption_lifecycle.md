# Downstream Project Consumption Lifecycle

This document describes how later projects consume the Codex CLI durable-team platform. A downstream project may use the user-level runtime, native Codex subagents, templates, governance ideas, and optional durable lanes, but it owns its own repository facts and business work.

## Non-Negotiable Boundary

`D:\PythonProject_langgraph` is the platform source repository; it owns the Codex orchestration line, templates, shared policies, and helper source.

A downstream project owns its own product scope, business artifacts, OpenSpec tree, Git history, durable state, release state, and local lessons learned. A downstream project must not treat the platform repository as its repo-local durable truth.

## Source Evidence Boundary

This downstream consumption lifecycle is refreshed against the same `fresh_source_reading_evidence.md` run as the platform lifecycle. The source evidence informs reusable tailoring rules only. A downstream project must still create or refresh its own customer evidence, metrics, release evidence, durable state, and lessons in its own repository before applying these rules.

## Downstream Lifecycle Tailoring Overlay

Downstream projects should use the general 0-11 / 12-layer lifecycle as a map, not as mandatory paperwork for every change.

- Predictive gates fit downstream work with clear scope, release risk, money/user/trust impact, compliance impact, or explicit rollback needs.
- Adaptive slices fit downstream work that needs exploration, prototypes, browser validation, user feedback, or small MVPs before design is frozen.
- Hybrid delivery fits downstream work that still needs discovery but must eventually pass local OpenSpec, tests, release, rollback, and retrospective checks.

## Downstream Lifecycle Depth Rule

Use these depth levels in downstream projects:

- Full 0-11 lifecycle: use for new products, major business pivots, user-facing releases, compliance-sensitive changes, payment or trust-impacting work, or long-lived platform-like downstream systems.
- Project MVP or release slice: keep all 12 layers visible. When risk is low, summarize cognitive, business, market, organization, growth, operations, and retrospective context; expand strategy, metrics, product, technical, and execution evidence. If the slice affects adoption, support, or customer-facing operation, expand growth and operations too.
- Ordinary local change: do not rewrite the full stack. Record the input, tools and techniques, and output evidence for the changed scope. Code-bearing changes need technical and execution evidence. Release-bearing changes need validation, release, rollback, and retrospective evidence.

A downstream project may be lightweight, but it must stay repo-local: its OpenSpec artifacts, `.omx/state/` state directory, release facts, and lessons learned belong to that project.

Downstream projects may consult `business_management_source_synthesis.md` for lifecycle tailoring. The synthesis should help choose the minimum sufficient business, discovery, product, technical, release, and learning artifacts, but it must not move downstream customer evidence, metrics, or durable truth into this platform repository.

Use `lifecycle_tailoring_rules.md` to decide whether the downstream project is whole-project lightweight, phase-local lightweight, module-level lightweight, hybrid, or full architecture. A downstream business may start lightweight, but customer commitments, revenue, payment flows, sensitive data, compliance exposure, support obligations, repeatable delivery, or agent automation beyond low-risk support require expansion of the affected layers. Expand the whole project only when coupling becomes systemic; otherwise keep lightening local to the low-risk phase or module.

## One-Person-Company Operating-System Inventory Rule

For downstream business work that is a real one-person-company operating system, use this fixed target:

- 12 trunk layers: cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, retrospective.
- 5 virtual departments: Strategy Office; Product & Market Office; Revenue & Growth Office; Operations Office; Governance Office.
- 30 responsibility domains: founder/CEO, chief of staff, business model, finance, risk, market intelligence, customer research, positioning, product strategy, offer, PRD, UX/service design, analytics, growth, sales, pricing, content, brand/trust, partnerships, customer success, support, delivery, community, knowledge, automation, security/privacy, legal/compliance, data governance, IP/assets, agent governance.
- 20 cross-cutting modules: finance, operations, engineering management, organization design, legal/compliance, security, knowledge management, risk management, personal productivity, AI agent governance, data governance, brand trust, toolchain governance, SLA governance, asset/IP governance, user-research governance, channel governance, exit governance, vendor governance, tax/administration governance.
- 60 core documents across company strategy, business/finance, market/user, product/service, metrics/data, growth/sales, operations/customer success, technology/automation, governance/risk, and agent/knowledge.
- 15 governed AI agents: Strategy, Research, Product, UX/Copy, Engineering, QA, Data, Growth, Sales, Customer Success, Support, Finance, Legal/Risk, Knowledge, and Chief of Staff.
- 15 recommended books: Scaling People; Working Backwards; High Output Management; INSPIRED; Product Operations; Measure What Matters; Lean Analytics; The Lean Startup; Obviously Awesome; Traction; Deploy Empathy; Shape Up; Team Topologies; Company of One; The E-Myth Revisited.

The minimum startup set is deliberately only 12 documents: `thesis.md`, `business-model.md`, `offer.md`, `pricing.md`, `user-segments.md`, `growth-model.md`, `finance-model.md`, `ops-playbook.md`, `metrics.md`, `risk-register.md`, `agent-governance.md`, and `monthly-review.md`.

Do not start a downstream one-person company by creating all 60 documents. Start with the 12 minimal documents, then expand only when risk, customer evidence, revenue, compliance, delivery, or operations requires deeper coverage.

The canonical count map is `one_person_company_inventory_map.md`. Use that map for concrete document-family, agent, module, and department references; use this lifecycle file for downstream adoption and process-group execution guidance.


## Downstream Adoption Canvas

A downstream project may use `adoption_canvas.md` as a lightweight adoption canvas before it deeply adopts platform capabilities. The adoption canvas explains why the project wants platform help and how success will be measured.

Recommended fields:

- local project purpose and current friction;
- platform capability being adopted;
- expected value outcome, such as less startup friction, less context loss, safer release flow, or better browser verification;
- repo-local boundaries that must not be moved into the platform repository;
- validation path and rollback path;
- feedback that should return to the platform as upstream improvement candidates.

## Consumer Value Feedback

Downstream success is not only successful installation or template copying. A downstream project should record whether platform adoption improved its own delivery outcome while preserving repo-local truth.

Feedback should be classified before upstreaming:

- Local-only lesson: stays in the downstream repository.
- Reusable platform lesson: becomes upstream feedback and may enter this platform through a platform OpenSpec change.
- Runtime defect: becomes a bug or hardening candidate for the platform only when it is reproducible outside one downstream project.

## 0. Cognitive Narrative Layer

Question: Why does this downstream project exist, and why should it use the platform?

### Inputs

- Project idea, target problem, local repository context, and user or operator intent.
- Platform startup rules, local project template files, and native Codex subagent availability.
- External constraints such as local-only Git use, IDE choice, browser needs, privacy, and budget.

### Tools And Techniques

- Project narrative framing explains the project purpose without turning it into platform implementation work.
- Customer-backward narrative checks explain which local user or operator problem the project solves.
- Cold-start summary design helps a new Codex session recover local project context.
- `README.md` is the project overview; it explains what the project is and how to start.
- `docs_bilingual/project_startup_summary.md` is the ASCII cold-start summary; it helps a new Codex session understand the project.
- `docs_bilingual/project_startup_summary.zh-CN.md` is the UTF-8 Chinese companion for the same startup summary.

### Outputs

- A clear local project narrative and startup surface.
- Project-specific non-goals and boundaries.
- Inputs for the business, market, and strategy layers.

## 1. Business Layer

Question: Is this downstream project worth doing or continuing?

### Inputs

- Cognitive-layer project purpose and local problem statement.
- User value, business value, time budget, tool budget, model budget, and maintenance cost.
- Platform adoption cost, including template updates and optional durable-lane complexity.

### Tools And Techniques

- Business value analysis estimates revenue, saved cost, productivity gain, or risk reduction.
- Company-of-one constraint analysis asks whether a smaller, more focused project would create more value than broader scope.
- Scope-cost tradeoff analysis decides whether platform capability should be used lightly or deeply.
- `docs_bilingual/business/brd.md` is the project BRD; it explains the project's business value, cost, user value, and expected return.
- `docs_bilingual/business/brd.zh-CN.md` is the UTF-8 Chinese companion for the project BRD.

### Outputs

- Project BRD, investment boundary, and continuation decision.
- Cost and value assumptions for project strategy and release depth.
- A decision on whether local Git, OpenSpec, and native subagents are sufficient or whether optional durable lanes are justified.

## 2. Market And User Layer

Question: Who needs this project, and in which scenarios?

### Inputs

- Business-layer target value and constraints.
- User interviews, observation, support feedback, browser validation, usage data, or domain evidence.
- Platform-provided capability categories that help classify development work without naming one-off businesses as platform requirements.

### Tools And Techniques

- User segmentation separates target users, operators, maintainers, payers, and stakeholders.
- Scenario analysis maps user tasks, constraints, and pain points.
- Interview and discovery analysis uses customer/support evidence before large implementation commitments.
- Feedback loops use prototypes, browser checks, or small MVPs to reduce uncertainty.
- `docs_bilingual/market/mrd.md` is the project MRD; it explains target users, usage scenes, pain points, and alternatives.
- `docs_bilingual/market/mrd.zh-CN.md` is the UTF-8 Chinese companion for the project MRD.
- `docs_bilingual/user_research/` is the user research directory; it can store interviews, observations, and feedback evidence.

### Outputs

- Project MRD, target users, target scenarios, and priority signals.
- User evidence for product requirements and strategy.
- Feedback on whether the platform template lacks a reusable capability.

## 3. Strategy Layer

Question: How does the downstream project win, and what will it refuse?

### Inputs

- Business-layer success criteria and cost boundaries.
- Market-layer user segments, scenarios, and demand evidence.
- Platform boundaries that separate project-local truth from shared platform runtime.
- Technical feasibility and operations constraints.

### Tools And Techniques

- Strategy-kernel analysis records diagnosis, guiding policy, and coherent action for the local project.
- Positioning and beachhead analysis decide where to focus first.
- Trade-off and non-goal design prevent the project from becoming a platform catch-all.
- Delivery-depth tailoring decides whether the project needs full 12-layer depth, MVP/release depth, or a small local change path.
- `docs_bilingual/strategy.md` is the project strategy file; it records diagnosis, guiding policy, coherent action, trade-offs, and non-goals.

### Outputs

- Project strategy, trade-offs, non-goals, and delivery-depth decision.
- Prioritization constraints for metrics, product, technical, organization, execution, growth, and operations layers.
- Decision to focus, pause, pivot, or research more.

## 4. Metrics Layer

Question: What evidence tells the downstream project whether it is working?

### Inputs

- Strategy-layer goals, trade-offs, and non-goals.
- Business-layer value assumptions and cost boundaries.
- Market-layer user evidence and adoption barriers.
- Product, technical, growth, operations, and retrospective signals.

### Tools And Techniques

- North Star metric design defines the main success measure for the project.
- Input metric decomposition identifies leading indicators that drive the project North Star metric.
- Guardrail metric design protects quality, cost, trust, security, reliability, and operator attention.
- Tracking-plan design records event, log, survey, support, or release evidence needed for decisions.
- `docs_bilingual/north_star_plan.md` is the project North Star plan; it defines the main success metric, input metrics, and levers.
- `docs_bilingual/north_star_plan.zh-CN.md` is the UTF-8 Chinese companion for the same plan.
- `docs_bilingual/metrics.md` is the metrics document; it defines project success and quality metrics.

### Outputs

- Project North Star plan, input metrics, guardrails, thresholds, and review cadence.
- Evidence requirements for product, technical, execution, growth, operations, and retrospective work.
- Decision thresholds for continue, stop, expand, pivot, refactor, or retire.

## 5. Product Layer

Question: What should the downstream project build or change?

### Inputs

- Strategy-layer priorities and non-goals.
- Metrics-layer success measures, thresholds, and guardrails.
- Market-layer user scenarios and pain points.
- Technical-layer feasibility, dependency, and safety constraints.

### Tools And Techniques

- PRD writing converts strategy and user evidence into scope, workflows, priorities, and acceptance criteria.
- PR/FAQ, opportunity mapping, or MVP framing may be used when the product problem is still uncertain.
- User journey mapping describes the end-to-end experience.
- Prototype and browser validation check whether the intended behavior is understandable.
- `docs_bilingual/prd.md` is the project PRD; it defines user stories, features, priorities, flows, and acceptance criteria.
- `docs_bilingual/prd.zh-CN.md` is the UTF-8 Chinese companion for the project PRD.
- `docs_bilingual/user_journey.md` is the user journey; it shows the end-to-end user path.
- `docs_bilingual/user_journey.zh-CN.md` is the UTF-8 Chinese companion for the user journey.

### Outputs

- Project PRD, user journey, feature scope, acceptance criteria, and out-of-scope list.
- Product evidence for technical design and execution planning.
- Feedback to strategy when the desired scope is too large for the selected delivery depth.

## 6. Technical Layer

Question: How can the downstream project be implemented safely without confusing platform tooling with business runtime?

### Inputs

- Product-layer scope, acceptance criteria, and user flows.
- Metrics-layer quality, security, cost, and reliability guardrails.
- Organization-layer ownership and approval constraints.
- Project-local source code, tests, dependencies, deployment constraints, and data constraints.
- Platform-provided guidance for native Codex subagents, OpenSpec, optional durable lanes, and local template checks.

### Tools And Techniques

- Technical design separates project business runtime from Codex platform tooling.
- Dependency classification decides whether a package belongs to the project business runtime or only to Codex tooling.
- Architecture and API design define modules, data, interfaces, trust boundaries, and compatibility.
- Data and security review defines state ownership, invariants, failure modes, and rollback boundaries.
- `docs_bilingual/technical/trd.md` is the project technical design; it explains technical choices, architecture, and tradeoffs.
- `docs_bilingual/technical/trd.zh-CN.md` is the UTF-8 Chinese companion for the technical design.
- `docs_bilingual/technical/api_spec.md` is the project API specification; when APIs exist, it defines interface inputs, outputs, errors, and permissions.
- `docs_bilingual/technical/api_spec.zh-CN.md` is the UTF-8 Chinese companion for the API specification.
- `src/` is the project source directory; it contains business or application code owned by the project.
- `tests/` is the project test directory; it contains tests owned by the project.
- Codex platform `PySide6` is a local GUI control-center dependency for Codex tooling. Downstream project `PySide6` is a business runtime dependency only when that project declares and owns it.
- The same separation applies to `SQLite`, `Redis`, `promptfoo`, and `jina-embeddings`; platform use does not automatically make them business dependencies.

### Outputs

- Project technical design, API specification, dependency classification, data boundary, and test boundary.
- Evidence that platform tooling does not pollute business runtime dependencies.
- Implementation constraints for organization, execution, operations, and Codex subagent tasks.


## 7. Organization Layer

Question: Who or what owns project responsibilities and approvals?

### Inputs

- Strategy, metrics, product scope, technical boundaries, and operating constraints.
- Human owner capacity, agent capabilities, vendor or external support, permission boundaries, and approval requirements.
- Platform-provided role guidance and project-local security or compliance requirements.

### Tools And Techniques

- Role-map design separates founder, owner, maintainer, reviewer, operator, agent, vendor, and customer-support responsibilities.
- Agent-governance design defines which AI agents may read, write, propose, review, test, deploy, or require approval.
- Responsibility-matrix design maps decisions, owners, reviewers, and escalation rules.
- Durable-lane threshold review prevents project-local durable automation from launching before the project has a frozen plan and independent execution slices.
- `docs_bilingual/role-map.md` is the project role map.
- `docs_bilingual/agent-governance.md` is the project agent-governance file when AI agents are used beyond a single main-session task.

### Outputs

- Role map, agent governance, responsibility matrix, escalation rules, and approval boundaries.
- Ownership and capacity constraints for execution, operations, and retrospective work.
- Clear separation between project-local authority and platform-provided mechanisms.


## 8. Execution Layer

Question: How does the downstream project deliver changes safely?

### Inputs

- Product-layer scope and acceptance criteria.
- Technical-layer design, dependency classification, and test requirements.
- Organization-layer ownership, approval, and optional durable-lane constraints.
- Project-local OpenSpec tree, Git state, branch policy, and release expectations.

### Tools And Techniques

- Local OpenSpec change control records why a project change is needed, how it is designed, and which tasks complete it.
- Shaping defines appetite, scope boundaries, and stop conditions before broad work starts.
- Native Codex subagents handle bounded expert work within the current Codex session.
- Optional durable lanes are selected only when project conditions meet thresholds.
- `openspec/config.yaml` is the project OpenSpec configuration; it binds the OpenSpec workflow to this repository.
- `openspec/changes/<change-id>/proposal.md` is the project-local OpenSpec proposal; it explains why a project change is needed.
- `openspec/changes/<change-id>/design.md` is the project-local OpenSpec design; it explains how the project change will be implemented.
- `openspec/changes/<change-id>/tasks.md` is the project-local OpenSpec task list; it tracks project work.
- `openspec/changes/<change-id>/*.zh-CN.md` are UTF-8 Chinese companions for the same project change artifacts.
- Use native `subagent` for bounded expert work inside the current Codex session.
- Use `native_omx` only when the project has a frozen plan and two or more mostly independent execution slices.
- Use `langgraph` only when the project needs graph phases, checkpoint recovery, approval gates, or survivor queues.

### Outputs

- Implemented and verified project changes.
- Local OpenSpec evidence, test evidence, Git evidence, and owner approval evidence.
- Release-ready artifacts or a clear reason to stop, revise, or roll back.

## 9. Growth Layer

Question: How does the downstream project acquire, activate, retain, and expand the right users?

### Inputs

- Strategy-layer positioning, target segment, and growth levers.
- Metrics-layer activation, retention, quality, and value thresholds.
- Product-layer offer, user journey, and onboarding assumptions.
- Execution-layer release-ready artifacts and known limits.
- Market-layer channel evidence and adoption barriers.

### Tools And Techniques

- Channel testing decides which acquisition or adoption paths deserve investment.
- Positioning review checks whether users understand why the project is different from alternatives.
- Onboarding and activation analysis identifies where users or operators get stuck.
- Retention and referral analysis checks whether value persists beyond first use.
- `docs_bilingual/growth-model.md` is the growth model; it defines channels, activation, retention, and expansion assumptions.
- `docs_bilingual/positioning.md` records external positioning and alternatives.

### Outputs

- Growth model, channel findings, onboarding improvements, and adoption evidence.
- Feedback to product, metrics, operations, and strategy when adoption or retention friction appears.
- Clear distinction between project growth facts and upstream platform adoption feedback.

## 10. Operations Layer

Question: How is the downstream project supported and kept usable after release?

### Inputs

- Released project version, changelog, rollback evidence, and known limits from execution.
- Growth-layer adoption, channel, and user-friction evidence.
- Organization-layer ownership, escalation, support, and agent-governance boundaries.
- Technical-layer observability, reliability, security, cost, and recovery constraints.

### Tools And Techniques

- Release planning defines rollout, communication, support readiness, and rollback readiness.
- Support-playbook design defines response paths, issue categories, service boundaries, and escalation rules.
- Customer-success or operator-success analysis tracks onboarding, activation, support outcomes, and trust recovery.
- Bug-triage design classifies defects, incidents, regressions, feature requests, and user education gaps.
- FAQ and documentation operations turn recurring questions into maintained knowledge assets.
- `docs_bilingual/release_plan.md` is the release plan; it defines rollout, release gates, and communication.
- `docs_bilingual/release_plan.zh-CN.md` is the UTF-8 Chinese companion for the release plan.
- `docs_bilingual/rollback_plan.md` is the rollback plan; it defines how to return to a safe version.
- `docs_bilingual/rollback_plan.zh-CN.md` is the UTF-8 Chinese companion for the rollback plan.
- `CHANGELOG.md` is the project changelog; it records user-visible and operator-visible changes.
- `docs_bilingual/support-playbook.md` is the support playbook.
- `docs_bilingual/faq.md` is the project FAQ.

### Outputs

- Released project version, changelog, rollback evidence, support records, FAQ updates, and operations evidence.
- Adoption, support, reliability, trust, and usability feedback for product, technical, growth, and retrospective layers.
- Evidence that released work remains usable, supportable, and recoverable.

## 11. Retrospective And Upstream Feedback Layer

Question: What did the downstream project learn, and what should be fed back upstream?

### Inputs

- Execution-layer delivery records, test results, defects, and release outcomes.
- Growth-layer adoption findings and experiment results.
- Operations-layer release results, rollback results, support evidence, and user feedback.
- Observed gaps in templates, startup summaries, Codex subagent use, or optional durable-lane rules.

### Tools And Techniques

- Retrospective analysis turns project experience into reusable local lessons.
- Experiment analysis decides whether to continue, stop, pivot, or expand.
- SOP and template review decides which repeated local work should become a project-local process.
- Upstream feedback separates platform improvement ideas from project-local facts.
- Archive discipline keeps project OpenSpec, durable state, and release state local to the project.
- `docs_bilingual/lessons_learned.md` is the project lessons-learned document; it records locally reusable experience.
- `docs_bilingual/lessons_learned.zh-CN.md` is the UTF-8 Chinese companion for the lessons-learned document.
- `docs_bilingual/upstream_feedback.md` is the platform feedback document; it records experience that may improve `D:\PythonProject_langgraph`.
- `docs_bilingual/upstream_feedback.zh-CN.md` is the UTF-8 Chinese companion for the platform feedback document.

### Outputs

- Local lessons learned, experiment conclusions, upstream feedback candidates, and follow-up tasks.
- Clear separation between project-local truth and platform improvement requests.
- Inputs for future template updates, governance updates, or project iterations.
- Reusable learning returned to the cognitive, business, market, strategy, metrics, product, technical, organization, execution, growth, and operations layers.

## Minimal Downstream Project Checklist

Small downstream projects can start with the minimum local surfaces:

- `AGENTS.md` as the project-level Codex instruction file.
- `docs_bilingual/project_startup_summary.md` as the ASCII cold-start summary.
- `docs_bilingual/project_startup_summary.zh-CN.md` as the UTF-8 Chinese cold-start summary companion.
- `openspec/` as the project-local OpenSpec governance tree.
- `.omx/state/` as the project-local durable state directory; it is needed only when durable lanes are used.
- `.gitignore` as the project ignore file; it ignores caches, state, generated artifacts, and local secrets.
