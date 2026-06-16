# PMI Project Management Reference Map

This document maps PMI project-management references to this repository's lifecycle documents. It does not reproduce PMI book content. It summarizes how the references are tailored for Codex platform governance and downstream project use.

## Reference Boundary

- `PMP/` is the local private reference directory for PMI PDFs, EPUBs, and Markdown notes; it is ignored by Git and must not be committed.
- `PMBOK Guide` is used as a value, principles, tailoring, quality, and governance reference for project management.
- `Process Groups: A Practice Guide` is used as a delivery-gate reference for initiating, planning, executing, monitoring and controlling, and closing.
- `Agile Practice Guide` is used as an adaptive delivery reference for uncertainty, MVP slices, feedback loops, and hybrid work.

These references are an overlay. They do not replace white papers, BRD, MRD, North Star plans, PRD, technical design, implementation plans, OpenSpec, or repository checkers. The same boundary applies to the `Business Management/` source library: product and management sources inform repository-specific lifecycle tailoring, but the repository records synthesized operating rules only.

## Local PMP Source Coverage

The local `PMP/` directory was read from local files only for this refresh. The fresh extraction evidence was regenerated at `2026-06-15T17:33:52Z` under `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260616/` and recorded 23 PMP-family sources: 9 PDFs / 3,035 pages, 2 EPUBs / 58 spine items, and 12 Markdown full-text notes, for 3,105 total PMP read units and 4,330,816 extracted characters. The tracked repository records the following coverage summary and synthesized governance mapping only.

| Local reference | Format | Coverage | Primary governance use |
| --- | --- | ---: | --- |
| `PMBOK Guide 8th Edition .pdf` | PDF | 401 pages | Primary value, performance-domain, AI-era, tailoring, and governance overlay |
| `PMBOK 7th Edition` Chinese PDF | PDF | 369 pages | Principles, value delivery, systems thinking, tailoring, and performance domains |
| `PMBOK 6th Edition` Chinese PDF | PDF | 812 pages plus low-text-page review | Inputs / Tools and Techniques / Outputs vocabulary and knowledge-area supplement |
| `Process groups _ a practice guide.pdf` | PDF | 390 pages | Initiating, Planning, Executing, Monitoring and Controlling, Closing delivery gate model |
| Chinese `ProcessGroupsPracticeGuide` PDF | PDF | 409 pages plus low-text-page review | Chinese companion for process-group delivery gates |
| `The Agile practice guide.pdf` | PDF | 188 pages | Adaptive, MVP, feedback-loop, and hybrid delivery guidance |
| Chinese Agile Practice Guide PDF | PDF | 184 pages plus low-text-page review | Chinese companion for adaptive and hybrid delivery |
| `The Standard for Program Management - Fifth Edition.epub` | EPUB | 16 spine items | Program-level alignment across multiple related initiatives |
| `The Standard for Portfolio Management-Fourth Edition.pdf` | PDF | 140 pages | Portfolio selection, prioritization, capacity, and value-balance overlay |
| Chinese portfolio-management standard PDF | PDF | 142 pages plus low-text-page review | Chinese companion for portfolio governance |
| `Project Management Offices a Practice Guide.epub` | EPUB | 42 spine items | PMO function, governance service, enablement, and oversight pattern |
| `PMP_MD/*.md` | Markdown | 12 local articles | PMBOK 8 and AI-era interpretation notes for local synthesis |

## Official PMI Web Freshness Check

This refresh also checked PMI public standards pages on 2026-06-16 to avoid treating the private local folder as the only freshness signal. The local extraction remains the content evidence boundary; the public check records current catalog metadata only.

| PMI public source | Official catalog status checked on 2026-06-16 | Repository decision |
| --- | --- | --- |
| <https://www.pmi.org/standards/pmbok> | `PMBOK Guide` is listed as the Eighth Edition, 408 pages, publication date November 2025, with second-printing errata dated 22 December 2025. | Treat PMBOK 8 as the current primary project-management overlay; keep PMBOK 7 and PMBOK 6 as continuity and I/T/O supplements. |
| <https://www.pmi.org/standards/process-groups> | `Process Groups: A Practice Guide` is listed as 370 pages, publication date November 2022, and describes five process groups plus 49 processes with inputs, tools and techniques, and outputs. | Use it as the execution-facing process-group grammar for lifecycle layers and delivery gates. |
| <https://www.pmi.org/standards/agile> | `Agile Practice Guide` is listed as 210 pages, publication date October 2017, with third- and fourth-printing errata. | Keep it as the agile/adaptive supplement until a newer official agile guide is added locally and freshly extracted. |
| <https://www.pmi.org/standards/program-management-fifth-edition> | `The Standard for Program Management - Fifth Edition` is listed as a PMI Standard, 247 pages, publication date March 2024. | Treat the local Fifth Edition EPUB as current for program-level coordination. |
| <https://www.pmi.org/standards/for-portfolio-management> | `The Standard for Portfolio Management - Fourth Edition` is listed as a PMI Standard, 189 pages, publication date November 2017. | Keep portfolio governance as prioritization, capacity, and value-balance overlay. |
| <https://www.pmi.org/standards/pmo> | `Project Management Offices: A Practice Guide` is listed as a PMI Practice Guide, 331 pages, publication date February 2025. | Use it as the PMO governance-services and enablement overlay, especially when several initiatives need shared standards or oversight. |

