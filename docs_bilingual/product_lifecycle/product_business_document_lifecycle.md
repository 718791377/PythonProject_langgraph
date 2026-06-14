# Product And Business Document Lifecycle

This document defines the general 0-11 / 12-layer document stack for commercial, internet, product, platform, and tooling work. It is product neutral and not bound to any single project-management source. It explains what each stage answers, which inputs it receives, which tools and techniques it uses, and which deliverable outputs it produces.

This document uses a process-group style structure. Each layer is written as Inputs, Tools And Techniques, and Outputs.

- Inputs are external inputs, project-external constraints, and inputs from other lifecycle layers.
- Tools And Techniques are the methods, files, checks, and governance techniques used while analyzing, deciding, designing, or delivering the layer.
- Outputs are final deliverables that can be published externally or passed to other lifecycle layers.

These rules are a general governance overlay. They do not replace white papers, BRDs, MRDs, North Star plans, PRDs, technical designs, implementation plans, OpenSpec artifacts, or repository checkers; they help those documents keep consistent inputs, processing, and outputs across the lifecycle.

The local source-library synthesis lives in `business_management_source_synthesis.md`. It summarizes page-level and spine-item-level reading of the ignored `Business Management/` library and translates the sources into repository-specific lifecycle rules rather than source-book excerpts.

## Source Evidence Boundary

This lifecycle stack now points to `fresh_source_reading_evidence.md` for the current `fresh-source-lifecycle-whitepaper-pmi-refresh-20260613` (`2026-06-13T22:50:48Z`) evidence boundary and to `ten_to_twelve_layer_bridge.md` for the research/white-paper layer bridge. Raw extraction text remains outside Git.

## Two Target Architecture Modes

This lifecycle now has two explicit operating modes.

| Mode | Inventory rule | Use it when |
| --- | --- | --- |
| Codex CLI durable-team platform | 12 layers + 4 virtual departments + 24 responsibility domains + 18 cross-cutting modules + 48 core documents + 12 governed AI agents + 12 recommended books | The work changes Codex orchestration, native subagent routing, `native_omx`, LangGraph, worktree safety, OpenSpec governance, local-main-first publication, templates, skill/profile governance, or reusable developer tooling |
| One-person-company operating system | 12 layers + 5 virtual departments + 30 responsibility domains + 20 cross-cutting modules + 60 core documents + 15 governed AI agents + 15 recommended books + 12 minimal startup documents | The work belongs to a downstream business, product, offer, customer, revenue, operations, finance, risk, or learning system |

The two modes share the same 12-layer trunk, but they do not share authority. The Codex platform may provide governance mechanisms and templates. A downstream one-person company owns its own customer evidence, revenue facts, financial evidence, product commitments, legal risk, release state, durable state, and lessons learned.

Canonical inventory maps now live in `codex_platform_inventory_map.md` and `one_person_company_inventory_map.md`. Treat those two files as the count authority when another document needs the 48-document or 60-document target; this lifecycle file explains how those inventories move through the 12-layer document stack.

## Execution-Facing Process-Group Rule

For any layer that drives work, use the PMI process-group style as the execution grammar:

- Inputs: source evidence, upstream layer outputs, constraints, risks, approvals, and current state.
- Tools and Techniques: analysis methods, templates, checkers, reviews, experiments, agent roles, gates, and control techniques.
- Outputs: approved documents, decisions, evidence, release artifacts, archive artifacts, or inputs to another layer.

This rule applies to every lifecycle layer, every delivery gate, and every release slice. It prevents a layer from becoming a loose essay with no start condition, no control technique, and no deliverable output.


## Value-Delivery Overlay

The document stack is not valuable because every file exists. It is valuable only when it helps the project identify value, align stakeholders, deliver usable outcomes, verify whether the outcomes worked, and feed learning into the next cycle.

Use value checks across all layers:

- Value identification asks what user, business, operational, trust, or learning value may exist.
- Value alignment asks whether stakeholders agree on purpose, boundaries, success criteria, and trade-offs.
- Value delivery asks which increment will become usable or inspectable.
- Value verification asks what evidence will prove the increment helped.
- Value learning asks what should be continued, stopped, expanded, or retired.

## Lightweight Project Canvas

A `project_canvas.md` file is a lightweight project canvas. It is optional for very small local changes, but recommended before writing a full BRD, MRD, PRD, or implementation plan for uncertain or cross-role work.

The canvas should fit on one page where possible and cover:

- purpose and value hypothesis;
- target users, operators, or stakeholders;
- success criteria and non-goals;
- scope boundary and constraints;
- main risks, assumptions, and dependencies;
- delivery style: predictive, adaptive, or hybrid;
- first value increment and feedback point;
- validation, rollback, and learning evidence.

## Governance-System Tailoring

Tailoring is not only choosing fewer documents. It is choosing the right governance system for the risk and uncertainty level.

The explicit tailoring authority for full versus lightweight use is `lifecycle_tailoring_rules.md`. Use it to decide whether the full architecture applies to the whole project, only the affected phase, only a bounded module, or only a release slice.

Tailor these dimensions together:

- Governance depth: who approves, who reviews, and which gates are mandatory.
- Document depth: whether a short canvas is enough or whether BRD, MRD, PRD, design, test, release, rollback, and retrospective files must be explicit.
- Role-collaboration depth: whether one maintainer, native `subagent` bursts, durable workers, or graph-shaped orchestration are justified.
- Validation depth: whether local checks, browser verification, CI, red-team review, or production smoke evidence is required.
- Release depth: whether the change is local-only, MR-gated, staged rollout, or rollback-backed release.
- Learning depth: whether a brief note is enough or a full retrospective and governance update are required.

## Quick Difference: White Paper vs North Star Plan

| Document | Core question | Main effect | Typical reader | Execution role |
| --- | --- | --- | --- | --- |
| White paper | Why does this direction make sense? | Changes cognition and frames a new narrative | Decision makers, collaborators, future maintainers | It justifies the direction but is not a task plan |
| North Star plan | How do we win and measure progress? | Converts strategy into a measurable system | Builders, maintainers, operators | It guides staged planning but is still above implementation tasks |

A white paper argues that a new direction is real and valuable. A strategy plan defines diagnosis, guiding policy, coherent action, and trade-offs. A North Star or metrics plan defines the key metric, input metrics, guardrails, and thresholds that show whether the strategy is working.

## General Lifecycle Tailoring Rules

Different projects should not write every document by default. Choose the minimum sufficient document set based on risk, uncertainty, impact, and delivery style.

- Predictive gates fit work with clear requirements, higher risk, and explicit release evidence or rollback evidence needs.
- Adaptive slices fit work with unclear requirements, user-feedback needs, spike work, MVP work, or small experiments.
- Hybrid delivery fits work that still needs discovery but must eventually pass review, test, release, and retrospective gates.

Use full architecture for the affected scope when work touches money, external users, customer commitments, trust, compliance, security, privacy, data ownership, durable state, runtime entrypoints, cross-project templates, shared interfaces, release gates, rollback safety, or long-lived platform behavior.

Use whole-project lightweight architecture only for early ideas, private spikes, local learning exercises, or small internal tools with no external users, no money or trust boundary, no sensitive data, no shared runtime entrypoint, and a reversible or disposable result.

Use phase-local or module-level lightweight architecture when the project overall needs stronger governance but one phase or module is bounded, low-risk, reversible, and has explicit escalation triggers. If risk, coupling, adoption, support, compliance, or rollback impact grows, expand the affected layer or module first and expand the whole project only when coupling becomes systemic.

## 0. Cognitive Narrative Layer

Core question: Why does this thing exist?

### Inputs

- Industry trends, technology trends, policy environment, user-behavior changes, or organization-strategy changes.
- Existing-solution gaps, repeated failure cases, long-term friction, and structural pain.
- Repeated problems found by the business, market, or technical layers; downstream feedback can trigger a new narrative.

### Tools And Techniques

- Trend analysis turns external changes into likely multi-year directions.
- Problem modeling reduces surface requests into structural tensions, constraints, and opportunities.
- Narrative reasoning explains why existing solutions are insufficient and why a new paradigm may work.
- Category and positioning analysis clarifies what mental frame the audience should use before they compare alternatives.
- `whitepaper.md` is the white paper file; it explains industry trends, structural pain, why existing solutions fail, and the new paradigm.

### Outputs

- White paper or narrative brief explaining why the direction is worth understanding and discussing.
- New-paradigm definition, key assumptions, evidence chain, and non-goal boundary.
- Direction candidates passed to the business layer for further evaluation.

## 1. Business Layer

Core question: Is this worth doing?

### Inputs

- Direction candidates, problem definitions, and key assumptions from the cognitive narrative layer.
- Organization goals, budget boundaries, resource constraints, compliance constraints, and operating priorities.
- User scale, competitor evidence, and willingness-to-pay signals from the market layer.

