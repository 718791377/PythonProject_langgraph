---
doc_id: general_template_phase0_update_patch_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-04-25
updated_at: 2026-05-25
phase: 0
target_template: D:\PythonProject_General
source_context:
  - docs_bilingual/project_startup_summary.md
  - docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md
  - docs_bilingual/implementation_plans/codex_langgraph_repository_split_migration_plan.md
  - docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md
  - docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md
  - docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.md
  - D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.md
  - D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.zh-CN.md
---

# D:\PythonProject_General Phase 0 模板更新补丁实施计划

> 冷启动契约：本文是自包含 Phase 0 实施计划。没有历史聊天上下文的新 Codex 会话，只要读取本文、`README.md`、`AGENTS.md`、`project_startup_summary.md` 和 `docs_bilingual/governance/template_completion_protocol.md`，即可安全地在 `D:\PythonProject_General` 实施 Phase 0 补丁。

## 双语对齐状态

- 英文 ASCII 文件：`docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md`，是实施 source of truth。
- 中文 companion 文件：本文。
- 对齐规则：source context、范围、安全规则、交付物、验证命令和验收标准必须同步。
- 当前结论：Phase 0 是 master template root 的小型安全性与可测试性补丁，不是完整 profile、skills governance、browser、web、publishing、OMX 或 LangGraph rollout。
- 名称解释规则：凡是列出脚本、路径、命令、变量或 profile 名称，都要补充一句简短解释，确保冷启动读者知道它是什么、用来做什么。

## 2026-05-25 状态刷新

本文现在记录初始 Phase 0 工作以及后续 Comet 治理同步之后，`D:\PythonProject_General` 的当前状态。

当前目标模板事实：

- `D:\PythonProject_General` 现在已经是本地 Git 仓库，分支为 `main`；旧版 Phase 0 中“master template root 尚未纳入 Git 管理”的说明现在只是历史上下文，不再是当前状态。
- 目标模板已经具备 hydration smoke test、本地 CI gate 和本地 MR review helper surface。local / remote CI/MR 设计仍然复用目标模板脚本，不维护另一套漂移的 checker sequence。
- 后续 Comet 同步已经加入项目级 Comet workflow skills、`docs/superpowers/` 占位目录、双语 Comet workflow policy、Comet-controlled OpenSpec + Superpowers governance 的 stable OpenSpec spec、本地已归档 OpenSpec change，以及 `tools/check_openspec_comet_superpowers_policy.py`。
- Comet 在这里只记录为 OpenSpec + Superpowers 治理能力。它不是 native subagent evidence，不是 oh-my-codex，不是 OMX，不是 `native_omx`，不是 LangGraph，也不是 durable-team backend。
- 当前目标模板 working tree 仍然保留 Comet 治理补丁为本地未提交改动，等待 operator review。既有未跟踪 `.idea/` 目录不属于本计划补丁范围。
- `D:\PythonProject_General_2` 由另一份 local Git / OpenSpec / native subagents only 计划治理；不得把它当成这份 `General` Phase 0 计划已经覆盖的目标。

Comet 同步后为 `General` 目标记录的最新验证证据：

- `git -C D:\PythonProject_General diff --check` 在线尾换行规范化后通过。
- `openspec validate --all` 在 `D:\PythonProject_General` 中通过。
- `comet status D:\PythonProject_General --json` 报告没有 active Comet changes。
- `comet doctor D:\PythonProject_General --json` 对项目级 Codex Comet skills 和脚本可执行性通过；global Codex Comet skills 可能报告缺失 warning，因为模板有意只携带 project-level skills。
- `python .\tools\test_template_hydration.py --root . --json` 在 `D:\PythonProject_General` 中通过。
- `.\tools\ci\local_gate.ps1 -Root . -Json` 在 `D:\PythonProject_General` 中通过。
- `.\tools\ci\local_mr_review.ps1 -Root . -Json -AllowDirty` 以 draft review 方式通过，因为目标补丁当时有意保留为未提交状态。

