---
doc_id: codex_user_level_skills_governance_and_profiles_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-04-25
---

# Codex 用户级 Skills 治理与 Profiles 实施计划

> 冷启动契约：本文是自包含实施计划。一个没有任何聊天上下文的新 Codex 会话，只要读取本文、`AGENTS.md`、`docs_bilingual/project_startup_summary.zh-CN.md`，以及当前正在实施的两份计划，就可以直接照着执行：
>
> - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
> - `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md`
>
> 长期最终目标仍然是 `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md`。该计划目前是 draft，不要把它当成已经实施完成的能力。

## 1. 目标

为同一台机器、同一个用户级 Codex 安装建立一套可维护的 skills 治理与 profile 体系，覆盖：

- `D:\PythonProject_langgraph`
- `D:\PythonProject_OpenClaw`
- `D:\PythonProject_CLIProxyAPI`
- `D:\project`
- 后续通过 `codex-ohmy` 打开的更多项目

目标不是简单删除 skills，而是在不丢失浏览器自动化、OpenSpec、Codex 编排治理、durable team、LangGraph 等跨项目能力的前提下，降低 skills context budget 压力。

## 2. 当前问题

当前启动时加载的 skill 描述过多。

截至 2026-04-25 的本机形态大致为：

- 约 131 个 `SKILL.md`
- 约 60 个用户级 skills
- 约 20 个仓库级 OpenSpec skills
- 约 51 个插件 skills
- Vercel 插件贡献约 47 个 skills
- 重复 skill 名称包括 `openspec-*`、`gh-fix-ci`、`gh-address-comments`

这会触发类似警告：

```text
Exceeded skills context budget of 2%.
Loaded skill descriptions were truncated.
```

这不是致命错误，但会降低自动 skill 路由准确性，并增加启动上下文负担。

## 3. 核心设计决策

不要通过粗暴关闭整个能力族来优化。

应将 skills 分为四层：

1. **核心用户级 skills**
   - 跨项目总是有用
   - 上下文成本低
   - 适合默认加载

2. **profile 门控的用户级 skills**
   - 对某类项目有用，但不适合所有项目默认加载
   - 由启动 profile 或项目策略启用

3. **仓库级 skills**
   - 由特定仓库拥有
   - 不得把该仓库事实或 durable state 泄漏给其他仓库

4. **插件 skills**
   - 由已启用插件提供
   - 在 launcher 支持细粒度过滤前，按 bundle 对待

## 4. 跨项目能力规则

以下能力不是 `D:\PythonProject_langgraph` 专属：

- OpenSpec 官方工作流
- Codex 编排治理
- durable team 路由策略
- LangGraph durable orchestration 策略
- 浏览器自动化与验证

但是事实与状态必须保持仓库隔离：

- `openspec/changes/`
- `openspec/specs/`
- `.omx/state/`
- `.omx/state/langgraph/`
- 仓库任务队列
- 仓库 memory summary
- 仓库 CI 与发布状态

采用如下规则：

```text
共享 runtime 与 policy：user-level
项目事实与 durable truth：repo-local
```

## 5. 必需 Profiles

先实现或文档化以下 profiles。如果 launcher 还不支持直接 profile 化加载，则先把它实现为 registry metadata 和项目策略，不要自动修改 `config.toml`。

### 5.1 `core`

非 Web 工作的默认 profile。

必须包含：

- skill 管理与诊断
- planning 与 review
- note / memory helpers
- worker / team 协议文档
- OpenSpec 通用工作流能力
- Codex 编排治理能力

不应强依赖 Vercel / Next.js 专属 skills。

### 5.2 `browser`

需要浏览器自动化项目的默认附加 profile，包括：

- `D:\PythonProject_OpenClaw`
- `D:\PythonProject_CLIProxyAPI`
- 任何需要浏览器 UI 验证、browser MCP、Playwright、Web 控制台测试的项目

当 Vercel 插件可用时，必须保留以下浏览器相关能力：

- `agent-browser`
- `agent-browser-verify`
- `verification`
- `investigation-mode`

如果 Vercel 插件不能部分加载，则对 browser profile 项目保留该插件，不要为了减负而全局禁用它。

### 5.3 `web`

用于 Vercel、Next.js、React、AI Web App、前端或部署工作。

可以包含：

