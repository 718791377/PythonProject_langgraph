# Product And Business Document Lifecycle

This document defines the general 0-8 document stack for commercial, internet, product, platform, and tooling work. It is product neutral. It explains what each stage answers, which files belong there, and how a white paper differs from a North Star plan.

## Quick Difference: White Paper vs North Star Plan

| Document | Core question | Main effect | Typical reader | Execution role |
| --- | --- | --- | --- | --- |
| White paper | Why does this direction make sense? | Changes cognition and frames a new narrative | Decision makers, collaborators, future maintainers | It justifies the direction but is not a task plan |
| North Star plan | How do we win and measure progress? | Converts strategy into a measurable system | Builders, maintainers, operators | It guides staged planning but is still above implementation tasks |

A white paper argues that a new direction is real and valuable. A North Star plan defines the long-term target, the key metric, input metrics, levers, and staged paths toward the target.

## 0. Cognitive Narrative Layer

Core question: Why does this thing exist?

Primary file:

- `whitepaper.md` is the white paper file; it explains industry trends, structural pain, why existing solutions fail, and the new paradigm.

Common contents:

- Future trend: what is likely to happen in the next several years.
- Core pain: what structural problem blocks users or operators.
- Existing-solution gap: why current tools or workflows are insufficient.
- New paradigm: what pattern or system changes the situation.
- Reasoning and evidence: what logic, data, or model supports the claim.

Decision output: the direction is worth understanding and discussing.

## 1. Business Layer

Core question: Is this worth doing?

Primary file:

- `brd.md` is the business requirements document; it explains business goals, revenue logic, cost structure, and return on investment.

Common contents:

- Business goal: what outcome the work should create.
- Revenue source: who pays and how value converts into income or saved cost.
- Market size: TAM, SAM, and SOM are market-sizing views for total market, serviceable market, and reachable market.
- Cost structure: development, operation, model, maintenance, compliance, and switching costs.
- CAC: customer acquisition cost; it estimates how much it costs to obtain one paying or active user.
- LTV: lifetime value; it estimates how much value one user creates over time.
- ROI: return on investment; it compares expected benefit with expected cost.

Decision output: do, do not do, or research more before deciding.

## 2. Market Layer

Core question: What do users actually need?

Primary file:

- `mrd.md` is the market requirements document; it turns market evidence and user needs into product direction.

Common contents:

- User segments: who the target users are.
- User scenarios: when and why they need the solution.
- Pain points: the real user problems behind feature requests.
- Competitor analysis: what alternatives exist and why they are insufficient.
- Entry strategy: which segment or use case should be served first.

Decision output: target users, target scenes, and market entry position.

## 3. Strategy And North Star Layer

Core question: How do we win?

Primary file:

- `north_star_plan.md` is the North Star plan; it defines the core metric, input metrics, growth or capability levers, and staged path.

Common contents:

- North Star metric: the one metric that best represents user value and long-term progress.
- Input metrics: leading indicators that drive the North Star metric.
- Levers: product, technology, process, distribution, or operational mechanisms that improve input metrics.
- Stage map: MVP, release train, and later phases.
- Boundaries: what the system will not do.

Decision output: measurable direction and prioritization logic.

## 4. Product Layer

Core question: What should the product be?

Primary file:

- `prd.md` is the product requirements document; it translates strategy into user-facing functions, flows, priorities, and acceptance criteria.

Common companion files:

- `user_journey.md` describes the end-to-end user journey; it shows what a user experiences before, during, and after using the product.
- `information_architecture.md` describes the information architecture; it shows how content, screens, and actions are organized.
- `prototype.fig` or another prototype file is the design prototype; it shows the intended interaction and layout in a design tool.

Decision output: what is in scope for the product and what is out of scope.

## 5. Technical Layer

Core question: How can it be implemented safely?

Primary files:

- `srs.md` is the system requirements specification; it defines system-level functional and non-functional requirements.
- `trd.md` is the technical requirements or technical design document; it explains the chosen technical solution and tradeoffs.
- `hld.md` is the high-level design; it defines major modules, trust boundaries, data flow, and integration points.
- `lld.md` is the low-level design; it defines concrete components, scripts, functions, schemas, and edge cases.
- `api_spec.md` is the API specification; it defines inputs, outputs, permissions, errors, and compatibility.
- `data_model.md` is the data model; it defines entities, fields, relationships, and persistence rules.

Decision output: the system can be built, tested, operated, and reviewed.

## 6. Execution Layer

Core question: How do we deliver it?

Primary files:

- `implementation_plan.md` is the implementation plan; it splits a chosen stage into executable work.
- `tasks.md` is the task list; it tracks concrete steps and completion state.
- `test_plan.md` is the test plan; it defines unit, integration, end-to-end, manual, and regression checks.
- `release_plan.md` is the release plan; it defines rollout timing, release gates, and communication.
- `rollback_plan.md` is the rollback plan; it defines how to return to a safe previous state.

Decision output: the work is ready to implement and release.

## 7. Growth And Adoption Layer

Core question: How does it become larger, more useful, or more adopted?

Primary files:

- `roadmap.md` is the product roadmap; it defines future versions and priority order.
- `growth_plan.md` is the growth plan; it defines acquisition, activation, retention, revenue, or adoption mechanisms.
- `metrics.md` is the metrics document; it defines DAU, MAU, retention, conversion, CAC, LTV, quality, or adoption metrics as appropriate.
- `adoption_report.md` is the adoption report; it records where the system is used and what friction remains.

Decision output: the system has a path to expand and improve.

## 8. Retrospective And Learning Layer

Core question: Did it work, and what should change?

Primary files:

- `post_mortem.md` is the incident or project retrospective; it records what happened, why it happened, impact, fix, and prevention.
- `ab_test_report.md` is the A/B test report; it compares variants and explains which one performed better.
- `feedback_summary.md` is the user feedback summary; it captures recurring user reactions and requests.
- `lessons_learned.md` is the lessons-learned document; it converts experience into reusable rules or future tasks.

Decision output: the next cycle starts with better evidence and fewer repeated mistakes.

## Minimum File Set By Project Size

Small internal tooling work usually needs a short North Star note, PRD, technical design, implementation plan, test plan, and retrospective. A public product, commercial product, or long-lived platform should add white paper, BRD, MRD, roadmap, metrics, and release governance.

The more a project affects money, users, trust, compliance, or long-term platform behavior, the more of this stack should be explicit.