### Tools And Techniques

- Business-model analysis determines how value converts into revenue, saved cost, efficiency gain, or risk reduction.
- Benefit and cost estimation compares development, operation, model, maintenance, compliance, acquisition, and migration costs.
- Company-of-one constraint analysis decides where staying small improves focus, quality, and resilience.
- Market sizing estimates TAM, SAM, and SOM; TAM is total market, SAM is serviceable market, and SOM is reachable market.
- Unit economics models CAC, LTV, and ROI; CAC is customer acquisition cost, LTV is lifetime value, and ROI is return on investment.
- `brd.md` is the business requirements document; it explains business goals, revenue logic, cost structure, and return on investment.

### Outputs

- BRD, business assumptions, investment boundary, and success criteria.
- Decision to do, not do, delay, or research more before deciding.
- Target audience and value assumptions for the market layer; business goals and constraints for the strategy layer.

## 2. Market Layer

Core question: What do users actually need?

### Inputs

- Target audience, value assumptions, and business constraints from the business layer.
- External user interviews, surveys, competitor observations, channel feedback, support feedback, and usage data.
- Problem frames from the cognitive narrative layer and real-use friction returned by the product or growth layers.

### Tools And Techniques

- User segmentation identifies target users, influencers, payers, and operators.
- Scenario analysis describes when, why, and under what constraints users need the solution.
- Customer interview analysis uses past behavior, switching triggers, and functional/social/emotional context instead of asking only for opinions.
- Pain-point analysis extracts real user problems behind feature requests.
- Competitor analysis compares alternatives, differentiation opportunities, and entry barriers.
- Adoption-segment analysis separates early enthusiasts, beachhead users, early majority buyers, and late adopters.
- Feedback loops reduce uncertainty through small-sample validation, prototype feedback, or MVP feedback.
- `mrd.md` is the market requirements document; it turns market evidence and user needs into product direction.

### Outputs

- MRD, target users, target scenarios, market entry position, and competitor-differentiation judgment.
- User-problem list, priority signals, and entry strategy.
- Market opportunity for the strategy layer; user scenarios and demand evidence for the product layer.

## 3. Strategy Layer

Core question: How do we win, and what do we deliberately refuse?

### Inputs

- New paradigm and long-term assumptions from the cognitive narrative layer.
- Business goals, cost boundaries, and success criteria from the business layer.
- User scenarios, demand evidence, competitor differences, and entry strategy from the market layer.
- Capability boundaries, risk constraints, and feasibility feedback from the technical layer.

### Tools And Techniques

- Strategy-kernel analysis records diagnosis, guiding policy, and coherent action before roadmap expansion.
- Beachhead and positioning analysis selects where to win first and which alternatives to frame against.
- Product-strategy analysis decides which offers, workflows, or capabilities belong in scope and which must be refused.
- Critical-path analysis identifies the constraint that most limits the next stage of progress.
- Stage tailoring chooses predictive, adaptive, or hybrid delivery based on risk and uncertainty.
- `strategy.md` is the strategy file; it records diagnosis, guiding policy, coherent action, trade-offs, and explicit non-goals.
- `product_strategy.md` is the product strategy file; it translates strategic choices into product or offer direction.

### Outputs

- Strategy, guiding policy, coherent action set, trade-offs, and non-goal boundary.
- Strategic priorities for the metrics, product, organization, execution, and growth layers.
- Decision to focus, pause, pivot, or run more discovery before scaling work.

## 4. Metrics Layer

Core question: What evidence tells us whether the strategy is working?

### Inputs

- Strategy, trade-offs, and desired outcomes from the strategy layer.
- Business goals, cost limits, and value assumptions from the business layer.
- Market, user, product, technical, growth, operations, and retrospective signals.
- Data availability, data quality, privacy, and instrumentation constraints from the technical layer.

### Tools And Techniques

- North Star metric design selects the measure that best represents durable user or operator value.
- Input metric decomposition identifies leading indicators that drive the North Star metric.
- OKR design translates strategy into focus, alignment, tracking, and review cadence.
- OMTM analysis selects the one metric that matters most for the current stage.
- Guardrail metric design protects quality, cost, trust, security, reliability, and operator attention.
- Tracking-plan and data-dictionary design define event names, dimensions, owners, and metric definitions.
- `metrics.yaml` is the machine-readable metrics contract; it defines North Star, input, guardrail, and stage metrics.
- `tracking_plan.md` is the tracking plan; it defines events, sources, owners, and quality checks.
- `data_dictionary.md` is the data dictionary; it defines metric terms and data ownership.

