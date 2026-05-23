# Codex CLI Durable-Team Platform Build Lifecycle

This document applies to building the Codex CLI personal production durable-team platform in `D:\PythonProject_langgraph`, which is the Codex orchestration source repository. It does not describe how a downstream business project should manage its own product work.

The full 0-11 / 12-layer lifecycle is kept as the authoritative platform map: cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, and retrospective. Individual MRs, MVP slices, and OpenSpec changes should tailor the depth of that map instead of expanding every layer by default.

Use `business_management_source_synthesis.md` as the source-library overlay for this platform lifecycle. It reinforces that the Codex platform is a one-person operating system: diagnose before building, keep mechanisms small, shape work before execution, measure outcomes, protect architecture and trust boundaries, define human and agent ownership explicitly, keep operations supportable, and turn repeated lessons into checkers or templates.

## Scope

The platform-build lifecycle covers reusable user-level and repository-level orchestration capabilities:

- `subagent` is the native Codex expert delegation layer; it handles bounded read, design, review, implementation, and verification slices.
- `native_omx` is the worker-centric durable backend lane; it is used only after a plan is frozen and two or more mostly independent execution slices exist.
- `langgraph` is the graph checkpoint and approval-gate backend lane; it is used when graph phases, checkpoint recovery, interrupt gates, or survivor queues are required.
- `OpenSpec` is the repository governance workflow; it records durable proposals, designs, tasks, stable specs, and archives.
- `D:\PythonProject_General` is the local project template directory; it initializes later projects without turning them into platform implementation locations.
- `D:\PythonProject_General_2` is the project template directory for other new computers where OMX, LangGraph features, and the Codex environment have not yet been developed or configured; it initializes later projects without turning them into platform implementation locations, while preserving interface compatibility for future upgrades to OMX, LangGraph, and the Codex CLI personal production-grade durable team platform.

## Lifecycle Tailoring Overlay

Platform-build work uses three delivery styles:

- Predictive gates fit work with clear requirements, high rollback risk, checker behavior changes, launcher/runtime entrypoint changes, or release evidence requirements.
- Adaptive slices fit unclear work that needs discovery, a spike, an MVP, operator feedback, or a documentation experiment before freezing design.
- Hybrid delivery fits work that still needs discovery but must eventually pass OpenSpec, checker, local-main-first publication, release, rollback, and retrospective gates.

This overlay is not a new lifecycle layer. It is a governance lens applied across the 0-11 platform-build lifecycle.

## Platform Value Outcomes

Platform work must track value outcomes, not only delivered files. The platform is successful when it reduces operator friction while preserving native Codex compatibility and repo-local truth.

Use these outcome checks across platform release slices:

- Operator friction reduction: the operator can understand status, next action, and rollback path faster than before.
- Cold-start continuation success: a new session can recover the required context from startup summaries, OpenSpec, and project files.
- Cross-session coordination quality: concurrent sessions can identify ownership and avoid path collisions.
- Repo-local state safety: each project keeps its own durable truth and release facts.
- Native Codex compatibility: raw native Codex remains available and recoverable.
- Rollback evidence: release slices that affect launchers, wrappers, or runtime behavior have a known safe rollback path.

## AI-Era Role Boundary

AI may accelerate research, draft generation, candidate planning, state summarization, and verification support. AI must not become the hidden approval authority.

The human operator and the current main Codex leader session keep responsibility for value judgment, risk trade-offs, approval gates, release timing, and rollback decisions. Durable lanes and automation are execution aids that must remain inspectable and consent-bounded.

## Platform Lifecycle Depth Rule

Use these depth levels when planning platform changes:

- Full 0-11 lifecycle: use for white paper or thesis updates, business-model decisions, MRD updates, strategy changes, metrics contracts, PRD/control-surface changes, architecture decisions, organization or agent-governance changes, delivery-system changes, adoption/template changes, support/operations changes, or retrospective-driven governance updates that can affect multiple projects.
- MVP or release slice: keep all 12 layers visible, but expand only the layers touched by the risk. A code-bearing platform slice normally expands strategy, metrics, product, technical, organization, execution, operations, and retrospective evidence; a template or adoption slice also expands growth evidence.
- Ordinary OpenSpec change or MR: do not rewrite the full 12-layer stack. Record the input, tools and techniques, and output evidence for the changed control surface. A code-bearing change must include technical-layer, organization-layer, execution-layer, operations-layer, and retrospective evidence before archive. A release-bearing change must include validation, release, rollback, support, and learning evidence.

The platform should not use full lifecycle documentation as a bureaucratic default. It should use the full map to prevent missing business value, user impact, measurable outcomes, native Codex compatibility, ownership boundaries, release safety, operations supportability, rollback, or long-term governance feedback.

Use `lifecycle_tailoring_rules.md` before classifying a platform change as lightweight. For this repository, changes that affect reusable orchestration behavior, native subagent routing, `native_omx`, LangGraph, worktree safety, OpenSpec governance, user-level launcher policy, skill/profile governance, local-main-first publication, or shared templates require full architecture coverage for the affected scope. A bounded documentation-only appendix or local helper may be module-level lightweight only when it does not change runtime entrypoints, durable state, secrets, CI gates, release gates, or downstream project dependencies.

## Codex Target Inventory Rule

The Codex CLI platform target is fixed as:

- 12 trunk layers: cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, retrospective.
- 4 virtual departments: Strategy & Product Office; Engineering & Platform Office; Agent Governance Office; Growth & Knowledge Office.
- 24 responsibility domains: CEO/strategy, chief of staff, business model, finance, market intelligence, customer research, product strategy, PM/PRD, CLI/UX, metrics, architecture, engineering management, code quality, DevOps, platform/toolchain, security, privacy/data protection, data governance, agent governance, agent evaluation, docs, support, brand/trust, knowledge/review.
- 18 cross-cutting modules: finance, operations, engineering management, organization design, legal/compliance, security, knowledge management, risk management, personal productivity, AI agent governance, data governance, brand trust, toolchain governance, SLA governance, asset/IP governance, user-research governance, channel governance, exit governance.
- 48 core documents across strategy/business, market/product, metrics/data, engineering/platform, security/risk, agent governance, growth/operations, and retrospective/knowledge.
- 12 governed AI agents: Research, PM, Architect, Code, Review, Test, Security, DevOps, Data, Docs, Ops, and Risk.
- 12 recommended books: Scaling People; Working Backwards; High Output Management; INSPIRED; Product Operations; Team Topologies; Accelerate; Shape Up; Lean Analytics; Designing Data-Intensive Applications; Secure by Design; The Staff Engineer's Path.

The canonical count map is `codex_platform_inventory_map.md`. Use that map for concrete document-family, agent, module, and department references; use this lifecycle file for process-group execution guidance across the 12 layers.

Every non-trivial platform release slice must state which layer, department, responsibility domain, cross-cutting module, core document, and governed-agent boundary it changes. When a slice changes execution behavior, it must also state Inputs, Tools and Techniques, and Outputs for the affected gate.


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
- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md` is the current MRD; it describes target users, capability profiles, runtime-owner boundaries, and adoption/risk scenes for personal developers and downstream projects.
- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.zh-CN.md` is the current Chinese companion for those market requirements.
- The abstract capability mapping now lives in Appendix A of the MRD rather than a separate reference file.
- The Chinese capability mapping also lives in the Chinese MRD appendix.

### Outputs

- A stable set of abstract capability profiles rather than a list of one-off business names.
- User and adoption assumptions for the strategy and metrics layers.
- Capability gaps that feed the strategy, metrics, product, technical, organization, and operations layers.

## 3. Strategy Layer

Question: What is the long-term target, and what should be refused?

### Inputs

- Business-layer maintenance justification and cost boundaries.
- Market-layer workflow segments and capability profiles.
- Technical constraints from native Codex compatibility, user-level helpers, repo-local durable state, and local templates.
- Operations and retrospective feedback from real platform incidents.

