# PMI Project Management Reference Map

This document maps PMI project-management references to this repository's lifecycle documents. It does not reproduce PMI book content. It summarizes how the references are tailored for Codex platform governance and downstream project use.

## Reference Boundary

- `PMP/` is the local private reference directory for PMI PDF files; it is ignored by Git and must not be committed.
- `PMBOK Guide` is used as a value, principles, tailoring, quality, and governance reference for project management.
- `Process Groups: A Practice Guide` is used as a delivery-gate reference for initiating, planning, executing, monitoring and controlling, and closing.
- `Agile Practice Guide` is used as an adaptive delivery reference for uncertainty, MVP slices, feedback loops, and hybrid work.

These references are an overlay. They do not replace white papers, BRD, MRD, North Star plans, PRD, technical design, implementation plans, OpenSpec, or repository checkers.

## Relationship To The 0-8 Lifecycle

| 0-8 layer | Product/business purpose | PMI overlay |
| --- | --- | --- |
| 0 Cognitive narrative | Explain why the direction exists | PMBOK value orientation helps keep the narrative tied to outcomes |
| 1 Business | Decide whether the work is worth doing | PMBOK success criteria and benefits thinking help define value |
| 2 Market | Identify users and needs | Agile discovery and feedback loops help reduce uncertainty |
| 3 Strategy | Define the North Star and levers | PMBOK tailoring helps choose governance depth by risk |
| 4 Product | Define product scope and behavior | Agile lifecycle selection helps decide predictive, adaptive, or hybrid planning |
| 5 Technical | Define implementation architecture | PMBOK quality, risk, and procurement ideas inform technical gates |
| 6 Execution | Deliver the work | Process Groups map directly to OpenSpec and GitLab-first delivery |
| 7 Growth | Expand adoption and usefulness | Agile inspection and adaptation support iterative adoption |
| 8 Retrospective | Learn and improve | Process closing and lessons learned become archive and governance updates |

## Process Groups To OpenSpec And GitLab Gates

| PMI process group | Codex platform delivery gate | Repository files and actions |
| --- | --- | --- |
| Initiating | Decide whether to open a change | `openspec/changes/<change-id>/proposal.md` is the OpenSpec proposal that states why a change is needed |
| Planning | Freeze design and execution scope | `openspec/changes/<change-id>/design.md` is the OpenSpec design; `tasks.md` is the task list used to track execution |
| Executing | Implement the planned work | Source, documentation, templates, or checker files are modified according to the accepted tasks |
| Monitoring and controlling | Verify and control change | `tools/run_openspec_guard.py` is the OpenSpec guard script; GitLab pipeline is the review-time CI gate |
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

- Discovery is still needed, but delivery must still pass OpenSpec, checker, and GitLab gates.
- A small spike should happen first, then a predictive delivery plan should be frozen.

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
