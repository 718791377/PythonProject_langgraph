# Codex CLI Durable-Team Platform Build Lifecycle

This document applies to building the Codex CLI personal production durable-team platform in `D:\PythonProject_langgraph`, which is the Codex orchestration source repository. It does not describe how a downstream business project should manage its own product work.

## Scope

The platform-build lifecycle covers reusable user-level and repository-level orchestration capabilities:

- `subagent` is the native Codex expert delegation layer; it handles bounded read, design, review, implementation, and verification slices.
- `native_omx` is the worker-centric durable backend lane; it is used only after a plan is frozen and two or more mostly independent execution slices exist.
- `langgraph` is the graph checkpoint and approval-gate backend lane; it is used when graph phases, checkpoint recovery, interrupt gates, or survivor queues are required.
- `OpenSpec` is the repository governance workflow; it records durable proposals, designs, tasks, stable specs, and archives.
- `D:\PythonProject_General_2` is the local project template directory; it initializes later projects without turning them into platform implementation locations.

## 0. Cognitive Narrative Layer

Question: Why should a personal developer have a production-grade durable team?

Platform files:

- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` is the future ASCII white paper; it should explain why single-session chat is not enough for production work.
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md` is the future UTF-8 Chinese companion; it should carry the same argument for Chinese maintainers.

Platform output: a durable narrative explaining why this is a production infrastructure project, not a prompt collection.

## 1. Business Layer

Question: Is this platform worth maintaining?

Platform files:

- `docs_bilingual/business/codex_cli_durable_team_brd.md` is the future ASCII business requirements document; it should estimate productivity gain, maintenance cost, model cost, and risk reduction.
- `docs_bilingual/business/codex_cli_durable_team_brd.zh-CN.md` is the future UTF-8 Chinese companion for the same business decision.

Platform output: a decision on whether the platform justifies ongoing maintenance, release gates, templates, and local tooling.

## 2. Market And User Layer

Question: Which developer workflows need the platform?

Platform files:

- `docs_bilingual/market/codex_cli_durable_team_mrd.md` is the future ASCII market requirements document; it should describe user segments, pain points, and adoption scenes for personal developers and small teams.
- `docs_bilingual/market/codex_cli_durable_team_mrd.zh-CN.md` is the future UTF-8 Chinese companion for those market requirements.
- `docs_bilingual/references/codex_business_capability_mapping.md` is the ASCII abstract capability mapping; it maps concrete workload examples to abstract capability profiles.
- `docs_bilingual/references/codex_business_capability_mapping.zh-CN.md` is the UTF-8 Chinese companion for the same mapping.

Platform output: a stable set of abstract capability profiles rather than a list of one-off business names.

## 3. Strategy And North Star Layer

Question: What is the long-term target, and how is progress measured?

Platform files:

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` is the ASCII North Star plan; it defines the ten-layer framework, release train, and long-term durable-team target.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` is the UTF-8 Chinese companion and current main discussion surface for the same North Star plan.

Candidate North Star metric:

- Cold-start continuation success rate is the rate at which a new Codex session can safely resume a project task with minimal repeated user explanation.

Input metrics:

- OpenSpec guard pass rate.
- Merge request pipeline pass rate.
- Context-retention reload incidents.
- Multi-session collision incidents.
- Rollback success rate.
- Manual context-restatement count.

Platform output: measurable direction for platform investments.

## 4. Product Layer

Question: What control surfaces should the platform expose?

Platform files:

- `docs_bilingual/product/codex_cli_durable_team_prd.md` is the future ASCII PRD; it should define user-facing commands, startup behavior, role routing, state inspection, release gates, and template update flows.
- `docs_bilingual/product/codex_cli_durable_team_prd.zh-CN.md` is the future UTF-8 Chinese companion for the PRD.
- `AGENTS.md` is the project-level Codex instruction surface; it tells Codex how this repository should be handled.
- `docs_bilingual/project_startup_summary.md` is the ASCII cold-start summary; it tells a new session how to recover context.
- `docs_bilingual/project_startup_summary.zh-CN.md` is the UTF-8 Chinese cold-start summary companion.

Platform output: explicit operator workflows and acceptance criteria.

## 5. Technical Layer

Question: How should the platform be implemented without breaking native Codex?

Platform files:

- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` is the ASCII MCP scope policy; it decides which MCP servers belong in Codex direct config, MCP Router, or neither.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` is the UTF-8 Chinese MCP scope policy companion.
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.md` is the ASCII LangGraph runtime policy; it defines where official LangGraph runtime belongs.
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` is the UTF-8 Chinese LangGraph runtime policy companion.
- `tools/langgraph_durable_orchestrator/` is the repo-local LangGraph compatibility source directory; it is source code, not durable state.
- `.omx/state/langgraph/` is the repo-local LangGraph durable state directory; it must not be moved into the user-level shared runtime.

Platform output: technical contracts and checker-backed boundaries.

## 6. Execution Layer

Question: How are platform changes delivered safely?

Platform files:

- `openspec/changes/<change-id>/proposal.md` is an ASCII OpenSpec proposal; it explains why a specific platform change is needed.
- `openspec/changes/<change-id>/design.md` is an ASCII OpenSpec design; it explains how the platform change will be implemented.
- `openspec/changes/<change-id>/tasks.md` is an ASCII OpenSpec task list; it tracks completion for that change.
- `openspec/changes/<change-id>/*.zh-CN.md` are UTF-8 Chinese companions for the same change artifacts.
- `tools/run_openspec_guard.py` is the OpenSpec guard script; it validates official refresh, repository rules, and clean-git expectations.

Platform output: small GitLab-first MRs with explicit validation evidence.

## 7. Growth And Adoption Layer

Question: How does the platform expand across projects without sharing repo-local truth?

Platform files:

- `D:\PythonProject_General_2\START_HERE.cmd` is the Windows double-click template launcher; it initializes or checks local projects.
- `D:\PythonProject_General_2\TEMPLATE_MANIFEST.md` is the template manifest; it explains which files belong to the local project template.
- `docs_bilingual/templates/template_update_policy.md` is the future ASCII template update policy; it should explain how initialized projects receive later template updates.
- `docs_bilingual/templates/template_update_policy.zh-CN.md` is the future UTF-8 Chinese companion for template update policy.

Platform output: downstream projects can adopt the platform without becoming platform implementation repositories.

## 8. Retrospective And Learning Layer

Question: What platform lessons should become rules, checkers, or templates?

Platform files:

- `docs_bilingual/memory/mainline_memory_summary.md` is the ASCII mainline memory summary; it captures durable context after major changes.
- `docs_bilingual/memory/mainline_memory_summary.zh-CN.md` is the UTF-8 Chinese memory summary companion.
- `docs_bilingual/governance/` is the governance directory; it stores rules that should outlive a single conversation.
- `tools/check_*.py` scripts are checker files; they enforce governance rules without relying only on prompts.

Platform output: repeated failures become scripts, policy, OpenSpec specs, or template updates.

## Release Slicing Rule

One platform MR should usually change one layer or one control surface. Good examples are: add one lifecycle reference, add one checker, archive one OpenSpec change, refine one release gate, or update one template rule.