### Tools And Techniques

- Strategy-kernel analysis records the diagnosis, guiding policy, coherent actions, and explicit non-goals for the platform.
- Release-train planning separates MVP, release slices, and long-term persistent-team targets.
- Backend-family selection keeps `subagent`, `native_omx`, and `langgraph` as distinct control surfaces.
- Kill-criteria design defines when a helper, template, skill profile, durable lane, or automation path should be paused or retired.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` is the ASCII North Star draft; it is a long-term target, not proof of implemented runtime behavior.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` is the UTF-8 Chinese companion and current main discussion surface for the same draft.

### Outputs

- A strategic platform direction for durable team investments.
- Explicit trade-offs, non-goals, and backend-family selection rules.
- Release scope and priority constraints for the metrics, product, technical, organization, execution, growth, operations, and retrospective layers.

## 4. Metrics Layer

Question: How is platform progress measured?

### Inputs

- Strategy-layer target, non-goals, and release priorities.
- Business-layer cost and benefit assumptions.
- Market-layer adoption assumptions and capability gaps.
- Execution, operations, and retrospective evidence from previous releases.

### Tools And Techniques

- North Star metric design focuses on safe cold-start continuation across sessions and projects.
- OKR and input-metric design track friction reduction, successful recovery, release safety, and rollback confidence.
- Guardrail metric design protects native Codex compatibility, repo-local durable truth, provider pacing budget, operator attention, and CI minutes.
- Tracking-plan design defines how local gates, MR reviews, release evidence, incidents, and context-retention reloads are counted.

### Outputs

- Candidate North Star metric: cold-start continuation success rate, which is the rate at which a new Codex session can safely resume a project task with minimal repeated user explanation.
- Input metrics: OpenSpec guard pass rate, local gate pass rate, local MR review pass rate, remote pipeline pass rate when used, context-retention reload incidents, multi-session collision incidents, rollback success rate, and manual context-restatement count.
- Guardrails for cost, skill-context noise, state leakage, native Codex regressions, hidden automation, and unsupported durable-lane launch.
- Metric thresholds that can trigger continue, pause, refine, roll back, or retire decisions.

## 5. Product Layer

Question: What control surfaces should the platform expose?

### Inputs

- Strategy-layer release targets, routing thresholds, and non-goals.
- Metrics-layer success measures and guardrails.
- User needs for startup recovery, role routing, status inspection, templates, and safe publication.
- Technical constraints from native Codex, user-level launchers, MCP scope, and repo-local state isolation.

### Tools And Techniques

- Control-surface design turns strategy into commands, startup behavior, role routing, state inspection, and template flows.
- PR/FAQ-style narrative checks keep new helpers tied to an operator outcome rather than implementation enthusiasm.
- Acceptance-criteria design converts operator workflows into checkable behavior.
- `docs_bilingual/product/codex_cli_durable_team_prd.md` is the future ASCII PRD; it should define user-facing commands, startup behavior, role routing, state inspection, release gates, and template update flows.
- `docs_bilingual/product/codex_cli_durable_team_prd.zh-CN.md` is the future UTF-8 Chinese companion for the PRD.
- `AGENTS.md` is the project-level Codex instruction surface; it tells Codex how this repository should be handled.
- `docs_bilingual/project_startup_summary.md` is the ASCII cold-start summary; it tells a new session how to recover context.
- `docs_bilingual/project_startup_summary.zh-CN.md` is the UTF-8 Chinese cold-start summary companion.

### Outputs

- Explicit operator workflows and acceptance criteria.
- Product-level boundaries for native Codex compatibility and additive orchestration.
- Inputs for the technical, organization, execution, growth, and operations layers.

## 6. Technical Layer

Question: How should the platform be implemented without breaking native Codex?

### Inputs

