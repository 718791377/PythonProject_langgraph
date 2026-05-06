# Downstream Project Consumption Lifecycle

This document describes how later projects consume the Codex CLI durable-team platform. A downstream project may use the user-level runtime, native Codex subagents, templates, governance ideas, and optional durable lanes, but it owns its own repository facts and business work.

## Non-Negotiable Boundary

`D:\PythonProject_langgraph` is the platform source repository; it owns the Codex orchestration line, templates, shared policies, and helper source.

A downstream project owns its own product scope, business artifacts, OpenSpec tree, Git history, durable state, release state, and local lessons learned. A downstream project must not treat the platform repository as its repo-local durable truth.

## Downstream Lifecycle Tailoring Overlay

Downstream projects should use the general 0-8 lifecycle as a map, not as mandatory paperwork for every change.

- Predictive gates fit downstream work with clear scope, release risk, money/user/trust impact, compliance impact, or explicit rollback needs.
- Adaptive slices fit downstream work that needs exploration, prototypes, browser validation, user feedback, or small MVPs before design is frozen.
- Hybrid delivery fits downstream work that still needs discovery but must eventually pass local OpenSpec, tests, release, rollback, and retrospective checks.

## Downstream Lifecycle Depth Rule

Use these depth levels in downstream projects:

- Full 0-8 lifecycle: use for new products, major business pivots, user-facing releases, compliance-sensitive changes, payment or trust-impacting work, or long-lived platform-like downstream systems.
- Project MVP or release slice: keep all 0-8 layers visible, summarize layers 0, 1, 2, and 7 when risk is low, and expand layers 3, 4, 5, 6, and 8 for strategy, product behavior, technical safety, delivery, and learning.
- Ordinary local change: do not rewrite the full stack. Record the input, tools and techniques, and output evidence for the changed scope. Code-bearing changes need technical and execution evidence. Release-bearing changes need validation, release, rollback, and retrospective evidence.

A downstream project may be lightweight, but it must stay repo-local: its OpenSpec artifacts, `.omx/state/` state directory, release facts, and lessons learned belong to that project.

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
- Feedback loops use prototypes, browser checks, or small MVPs to reduce uncertainty.
- `docs_bilingual/market/mrd.md` is the project MRD; it explains target users, usage scenes, pain points, and alternatives.
- `docs_bilingual/market/mrd.zh-CN.md` is the UTF-8 Chinese companion for the project MRD.
- `docs_bilingual/user_research/` is the user research directory; it can store interviews, observations, and feedback evidence.

### Outputs

- Project MRD, target users, target scenarios, and priority signals.
- User evidence for product requirements and strategy.
- Feedback on whether the platform template lacks a reusable capability.

## 3. Strategy And North Star Layer

Question: How does the downstream project define success?

### Inputs

- Business-layer success criteria and cost boundaries.
- Market-layer user segments, scenarios, and demand evidence.
- Platform boundaries that separate project-local truth from shared platform runtime.

### Tools And Techniques

- North Star metric design defines the main success measure for the project.
- Input metric decomposition identifies leading indicators that drive the project North Star metric.
- Delivery-depth tailoring decides whether the project needs full 0-8, MVP/release depth, or a small local change path.
- `docs_bilingual/north_star_plan.md` is the project North Star plan; it defines the main success metric, input metrics, and levers.
- `docs_bilingual/north_star_plan.zh-CN.md` is the UTF-8 Chinese companion for the same plan.

### Outputs

- Project North Star plan, input metrics, levers, and non-goals.
- Delivery-depth decision for the current project phase.
- Prioritization constraints for product, technical, and execution layers.

## 4. Product Layer

Question: What should the downstream project build or change?

### Inputs

- Strategy-layer priorities, North Star metric, non-goals, and phase boundary.
- Market-layer user scenarios and pain points.
- Technical-layer feasibility, dependency, and safety constraints.

### Tools And Techniques

- PRD writing converts strategy and user evidence into scope, workflows, priorities, and acceptance criteria.
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

## 5. Technical Layer

Question: How can the downstream project be implemented safely without confusing platform tooling with business runtime?

### Inputs

- Product-layer scope, acceptance criteria, and user flows.
- Project-local source code, tests, dependencies, deployment constraints, and data constraints.
- Platform-provided guidance for native Codex subagents, OpenSpec, optional durable lanes, and local template checks.

### Tools And Techniques

