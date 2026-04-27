---
doc_id: codex_user_level_skills_governance_policy
lang: zh-CN
doc_class: governance
status: active
---

# Codex 用户级 Skills 治理策略

## 1. 目的

本策略定义本机 Codex 编排线中，用户级 Codex skills、仓库本地 skills、插件 skills 与 profile 元数据的治理方式。目标是在不丢失跨项目能力的前提下，降低启动时 skills 上下文压力；这些跨项目能力包括 OpenSpec 工作流、Codex 编排治理、durable-team routing、LangGraph 策略、浏览器自动化与验证能力。

本策略是声明式策略。它不会删除 skills、禁用插件，也不会修改 `C:\Users\lenovo\.codex\config.toml`。

## 2. 权威边界

使用以下边界规则：

```text
共享 runtime 与 policy：user-level
项目事实与 durable truth：repo-local
```

用户级策略可以描述可复用 skills、启动 profiles 与共享 runtime 行为。仓库本地状态仍归拥有它的仓库管理，包括 `openspec/changes/`、`openspec/specs/`、`.omx/state/`、`.omx/state/langgraph/`、仓库任务队列、memory summaries、CI state 与 release state。

`D:\PythonProject_langgraph` 是本治理策略及相关实施计划的 source of truth。它不得把 repo-local durable state 移入用户级共享 runtime，也不得把自己的 repo-local state 当作其他项目的全局状态。

## 3. Skill 分层模型

Skills 按四个主要层级治理：

1. `core_user`：用户级 skills，适合默认加载，跨项目通用、上下文成本低且默认启用风险较小。
2. `profile_user`：用户级 skills，适用于某类项目，但应由 profile 或项目策略启用。
3. `repo_local`：由特定仓库拥有的 skills，例如仓库 OpenSpec skills。仓库本地 skills 不得把仓库事实或 durable state 泄漏到其他仓库。
4. `plugin`：供应商或插件提供的 skills。在 launcher 支持细粒度 plugin-skill 过滤之前，插件 skills 按 bundle-managed 处理。

Inventory 工具可以报告更细的 source label，但策略决策应映射回这四个层级。

## 4. 放置规则

把 skill 放在拥有该行为的最低权威层：

- 跨项目 workflow instructions 应放在用户级 skills 或用户级治理文档中。
- 仓库事实、active changes 与 durable task state 应留在仓库内。
- 已初始化 OpenSpec 的仓库可以拥有 OpenSpec workflow skills，但生成文件必须视为 managed artifacts。
- Plugin skills 应留在 plugin cache 中，不应由仓库变更直接编辑。
- 具有广泛适用性的新 skills 应先按 profile-gated 处理，除非它们明显适合 `core` 默认启用。

在 inventory 和治理检查能够衡量影响之前，不要批量改写 skill descriptions。

## 5. Profile 定义

Profile registry 位于 `docs_bilingual/governance/codex_skills_profiles.registry.yaml`，该文件登记可用 profiles、默认映射与治理约束。

必需 profiles：

- `core`：默认常驻的跨项目基础 profile，用于 skill 管理、诊断、规划、评审、笔记、worker/team 协议文档、通用 OpenSpec 工作流和 Codex 编排治理。
- `openspec`：OpenSpec 工作流能力 profile，当仓库使用 OpenSpec 时提供 proposal、apply、verify、sync、archive 与 refresh 指引。
- `orchestration`：Codex subagent、OMX、durable-team、LangGraph、routing、state 与 recovery policy 的 profile。
- `browser`：浏览器自动化、browser MCP、Playwright、可视化验证、Web 控制台测试与 agent-browser workflow 的 profile。
- `web`：Vercel、Next.js、React、AI web app、frontend 与 deployment 工作的 profile。
- `github`：GitHub issue 与 PR 工作流 profile，仅在任务当前需要时启用。
- `full`：用于广泛 skill discovery 的短期 troubleshooting profile。

`full` 不是长期默认 profile。

## 6. 项目默认值

默认 profiles 是声明式项目策略，不是自动 launcher mutation：

