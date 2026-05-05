# Codex CLI Durable-Team Platform Build Lifecycle

This document applies to building the Codex CLI personal production durable-team platform in `D:\PythonProject_langgraph`, which is the Codex orchestration source repository. It does not describe how a downstream business project should manage its own product work.

The full 0-8 lifecycle is kept as a platform map. Individual MRs, MVP slices, and OpenSpec changes should tailor the depth of that map instead of expanding every layer by default.

## Scope

The platform-build lifecycle covers reusable user-level and repository-level orchestration capabilities:

- `subagent` is the native Codex expert delegation layer; it handles bounded read, design, review, implementation, and verification slices.
- `native_omx` is the worker-centric durable backend lane; it is used only after a plan is frozen and two or more mostly independent execution slices exist.
- `langgraph` is the graph checkpoint and approval-gate backend lane; it is used when graph phases, checkpoint recovery, interrupt gates, or survivor queues are required.
- `OpenSpec` is the repository governance workflow; it records durable proposals, designs, tasks, stable specs, and archives.
- `D:\PythonProject_General_2` is the local project template directory; it initializes later projects without turning them into platform implementation locations.

## Lifecycle Tailoring Overlay

Platform-build work uses three delivery styles:

- Predictive gates fit work with clear requirements, high rollback risk, checker behavior changes, launcher/runtime entrypoint changes, or release evidence requirements.
- Adaptive slices fit unclear work that needs discovery, a spike, an MVP, operator feedback, or a documentation experiment before freezing design.
- Hybrid delivery fits work that still needs discovery but must eventually pass OpenSpec, checker, GitLab pipeline, release, rollback, and retrospective gates.

This overlay is not a new lifecycle layer. It is a governance lens applied across the 0-8 platform-build lifecycle.

## Platform Lifecycle Depth Rule

Use these depth levels when planning platform changes:

- Full 0-8 lifecycle: use for North Star updates, major release train definitions, backend-family decisions, persistent-team architecture, native Codex compatibility changes, or user-level orchestration policy changes that can affect multiple projects.
- MVP or release slice: keep all 0-8 layers visible, but only summarize layers 0, 1, 2, and 7; expand layers 3, 4, 5, 6, and 8 because they define strategy, product behavior, technical contracts, delivery gates, and learning capture.
- Ordinary OpenSpec change or MR: do not rewrite the full 0-8 stack. Record the input, tools and techniques, and output evidence for the changed control surface. A code-bearing change must include technical-layer and execution-layer evidence before archive. A release-bearing change must include validation, release, rollback, and retrospective evidence.

The platform should not use full 0-8 documentation as a bureaucratic default. It should use the full map to prevent missing business value, user impact, native Codex compatibility, release safety, rollback, or long-term governance feedback.

## 0. Cognitive Narrative Layer

Question: Why should a personal developer have a production-grade durable team?

### Inputs

- Repeated single-session context loss, multi-session collision, and prompt-only governance failures.
- Downstream project needs for safe continuation, browser-capable development, local templates, and reproducible release gates.
- Operator expectations that native Codex remains the base layer and oh-my-codex remains additive.

### Tools And Techniques

- Narrative framing separates production infrastructure from a prompt collection.
- Failure-pattern analysis turns repeated session, context, and release failures into durable platform requirements.
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` is the canonical ASCII white paper; it explains why single-session chat is not enough for production work.
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md` is the UTF-8 Chinese companion; it carries the same argument for Chinese maintainers.

### Outputs

- A durable narrative explaining why this is a production infrastructure project, not a prompt collection.
- Explicit non-goals, including not replacing native Codex and not turning downstream projects into platform implementation repositories.
- Direction candidates for the business, market, and strategy layers.

## 1. Business Layer

Question: Is this platform worth maintaining?

### Inputs

- Narrative-layer justification for durable personal-development infrastructure.
- Maintenance costs for scripts, templates, checkers, skills, native subagents, and optional durable backends.
- Risk cost from context loss, dirty worktrees, failed release gates, unsafe rollback, and cross-project state leakage.

### Tools And Techniques

- Productivity and risk-reduction analysis estimates whether durable continuation saves more work than it adds.
- Cost analysis separates platform tooling costs from downstream business runtime costs.
- `docs_bilingual/business/codex_cli_durable_team_brd.md` is the future ASCII business requirements document; it should estimate productivity gain, maintenance cost, model cost, and risk reduction.
- `docs_bilingual/business/codex_cli_durable_team_brd.zh-CN.md` is the future UTF-8 Chinese companion for the same business decision.

### Outputs

- A decision on whether the platform justifies ongoing maintenance, release gates, templates, and local tooling.
- Cost and benefit assumptions that guide release depth and rollback expectations.
- Constraints for the strategy layer and product layer.