- Technical design separates project business runtime from Codex platform tooling.
- Dependency classification decides whether a package belongs to the project business runtime or only to Codex tooling.
- Architecture and API design define modules, data, interfaces, trust boundaries, and compatibility.
- `docs_bilingual/technical/trd.md` is the project technical design; it explains technical choices, architecture, and tradeoffs.
- `docs_bilingual/technical/trd.zh-CN.md` is the UTF-8 Chinese companion for the technical design.
- `docs_bilingual/technical/api_spec.md` is the project API specification; when APIs exist, it defines interface inputs, outputs, errors, and permissions.
- `docs_bilingual/technical/api_spec.zh-CN.md` is the UTF-8 Chinese companion for the API specification.
- `src/` is the project source directory; it contains business or application code owned by the project.
- `tests/` is the project test directory; it contains tests owned by the project.
- Codex platform `PySide6` is a local GUI control-center dependency for Codex tooling. Downstream project `PySide6` is a business runtime dependency only when that project declares and owns it.
- The same separation applies to `SQLite`, `Redis`, `promptfoo`, and `jina-embeddings`; platform use does not automatically make them business dependencies.

### Outputs

- Project technical design, API specification, dependency classification, and test boundary.
- Evidence that platform tooling does not pollute business runtime dependencies.
- Implementation constraints for local OpenSpec changes and Codex subagent tasks.

## 6. Execution Layer

Question: How does the downstream project deliver changes safely?

### Inputs

- Product-layer scope and acceptance criteria.
- Technical-layer design, dependency classification, and test requirements.
- Project-local OpenSpec tree, Git state, branch policy, and release expectations.

### Tools And Techniques

- Local OpenSpec change control records why a project change is needed, how it is designed, and which tasks complete it.
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
- Local OpenSpec evidence, test evidence, and Git evidence.
- Release-ready artifacts or a clear reason to stop, revise, or roll back.

## 7. Release, Growth, And Adoption Layer

Question: How is the downstream project released, adopted, and improved?

### Inputs

- Execution-layer release-ready artifacts, validation evidence, and known risks.
- Strategy-layer success metrics and growth levers.
- User feedback, adoption friction, and deployment constraints.

### Tools And Techniques

- Release planning defines rollout, release gates, communication, and rollback readiness.
- Metrics tracking measures project success and quality.
- Changelog and adoption reporting record user-visible or operator-visible changes.
- `docs_bilingual/release_plan.md` is the release plan; it defines rollout, release gates, and communication.
- `docs_bilingual/release_plan.zh-CN.md` is the UTF-8 Chinese companion for the release plan.
- `docs_bilingual/rollback_plan.md` is the rollback plan; it defines how to return to a safe version.
- `docs_bilingual/rollback_plan.zh-CN.md` is the UTF-8 Chinese companion for the rollback plan.
- `CHANGELOG.md` is the project changelog; it records user-visible and operator-visible changes.
- `docs_bilingual/metrics.md` is the metrics document; it defines project success and quality metrics.
- `docs_bilingual/metrics.zh-CN.md` is the UTF-8 Chinese companion for the metrics document.

### Outputs

- Released project version, changelog, rollback evidence, and metrics evidence.
- Adoption or growth findings for the next project iteration.
- Feedback to product and strategy layers when user-visible behavior changes.

## 8. Retrospective And Upstream Feedback Layer

Question: What did the downstream project learn, and what should be fed back upstream?

### Inputs

- Execution-layer delivery records, test results, defects, and release outcomes.
- Release-layer metrics, adoption reports, rollback results, and user feedback.
- Observed gaps in templates, startup summaries, Codex subagent use, or optional durable-lane rules.

### Tools And Techniques

- Retrospective analysis turns project experience into reusable local lessons.
- Upstream feedback separates platform improvement ideas from project-local facts.
- Archive discipline keeps project OpenSpec, durable state, and release state local to the project.
- `docs_bilingual/lessons_learned.md` is the project lessons-learned document; it records locally reusable experience.
- `docs_bilingual/lessons_learned.zh-CN.md` is the UTF-8 Chinese companion for the lessons-learned document.
- `docs_bilingual/upstream_feedback.md` is the platform feedback document; it records experience that may improve `D:\PythonProject_langgraph`.
- `docs_bilingual/upstream_feedback.zh-CN.md` is the UTF-8 Chinese companion for the platform feedback document.

### Outputs

- Local lessons learned, upstream feedback candidates, and follow-up tasks.
- Clear separation between project-local truth and platform improvement requests.
- Inputs for future template updates, governance updates, or project iterations.

## Minimal Downstream Project Checklist

Small downstream projects can start with the minimum local surfaces:

- `AGENTS.md` as the project-level Codex instruction file.
- `docs_bilingual/project_startup_summary.md` as the ASCII cold-start summary.
- `docs_bilingual/project_startup_summary.zh-CN.md` as the UTF-8 Chinese cold-start summary companion.
- `openspec/` as the project-local OpenSpec governance tree.
- `.omx/state/` as the project-local durable state directory; it is needed only when durable lanes are used.
- `.gitignore` as the project ignore file; it ignores caches, state, generated artifacts, and local secrets.