Official catalog page counts may differ from extracted local page counts because local source package, front matter, print/export format, or EPUB spine boundaries differ. When they differ, use local extraction for proof that the local source was read and PMI public pages for current catalog metadata.

## Document-Type PMI Tailoring Matrix

Use PMI overlays differently by document type. Do not repeat every PMI edition in every document; choose the minimum authority needed for the decision being made.

| Repository document or layer | Primary PMI overlay | Older-version or companion use | Stop condition |
| --- | --- | --- | --- |
| White paper | PMBOK 8 value, governance, tailoring, and AI-era framing; Process Groups only as high-level delivery discipline | Do not expand PMBOK 6 I/T/O details in the narrative unless a platform boundary depends on them | Stop at strategic framing and link to lifecycle/PMI maps for execution detail |
| Research note | Runtime/governance evidence first; PMI only when translating capability findings into governed execution | PMBOK 6 can clarify I/T/O vocabulary; PMBOK 7 can clarify principles; mark official source vs repository-derived inference | Stop when the point becomes product narrative or lifecycle count authority |
| Lifecycle layer documents | Process Groups as execution grammar; PMBOK 8 as value/tailoring overlay | PMBOK 6 supports detailed Inputs / Tools and Techniques / Outputs; translations support terminology only | Stop expanding older editions once the layer has clear I/T/O and control gates |
| North Star plan | PMBOK 8 and PMBOK 7 value/performance thinking; portfolio thinking only for capacity and value trade-offs | Process Groups appear only as operating cadence and evidence gates | Stop before turning metrics strategy into a full project-management manual |
| Tailoring rules | PMBOK 8 tailoring, Agile adaptive/hybrid guidance, and Process Groups gates | PMBOK 6 I/T/O grammar and older editions clarify execution wording | Stop when the selected tailoring outcome and escalation triggers are explicit |
| OpenSpec / implementation plans | Process Groups plus repository local-main-first gates | PMBOK 6 I/T/O wording may be used for plan sections; PMO/program/portfolio only when coordination scope requires it | Stop when proposal, design, tasks, verification, rollback, and archive evidence are sufficient |
| Downstream one-person-company documents | PMBOK 8 value/tailoring and Agile feedback loops | PMO/program/portfolio overlays apply only when several initiatives, governance services, or capacity trade-offs exist | Stop before importing enterprise governance into a single low-risk owner workflow |

## Older-Version Expansion Rule

Older PMI versions and companion translations should be expanded only when they add a concrete execution benefit: I/T/O vocabulary, knowledge-area continuity, translation clarity, or historical comparison. When PMBOK 8 already covers the governance point and the document is not defining execution grammar, cite PMBOK 8 plus the current lifecycle authority instead of listing PMBOK 6, PMBOK 7, and PMBOK 8 side by side.

## Agile, Program, Portfolio, And PMO Entry/Exit Rules

- Agile guidance enters when uncertainty, feedback loops, MVP slices, or hybrid planning are needed; it does not override PMBOK 8 as the primary governance overlay.
- Program governance enters when multiple related initiatives need coordinated benefits, dependencies, or roadmap alignment.
- Portfolio governance enters when competing initiatives require value, capacity, risk, or investment trade-offs.
- PMO practice enters when a shared governance service, standard, enablement function, or oversight pattern is needed.
- A single repository, single maintainer, single release slice, and low-risk local workflow should not import program, portfolio, or PMO ceremony by default.
- Exit the heavier overlay when the coordination concern is closed and the remaining work is a bounded project, phase, or module with clear owner and rollback evidence.

## Latest-Primary Authority Rule

Use the latest official or most readable reference present in the local `PMP/` source set as the primary authority for its knowledge family. Older versions and companion translations are used only to clarify vocabulary, historical continuity, translation, and process detail.