### Outputs

- Metrics contract, OKRs, OMTM, guardrails, thresholds, and review cadence.
- Evidence requirements for product, technical, execution, growth, operations, and retrospective work.
- Decision thresholds for continue, stop, expand, pivot, refactor, or retire.

## 5. Product Layer

Core question: What should the product be?

### Inputs

- Strategic priorities, trade-offs, and non-goals from the strategy layer.
- Metrics, thresholds, and evidence requirements from the metrics layer.
- User segments, scenarios, pain points, and demand evidence from the market layer.
- Feasibility boundaries, interface constraints, security constraints, and cost constraints from the technical layer.
- Adoption friction, feedback summaries, and experiment results returned by the growth, operations, or retrospective layers.

### Tools And Techniques

- User-flow design splits user goals into entry, action, feedback, and completion paths.
- Information architecture organizes content, screens, objects, and actions.
- PR/FAQ and narrative planning describe the customer-backward outcome before implementation details.
- Opportunity mapping and product kata connect user problems, assumptions, experiments, and success metrics.
- Prototype validation uses low-fidelity or high-fidelity prototypes to test interaction and layout clarity.
- Prioritization sorts work by value, risk, cost, and dependencies into P0, P1, and P2 groups.
- Acceptance-criteria design turns functional needs into testable and reviewable results.
- `prd.md` is the product requirements document; it translates strategy into user-facing functions, flows, priorities, and acceptance criteria.
- `offer.md` is the offer document; it defines what is sold or delivered and the promise boundary.
- `user_journey.md` describes the end-to-end user journey; it shows what a user experiences before, during, and after using the product.
- `information_architecture.md` describes the information architecture; it shows how content, screens, and actions are organized.
- `prototype.fig` or another prototype file is the design prototype; it shows the intended interaction and layout in a design tool.

### Outputs

- PRD, offer definition, user journey, information architecture, prototype, and acceptance criteria.
- What is in scope for the product, what is out of scope, and which needs move to later stages.
- System-requirement sources for the technical layer; feature scope and acceptance evidence for the execution layer.

## 6. Technical Layer

Core question: How can it be implemented safely?

### Inputs

- PRD, user flows, acceptance criteria, and scope boundaries from the product layer.
- Strategy, metrics, long-term evolution direction, and non-goal boundary.
- Organization constraints, owner boundaries, and approval constraints from the organization layer.
- External technical constraints, including security, privacy, performance, cost, compatibility, deployment environment, and supply-chain limits.
- Defects, performance bottlenecks, operations friction, and technical debt returned by the execution, operations, or retrospective layers.

### Tools And Techniques

- Architecture design decomposes modules, interfaces, data flows, state boundaries, and trust boundaries.
- Dependency and component-boundary design protects long-term changeability and prevents accidental coupling.
- Data-system design checks reliability, scalability, maintainability, consistency, and derived-data responsibilities.
- Security-by-design analysis turns domain invariants, input constraints, and failure modes into default-safe behavior.
- Risk analysis identifies security, privacy, availability, cost, maintainability, and migration risks.
- Quality gates define testing, review, rollback, observability, and compatibility requirements.
- Build-or-buy judgment decides whether to build, reuse, buy, integrate, or delay.
- `srs.md` is the system requirements specification; it defines system-level functional and non-functional requirements.
- `trd.md` is the technical requirements or technical design document; it explains the chosen technical solution and tradeoffs.
- `hld.md` is the high-level design; it defines major modules, trust boundaries, data flow, and integration points.
- `lld.md` is the low-level design; it defines concrete components, scripts, functions, schemas, and edge cases.
- `api_spec.md` is the API specification; it defines inputs, outputs, permissions, errors, and compatibility.
- `data_model.md` is the data model; it defines entities, fields, relationships, and persistence rules.

### Outputs

- SRS, TRD, HLD, LLD, API specification, data model, and risk-control notes.
- Technical evidence that the system can be built, tested, operated, reviewed, and rolled back.
- Implementation boundaries, dependencies, test requirements, and release risks for the organization and execution layers.

## 7. Organization Layer

Core question: Who or what owns each responsibility, decision, and approval?

### Inputs

- Strategy, metrics, product scope, technical boundaries, and operating constraints.
- Human capacity, agent capabilities, vendor or external support, permission boundaries, and approval requirements.
- Cognitive load, team or agent interaction modes, and support expectations from operations.

### Tools And Techniques