## 2. Market And User Layer

Question: Which developer workflows need the platform?

### Inputs

- Personal developer and small-team workflow pain points.
- Downstream project adoption needs from local Git, OpenSpec, browser automation, and native Codex subagents.
- Abstract workload examples that should become reusable capability profiles rather than one-off business names.

### Tools And Techniques

- User segmentation distinguishes platform maintainers, downstream project maintainers, operators, and occasional consumers.
- Capability profiling abstracts concrete work into reusable development capabilities.
- `docs_bilingual/market/codex_cli_durable_team_mrd.md` is the future ASCII market requirements document; it should describe user segments, pain points, and adoption scenes for personal developers and small teams.
- `docs_bilingual/market/codex_cli_durable_team_mrd.zh-CN.md` is the future UTF-8 Chinese companion for those market requirements.
- `docs_bilingual/references/codex_business_capability_mapping.md` is the ASCII abstract capability mapping; it maps concrete workload examples to abstract capability profiles.
- `docs_bilingual/references/codex_business_capability_mapping.zh-CN.md` is the UTF-8 Chinese companion for the same mapping.

### Outputs

- A stable set of abstract capability profiles rather than a list of one-off business names.
- User and adoption assumptions for the North Star plan.
- Capability gaps that feed the product and technical layers.

## 3. Strategy And North Star Layer

Question: What is the long-term target, and how is progress measured?

### Inputs

- Business-layer maintenance justification and cost boundaries.
- Market-layer workflow segments and capability profiles.
- Technical constraints from native Codex compatibility, user-level helpers, repo-local durable state, and local templates.

### Tools And Techniques

- North Star metric design focuses on safe cold-start continuation across sessions and projects.
- Release-train planning separates MVP, release slices, and long-term persistent-team targets.
- Backend-family selection keeps `subagent`, `native_omx`, and `langgraph` as distinct control surfaces.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` is the ASCII North Star plan; it defines the ten-layer framework, release train, and long-term durable-team target.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` is the UTF-8 Chinese companion and current main discussion surface for the same North Star plan.

### Outputs

- A measurable platform direction for durable team investments.
- Candidate North Star metric: cold-start continuation success rate, which is the rate at which a new Codex session can safely resume a project task with minimal repeated user explanation.
- Input metrics: OpenSpec guard pass rate, merge request pipeline pass rate, context-retention reload incidents, multi-session collision incidents, rollback success rate, and manual context-restatement count.
- Release scope and priority constraints for the product, technical, and execution layers.

## 4. Product Layer

Question: What control surfaces should the platform expose?

### Inputs

- Strategy-layer release targets, routing thresholds, and success metrics.
- User needs for startup recovery, role routing, status inspection, templates, and safe publication.
- Technical constraints from native Codex, user-level launchers, MCP scope, and repo-local state isolation.

### Tools And Techniques

- Control-surface design turns strategy into commands, startup behavior, role routing, state inspection, and template flows.
- Acceptance-criteria design converts operator workflows into checkable behavior.
- `docs_bilingual/product/codex_cli_durable_team_prd.md` is the future ASCII PRD; it should define user-facing commands, startup behavior, role routing, state inspection, release gates, and template update flows.
- `docs_bilingual/product/codex_cli_durable_team_prd.zh-CN.md` is the future UTF-8 Chinese companion for the PRD.
- `AGENTS.md` is the project-level Codex instruction surface; it tells Codex how this repository should be handled.
- `docs_bilingual/project_startup_summary.md` is the ASCII cold-start summary; it tells a new session how to recover context.
- `docs_bilingual/project_startup_summary.zh-CN.md` is the UTF-8 Chinese cold-start summary companion.

### Outputs

- Explicit operator workflows and acceptance criteria.
- Product-level boundaries for native Codex compatibility and additive orchestration.
- Inputs for the technical layer and execution layer.

## 5. Technical Layer

Question: How should the platform be implemented without breaking native Codex?

### Inputs

- Product-layer control surfaces and acceptance criteria.
- Strategy-layer backend-family boundaries for native subagents, native_omx, and LangGraph.
- External constraints from Windows shells, MCP servers, official LangGraph runtime, local model services, and Git repositories.

### Tools And Techniques

- Architecture boundary design separates user-level runtime, repo-local source, repo-local durable state, and downstream project state.
- Compatibility design preserves native Codex behavior before adding wrappers or helper layers.
- Checker-backed governance turns safety rules into scripts instead of prompt-only reminders.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` is the ASCII MCP scope policy; it decides which MCP servers belong in Codex direct config, MCP Router, or neither.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` is the UTF-8 Chinese MCP scope policy companion.
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.md` is the ASCII LangGraph runtime policy; it defines where official LangGraph runtime belongs.
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` is the UTF-8 Chinese LangGraph runtime policy companion.
- `tools/langgraph_durable_orchestrator/` is the repo-local LangGraph compatibility source directory; it is source code, not durable state.
- `.omx/state/langgraph/` is the repo-local LangGraph durable state directory; it must not be moved into the user-level shared runtime.