- Product-layer control surfaces and acceptance criteria.
- Metrics-layer guardrails for compatibility, state safety, cost, and release evidence.
- Strategy-layer backend-family boundaries for native subagents, native_omx, and LangGraph.
- Organization-layer ownership and approval constraints.
- External constraints from Windows shells, MCP servers, official LangGraph runtime, local model services, and Git repositories.

### Tools And Techniques

- Architecture boundary design separates user-level runtime, repo-local source, repo-local durable state, and downstream project state.
- Compatibility design preserves native Codex behavior before adding wrappers or helper layers.
- Data and state-contract design treats `.omx/state/`, OpenSpec archives, Git refs, and helper install artifacts as separate consistency domains.
- Secure-by-design review makes cleanup, launcher, MCP, and credential behavior fail closed and keep useful errors visible.
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
- Implementation constraints for organization, execution, operations, and local-main-first delivery.


## 7. Organization Layer

Question: Who or what owns each platform responsibility, decision, and approval?

### Inputs

- Strategy, metrics, product scope, technical boundaries, and operating constraints.
- Human operator authority, current main Codex leader responsibility, native subagent roles, optional durable-worker roles, and external tool boundaries.
- Session-ownership claims, worktree isolation evidence, and approval requirements.

### Tools And Techniques

- Role-map design separates the human operator, current main Codex leader session, native expert subagents, durable workers, and external reviewers.
- Agent-governance design defines which agents may read, write, propose, review, test, deploy, or require approval.
- Durable-team threshold design prevents automatic durable launch before a plan is frozen and independent execution slices exist.
- Responsibility-matrix design maps release decisions, rollback decisions, state mutation, remote publication, and mirror sync to explicit owners.
- Session-ownership checks prevent multiple sessions from writing the same paths without explicit coordination.

### Outputs

- Agent governance, role map, responsibility matrix, launch thresholds, and approval boundaries.
- Ownership constraints for execution, operations, and retrospective work.
- Explicit decision rights so automation does not become hidden authority.


## 8. Execution Layer

Question: How are platform changes delivered safely?

### Inputs

- Product-layer acceptance criteria and technical-layer contracts.
- Organization-layer ownership, approval, and durable-lane constraints.
- OpenSpec proposals, designs, tasks, stable specs, and archive status.
- local-main-first publication rules and current session ownership claims.

### Tools And Techniques

- OpenSpec change control records proposal, design, tasks, specs, and archive evidence.
- Shaping records appetite, boundaries, rabbit holes, and circuit-breaker conditions before broad implementation.
- local-main-first delivery uses feature branches, local commits, local gate, local MR review, local main integration after approval, GitLab publication, and GitHub mirror sync.
- Repository checkers validate bilingual documents, name clarity, session claims, safety rule backing, and OpenSpec health.
- `openspec/changes/<change-id>/proposal.md` is an ASCII OpenSpec proposal; it explains why a specific platform change is needed.
- `openspec/changes/<change-id>/design.md` is an ASCII OpenSpec design; it explains how the platform change will be implemented.
- `openspec/changes/<change-id>/tasks.md` is an ASCII OpenSpec task list; it tracks completion for that change.
- `openspec/changes/<change-id>/*.zh-CN.md` are UTF-8 Chinese companions for the same change artifacts.
- `tools/run_openspec_guard.py` is the OpenSpec guard script; it validates official refresh, repository rules, and clean-git expectations.
- `tools/ci/local_gate.ps1` and `tools/ci/local_mr_review.ps1` are the shared local publication gates.

### Outputs

- Small local-main-first integration packages with explicit validation evidence.
- Completed or archived OpenSpec changes with stable-spec updates when required.
- Release, rollback, verification, and publication evidence for platform-affecting changes.

## 9. Growth Layer

Question: How does the platform expand across projects without sharing repo-local truth?

### Inputs

- Execution-layer releases, templates, helper scripts, and operator guidance.
- Metrics-layer adoption and friction signals.
- Downstream project needs for local Git, OpenSpec, native subagents, browser capability, and no shared repo-local truth.
- Template feedback from initialized projects.

### Tools And Techniques

