---
doc_id: personal_production_one_person_company_operations_whitepaper
lang: en
canonical: docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md
translation_of: null
doc_class: whitepaper
status: draft
---

# White Paper: Personal Production One-Person Company Operations

## Purpose

This white paper explains why a solo operator needs a personal production one-person-company operating system, and how that system should stay useful without turning every small business move into enterprise bureaucracy.

It is a downstream business operating-system white paper. It does not replace the Codex CLI personal production durable-team white paper, and it does not move downstream customer, revenue, finance, legal, support, or operations truth into this platform repository.

## Fresh Source Evidence For This Refresh

This refresh is grounded in a new local extraction run named `one-person-company-pmi-refresh-stageb-20260619` generated at `2026-06-18T18:37:58Z`. The run read the ignored local `Business Management/` and `PMP/` source roots by PDF page, EPUB spine item, and Markdown full document, then wrote local ignored evidence under `.omx/state/langgraph/extraction/business_pmp_20260619/`.

The run covered 54 sources: 31 Business Management sources and 23 PMP sources. Format coverage was 31 PDFs / 9,280 pages, 9 EPUBs / 362 spine items, and 14 Markdown full-text files. All 54 sources completed with `ok` status, for 9,656 read units and 18,492,044 extracted characters. A separate tracked-lifecycle Markdown fresh read, `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619`, read 26 `docs_bilingual/product_lifecycle/` Markdown documents as full documents for 310,349 characters, all with `ok` status.

Tracked documents may cite aggregate counts, source-family names, and repository-specific synthesis only. Raw extraction text remains ignored local evidence and must not be copied into tracked documentation.

## Why This Operating System Exists

A one-person company can look small from the outside while still carrying serious operating complexity: customer discovery, positioning, pricing, delivery, support, cashflow, risk, automation, legal boundaries, and learning loops. The goal is not to imitate a large company. The goal is to keep the solo operator able to make clear decisions while AI agents and automation increase throughput.

The operating system therefore has three design constraints:

- Keep the smallest viable company surface visible.
- Expand only the layers touched by customer, revenue, trust, compliance, support, delivery, or automation risk.
- Keep final accountability with the human owner, even when governed AI agents draft, inspect, analyze, or execute parts of the work.

## Canonical Inventory

The target inventory is fixed by `one_person_company_inventory_map.md`:

| Element | Count | Meaning |
| --- | ---: | --- |
| Trunk layers | 12 | Cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, retrospective |
| Virtual departments | 5 | Strategy Office, Product and Market Office, Revenue and Growth Office, Operations Office, Governance Office |
| Responsibility domains | 30 | Six domains per virtual department |
| Cross-cutting modules | 20 | Shared controls for finance, operations, engineering, organization, legal, security, knowledge, risk, productivity, agents, data, trust, toolchain, SLA, assets, research, channels, exit, vendors, and tax |
| Core documents | 60 | Ten document families with six documents each |
| Governed AI agents | 15 | Role-bounded assistants with explicit human-review gates |
| Recommended books | 15 | Strategy, product, growth, operations, organization, and one-person-company references |
| Minimal startup documents | 12 | The smallest launch set for a real operating loop |

## Dedicated North Star

The one-person-company North Star is a separate document at `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md`. Its primary metric is validated operating-loop throughput: the number of business loops that start from customer or operating evidence, pass the required human and governance gates, produce a shipped or validated business output, and feed learning back into the next cycle within the review period.

This North Star is not the Codex durable-team platform North Star. The platform North Star measures orchestration capability. The one-person-company North Star measures downstream business learning and delivery.

## The 12-Layer Operating Model

Each layer has a primary question and an I/T/O contract. I/T/O means Inputs, Tools and Techniques, and Outputs.

