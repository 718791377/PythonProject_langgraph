# One-Person Company Inventory Map

This map is the concise canonical inventory for the downstream one-person-company operating-system target.

## Canonical Inventory

| Inventory element | Count | Canonical shape |
| --- | ---: | --- |
| Trunk layers | 12 | Cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, retrospective |
| Virtual departments | 5 | Strategy Office; Product and Market Office; Revenue and Growth Office; Operations Office; Governance Office |
| Responsibility domains | 30 | Six domains per department |
| Cross-cutting modules | 20 | Finance, operations, engineering, organization, legal, security, knowledge, risk, productivity, agent, data, trust, toolchain, SLA, asset, research, channel, exit, vendor, tax |
| Core documents | 60 | Ten document families |
| Governed AI agents | 15 | Strategy, Research, Product, UX and Copy, Engineering, QA, Data, Growth, Sales, Customer Success, Support, Finance, Legal and Risk, Knowledge, Chief of Staff |
| Recommended books | 15 | Strategy, product, growth, operating-system, and solo-business references |
| Minimal startup documents | 12 | The smallest operating set for launch |

## Source-Family Rationale

| Source family | Role in this map | Why it is authoritative here |
| --- | --- | --- |
| Fresh architecture-note extraction under `.omx/state/langgraph/extraction/` | Exact inventory counts and named structures | The local one-person-company architecture note defines the 12 layer, 5 department, 30 domain, 20 module, 60 document, 15 agent, 15 book, and 12 startup-document target |
| Business-management sources | Operating principles | They justify company-of-one scope discipline, product discovery, pricing clarity, traction loops, operating cadence, process design, and intentional systemization |
| PMP sources | Process-group operating gate | They supply the common gate model used to run planning, execution, control, and closeout across business work |
| Existing lifecycle docs in `docs_bilingual/product_lifecycle/` | Platform-to-project boundary alignment | They keep this target positioned as downstream business architecture, not as platform durable truth |

## 12 Trunk Layers

| # | Layer | Primary question | Primary owner surface |
| ---: | --- | --- | --- |
| 0 | Cognitive narrative | Why should the company exist | Company thesis and vision |
| 1 | Business | How does it earn and stay viable | Business model and finance model |
| 2 | Market | Which users and segments matter most | Market map and user segments |
| 3 | Strategy | What is the narrow win condition | Strategy and annual plan |
| 4 | Metrics | What evidence changes the next move | North Star, funnel, tracking |
| 5 | Product | What is being sold and delivered | Offer, PRD, service blueprint |
| 6 | Technical | Which automation and systems support delivery | Tech stack and automation map |
| 7 | Organization | How the founder, agents, and partners divide work | Role map and agent governance |
| 8 | Execution | How work gets done now | Quarterly plan and delivery plan |
| 9 | Growth | How demand compounds | Growth model and channel map |
| 10 | Operations | How fulfillment, support, and retention stay stable | Ops playbook and customer success |
| 11 | Retrospective | How learning updates the company system | Monthly review and learning log |

## 5 Departments and 30 Domains

### Strategy Office

1. Founder and CEO
2. Chief of staff
3. Business model owner
4. Finance owner
5. Risk owner
6. Personal operating-system owner

### Product and Market Office

7. Market intelligence
8. Customer research
9. Positioning owner
10. Product strategy owner
11. Offer owner
12. PRD and service-design owner

### Revenue and Growth Office

13. Analytics owner
14. Growth owner
15. Sales owner
16. Pricing owner
17. Content owner
18. Brand and trust owner

### Operations Office

19. Partnerships owner
20. Customer success owner
21. Support owner
22. Delivery owner
23. Community owner
24. Knowledge owner

### Governance Office

25. Automation owner
26. Security and privacy owner
27. Legal and compliance owner
28. Data governance owner
29. Asset and IP owner
30. Agent governance owner

## 20 Cross-Cutting Modules

| Module group | Modules |
| --- | --- |
| Core business control | Finance, operations, engineering management, organization design, legal and compliance, security, knowledge management |
| Durable execution control | Risk management, personal productivity, AI agent governance, data governance, brand trust, toolchain governance, SLA governance |
| Scale and boundary control | Asset and IP governance, user-research governance, channel governance, exit governance, vendor governance, tax and administration governance |

## 60 Core Documents

The fresh architecture note fixes the target at 60 core documents. This canonical map normalizes that target into ten six-document families so the count stays exact and operable.

