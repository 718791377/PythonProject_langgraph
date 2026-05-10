# Product And Business Document Lifecycle

This document defines the general 0-8 document stack for commercial, internet, product, platform, and tooling work. It is product neutral and not bound to any single project-management source. It explains what each stage answers, which inputs it receives, which tools and techniques it uses, and which deliverable outputs it produces.

This document uses a process-group style structure. Each layer is written as Inputs, Tools And Techniques, and Outputs.

- Inputs are external inputs, project-external constraints, and inputs from other lifecycle layers.
- Tools And Techniques are the methods, files, checks, and governance techniques used while analyzing, deciding, designing, or delivering the layer.
- Outputs are final deliverables that can be published externally or passed to other lifecycle layers.

These rules are a general governance overlay. They do not replace white papers, BRDs, MRDs, North Star plans, PRDs, technical designs, implementation plans, OpenSpec artifacts, or repository checkers; they help those documents keep consistent inputs, processing, and outputs across the lifecycle.

The local source-library synthesis lives in `business_management_source_synthesis.md`. It summarizes page-level and spine-item-level reading of the ignored `Business Management/` library and translates the sources into repository-specific lifecycle rules rather than source-book excerpts.

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

A white paper argues that a new direction is real and valuable. A North Star plan defines the long-term target, the key metric, input metrics, levers, and staged paths toward the target.

## General Lifecycle Tailoring Rules

Different projects should not write every document by default. Choose the minimum sufficient document set based on risk, uncertainty, impact, and delivery style.

- Predictive gates fit work with clear requirements, higher risk, and explicit release evidence or rollback evidence needs.
- Adaptive slices fit work with unclear requirements, user-feedback needs, spike work, MVP work, or small experiments.
- Hybrid delivery fits work that still needs discovery but must eventually pass review, test, release, and retrospective gates.

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

## 3. Strategy And North Star Layer

Core question: How do we win?

### Inputs

- New paradigm and long-term assumptions from the cognitive narrative layer.
- Business goals, cost boundaries, and success criteria from the business layer.
- User scenarios, demand evidence, competitor differences, and entry strategy from the market layer.
- Capability boundaries, risk constraints, and feasibility feedback from the technical layer.

### Tools And Techniques

- Strategy-kernel analysis records diagnosis, guiding policy, and coherent action before roadmap expansion.
- North Star metric design selects the one metric that best represents user value and long-term progress.
- Input metric decomposition defines leading indicators that drive the North Star metric.
- OKR and stage-metric design translates strategy into focus, alignment, tracking, and decision thresholds.
- Lever identification finds product, technology, process, distribution, or operating mechanisms that most change outcomes.
- Stage tailoring chooses predictive, adaptive, or hybrid delivery based on risk and uncertainty.
- `north_star_plan.md` is the North Star plan; it defines the core metric, input metrics, growth or capability levers, and staged path.

### Outputs

- North Star plan, staged path, prioritization logic, and non-goal boundary.
- MVP definition; MVP means minimum viable product or minimum viable capability for testing key assumptions.
- Release train definition; release train is a fixed-cadence version delivery plan.
- Scope priorities for the product layer; stage gates and roadmap constraints for the execution layer.

## 4. Product Layer

Core question: What should the product be?

### Inputs

- North Star metric, staged path, prioritization logic, and non-goal boundary from the strategy layer.
- User segments, scenarios, pain points, and demand evidence from the market layer.
- Feasibility boundaries, interface constraints, security constraints, and cost constraints from the technical layer.
- Adoption friction, feedback summaries, and experiment results returned by the growth or retrospective layers.

### Tools And Techniques

- User-flow design splits user goals into entry, action, feedback, and completion paths.
- Information architecture organizes content, screens, objects, and actions.
- PR/FAQ and narrative planning describe the customer-backward outcome before implementation details.
- Opportunity mapping and product kata connect user problems, assumptions, experiments, and success metrics.
- Prototype validation uses low-fidelity or high-fidelity prototypes to test interaction and layout clarity.
- Prioritization sorts work by value, risk, cost, and dependencies into P0, P1, and P2 groups.
- Acceptance-criteria design turns functional needs into testable and reviewable results.
- `prd.md` is the product requirements document; it translates strategy into user-facing functions, flows, priorities, and acceptance criteria.
- `user_journey.md` describes the end-to-end user journey; it shows what a user experiences before, during, and after using the product.
- `information_architecture.md` describes the information architecture; it shows how content, screens, and actions are organized.
- `prototype.fig` or another prototype file is the design prototype; it shows the intended interaction and layout in a design tool.

### Outputs

- PRD, user journey, information architecture, prototype, and acceptance criteria.
- What is in scope for the product, what is out of scope, and which needs move to later stages.
- System-requirement sources for the technical layer; feature scope that can be decomposed by the execution layer.