| Knowledge family | Primary for this refresh | Supplemental or historical use |
| --- | --- | --- |
| Project management body of knowledge | `PMBOK Guide 8th Edition .pdf` | PMBOK 7 supports principles and value-delivery continuity; PMBOK 6 supports process vocabulary and I/T/O structure |
| Process-group execution grammar | `Process groups _ a practice guide.pdf` | Chinese ProcessGroups PDF is a companion reference when extracted text is readable enough for terminology checks |
| Agile and hybrid delivery | English `The Agile practice guide.pdf` in this local source set | Chinese Agile PDF is companion-only because the extraction audit records very low text; update this rule only after a newer official guide is added locally and freshly extracted |
| Program governance | `The Standard for Program Management - Fifth Edition.epub` | Earlier program-management concepts should be treated as historical continuity only if added later |
| Portfolio governance | `The Standard for Portfolio Management-Fourth Edition.pdf` in this local source set | Chinese portfolio PDF is companion-only because the extraction audit records very low text |
| PMO governance services | `Project Management Offices a Practice Guide.epub` | Earlier PMO practice material is supplemental only if added later |

Low-text companion PDFs are never treated as the primary authority for this repository. When a public PMI catalog or local source set changes, add the newer source to `PMP/`, rerun page/spine/full-text extraction, and update this map before changing lifecycle rules.

## Process-Group Operating Overlay For Every Layer

When a lifecycle layer affects execution, write it in the same process-group discipline:

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Purpose, value hypothesis, authorization, stakeholder signal, scope boundary, initial risks | Charter-like framing, stakeholder identification, problem framing, value-case check | Decision that the layer or change should exist, named owner, scope boundary, initial risk log |
| Planning | Approved purpose, upstream layer outputs, constraints, tailored governance depth, risk log | Decomposition, acceptance criteria, validation design, release/rollback planning, owner mapping, communication planning | Work plan, I/T/O checklist, acceptance criteria, validation path, release/rollback boundary, communications plan |
| Executing | Approved plan, source evidence, templates, worktree/ownership state, agent boundaries | Drafting, implementation, reviews, tests, controlled agent delegation, documentation updates | Drafts, code, tests, templates, docs, agent work products, review comments, controlled implementation artifacts |
| Monitoring and Controlling | Active work products, metrics, issues, review feedback, local gate output, CI evidence | Quality checks, change control, variance review, risk response, diff review, gate reruns | Issue log, change decisions, metric checks, local-gate evidence, CI evidence, acceptance deltas, rollback readiness |
| Closing | Accepted work, final evidence, archive candidates, lessons, residual risks | Closeout review, archive/sync, release note update, retrospective, next-cycle triage | Final artifact, OpenSpec archive or project closeout, stable-spec/doc sync, lessons learned, next-cycle inputs |

## PMBOK 8 Primary Overlay

Use PMBOK 8th Edition as the primary project-management overlay for this repository. The primary overlay means the reference used to frame value delivery, project-canvas alignment, performance domains, AI-era project governance, hybrid delivery, and tailoring. It does not replace the repository's own document stack.

Supplemental overlays have narrower roles:

- `PMBOK 6th Edition` is the process and knowledge-area supplement; it helps translate lifecycle layers into inputs, tools and techniques, outputs, and control gates.
- `Process Groups: A Practice Guide` is the delivery-gate supplement; it maps initiating, planning, executing, monitoring and controlling, and closing to OpenSpec and local-main-first work.
- `PMBOK 7th Edition` is the principles and value-delivery supplement; it bridges principles, performance domains, system thinking, and tailoring.
- `Agile Practice Guide` is the adaptive and hybrid delivery supplement; it informs MVP slices, feedback loops, iteration, and reversible releases.

The repository should use these sources as structure, not as copied text. The local reading audit may record which local files were readable, but lifecycle documents should contain repository-specific mappings only.

## Relationship To The 0-11 / 12-Layer Lifecycle

| 0-11 layer | Product/business purpose | PMI overlay |
| --- | --- | --- |
| 0 Cognitive narrative | Explain why the direction exists | PMBOK value orientation helps keep the narrative tied to outcomes |
| 1 Business | Decide whether the work is worth doing | Success criteria and benefits thinking help define value |
| 2 Market | Identify users and needs | Agile discovery and feedback loops help reduce uncertainty |
| 3 Strategy | Define how to win and what to refuse | Tailoring helps choose governance depth by risk |
| 4 Metrics | Define evidence and decision thresholds | Measurement and performance-domain thinking keep progress inspectable |
| 5 Product | Define product scope and behavior | Agile lifecycle selection helps decide predictive, adaptive, or hybrid planning |
| 6 Technical | Define implementation architecture | Quality, risk, procurement, and stakeholder constraints inform technical gates |
| 7 Organization | Define owners, roles, and approvals | Stakeholder, resource, and governance domains clarify responsibility |
| 8 Execution | Deliver the work | Process Groups map directly to OpenSpec and local-main-first delivery |
| 9 Growth | Expand adoption and usefulness | Agile inspection and adaptation support iterative adoption |
| 10 Operations | Keep released work supportable | Quality, risk, issue, and change-control practices support live operation |
| 11 Retrospective | Learn and improve | Process closing and lessons learned become archive and governance updates |

