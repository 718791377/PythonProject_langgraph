# Design

## Placement

The change adds a new `docs_bilingual/product_lifecycle/` directory. This directory is the product and platform lifecycle reference area for durable planning concepts that are broader than a single implementation plan.

The directory contains three document pairs:

- `product_business_document_lifecycle.md` is the ASCII main reference for the 0-8 product and business document stages.
- `product_business_document_lifecycle.zh-CN.md` is the UTF-8 Chinese companion for the same 0-8 stages.
- `codex_durable_team_platform_build_lifecycle.md` is the ASCII main reference for building the Codex CLI durable-team platform itself.
- `codex_durable_team_platform_build_lifecycle.zh-CN.md` is the UTF-8 Chinese companion for platform-build stages.
- `codex_project_consumption_lifecycle.md` is the ASCII main reference for later projects that consume the platform.
- `codex_project_consumption_lifecycle.zh-CN.md` is the UTF-8 Chinese companion for project-consumption stages.

## Boundary Model

The platform-build lifecycle and project-consumption lifecycle must stay separate.

Platform-build documentation belongs to `D:\PythonProject_langgraph`, which is the Codex orchestration source repository. It may define reusable rules, templates, checkers, OpenSpec governance, subagent profiles, durable backend policies, release gates, and shared tooling.

Project-consumption documentation belongs to each later project repository. It may use shared user-level runtime and templates, but it owns its own `AGENTS.md`, its own `docs_bilingual/project_startup_summary.md`, its own `openspec/` tree, and its own `.omx/state/` durable truth.

## Stage Model

The general 0-8 model remains product neutral:

0. Cognitive narrative layer.
1. Business decision layer.
2. Market demand layer.
3. Strategy and North Star layer.
4. Product definition layer.
5. Technical design layer.
6. Execution and delivery layer.
7. Growth and adoption layer.
8. Review and learning layer.

The Codex platform-build reference maps each stage to platform documents. The project-consumption reference maps the same stage logic to downstream projects while explicitly stating which documents are optional for small projects.

## Validation

The change is documentation only. Validation uses OpenSpec and repository documentation checkers rather than runtime tests.