| Document family | Count | Canonical documents |
| --- | ---: | --- |
| Company strategy | 6 | `company-thesis.md`, `vision.md`, `strategy.md`, `annual-plan.md`, `quarterly-plan.md`, `decision-log.md` |
| Business and finance | 6 | `business-model.md`, `offer.md`, `pricing.md`, `unit-economics.md`, `finance-model.md`, `cashflow.md` |
| Market and user | 6 | `market-map.md`, `user-segments.md`, `competitor-analysis.md`, `alternative-solutions.md`, `research-repository.md`, `interview-guide.md` |
| Product and service | 6 | `product-strategy.md`, `prd.md`, `service-blueprint.md`, `onboarding.md`, `customer-journey.md`, `roadmap.md` |
| Metrics and data | 6 | `metrics.yaml`, `north-star.md`, `funnel-dashboard.md`, `tracking-plan.md`, `data-dictionary.md`, `experiment-log.md` |
| Growth and sales | 6 | `growth-model.md`, `channel-map.md`, `sales-playbook.md`, `landing-page.md`, `email-sequences.md`, `content-calendar.md` |
| Operations and customer success | 6 | `ops-playbook.md`, `customer-success-playbook.md`, `support-policy.md`, `faq.md`, `refund-policy.md`, `feedback-triage.md` |
| Technology and automation | 6 | `tech-stack.md`, `automation-map.md`, `tool-stack.md`, `vendor-register.md`, `api-dependency-map.md`, `backup-restore.md` |
| Governance and risk | 6 | `legal-checklist.md`, `terms-of-service.md`, `privacy-policy.md`, `contract-template.md`, `risk-register.md`, `compliance-checklist.md` |
| Agent and knowledge | 6 | `agent-governance.md`, `agent-role-map.md`, `agent-permissions.md`, `human-review-checklist.md`, `monthly-review.md`, `learning-log.md` |

## 15 Governed AI Agents

| Agent | Main lane | Human gate |
| --- | --- | --- |
| Strategy Agent | Opportunity analysis and strategy drafting | Final strategic trade-off |
| Research Agent | User, market, and competitor research | Insight interpretation |
| Product Agent | PRD, roadmap, and service-design drafts | Scope and public promise |
| UX and Copy Agent | Landing page, onboarding, and message drafts | External publication |
| Engineering Agent | Product and automation implementation | Merge and release approval |
| QA Agent | Test and acceptance review | Release signoff |
| Data Agent | Metrics analysis and experiment review | Metric definition changes |
| Growth Agent | Channel tests and content experiments | Budgeted campaign launch |
| Sales Agent | Proposal and sales-asset drafting | Pricing and commitment |
| Customer Success Agent | Renewal, case, and lifecycle support drafts | Customer commitments |
| Support Agent | FAQ, reply drafts, and triage | Refunds and complaint decisions |
| Finance Agent | Cost, budget, and cashflow review | Payment and tax decisions |
| Legal and Risk Agent | Terms, license, and risk drafts | Contract and policy release |
| Knowledge Agent | SOP, review, and knowledge-base updates | Durable decision archive |
| Chief of Staff Agent | Weekly, monthly, and cadence summaries | Priority resets |

## 15 Recommended Books

1. Scaling People
2. Working Backwards
3. High Output Management
4. INSPIRED
5. Product Operations
6. Measure What Matters
7. Lean Analytics
8. The Lean Startup
9. Obviously Awesome
10. Traction
11. Deploy Empathy
12. Shape Up
13. Team Topologies
14. Company of One
15. The E-Myth Revisited

## 12 Minimal Startup Documents

1. `company-thesis.md` - states why the company exists and what belief it tests.
2. `business-model.md` - defines how the company creates, delivers, and captures value.
3. `offer.md` - describes the first paid or validated offer.
4. `pricing.md` - records the price logic, packaging, and discount boundaries.
5. `user-segments.md` - identifies the first target users and non-targets.
6. `growth-model.md` - explains the first demand and adoption loop.
7. `finance-model.md` - tracks costs, cashflow assumptions, and runway constraints.
8. `ops-playbook.md` - defines delivery, support, and operating cadence.
9. `metrics.yaml` - provides the machine-readable metric contract.
10. `risk-register.md` - records risks, triggers, responses, and owners.
11. `agent-governance.md` - defines AI-agent roles, permissions, and human review.
12. `monthly-review.md` - captures learning, decisions, and next-cycle updates.

## Process-Group Operating Gate

| Process group | Gate question | Required output for this inventory |
| --- | --- | --- |
| Initiating | Should a business line, document family, or agent surface exist | Customer problem, value case, owner, and scope boundary |
| Planning | How should it run this cycle | Success criteria, dependencies, cash and time constraints, risk response, and human-vs-agent boundary |
| Executing | What is being shipped or operated now | Draft artifact, active plan, customer-facing work, and validation evidence |
| Monitoring and Controlling | Is the company system still healthy | Metrics review, issue log, cash and support checks, customer feedback, and rollback or stop triggers |
| Closing | What becomes durable after the cycle | Updated policy or playbook, review artifact, archived decision, and next-cycle input |

## Use Rule

Use this map when a downstream business project needs a canonical operating-system target. Start from the 12 minimal startup documents, then expand into the 60-document system only when customer evidence, revenue exposure, delivery complexity, or governance risk makes the deeper layer necessary.
