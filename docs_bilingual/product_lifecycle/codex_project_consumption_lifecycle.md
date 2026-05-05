# Downstream Project Consumption Lifecycle

This document applies to later projects that consume the Codex CLI durable-team platform. A downstream project may use shared user-level runtime, templates, subagent profiles, OpenSpec practices, and checkers, but it must own its own project truth.

## Non-Negotiable Boundary

A downstream project must not use `D:\PythonProject_langgraph\.omx/state/` as its durable truth. That path is the platform repository state directory. Each downstream project owns its own `.omx/state/` directory inside its own repository.

## 0. Cognitive Narrative Layer

Question: Why does this downstream project exist?

Recommended files:

- `README.md` is the project overview; it explains what this project is and how to start.
- `docs_bilingual/project_startup_summary.md` is the ASCII cold-start summary; it helps a new Codex session understand the project.
- `docs_bilingual/project_startup_summary.zh-CN.md` is the UTF-8 Chinese companion for the same startup summary.

Small-project rule: a separate white paper is optional unless the project needs external alignment, funding, public explanation, or long-lived strategic narrative.

## 1. Business Layer

Question: Is this downstream project worth doing?

Recommended files:

- `docs_bilingual/business/brd.md` is the project BRD; it explains business value, cost, user value, and return expectations for this project.
- `docs_bilingual/business/brd.zh-CN.md` is the UTF-8 Chinese companion for the project BRD.

Small-project rule: if there is no commercial decision, a short value note inside `README.md` may be enough.

## 2. Market And User Layer

Question: Who needs this project and in which scenes?

Recommended files:

- `docs_bilingual/market/mrd.md` is the project MRD; it explains target users, use scenes, pain points, and alternatives.
- `docs_bilingual/market/mrd.zh-CN.md` is the UTF-8 Chinese companion for the project MRD.
- `docs_bilingual/user_research/` is the user research directory; it can store interviews, observations, and feedback evidence.

Small-project rule: if the user is only the repository owner, a short scenario list can replace a full MRD.

## 3. Strategy And North Star Layer

Question: What does success mean for this project?

Recommended files:

- `docs_bilingual/north_star_plan.md` is the project North Star plan; it defines the main success metric, input metrics, and levers for this project.
- `docs_bilingual/north_star_plan.zh-CN.md` is the UTF-8 Chinese companion for the same plan.

Small-project rule: a project may use a one-page North Star note instead of a full strategic plan.

## 4. Product Layer

Question: What should this project build?

Recommended files:

- `docs_bilingual/prd.md` is the project PRD; it defines user stories, features, priorities, flows, and acceptance criteria.
- `docs_bilingual/prd.zh-CN.md` is the UTF-8 Chinese companion for the project PRD.
- `docs_bilingual/user_journey.md` is the user journey; it shows the user's end-to-end path.
- `docs_bilingual/user_journey.zh-CN.md` is the UTF-8 Chinese companion for the user journey.

Small-project rule: simple developer tools may place product scope directly in an OpenSpec proposal.

## 5. Technical Layer

Question: How should this downstream project implement its own system?

Recommended files:

- `docs_bilingual/technical/trd.md` is the project technical design; it explains technical choices, architecture, and tradeoffs.
- `docs_bilingual/technical/trd.zh-CN.md` is the UTF-8 Chinese companion for the technical design.
- `docs_bilingual/technical/api_spec.md` is the project API specification; it defines interface inputs, outputs, errors, and permissions when APIs exist.
- `docs_bilingual/technical/api_spec.zh-CN.md` is the UTF-8 Chinese companion for the API specification.
- `src/` is the project source directory; it contains business or application code owned by this project.
- `tests/` is the project test directory; it contains tests owned by this project.

Important separation:

- Codex platform `PySide6` is a local GUI control-center dependency for Codex tooling.
- A downstream project `PySide6` dependency is a business runtime dependency only if that project declares and owns it.
- The same separation applies to `SQLite`, `Redis`, `promptfoo`, and `jina-embeddings`; they are not automatically business dependencies just because the platform uses them.

## 6. Execution Layer

Question: How does this project deliver changes?

Recommended files:

- `openspec/config.yaml` is the project OpenSpec configuration; it binds OpenSpec workflow to this repository.
- `openspec/changes/<change-id>/proposal.md` is a project-local OpenSpec proposal; it explains why one project change is needed.
- `openspec/changes/<change-id>/design.md` is a project-local OpenSpec design; it explains how one project change will be implemented.
- `openspec/changes/<change-id>/tasks.md` is a project-local OpenSpec task list; it tracks project work.
- `openspec/changes/<change-id>/*.zh-CN.md` are UTF-8 Chinese companions for the same project change artifacts.

Codex platform usage:

- Use native `subagent` for bounded expert work inside the current Codex session.
- Use `native_omx` only when the project has a frozen plan and two or more mostly independent execution slices.
- Use `langgraph` only when the project needs graph phases, checkpoint recovery, approval gates, or survivor queues.

## 7. Release, Growth, And Adoption Layer

Question: How is this project released and improved over time?

Recommended files:

- `docs_bilingual/release_plan.md` is the release plan; it defines rollout, release gates, and communication.
- `docs_bilingual/release_plan.zh-CN.md` is the UTF-8 Chinese release plan companion.
- `docs_bilingual/rollback_plan.md` is the rollback plan; it defines how to return to a safe version.
- `docs_bilingual/rollback_plan.zh-CN.md` is the UTF-8 Chinese rollback plan companion.
- `CHANGELOG.md` is the project changelog; it records user-visible and operator-visible changes.
- `docs_bilingual/metrics.md` is the metrics document; it defines project success and quality metrics.
- `docs_bilingual/metrics.zh-CN.md` is the UTF-8 Chinese metrics companion.

Small-project rule: local-only projects may combine release and rollback notes until they have real users or automation.

## 8. Retrospective And Upstream Feedback Layer

Question: What should this project learn locally, and what should feed back to the platform?

Recommended files:

- `docs_bilingual/lessons_learned.md` is the project lessons-learned document; it records reusable local experience.
- `docs_bilingual/lessons_learned.zh-CN.md` is the UTF-8 Chinese lessons-learned companion.
- `docs_bilingual/upstream_feedback.md` is the platform feedback document; it records lessons that may improve `D:\PythonProject_langgraph`.
- `docs_bilingual/upstream_feedback.zh-CN.md` is the UTF-8 Chinese platform feedback companion.

Upstream rule: a downstream project lesson becomes a platform rule only after the platform repository accepts it through a platform OpenSpec change.

## Minimal Downstream Project Checklist

Every downstream project should have at least:

- `AGENTS.md` as the project-level Codex instruction file.
- `docs_bilingual/project_startup_summary.md` as the ASCII cold-start summary.
- `docs_bilingual/project_startup_summary.zh-CN.md` as the UTF-8 Chinese cold-start summary companion.
- `openspec/` as the project-local OpenSpec governance tree.
- `.omx/state/` as the project-local durable state directory when durable lanes are used.
- `.gitignore` as the project ignore file for caches, state, generated artifacts, and local secrets.

The platform may provide templates and helpers, but the project remains the owner of its own requirements, state, releases, and lessons.