### Outputs

- Technical contracts and checker-backed boundaries.
- Source-of-truth decisions for user-level helpers, repo-local source, and repo-local durable truth.
- Implementation constraints for OpenSpec changes and GitLab-first delivery.

## 6. Execution Layer

Question: How are platform changes delivered safely?

### Inputs

- Product-layer acceptance criteria and technical-layer contracts.
- OpenSpec proposals, designs, tasks, stable specs, and archive status.
- GitLab-first publication rules and current session ownership claims.

### Tools And Techniques

- OpenSpec change control records proposal, design, tasks, specs, and archive evidence.
- GitLab-first delivery uses feature branches, merge requests, pipelines, and post-merge GitHub sync.
- Repository checkers validate bilingual documents, name clarity, session claims, safety rule backing, and OpenSpec health.
- `openspec/changes/<change-id>/proposal.md` is an ASCII OpenSpec proposal; it explains why a specific platform change is needed.
- `openspec/changes/<change-id>/design.md` is an ASCII OpenSpec design; it explains how the platform change will be implemented.
- `openspec/changes/<change-id>/tasks.md` is an ASCII OpenSpec task list; it tracks completion for that change.
- `openspec/changes/<change-id>/*.zh-CN.md` are UTF-8 Chinese companions for the same change artifacts.
- `tools/run_openspec_guard.py` is the OpenSpec guard script; it validates official refresh, repository rules, and clean-git expectations.

### Outputs

- Small GitLab-first MRs with explicit validation evidence.
- Completed or archived OpenSpec changes with stable-spec updates when required.
- Release, rollback, and verification evidence for platform-affecting changes.

## 7. Growth And Adoption Layer

Question: How does the platform expand across projects without sharing repo-local truth?

### Inputs

- Execution-layer releases, templates, helper scripts, and operator guidance.
- Downstream project needs for local Git, OpenSpec, native subagents, browser capability, and no shared repo-local truth.
- Template feedback from initialized projects.

### Tools And Techniques

- Template packaging separates new-PC bootstrap files, reusable project files, and project-local generated state.
- Adoption analysis tracks which capabilities are reused across projects without merging durable state.
- Template update policy defines how initialized projects receive later improvements.
- `D:\PythonProject_General_2\START_HERE.cmd` is the Windows double-click template launcher; it initializes or checks local projects.
- `D:\PythonProject_General_2\TEMPLATE_MANIFEST.md` is the template manifest; it explains which files belong to the local project template.
- `docs_bilingual/templates/template_update_policy.md` is the future ASCII template update policy; it should explain how initialized projects receive later template updates.
- `docs_bilingual/templates/template_update_policy.zh-CN.md` is the future UTF-8 Chinese companion for template update policy.

### Outputs

- Downstream projects can adopt the platform without becoming platform implementation repositories.
- Template update rules and adoption reports.
- Feedback to strategy, product, and technical layers when adoption friction appears.

## 8. Retrospective And Learning Layer

Question: What platform lessons should become rules, checkers, or templates?

### Inputs

- Execution-layer validation results, release outcomes, rollback outcomes, and incidents.
- Growth-layer adoption reports and downstream feedback.
- Session-collision, context-loss, MCP noise, wrapper, and toolchain failures observed during real work.

### Tools And Techniques

- Retrospective analysis turns repeated failures into governance rules.
- Checker design turns rules into script controls so new sessions do not depend only on prompt memory.
- Archive and memory updates capture durable context after major changes.
- `docs_bilingual/memory/mainline_memory_summary.md` is the ASCII mainline memory summary; it captures durable context after major changes.
- `docs_bilingual/memory/mainline_memory_summary.zh-CN.md` is the UTF-8 Chinese memory summary companion.
- `docs_bilingual/governance/` is the governance directory; it stores rules that should outlive a single conversation.
- `tools/check_*.py` scripts are checker files; they enforce governance rules without relying only on prompts.

### Outputs

- Repeated failures become scripts, policy, OpenSpec specs, or template updates.
- Lessons learned for future release slicing and routing policy.
- Updates to startup summaries, governance documents, and checkers when needed.

## Release Slicing Rule

One platform MR should usually change one layer or one control surface. Good examples are: add one lifecycle reference, add one checker, archive one OpenSpec change, refine one release gate, or update one template rule.