## 5. Technical Layer

Core question: How can it be implemented safely?

### Inputs

- PRD, user flows, acceptance criteria, and scope boundaries from the product layer.
- Stage constraints, long-term evolution direction, and non-goal boundary from the strategy layer.
- External technical constraints, including security, privacy, performance, cost, compatibility, deployment environment, and supply-chain limits.
- Defects, performance bottlenecks, operations friction, and technical debt returned by the execution, growth, or retrospective layers.

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
- Implementation boundaries, dependencies, test requirements, and release risks for the execution layer.

## 6. Execution Layer

Core question: How do we deliver it?

### Inputs

- Scope, priorities, acceptance criteria, and non-goal boundary from the product layer.
- Design, interfaces, dependencies, risk controls, and test requirements from the technical layer.
- Staged path, release cadence, and success criteria from the strategy layer.
- External inputs, including team capacity, time window, release limits, approval limits, and operating windows.

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
- Adoptable capabilities for the growth layer; delivery records, issue records, and learning material for the retrospective layer.

## 7. Growth And Adoption Layer

Core question: How does it become larger, more useful, or more adopted?

### Inputs

- Released capabilities, release records, known limits, and adoption entry points from the execution layer.
- North Star metric, input metrics, and growth levers from the strategy layer.
- User segments and channel signals from the market layer.
- Lessons learned, feedback summaries, and experiment results from the retrospective layer.

### Tools And Techniques

- Roadmap planning orders later versions by user value, business value, technical dependencies, and risk.
- Growth experiments test acquisition, activation, retention, revenue, or adoption mechanisms in small batches.
- Traction-channel testing compares candidate channels against a defined traction goal and critical path.
- Positioning and whole-product review ensure users understand the category, alternatives, value, onboarding, support, and trust story.
- Metrics system defines DAU, MAU, retention, conversion, CAC, LTV, quality, or adoption metrics; DAU means daily active users and MAU means monthly active users.
- Adoption analysis records where the system is used, why it is used, and what friction remains.
- `roadmap.md` is the product roadmap; it defines future versions and priority order.
- `growth_plan.md` is the growth plan; it defines acquisition, activation, retention, revenue, or adoption mechanisms.
- `metrics.md` is the metrics document; it defines DAU, MAU, retention, conversion, CAC, LTV, quality, or adoption metrics as appropriate.
- `adoption_report.md` is the adoption report; it records where the system is used and what friction remains.

### Outputs

- Roadmap, growth plan, metrics system, adoption report, and later-version candidates.
- Path for the system to expand, be adopted, improve, or commercialize.
- Metric progress for the strategy layer; demand changes for the product layer; experiment and adoption evidence for the retrospective layer.

## 8. Retrospective And Learning Layer

Core question: Did it work, and what should change?

### Inputs

- Delivery records, test results, release results, defect records, and incident records from the execution layer.
- Metric results, adoption reports, experiment results, and user feedback from the growth layer.
- Repeated problems, unmet needs, and technical debt returned by the market, product, and technical layers.
- External inputs, including customer feedback, audit findings, compliance changes, and operating events.

### Tools And Techniques

- Retrospective analysis identifies what happened, why it happened, impact scope, fixes, and prevention actions.
- Experiment analysis compares variant outcomes and decides whether to continue, stop, or expand.
- Learning capture turns incidents, delivery, and feedback into reusable rules, templates, checklist items, or follow-up tasks.
- Operating-system refinement turns repeated work into SOPs, templates, metrics, ownership rules, or automation only when they reduce future friction.
- Closing gates confirm that deliverables, documentation, release state, rollback evidence, and lessons learned are archived.
- `post_mortem.md` is the incident or project retrospective; it records what happened, why it happened, impact, fix, and prevention.
- `ab_test_report.md` is the A/B test report; it compares variants and explains which one performed better.
- `feedback_summary.md` is the user feedback summary; it captures recurring user reactions and requests.
- `lessons_learned.md` is the lessons-learned document; it converts experience into reusable rules or future tasks.

### Outputs

- Retrospective report, experiment report, feedback summary, lessons learned, and governance-update recommendations.
- Clear judgment about what to continue, stop, expand, refactor, or retire in the next cycle.
- Reusable learning returned to the cognitive narrative, business, market, strategy, product, technical, and execution layers.

## Minimum File Set By Project Size

Small internal tooling work usually needs a short North Star note, PRD, technical design, implementation plan, test plan, and retrospective. An implementation plan splits a chosen stage into executable work; a test plan defines validation; a retrospective captures learning. A public product, commercial product, or long-lived platform should add white paper, BRD, MRD, roadmap, metrics, and release governance. A roadmap orders later versions; metrics define measurement; release governance defines rollout gates and rollback requirements.

The more a project affects money, users, trust, compliance, or long-term platform behavior, the more of this stack should be explicit.