- Role-map design separates founder, owner, reviewer, operator, agent, vendor, and customer-success responsibilities.
- Agent-governance design defines which AI agents may read, write, propose, review, test, deploy, or require approval.
- RACI-style responsibility mapping defines who is responsible, accountable, consulted, and informed for key decisions.
- Team API and cognitive-load analysis define collaboration boundaries, handoff expectations, and platform responsibilities.
- Escalation and approval design defines which decisions need human confirmation.
- `role-map.md` is the role map; it defines human, agent, vendor, and reviewer responsibilities.
- `agent-governance.md` is the agent governance file; it defines agent permissions, approval gates, and rollback boundaries.
- `responsibility_matrix.md` is the responsibility matrix; it maps decisions, owners, reviewers, and escalation rules.
- `operating_model.md` is the operating model; it defines cadence, ownership, communication, and review loops.

### Outputs

- Role map, agent governance, responsibility matrix, operating model, and approval boundaries.
- Ownership and capacity constraints for execution, operations, and retrospective work.
- Explicit decision rights so automation does not become hidden authority.

## 8. Execution Layer

Core question: How do we deliver it?

### Inputs

- Scope, priorities, acceptance criteria, and non-goal boundary from the product layer.
- Design, interfaces, dependencies, risk controls, and test requirements from the technical layer.
- Metrics, thresholds, release cadence, and success criteria from the metrics layer.
- Ownership, approval, capacity, and agent-governance constraints from the organization layer.
- External inputs, including time window, release limits, approval limits, and operating windows.

### Tools And Techniques

- Work decomposition splits scope into small slices that are verifiable, reversible, and reviewable.
- Shaping defines appetite, boundaries, rabbit holes, and the circuit breaker before a team or agent starts broad execution.
- Plan freeze locks key design, task list, acceptance criteria, and risk boundaries before implementation.
- Change control uses OpenSpec, code review, CI, testing, and release gates to control scope drift.
- Monitoring and controlling tracks progress, risk, defects, dependencies, and acceptance status during execution.
- `implementation_plan.md` is the implementation plan; it splits a chosen stage into executable work.
- `tasks.md` is the task list; it tracks concrete steps and completion state.
- `test_plan.md` is the test plan; it defines unit, integration, end-to-end, manual, and regression checks.
- `release_plan.md` is the release plan; it defines rollout timing, release gates, and communication.
- `rollback_plan.md` is the rollback plan; it defines how to return to a safe previous state.

### Outputs

- Executable tasks, test plan, release plan, rollback plan, and delivery evidence.
- Implemented, verified, released, or release-ready work results.
- Adoptable capabilities for the growth and operations layers; delivery records, issue records, and learning material for the retrospective layer.

## 9. Growth Layer

Core question: How does it reach, activate, retain, and monetize the right audience?

### Inputs

- Released or release-ready capabilities, known limits, and adoption entry points from the execution layer.
- Strategy, metrics, input metrics, growth levers, and guardrails.
- User segments, positioning, channel signals, and market evidence.
- Operations feedback, support friction, trust signals, and customer-success findings.

### Tools And Techniques

- Roadmap planning orders later versions by user value, business value, technical dependencies, and risk.
- Growth experiments test acquisition, activation, retention, revenue, or adoption mechanisms in small batches.
- Traction-channel testing compares candidate channels against a defined traction goal and critical path.
- Positioning and whole-product review ensure users understand the category, alternatives, value, onboarding, support, and trust story.
- Metrics system defines DAU, MAU, retention, conversion, CAC, LTV, quality, or adoption metrics; DAU means daily active users and MAU means monthly active users.
- Adoption analysis records where the system is used, why it is used, and what friction remains.
- `roadmap.md` is the product roadmap; it defines future versions and priority order.
- `growth_plan.md` is the growth plan; it defines acquisition, activation, retention, revenue, or adoption mechanisms.
- `channel_tests.md` records channel hypotheses, tests, and results.
- `adoption_report.md` is the adoption report; it records where the system is used and what friction remains.

### Outputs

- Roadmap, growth plan, channel tests, adoption report, and later-version candidates.
- Path for the system to expand, be adopted, improve, or commercialize.
- Metric progress for the metrics and strategy layers; demand changes for the product layer; adoption evidence for the operations and retrospective layers.

## 10. Operations Layer

Core question: How does the system keep serving users after release?

### Inputs

- Released capabilities, changelog, rollback evidence, and known limits from execution.
- Adoption, channel, and user-friction evidence from growth.
- Ownership, escalation, support, and agent-governance boundaries from organization.
- Quality, reliability, cost, security, support, and customer-success signals.