| Project | Default profiles | Rule |
| --- | --- | --- |
| `D:\PythonProject_langgraph` | `core`, `openspec`, `orchestration` | Codex 编排治理与实施计划的 source of truth。 |
| registry browser legacy application project | `core`, `browser`, `orchestration` | 浏览器自动化预期可用，且必须继续保留。 |
| `D:\PythonProject_CLIProxyAPI` | `core`, `browser`, `orchestration` | 可能需要浏览器或 endpoint 验证，且必须继续保留。 |
| `D:\project` | `core` | 只有在仓库证据要求时才增加 browser 或 web。 |
| future projects | `core` first | 只有在项目证据要求时才增加 `browser`、`web`、`github` 或 `full`。 |

## 7. Duplicate Skill 策略

Duplicate skill names 按 scope 和 authority 处理：

- 同一个 governed layer 内的重复名称属于错误，除非 registry 为正在调查的 managed generated artifact 声明临时例外。
- 跨 layer 重复名称在策略记录 preferred source 之前先作为 warning 处理。
- 仓库本地 OpenSpec 嵌套重复项不得删除，直到在 clean clone 中确认 OpenSpec regeneration 与 OpenSpec guard 均为 green。
- GitHub skill 重复项在 GitHub plugin 是 active workflow surface 时应优先使用 plugin source。
- Plugin duplicates 仅报告；除非 plugin manager 或 launcher 暴露受支持的过滤机制，否则不由仓库 MR 直接处理。

当前 policy preference 为：

- `gh-address-comments`：处理 GitHub review comments 的 skill；GitHub review 工作活跃时优先使用 plugin 来源。
- `gh-fix-ci`：修复 GitHub CI 的 skill；GitHub CI 工作活跃时优先使用 plugin 来源。
- `openspec-*`：仓库本地生成的 OpenSpec skills；在官方生成行为验证前，仓库 OpenSpec 工作优先使用该来源。

## 8. Description 长度限制

建议的 frontmatter `description` 长度限制：

- user-level skills：180 个英文字符或 80 个中文字符。
- repository-local skills：220 个英文字符或 100 个中文字符。
- plugin skills：只报告；不要从仓库 MR 中编辑 vendor 或 plugin 文件。

只有在 inventory output 让变更可衡量、可 review 后，才应缩短过长 descriptions。

## 9. Plugin 处理规则

不要仅为了降低 context pressure 而禁用整个 plugin，尤其当 active project 依赖该 plugin 的能力时。

对于 Vercel plugin，browser 项目必须在可用时保留以下 browser-oriented skills：

- `agent-browser`：Vercel plugin 的浏览器自动化 skill，用于 agent-driven browser sessions。
- `agent-browser-verify`：Vercel plugin 的浏览器验证 skill，用于检查浏览器行为。
- `verification`：Vercel plugin 的 full-story verification skill，用于 acceptance 与 behavior checks。
- `investigation-mode`：Vercel plugin 的结构化 debugging workflow skill，用于浏览器或应用调查。

如果当前不支持 partial plugin skill loading，则对于 `browser` 与 `web` profile 项目，应保持 Vercel plugin 可用，而不是全局禁用它。

## 10. 安全规则

- 没有 backup 和明确用户批准，不得删除 user-level skills。
- 当 browser automation 是必需能力且没有替代方案时，不得禁用 Vercel plugin。
- 不得把 repository durable state 移入 user-level locations。
- 不得从 repository MR 自动编辑 `C:\Users\lenovo\.codex\config.toml`。
- 除非 scoped selector policy 允许，不得把历史 `.omx/state` records 视为 live activation selectors。

## 11. 发布工作流

本仓库使用 GitLab 作为权威 review 与 merge surface：

1. 创建 feature branch。
2. 将 feature branch 推送到 GitLab。
3. 打开或更新 GitLab MR。
4. 等待 GitLab pipeline 通过。
5. 合并到 GitLab `main`。
6. 将该 GitLab `main` commit 精确同步到 GitHub `main`。
7. 除非用户明确覆盖此 workflow，否则不要打开 GitHub PR。

## 12. 必需检查

在结束 skills governance MR 之前，至少运行：

```powershell
git diff --check
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/inventory_codex_skills.py --root . --json
```

当 governance check 属于本次范围时，还要运行：

```powershell
python tools/check_codex_skills_governance.py --root . --json
python -m pytest test/check_codex_skills_governance.test.py
```