| # | Layer | Primary question | Inputs | Tools and Techniques | Outputs |
| ---: | --- | --- | --- | --- | --- |
| 0 | Cognitive narrative | Why should this company exist? | Founder belief, customer pain, personal constraints, market signal | Thesis writing, PR/FAQ thinking, strategy diagnosis, stop-condition framing | `company-thesis.md`, vision statement, explicit non-goals |
| 1 | Business | How does the company earn and stay viable? | Offer hypothesis, cost base, pricing signal, cash runway | Business-model mapping, unit-economics review, cashflow modeling, scenario checks | `business-model.md`, `finance-model.md`, `cashflow.md` |
| 2 | Market | Which users and segments matter first? | User interviews, alternative solutions, channel observations, competitor evidence | Segmentation, positioning, competitor analysis, interview synthesis | `market-map.md`, `user-segments.md`, research repository |
| 3 | Strategy | What is the narrow win condition? | Narrative, business model, market evidence, capacity constraints | Good-strategy diagnosis, annual/quarterly planning, trade-off review, decision logging | `strategy.md`, `annual-plan.md`, `quarterly-plan.md` |
| 4 | Metrics | What evidence changes the next move? | North Star candidate, funnel events, financial limits, support signals | OMTM selection, OKR review, tracking-plan design, guardrail definition | `north-star.md`, `metrics.yaml`, funnel dashboard, experiment log |
| 5 | Product | What is sold and delivered? | Customer jobs, offer promise, constraints, acceptance evidence | Product discovery, PRD writing, service-blueprint design, MVP slicing | `offer.md`, `prd.md`, service blueprint, roadmap |
| 6 | Technical | Which systems and automation support delivery? | Product promise, data needs, security constraints, support load | Architecture review, automation mapping, vendor review, backup/restore planning | `tech-stack.md`, `automation-map.md`, dependency map, recovery notes |
| 7 | Organization | How do the founder, agents, and partners divide work? | Role load, agent candidates, vendor boundaries, review needs | Responsibility mapping, agent-governance design, permission review, human-review gates | role map, `agent-governance.md`, permissions, review checklist |
| 8 | Execution | How does current work get shipped? | Approved cycle plan, capacity, risks, dependencies, validation plan | Process-group planning, work slicing, Kanban or cycle planning, acceptance review | delivery plan, committed work, validation evidence, release candidate |
| 9 | Growth | How does demand compound? | Segment evidence, channel signal, content assets, conversion data | Traction-channel testing, growth-loop design, sales-playbook iteration, pricing review | `growth-model.md`, channel map, sales playbook, content calendar |
| 10 | Operations | How do delivery, support, and retention stay stable? | Customer commitments, support tickets, fulfillment constraints, SLA needs | Ops-playbook design, customer-success review, support triage, refund-policy review | `ops-playbook.md`, customer-success playbook, support policy, FAQ |
| 11 | Retrospective | How does learning update the company? | Metrics, decisions, incidents, customer feedback, finance/support evidence | Monthly review, decision archive, lessons-learned synthesis, next-cycle prioritization | `monthly-review.md`, learning log, updated policies, next-cycle inputs |

## Five Virtual Departments And Thirty Domains

The virtual departments are not headcount. They are accountability lenses for a solo operator.

| Department | Six domains |
| --- | --- |
| Strategy Office | Founder and CEO; Chief of Staff; business model owner; finance owner; risk owner; personal operating-system owner |
| Product and Market Office | Market intelligence; customer research; positioning owner; product strategy owner; offer owner; PRD and service-design owner |
| Revenue and Growth Office | Analytics owner; growth owner; sales owner; pricing owner; content owner; brand and trust owner |
| Operations Office | Partnerships owner; customer success owner; support owner; delivery owner; community owner; knowledge owner |
| Governance Office | Automation owner; security and privacy owner; legal and compliance owner; data-governance owner; asset and IP owner; agent-governance owner |

## Twenty Cross-Cutting Modules

Cross-cutting modules prevent local decisions from becoming hidden risk. They are activated only when the affected work needs them.

| Module group | Modules |
| --- | --- |
| Core business controls | Finance, operations, engineering management, organization design, legal and compliance, security, knowledge management |
| Durable execution controls | Risk management, personal productivity, AI-agent governance, data governance, brand trust, toolchain governance, SLA governance |
| Boundary and scale controls | Asset and IP governance, user-research governance, channel governance, exit governance, vendor governance, tax and administration governance |

## Sixty Core Documents