## 2026-05-25 冷启动补读与提示词哨兵修订

本次更新先按 `docs_bilingual/project_startup_summary.md` 冷启动入口重新读取，并按 read order 补读继续本计划必须需要的文件：

- `docs_bilingual/project_startup_summary.zh-CN.md`：中文启动摘要，用来确认当前仓库、发布、安全与上下文保留哨兵规则。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` 与 `.zh-CN.md`：当前主线 memory summary，用来确认本仓库仍是 Codex user-level orchestration line 的 source of truth。
- `AGENTS.md`：仓库级 Codex 指令面，用来确认 OpenSpec、worktree、MCP、launcher、LangGraph、native subagents 和提示词哨兵边界。
- `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md`：多会话 worktree 隔离政策，用来确认模板计划更新应串行写入，且本地 `main` 不应作为随意 feature scratch。
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.md`：LangGraph runtime 政策，用来确认官方 `langgraph` 安装在用户级共享 venv，而 repo-local 兼容/编排源码才属于模板化候选。
- `docs_bilingual/governance/user_level_launcher_payload_policy.md`：launcher payload 政策，用来确认 Windows 启动指令应使用短 payload 或文件引用，避免把长提示词 inline 到命令行。
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`：自动 orchestration activation 政策，用来确认 General 模板可以记录路由规则，但 durable team 仍必须阈值门控。
- `docs_bilingual/governance/openspec_usage_convention.md`、`openspec_opsx_project_usage_policy.md` 与 `openspec_official_workflow_policy.md`：OpenSpec 使用政策，用来确认本次只是更新实施计划，不打开新的 active OpenSpec change。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md`：MCP scope 政策，用来区分 Codex-direct `omx_*` MCP、`chrome-devtools`、`pencil` 与默认禁用的 `mcp_router` bridge。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` 与 `codex_user_level_cross_session_durable_state_isolation_plan.md`：active implementation plans，用来确认 native Codex、oh-my-codex、`native_omx`、LangGraph、repo-local durable state 和 consumer project 隔离边界。
- `openspec list --json`：OpenSpec 状态检查命令，本次读取结果为 `changes: []`。

本次补读后的 General 模板修订约束：

- 如果 Codex 启动提示、渲染后的 `AGENTS.md`、context-retention canary 或 Windows 终端输出出现乱码，必须以 UTF-8 读取的 `docs_bilingual/project_startup_summary.md` 与 `.zh-CN.md` 为准；不得把乱码文本复制到模板文档、launcher payload、generated helper 或 OpenSpec artifact。
- 如果 General 模板提供上下文保留哨兵，哨兵字面提示词只能由生成项目的 `docs_bilingual/project_startup_summary.md` 与 `.zh-CN.md` 承载；`AGENTS.md`、launcher、installer、OpenSpec proposal/design/tasks/spec、checker 和 native agent TOML 只能引用规则，不得重复字面提示。
- General 模板不得把本仓库的具体哨兵标记、live session facts、active claims 或 `.omx/state/` 当作新项目默认事实；新项目应在 hydrate 后生成自己的启动摘要、OpenSpec artifacts 和 repo-local durable state。
- Launcher payload 必须保持 Windows-safe：不要把长 generated orchestration instructions 通过 `-c developer_instructions=...` inline 传入命令行；应使用 file-backed instruction path、短引用或模板内受控 payload 组装脚本。
- LangGraph 相关源码如果进入 General，必须作为通用模板源码或可选 profile 交付，不能是 `D:\PythonProject_langgraph` 的 live runtime state；官方 `langgraph` 包仍属于用户级共享安装，repo-local `.omx/state/langgraph/` 只允许作为生成项目运行后的本地状态。
- Comet 仍只记录为 OpenSpec + Superpowers 治理能力：它不是 native subagent evidence，不是 oh-my-codex，不是 `native_omx`，不是 LangGraph，也不是 durable-team backend。

## 1. 目标

为 `D:\PythonProject_General` 创建一个小型、可 review、可回滚的 Phase 0 补丁，让模板本身在加入更大的 profile、skills、browser、web、publishing 或 orchestration 能力之前，先具备更好的维护安全性与可验证性。

该补丁应能让模板在三种状态下更容易验证：

1. master template root：`D:\PythonProject_General`
2. 由 `new-openspec-project.ps1` 生成的新项目；该脚本是 PowerShell 模板 hydrate 工具
3. 只知道生成后仓库文件、没有聊天上下文的新 Codex 会话

补丁还必须保持 General 模板可被多个项目复用。不得把 `D:\PythonProject_langgraph`、legacy browser consumer repository、`D:\PythonProject_CLIProxyAPI` 或其他 consumer 仓库的 repo-local 事实写入通用模板，并伪装成所有项目都适用的事实。

## 2. Source Context 与当前状态

本 Phase 0 计划派生自更大的 General 模板升级计划双语文件：

- `D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.md`：目标模板的英文 source upgrade plan。
- `D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.zh-CN.md`：目标模板的中文 companion upgrade plan。

本文同时吸收 `D:\PythonProject_langgraph` 的本地编排边界：

- `project_startup_summary.md` 说明本仓库是 user-level Codex orchestration line 的 source of truth。
- `codex_cli_personal_production_durable_team_plan.md` 是长期 north-star 草案，不是已经实现的运行时行为。
- `codex_langgraph_repository_split_migration_plan.md` 要求新的编排实现留在 `D:\PythonProject_langgraph`，不要回流到 legacy source repository。
- `codex_oh_my_codex_user_level_team_mode_plan.md` 要求 native Codex 保持 base layer，oh-my-codex 作为 additive workflow layer，`native_omx` 与 `langgraph` 作为不同 durable backend family，并且 durable-team launch 必须阈值门控。
- `codex_user_level_cross_session_durable_state_isolation_plan.md` 要求 repo-local `.omx/state` 隔离，防止某个项目或会话的 stale state 变成另一个项目的 activation truth。
- `codex_user_level_skills_governance_and_profiles_plan.md` 要求使用 profile 化 skills governance；不得为了压缩上下文而全局禁用其他项目仍可能需要的 browser、Vercel、GitHub、OpenSpec 或 orchestration 能力。

当前状态：

- 本文定义要应用到 `D:\PythonProject_General` 的 Phase 0 补丁。
- 本仓库内的这份计划用于记录目标模板的预期状态和已观察状态；只有后续步骤显式编辑 `D:\PythonProject_General` 时，才会修改目标模板。
- 除非 operator 明确扩大任务，否则 Phase 1 与 Phase 2 后续工作仍然不在当前范围内；Comet 治理同步是有界的 OpenSpec + Superpowers 治理更新，不是大范围 durable-orchestration rollout。

## 3. 当前观察到的状态

截至 2026-04-25，目标模板根目录已经具备这些基础内容：

- OpenSpec 双语 repository starter 文件。
- `AGENTS.md`：生成项目中 Codex 会话优先遵守的仓库级操作契约。
- `project_startup_summary.md` 与 `project_startup_summary.zh-CN.md`：冷启动会话读取的启动摘要。
- OpenSpec governance 文档与 `strict-governance` schema 文件：定义结构化变更流程的 policy document 和 schema gate。
- GitHub Actions 与 GitLab CI guard surface。
- git hook 模板。
- `new-openspec-project.ps1`：把该模板复制并 hydrate 成新项目的 PowerShell 生成器。
- Windows Explorer 与 PyCharm launcher helper：从右键菜单或 PyCharm External Tool 调用同一个项目生成器的可选入口。
- 根目录后台进程入口：`project-background.cmd`、`project-background.ps1` 与 `project-background.json`，用于启动、检查、查看日志和停止项目本地后台进程。
- `tools/project_background.py`：后台进程入口实际调用的 Python supervisor。
- `tools/background_keepalive.py`：默认 harmless keepalive 进程，用于在真实服务或 daemon 尚不存在时验证后台持久化能力。
- placeholder 与 OpenSpec 验证脚本。

重要发现：

- 历史说明：2026-04-25 时 master template root 尚未纳入 Git 管理；到 2026-05-25，`D:\PythonProject_General` 已经是本地 Git 仓库，分支为 `main`。
- master template root 中保留 raw placeholder 是正常现象，因为它是生成项目的模板源。
- 生成后的测试项目在 hydrate 后不应再有 unresolved placeholders。
- background-process 支持已经存在，应在生成后项目中做 smoke test。
- 模板根目录 `.gitignore` 对 Python、Node、OpenSpec、Codex、OMX 与本地 runtime 产物覆盖不足。
- `D:\PythonProject_langgraph` 中部分 helper scripts 已支持 `--json`；General 模板 helper surface 应在 Phase 0 先记录差异，并在后续阶段统一补齐 JSON 输出。

## 4. Phase 0 范围

Phase 0 只处理模板可维护性与验证准备度。

范围内：

1. 新增或更新 Phase 0 补丁计划文档。
2. 如果目标模板使用 `docs_bilingual/docs_registry.yaml` 登记 implementation plans，则将本计划双语文件登记进去。
3. 为 template root 更新 `.gitignore`，覆盖 local-only runtime 与 tooling artifacts。
4. 增加模板 hydration smoke-test 脚本：创建临时生成项目，并验证生成项目没有 unresolved placeholders；不要求 master template root 没有 placeholders。
5. 文档化 master-template placeholder 与 generated-project placeholder 的区别。
6. 验证 generated-project background entry point，并且不留下长期后台进程。
7. 记录 guard surface 兼容性说明，尤其是 JSON 输出差异；不强行做大范围 helper rewrite。
8. 保持所有改动足够小，便于 focused review 与 rollback。

Phase 0 不做：

- 不实现 profile-aware project generation。
- 不实现 skills inventory 或 skills governance checks。
- 不删除、禁用、移动或缩短 user-level skills。
- 不修改 `C:\Users\lenovo\.codex\config.toml`；它是模板仓库之外的 user-level Codex 配置文件。
- 不修改全局 Codex、Git、npm、Python、PowerShell、Vercel、GitHub、browser 或 OpenSpec plugin 安装。
- 不在目标模板补丁中修改 `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI`、`D:\project` 或 `D:\PythonProject_langgraph` 等真实项目仓库。
- 不要求 template root 必须有 GitLab 或 GitHub remote。
- 不重设计 `strict-governance`；它是仓库本地 OpenSpec review 与 approval gate 使用的 schema。
- 不强制所有 guard helper 支持 JSON 输出；Phase 0 最多记录 inventory note，并让 `tools/test_template_hydration.py --json` 支持 JSON。
- 不 rollout browser、web、Vercel、GitHub、publishing-profile、OMX 或 LangGraph durable-state profile 行为。
- 不把其他项目的 `.omx/state` 当作恢复路径或启动权威。

## 5. 安全规则

1. 除 smoke test 创建的临时目录外，不编辑生成后的子项目。
2. 不删除 user-level Codex skills 或 plugin cache。
3. 不修改全局 Codex、Git、npm、Python、PowerShell、Vercel、GitHub、browser 或 OpenSpec plugin 配置。
4. 不假设 master template root 应该通过 placeholder check；只有生成后项目应该通过 placeholder check。
5. 不在没有收尾或隔离到 `.project-runtime/` 的情况下启动长期后台进程；`.project-runtime/` 是本地 runtime-state 目录。
6. 不把 `D:\PythonProject_langgraph` 的项目特定事实写进通用模板。
7. 不把 user-level orchestration line 的新实现重新路由到 legacy source repository。
8. 英文 implementation-plan 文件必须保持 ASCII-only。
9. 中文 companion 文件必须注册，并随英文 source 同步更新。
10. 如果当前 host 不支持某个 configured background launcher，必须报告真实诊断；不得伪造成功。
11. repo-local durable state 必须保持 ignored 与 isolated；不得跨项目复制或复用 `.omx/state`。

## 6. 交付物

### 6.1 文档

创建并维护：

- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md`：英文 ASCII Phase 0 implementation source of truth。
- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md`：中文 companion，用来解释同一套实施范围和安全规则。

按需在目标模板中更新：

- `docs_bilingual/docs_registry.yaml`：双语文档 registry，用于冷启动会话与文档检查。
- `README.md`：英文模板概览与操作入口。
- `README.zh-CN.md`：中文模板概览与操作入口。
- `docs_bilingual/governance/template_completion_protocol.md`：英文模板补全策略，用于把模板默认值替换成真实项目事实。
- `docs_bilingual/governance/template_completion_protocol.zh-CN.md`：模板补全策略的中文 companion。

### 6.2 模板 Git 基线

如果 Phase 0 实施时目标模板仍然没有 Git baseline，则使用下面流程。到 2026-05-25，`D:\PythonProject_General` 已经是本地 Git 仓库，分支为 `main`，所以这段流程现在是历史 fallback guidance，而不是当前预期动作：

1. 在 `D:\PythonProject_General` 执行 `git init`；该命令为模板根目录创建仓库元数据。
2. 创建或重命名初始分支为 `main`；这会为可复用模板提供稳定 baseline branch。
3. 只暂存已经验证过的模板基线；runtime 与临时文件必须继续 ignored。
4. 提交，提交信息可使用 `Initialize Codex production template baseline`。

本交付物验收：

- `git -C D:\PythonProject_General status --short --branch` 在提交后显示 `main` 分支。
- runtime 与临时文件不会被暂存。

### 6.3 模板 ignore 规则

更新 `.gitignore`，至少忽略：

```gitignore
# Codex / OMX durable runtime state
.omx/