### Tools And Techniques

- Support-playbook design defines response paths, issue categories, service boundaries, and escalation rules.
- Customer-success analysis tracks onboarding, activation, renewals, support outcomes, and trust recovery.
- Bug-triage design classifies defects, incidents, regressions, feature requests, and user education gaps.
- FAQ and documentation operations turn recurring questions into maintained knowledge assets.
- Operating-cadence review keeps weekly, monthly, quarterly, or release reviews lightweight and evidence-based.
- `ops-playbook.md` is the operations playbook; it defines support, issue handling, cadence, and escalation.
- `support-playbook.md` is the support playbook; it defines support categories, response rules, and handoff paths.
- `faq.md` is the FAQ; it turns repeated questions into maintained answers.
- `customer-success.md` records customer-success or operator-success practices.
- `issue_log.md` records active blockers, incidents, and support issues.

### Outputs

- Operations playbook, support records, FAQ updates, customer-success notes, and issue-log evidence.
- Support, reliability, trust, and usability feedback for the product, technical, growth, and retrospective layers.
- Operating evidence that released work remains usable, supportable, and recoverable.

## 11. Retrospective Layer

Core question: Did it work, what changed, and what should compound?

### Inputs

- Delivery records, test results, release results, defect records, and incident records from the execution layer.
- Metric results, adoption reports, experiment results, support evidence, and user feedback from growth and operations.
- Repeated problems, unmet needs, and technical debt returned by the market, product, technical, organization, execution, and operations layers.
- External inputs, including customer feedback, audit findings, compliance changes, and operating events.

### Tools And Techniques

- Retrospective analysis identifies what happened, why it happened, impact scope, fixes, and prevention actions.
- Experiment analysis compares variant outcomes and decides whether to continue, stop, or expand.
- Learning capture turns incidents, delivery, and feedback into reusable rules, templates, checklist items, or follow-up tasks.
- Operating-system refinement turns repeated work into SOPs, templates, metrics, ownership rules, or automation only when they reduce future friction.
- Closing gates confirm that deliverables, documentation, release state, rollback evidence, and lessons learned are archived.
- `post_mortem.md` is the incident or project retrospective; it records what happened, why it happened, impact, fix, and prevention.
- `monthly-review.md` is the monthly review; it consolidates strategy, metrics, operations, and learning decisions.
- `ab_test_report.md` is the A/B test report; it compares variants and explains which one performed better.
- `feedback_summary.md` is the user feedback summary; it captures recurring user reactions and requests.
- `lessons_learned.md` is the lessons-learned document; it converts experience into reusable rules or future tasks.

### Outputs

- Retrospective report, monthly review, experiment report, feedback summary, lessons learned, and governance-update recommendations.
- Clear judgment about what to continue, stop, expand, refactor, automate, delegate, or retire in the next cycle.
- Reusable learning returned to the cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, and operations layers.

## Minimum File Set By Project Size

Small internal tooling work usually needs a short strategy or North Star note, metrics note, PRD, technical design, owner or role note, implementation plan, test plan, operations note, and retrospective. An implementation plan splits a chosen stage into executable work; a test plan defines validation; a retrospective captures learning. A public product, commercial product, or long-lived platform should add white paper, BRD, MRD, roadmap, metrics, and release governance. A roadmap orders later versions; metrics define measurement; release governance defines rollout gates and rollback requirements.

For the Codex CLI durable-team platform, `docs_bilingual/north_star_plan.md` is the repository-level North Star plan. It defines the primary success metric, input metrics, guardrails, staged decision thresholds, and the 12-layer platform/downstream inventory comparison.

For a downstream one-person-company operating system, the lightweight floor is the 12 minimal startup documents defined in `one_person_company_inventory_map.md`: `company-thesis.md`, `business-model.md`, `offer.md`, `pricing.md`, `user-segments.md`, `growth-model.md`, `finance-model.md`, `ops-playbook.md`, `metrics.yaml`, `risk-register.md`, `agent-governance.md`, and `monthly-review.md`. A downstream project should expand toward the 60-document system only when customer evidence, revenue exposure, delivery complexity, governance risk, or long-term operating cost justifies the deeper architecture.

The more a project affects money, users, trust, compliance, or long-term platform behavior, the more of this stack should be explicit. Lightweight mode may be whole-project only for low-risk early work; otherwise keep high-risk phases or modules on the full architecture path and lighten only bounded low-risk slices.