The full document system has ten families. A one-person company starts from the minimal startup set and expands only when evidence justifies deeper coverage.

| Family | Documents |
| --- | --- |
| Company strategy | `company-thesis.md`, `vision.md`, `strategy.md`, `annual-plan.md`, `quarterly-plan.md`, `decision-log.md` |
| Business and finance | `business-model.md`, `offer.md`, `pricing.md`, `unit-economics.md`, `finance-model.md`, `cashflow.md` |
| Market and users | `market-map.md`, `user-segments.md`, `competitor-analysis.md`, `alternative-solutions.md`, `research-repository.md`, `interview-guide.md` |
| Product and service | `product-strategy.md`, `prd.md`, `service-blueprint.md`, `onboarding.md`, `customer-journey.md`, `roadmap.md` |
| Metrics and data | `metrics.yaml`, `north-star.md`, `funnel-dashboard.md`, `tracking-plan.md`, `data-dictionary.md`, `experiment-log.md` |
| Growth and sales | `growth-model.md`, `channel-map.md`, `sales-playbook.md`, `landing-page.md`, `email-sequences.md`, `content-calendar.md` |
| Operations and customer success | `ops-playbook.md`, `customer-success-playbook.md`, `support-policy.md`, `faq.md`, `refund-policy.md`, `feedback-triage.md` |
| Technical and automation | `tech-stack.md`, `automation-map.md`, `tool-stack.md`, `vendor-register.md`, `api-dependency-map.md`, `backup-restore.md` |
| Governance and risk | `legal-checklist.md`, `terms-of-service.md`, `privacy-policy.md`, `contract-template.md`, `risk-register.md`, `compliance-checklist.md` |
| Agents and knowledge | `agent-governance.md`, `agent-role-map.md`, `agent-permissions.md`, `human-review-checklist.md`, `monthly-review.md`, `learning-log.md` |

## Twelve Minimal Startup Documents

The startup set is intentionally smaller than the full system:

1. `company-thesis.md` - states why the company exists and what belief it tests.
2. `business-model.md` - explains how the company creates, delivers, and captures value.
3. `offer.md` - defines the first paid or validated promise.
4. `pricing.md` - records packaging, price logic, and discount boundaries.
5. `user-segments.md` - identifies first target users and explicit non-targets.
6. `growth-model.md` - explains the first demand and adoption loop.
7. `finance-model.md` - tracks cost, runway, cashflow, and viability assumptions.
8. `ops-playbook.md` - defines fulfillment, support, and operating cadence.
9. `metrics.yaml` - keeps the machine-readable metric contract.
10. `risk-register.md` - records risks, triggers, responses, and owners.
11. `agent-governance.md` - defines AI-agent roles, permissions, and human review.
12. `monthly-review.md` - captures learning, decisions, and next-cycle updates.

These documents are enough to express why the company exists, what it sells, who it serves, how it grows, how it stays financially alive, how it delivers, how it measures progress, what risks are controlled, how AI agents are governed, and how learning updates the system.

## Fifteen Governed AI Agents

Agents expand capacity, not authority.

| Agent | Primary channel | Human review gate |
| --- | --- | --- |
| Strategy Agent | Opportunity analysis and strategy drafts | Final strategic choice |
| Research Agent | User, market, and competitor research | Insight interpretation |
| Product Agent | PRD, roadmap, and service-design drafts | Scope and external promise |
| UX and Copy Agent | Landing pages, onboarding, and copy drafts | Public release |
| Engineering Agent | Product and automation implementation support | Merge and release approval |
| QA Agent | Test and acceptance review | Release sign-off |
| Data Agent | Metrics analysis and experiment review | Metric-definition changes |
| Growth Agent | Channel tests and content experiments | Paid or budgeted launch |
| Sales Agent | Proposals and sales-material drafts | Pricing and commitments |
| Customer Success Agent | Renewal, case, and lifecycle-support drafts | Customer promise |
| Support Agent | FAQ, reply drafts, and issue triage | Refund and complaint decisions |
| Finance Agent | Cost, budget, and cashflow review | Payment and tax decisions |
| Legal and Risk Agent | Terms, license, and risk drafts | Contract and policy publication |
| Knowledge Agent | SOP, retrospective, and knowledge-base updates | Persistent decision archive |
| Chief of Staff Agent | Weekly reports, monthly summaries, and cadence review | Priority reset |