- `nextjs`
- `react-best-practices`
- `shadcn`
- `ai-sdk`
- `ai-gateway`
- `vercel-cli`
- `vercel-api`
- `deployments-cicd`
- `env-vars`
- `observability`
- `vercel-functions`
- `vercel-storage`

### 5.4 `github`

只有在 GitHub issue / PR 工作流活跃时启用。

对本仓库而言，GitHub 通常只是合并后的同步目标，不是 review 面。

默认不要开 GitHub PR。先走 GitLab MR，再把合并后的 `main` 同步到 GitHub。

### 5.5 `full`

临时排障 profile。

只适合短会话使用，用于广泛发现插件能力；不能作为长期默认。

## 6. 项目默认值

在 registry 或 policy 中记录这些默认值：

| 项目 | 默认 profiles | 说明 |
| --- | --- | --- |
| `D:\PythonProject_langgraph` | `core`, `openspec`, `orchestration` | Codex 编排治理和实施计划的 source of truth。 |
| `D:\PythonProject_OpenClaw` | `core`, `browser`, `orchestration` | 预期需要浏览器自动化。必须保留浏览器验证能力。 |
| `D:\PythonProject_CLIProxyAPI` | `core`, `browser`, `orchestration` | 可能需要浏览器或 endpoint 验证。 |
| `D:\project` | `core`，再按项目发现结果追加 | 先根据仓库内容判断是否需要 browser 或 web。 |
| 后续项目 | 先用 `core` | 只有项目证据需要时再加 `browser`、`web`、`github` 或 `full`。 |

## 7. 实施产物

通过小型 GitLab MR 分阶段实施。不要一次做成难以 review 的大变更。

### 7.1 新增 skills 治理政策

创建：

- `docs_bilingual/governance/codex_user_level_skills_governance_policy.md`
- `docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md`

政策必须定义：

- skill 分层模型
- 放置规则
- profile 定义
- 项目默认值
- 重复 skill 策略
- description 长度限制
- 插件处理规则
- user-level 与 repo-local 权威边界
- GitLab-first 发布流程

并在 `docs_bilingual/docs_registry.yaml` 中注册。

### 7.2 新增 skills inventory 报告工具

创建：

- `tools/inventory_codex_skills.py`

工具必须：

- 扫描 `%USERPROFILE%\.codex\skills` 下的用户级 skills
- 扫描 `.codex/skills` 下的仓库级 skills
- 可选扫描 `%USERPROFILE%\.codex\plugins\cache` 下的插件 skills
- 解析 `SKILL.md` frontmatter
- 输出 JSON，字段包括：
  - name
  - description length
  - source layer
  - file path
  - duplicate name group
  - suspected profile
  - status suggestion

必需命令：

```powershell
python tools/inventory_codex_skills.py --root . --json
```

### 7.3 新增 skills governance 检查

创建：

- `tools/check_codex_skills_governance.py`
- `test/check_codex_skills_governance.test.py`

检查必须在以下情况失败：

- 同一层内出现重复 skill 名称
- 用户级 skill description 超过配置限制
- 仓库级 skill description 超过配置限制
- 缺少治理文档 registry 条目
- registry 中出现未知 profile 标签

检查应在以下情况给 warning，而不是失败：

- user/plugin 跨层重复，但 policy 明确标注了 preferred source
- 插件 bundle 当前不能部分加载
- 已知 Vercel 插件 bulk load

必需命令：

```powershell
python tools/check_codex_skills_governance.py --root . --json
```

### 7.4 新增项目 skills profile registry

创建：

- `docs_bilingual/governance/codex_skills_profiles.registry.yaml`

最低 schema：

```yaml
version: 1
profiles:
  core:
    description: Always-on cross-project Codex skills.
  browser:
    description: Browser automation and visual verification skills.
  web:
    description: Vercel, Next.js, React, AI web app, and deployment skills.
  github:
    description: GitHub issue and PR workflow skills.
  full:
    description: Temporary broad discovery profile.
projects:
  D:\PythonProject_langgraph:
    profiles: [core, openspec, orchestration]
  D:\PythonProject_OpenClaw:
    profiles: [core, browser, orchestration]
  D:\PythonProject_CLIProxyAPI:
    profiles: [core, browser, orchestration]
  D:\project:
    profiles: [core]
```

该 registry 必须是声明式文件。不要让它自动修改用户级 `config.toml`。

### 7.5 规范化 OpenSpec skill 重复