# Temporary and runtime state
.tmp/
.project-runtime/
openspec-guard-report.json

# Python
__pycache__/
*.pyc
.pytest_cache/
.venv/

# Node / frontend
node_modules/

# Build / coverage outputs
dist/
build/
coverage/
htmlcov/
```

ignore 条目含义：

- `.omx/`：仓库本地 durable orchestration state，不应提交。
- `.tmp/`：模板 hydration 测试和其他临时输出使用的 scratch 目录。
- `.project-runtime/`：本地后台进程 pid、日志、heartbeat 和 stop-signal 状态目录。
- `openspec-guard-report.json`：本地或 CI 生成的 guard 报告。
- Python 条目：字节码缓存、pytest cache 与本地虚拟环境。
- Node 与 build 条目：依赖安装目录、构建输出与覆盖率输出。

### 6.4 模板 hydration smoke test

新增：

- `tools/test_template_hydration.py`：smoke-test runner，用于生成临时项目并验证生成结果。

最低行为要求：

1. 定位 master template root。
2. 在 `.tmp/` 下创建临时输出目录；`.tmp/` 是被 Git 忽略的模板本地 scratch 目录。
3. 运行 `new-openspec-project.ps1 -ProjectName TemplateSmokeTest -DestinationRoot <temp> -SkipOfficialOpenSpecBootstrap`；该命令生成测试项目，但不刷新官方 OpenSpec managed files。
4. 在生成项目中运行 `python tools/check_placeholders.py .`；该命令验证模板 hydrate 后已替换 raw placeholders。
5. 断言生成项目中的 `tools/project_background.py` 存在且非空；该文件是生成项目的 background supervisor。
6. 运行 `project-background.cmd doctor` 或等价安全检查；该命令验证后台入口可用性，但不留下长期后台进程。
7. 对受限 host 上的 configured launcher unavailability 给出真实诊断；但遇到 traceback、缺失文件或假成功时必须失败。
8. 运行 guard help 检查：
   - `python tools/run_openspec_guard.py --help`：确认生成项目暴露统一本地 OpenSpec guard 的 help。
   - `python tools/verify_official_openspec.py --help`：确认生成项目暴露官方 OpenSpec verification wrapper 的 help。
   - `python tools/enforce_openspec_policy.py --help`：确认生成项目暴露仓库 policy enforcement helper 的 help。
   - `python tools/check_hosting_enforcement.py --help`：确认生成项目暴露 hosting enforcement helper 的 help。
9. 除非传入 `--keep-temp`，否则清理临时输出；`--keep-temp` 用于调试失败的 smoke test。
10. 失败时返回非零 exit code。
11. 支持 `--json` 输出；该参数让 CI job 和 Codex 会话读取机器可解析报告。

推荐命令：

```powershell
python tools/test_template_hydration.py --root . --json
```

这条命令会在当前模板根目录上运行 hydration smoke test，并输出 JSON 报告。

### 6.5 Guard surface 兼容性记录

Phase 0 应记录但不一定修复 `D:\PythonProject_langgraph` 与 `D:\PythonProject_General` helper 能力之间的差异。

已知后续需要检查的差异：

- 部分 `D:\PythonProject_langgraph` helper scripts 支持 `--json`。
- 部分 `D:\PythonProject_General` helper scripts 可能还不支持 `--json`。

安全顺序是：

1. Phase 0 先记录 inventory。
2. 后续阶段再统一增加 JSON 输出。
3. 不在这个小型安全补丁里做大范围 helper rewrite。

## 7. 用户确认后的实施步骤

1. 创建 `D:\PythonProject_General` 的 timestamped backup archive，除非 Git 已经捕获干净 baseline。
2. 如有需要，在目标模板中新增或更新 Phase 0 implementation plan 双语文件。
3. 如果目标模板使用 `docs_bilingual/docs_registry.yaml` 登记 implementation plans，则将本计划双语文件登记进去。
4. 更新 `.gitignore`，加入 local runtime 与 tool artifacts 规则，避免日志、缓存和临时目录进入提交。
5. 新增 `tools/test_template_hydration.py`；该脚本负责测试生成项目的 hydrate 结果。
6. 运行模板 hydration smoke test。
7. 对 plan 文件做定向检查：
   - 英文文件 non-ASCII 数量为 0。
   - 两个文件都没有 trailing whitespace。
   - 如果 registry 用于 implementation plans，两个文件都已登记到 `docs_bilingual/docs_registry.yaml`。
8. 通过 smoke test 运行生成项目的 placeholder check。
9. 如果 template root 还不是 Git repository，则初始化 Git，设置 `main` 分支，并提交已验证基线。
10. 除非用户明确要求打包后续阶段，否则在 Phase 0 通过前，暂缓 profile、skills、publishing、browser、web、OMX 和 LangGraph 大范围 rollout。

## 8. 验证命令

除非特别说明，均在 `D:\PythonProject_General` 下运行。

```powershell
python tools/test_template_hydration.py --root . --json
```

预期解释：

- `tools/test_template_hydration.py` 应该对生成项目通过。
- 在 master template root 直接运行 `python tools/check_placeholders.py .` 可能会报告 raw placeholders；在 checker 具备 template-root 模式前，这是预期结果。权威 placeholder 检查是 smoke test 对生成项目执行的检查。
- `--root .` 表示把当前目录作为模板根目录。
- `--json` 表示输出机器可解析报告，而不是只输出人类可读文本。

可选检查：

```powershell
python tools/verify_official_openspec.py --root .
python tools/enforce_openspec_policy.py --root .
python tools/run_openspec_guard.py --root .
project-background.cmd doctor
git status --short --branch
```

可选命令含义：

- `tools/verify_official_openspec.py` 检查官方 OpenSpec managed files 与验证面是否存在。
- `tools/enforce_openspec_policy.py` 检查仓库本地 OpenSpec policy 规则。
- `tools/run_openspec_guard.py` 运行 hooks 或 CI 使用的组合 guard 流程。
- `project-background.cmd doctor` 检查 background launcher，不应故意留下长期后台进程。
- `git status --short --branch` 显示目标模板是否有干净 Git baseline。

如果 official OpenSpec bootstrap 改写 managed files，必须显式检查并提交这些 drift，不要隐藏 drift。

## 9. 验收标准

Phase 0 满足以下条件才算完成。根据 2026-05-25 状态刷新，目标模板已经满足原始 Phase 0 的 Git、hydration、local gate 和 local MR helper 形态；当前剩余目标工作是对后续 Comet 治理补丁做 review 以及 commit / publish 决策：

- 双语 Phase 0 plan 文件存在且已对齐。
- 如果目标模板 registry 用于 implementation plans，则 plan 双语文件已登记进去。
- `.gitignore` 覆盖常见 local-only runtime、durable-state、dependency、build 与 tooling artifacts，避免这些文件被提交。
- 模板 hydration smoke test 存在，并能生成测试项目。
- 生成的测试项目通过 placeholder scanning。
- 生成项目的 background entry files 存在且非空。
- smoke test 对 launcher 限制给出真实报告，并在 traceback、缺失文件或假成功时失败。
- guard help checks 已作为 smoke test 的一部分运行，或已明确记录为 unsupported diagnostics。
- 英文 implementation-plan 文件保持 ASCII-only。
- 没有修改 user-level Codex skills、plugin cache 或全局配置文件。
- 没有把任何现有真实项目仓库作为目标模板补丁的一部分修改。
- 如果 Phase 0 中初始化了目标模板 Git，则 `main` 分支存在，并且 runtime 或临时文件未被暂存。

更广义的 production-template upgrade 要等后续阶段也满足以下条件后才算完成：

- 默认生成只使用 `core` 即可工作。
- browser 与 web 项目可以 opt into browser automation 与 web guidance，但这些能力不会成为所有项目默认值。
- orchestration 项目获得 durable-state 与 backend-family guidance。
- publishing profile 文本匹配所选发布模式。
- skills inventory 与 check tools 可以运行，且不修改 user-level skills。
- 模板根目录在验证后拥有 Git `main` baseline commit。

## 10. 回滚计划

如果 Phase 0 引入问题：

1. revert Phase 0 commit 或 patch
2. 只删除 `.tmp/` 下由测试创建的临时目录
3. 不删除 user-level skills 或 plugin caches
4. 除非用户明确指出某个生成项目只是测试输出，否则不删除真实生成项目
5. 不在 rollback 中删除或改写任何真实项目的 repo-local `.omx/state`
6. 回滚后重新运行一次干净的 template hydration smoke test

## 11. 后续阶段交接

Phase 0 之后，后续阶段可以继续实现：

- profile-aware project generation：`core` 表示默认非 Web 仓库，`browser` 表示浏览器自动化项目，`web` 表示前端和部署项目，`python-cli` 表示 Python 命令行工具，`agent-service` 表示 daemon 或 worker 服务，`orchestration` 表示 Codex 或 durable-team 仓库，`full` 表示临时广泛发现模式
- skills governance inventory 与 profile registry
- 为 `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 等项目保留 browser automation profile
- 所有 guard helper 的 JSON 输出对齐
- 发布流程 profile：`gitlab-first-github-sync`、`github-pr` 与 `local-only`
- OMX 与 LangGraph 的 repo-local durable state 隔离默认规则
- generated-project guidance，明确 `native_omx` 与 `langgraph` 是不同 durable backend family
- 明确 routing guidance：durable team launch 是阈值门控的，不会在 repository startup 时自动启动