- Template packaging separates new-PC bootstrap files, reusable project files, and project-local generated state.
- Adoption analysis tracks which capabilities are reused across projects without merging durable state.
- Positioning and onboarding review ensure commands, profiles, and docs explain when to use raw Codex, wrapped Codex, native subagents, native_omx, or LangGraph.
- Template update policy defines how initialized projects receive later improvements.
- `D:\PythonProject_General_2\START_HERE.cmd` is the Windows double-click template launcher; it initializes or checks local projects.
- `D:\PythonProject_General_2\TEMPLATE_MANIFEST.md` is the template manifest; it explains which files belong to the local project template.
- `docs_bilingual/templates/template_update_policy.md` is the future ASCII template update policy; it should explain how initialized projects receive later template updates.
- `docs_bilingual/templates/template_update_policy.zh-CN.md` is the future UTF-8 Chinese companion for template update policy.

### Outputs

- Downstream projects can adopt the platform without becoming platform implementation repositories.
- Template update rules, onboarding notes, adoption reports, and profile-selection guidance.
- Feedback to strategy, metrics, product, technical, organization, and operations layers when adoption friction appears.


## 10. Operations Layer

Question: How does the platform stay usable after release?

### Inputs

- Released helpers, templates, specs, startup summaries, and checker behavior from execution.
- Adoption reports, operator questions, skill-profile feedback, support friction, and incident signals from growth.
- Technical constraints, ownership boundaries, and rollback paths.

### Tools And Techniques

- Support-playbook design defines how to triage wrapper failures, cleanup-output noise, skill-context budget warnings, MCP startup issues, and CI drift.
- Health-check and status-surface review keeps read-only status helpers useful before any durable lane is launched.
- Documentation operations turn repeated operator questions into startup-summary, governance, template, or FAQ updates.
- Changelog and release-note discipline records user-visible control-surface changes.
- Runner-minute and provider-pacing review keeps publication and agent fan-out cost visible.

### Outputs

- Support notes, troubleshooting guidance, FAQ updates, changelog entries, and health-check expectations.
- Operations evidence that released platform work remains understandable, recoverable, and supportable.
- Feedback to product, technical, organization, growth, and retrospective layers.


## 11. Retrospective Layer

Question: What platform lessons should become rules, checkers, or templates?

### Inputs

- Execution-layer validation results, release outcomes, rollback outcomes, and incidents.
- Growth-layer adoption reports and downstream feedback.
- Operations-layer support records, startup noise, skill-profile issues, and toolchain failures.
- Session-collision, context-loss, MCP noise, wrapper, and durable-lane failures observed during real work.

### Tools And Techniques

- Retrospective analysis turns repeated failures into governance rules.
- Checker design turns rules into script controls so new sessions do not depend only on prompt memory.
- Operating-cadence review decides whether repeated manual work should become a template, checker, wrapper change, skill profile, or documented non-goal.
- Archive and memory updates capture durable context after major changes.
- `docs_bilingual/memory/mainline_memory_summary.md` is the ASCII mainline memory summary; it captures durable context after major changes.
- `docs_bilingual/memory/mainline_memory_summary.zh-CN.md` is the UTF-8 Chinese memory summary companion.
- `docs_bilingual/governance/` is the governance directory; it stores rules that should outlive a single conversation.
- `tools/check_*.py` scripts are checker files; they enforce governance rules without relying only on prompts.

### Outputs

- Repeated failures become scripts, policy, OpenSpec specs, templates, skill profiles, or documented non-goals.
- Lessons learned for future release slicing and routing policy.
- Updates to startup summaries, governance documents, and checkers when needed.
- Reusable learning returned to the cognitive, business, market, strategy, metrics, product, technical, organization, execution, growth, and operations layers.

## Release Slicing Rule

One platform MR should usually change one layer or one control surface. Good examples are: add one lifecycle reference, add one checker, archive one OpenSpec change, refine one release gate, update one template rule, or adjust one supportable profile-selection mechanism.