调查为什么 `.codex/skills/openspec-*` 里存在嵌套重复的 `openspec-*/SKILL.md`。

删除任何文件前：

1. 运行 `openspec init --tools codex --force`。
2. 运行 `openspec update --force`。
3. 比较重新生成的文件。
4. 确认嵌套副本是 OpenSpec 1.3.1 官方输出，还是迁移遗留。
5. 只有在干净 clone 中 `tools/run_openspec_guard.py --root . --tool codex --refresh-managed-files --require-clean-git --json` 保持绿色时，才允许删除重复项。

### 7.6 先建 registry，再缩短 descriptions

不要先批量编辑 descriptions。

先创建 inventory 与 governance check，让 description 改动可以被度量和 review。

建议限制：

- 用户级 `description`：英文 180 字符以内，中文 80 字以内
- 仓库级 `description`：英文 220 字符以内，中文 100 字以内
- 插件 descriptions：只报告，不编辑 vendor/plugin 文件

## 8. 分阶段执行

### Phase 0：Baseline inventory

交付物：

- inventory script
- JSON 输出 artifact
- 不删除 skill
- 不禁用 plugin

验收：

```powershell
python tools/inventory_codex_skills.py --root . --json
```

必须能报告当前 counts 和 duplicates。

### Phase 1：Governance policy and registry

交付物：

- 中英文 governance policy
- profiles registry YAML
- docs registry 更新

验收：

```powershell
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
```

必须通过。

### Phase 2：Governance check

交付物：

- governance check script
- tests
- 如果稳定，再接入 CI

验收：

```powershell
python tools/check_codex_skills_governance.py --root . --json
python -m pytest test/check_codex_skills_governance.test.py
```

必须通过。

### Phase 3：Safe cleanup proposal

交付物：

- 识别重复项的生成报告
- OpenSpec 重复项调查结论
- GitHub 重复 skills 的 preferred source 决策
- 未经用户明确批准，不做破坏性 user-level cleanup

验收：

- `D:\PythonProject_OpenClaw` 不丢失浏览器能力
- `D:\PythonProject_CLIProxyAPI` 不丢失浏览器能力
- OpenSpec guard 保持绿色

### Phase 4：Profile launcher integration

交付物：

- profile 到 launcher 的映射文档
- 未来可选 launcher 支持，例如 `codex-ohmy-core`、`codex-ohmy-browser`、`codex-ohmy-web`、`codex-ohmy-full`

验收：

- 默认会话加载更少 skills
- browser 项目仍可使用浏览器验证
- web 项目仍可按需启用 Vercel / Next.js skills

## 9. 安全规则

1. 未备份且未得到用户明确批准，不删除用户级 skills。
2. 如果项目需要浏览器自动化且没有替代能力，不要禁用整个 Vercel 插件。
3. 不要把 repo-local durable state 移动到 user-level 位置。
4. 本仓库默认不创建 GitHub PR。
5. 不要在 repository MR 中自动修改 `C:\Users\lenovo\.codex\config.toml`。
6. 不要把 `D:\PythonProject_langgraph` 的 repo-local state 当成其他项目的 global state。
7. 除非 scoped selector policy 明确允许，不要把历史 `.omx/state` 记录当成 live activation selector。

## 10. 验证命令

每个 MR 结束前运行：

```powershell
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/run_openspec_guard.py --root . --tool codex --refresh-managed-files --require-clean-git --json
git diff --check
```

由于 `run_openspec_guard.py --require-clean-git` 会受到本地未跟踪草稿文件影响，必要时在干净临时 clone 中运行。

## 11. 发布流程

遵循本仓库发布规则：

1. 创建 feature branch。
2. 推送到 GitLab。
3. 创建或更新 GitLab MR。
4. 等待 GitLab pipeline 通过。
5. 合并到 GitLab `main`。
6. 将 GitLab `main` 直接同步到 GitHub `main`。
7. 除非明确要求，不创建 GitHub PR。

## 12. 完成定义

满足以下条件时，本计划完成：

- skills inventory 可重复运行
- 中英文 skills governance policy 已存在
- project profile registry 已存在
- governance checks 已自动化
- 重复项与长 description 问题能够以明确 severity 报告
- 不丢失跨项目浏览器能力
- 后续新增 skills 有明确放置和生命周期规则
- 冷启动 Codex 会话读取本文后，能够知道要创建哪些文件、运行哪些命令，以及不能越过哪些安全边界