## Project Canvas And Performance-Domain Mapping

A `project_canvas.md` file is a lightweight project canvas. It aligns purpose, value, stakeholders, boundaries, risks, delivery style, and outcome checks before a team expands the full lifecycle stack.

For this repository, PMBOK 8th Edition performance-domain thinking maps to these governance concerns:

| Performance concern | Repository mapping |
| --- | --- |
| Governance | User authority, OpenSpec changes, local-main-first review, release consent, and checker-backed safety rules |
| Scope | Platform repository boundaries, downstream project boundaries, and non-goals |
| Schedule | Release slices, current mainline, phase gates, and closeout timing |
| Finance | GitLab runner minutes, provider pacing budget, local model cost, operator attention, and maintenance time |
| Stakeholders | User/operator, main Codex leader session, subagents, durable workers, downstream project maintainers, and reviewers |
| Resources | Worktrees, wrappers, user-level helpers, local models, MCP tools, and repo-local state directories |
| Risk | Cross-session collision, stale main, state leakage, lane mis-selection, hidden automation, and rollback failure |

## Process Groups To OpenSpec And Local-Main-First Gates

| PMI process group | Codex platform delivery gate | Repository files and actions |
| --- | --- | --- |
| Initiating | Decide whether to open a change | `openspec/changes/<change-id>/proposal.md` is the OpenSpec proposal that states why a change is needed |
| Planning | Freeze design and execution scope | `openspec/changes/<change-id>/design.md` is the OpenSpec design; `tasks.md` is the task list used to track execution |
| Executing | Implement the planned work | Source, documentation, templates, or checker files are modified according to the accepted tasks |
| Monitoring and controlling | Verify and control change | `tools/run_openspec_guard.py` is the OpenSpec guard script; `tools/ci/local_gate.ps1` and `tools/ci/local_mr_review.ps1` are the local review gates; GitLab pipeline is later clean-environment confirmation when used |
| Closing | Archive and learn | `openspec archive` is the archive command that moves completed changes into `openspec/changes/archive/` and syncs stable specs |

## Predictive, Adaptive, And Hybrid Use

Use a predictive-style gate when:

- Requirements are clear.
- Risk is high enough to require explicit release or rollback evidence.
- The change modifies governance, templates, runtime entrypoints, or checker behavior.

Use an adaptive-style slice when:

- Requirements are unclear.
- User or operator feedback is needed before locking the design.
- The safest next step is a spike, MVP, or small documentation experiment.

Use a hybrid approach when:

- Discovery is still needed, but delivery must still pass OpenSpec, checker, and local-main-first gates.
- A small spike should happen first, then a predictive delivery plan should be frozen.

Use `lifecycle_tailoring_rules.md` as the decision record for whether predictive, adaptive, or hybrid work uses the full architecture, whole-project lightweight architecture, phase-local lightweight architecture, or module-level lightweight architecture. The tailoring decision itself should state Inputs, Tools and Techniques, and Outputs before execution starts.

Program, portfolio, and PMO-style oversight become relevant when multiple related initiatives, shared capacity, cross-project value trade-offs, or governance services are involved. In that case, do not mark the entire project lightweight; keep the program or portfolio decision surface explicit and lighten only bounded modules or phases when their risk permits.

## Codex Execution Mode Mapping

| Work condition | Recommended Codex mode | Why |
| --- | --- | --- |
| Single clear slice | Main session or one native `subagent` | Keeps execution lightweight |
| Bounded multi-face research | Multiple analyst `subagent` calls first | Keeps research homogeneous before escalating to architecture or planning |
| Frozen plan with two or more independent slices | `native_omx` durable team | Uses worker-centric durable execution only when the threshold is met |
| Checkpoints, approval gates, survivor queues, or graph phases | `langgraph` backend lane | Uses graph-shaped recovery only when the task needs it |

## Minimal Project Governance Files

Downstream projects do not need the full platform stack by default. They should add project-management files when risk or complexity requires them:

- `project_charter.md` is the project charter; it states objectives, scope, success criteria, and key stakeholders.
- `risk_register.md` is the risk register; it tracks risks, impact, probability, response, and owner.
- `issue_log.md` is the issue log; it records active blockers and resolution status.
- `release_plan.md` is the release plan; it defines rollout, release gates, and communication.
- `rollback_plan.md` is the rollback plan; it defines how to return to a known safe state.
- `lessons_learned.md` is the lessons-learned document; it records reusable experience after delivery or incidents.

Small local projects may combine these files, but high-risk projects should keep them explicit.

## Platform Rule

The Codex platform repository may define shared lifecycle references, templates, checkers, and role policies. It must not become the repo-local durable truth for downstream projects. Downstream projects own their own OpenSpec tree, durable state, release state, and lessons learned.