## Recommended Reading Set

The reading set is a practical reference base, not a certification list:

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

## PMI Process-Group Operating Model

Execution work should be written in process-group form whenever it affects customers, revenue, trust, support, compliance, delivery commitments, release safety, or governed automation.

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Customer problem, value case, candidate business line, active document family, agent surface, cash and time boundary | Customer-evidence review, owner mapping, revenue and risk framing, scope boundary, stop-condition framing | Problem statement, value case, accountable owner, scope boundary, initial risk or stop condition |
| Planning | Initiating outputs, capacity, dependencies, cash/time limits, support load, human-vs-agent boundary | Cycle planning, offer and segment review, risk response planning, validation planning, budget/runway check, human-review design | Success criteria, dependency map, cash/time constraints, risk response, validation plan, human-review gate |
| Executing | Approved cycle plan, customer evidence, operating templates, agent rules, validation plan | Shipping, selling, supporting, interviewing, measuring, controlled AI drafting and checking | Draft or shipped artifact, active customer-facing work, validation evidence, issue log |
| Monitoring and Controlling | Metrics, issue log, cash/support signals, customer feedback, risk triggers | Metric review, cash check, support review, feedback synthesis, change control, rollback or stop decision | Metric review, updated issue log, cash/support check, customer feedback synthesis, rollback/stop trigger |
| Closing | Cycle outputs, decisions, finance/support evidence, lessons learned | Monthly review, policy or playbook update, archive, next-cycle prioritization | Updated policy or playbook, retrospective artifact, archived decision, next-cycle input |

## Tailoring Rules

A one-person company should not default to the full 60-document system. Tailoring has five explicit outcomes:

| Tailoring outcome | Use when | Required minimum |
| --- | --- | --- |
| Full architecture for affected scope | New product, major business pivot, customer-visible release, payment, compliance, sensitive data, trust impact, repeated delivery, support obligation, external commitment, or broad agent automation | All affected layers show I/T/O, risks, owners, validation, and retrospective path |
| Whole-project lightweight | Private, reversible, low-risk work with no external users, no money, no sensitive data, no support promise, no shared runtime, and no release commitment | Minimal startup documents plus explicit stop condition |
| Phase-local lightweight | Discovery, prototype, interview, or content exploration is low risk inside a larger governed project | Keep lightweight treatment inside the phase; expand before customer, revenue, trust, or release impact |
| Module-level lightweight | One bounded module is reversible and does not change the whole operating model | Module I/T/O, owner, validation, rollback path |
| Hybrid | Discovery is uncertain, but final delivery may affect production, users, trust, revenue, compliance, runtime behavior, or release safety | Lightweight discovery followed by full controls for affected delivery layers |

The default is local lightness, not global informality. Start small, then expand the exact layer, phase, or module that carries risk. Expand the whole project only when coupling becomes systemic.

## Relationship To The Codex CLI Durable-Team White Paper

The Codex CLI durable-team white paper describes the platform that helps a solo maintainer coordinate native Codex, expert bursts, durable lanes, LangGraph, OpenSpec, worktrees, release safety, and repo-local durable state.

This white paper describes the downstream business operating system that may consume such platform capability. The two documents should cross-link but remain separate:

- Platform white paper: owns developer-orchestration narrative and runtime boundary.
- One-person-company white paper: owns downstream business-operating narrative and company system boundary.
- Inventory maps: own exact counts.
- Lifecycle and PMI maps: own process grammar and tailoring authority.

Do not merge these documents unless one becomes a thin duplicate with no independent audience, no separate update trigger, and no unique downstream references.

## Non-Goals

- Do not require all 60 documents before first validated offer.
- Do not let AI agents make final pricing, legal, release, customer, or finance commitments.
- Do not move downstream customer evidence, revenue facts, legal facts, support facts, or durable state into the platform repository.
- Do not treat the platform repository as the operating truth of a future business project.
