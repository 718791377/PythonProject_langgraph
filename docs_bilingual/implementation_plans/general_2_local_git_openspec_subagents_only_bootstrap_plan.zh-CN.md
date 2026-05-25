# D:\PythonProject_General_2 本地 Git + OpenSpec + native Codex subagents only 迁移实施方案（待确认草案）

> 状态：待用户确认。
> 跟踪范围：本文件位于 `D:\PythonProject_langgraph\docs_bilingual\implementation_plans\`，但已通过本机 `.git\info\exclude` 排除，因此只作为本地实施草案，不被项目 Git 跟踪。
> 目标目录：`D:\PythonProject_General_2`，这是准备在本机和新电脑复用的本地项目模板目录。
> 模式边界：只使用本地 Git、OpenSpec、native Codex subagents；不使用 GitLab/GitHub、omx durable team、LangGraph durable backend。

## 0. 2026-05-25 冷启动补读刷新

本次更新先按 `docs_bilingual/project_startup_summary.md` 冷启动入口重新读取，并按 read order 补读继续本计划必须需要的文件：

- `docs_bilingual/project_startup_summary.zh-CN.md`：中文启动摘要，用来确认当前仓库、发布、安全与提示词哨兵规则。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` 与 `.zh-CN.md`：当前主线 memory summary，用来确认本仓库仍是 Codex orchestration line 的 source of truth。
- `AGENTS.md`：仓库级 Codex 指令面，用来确认 native agents、skills、profiles、OpenSpec、worktree、MCP、launcher 与提示词哨兵边界。
- `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md`：多会话 worktree 隔离政策，用来确认一项可写任务应有单一写入者。
- `docs_bilingual/governance/openspec_usage_convention.md`、`openspec_opsx_project_usage_policy.md` 与 `openspec_official_workflow_policy.md`：OpenSpec 使用政策，用来确认本次只是更新本地实施计划，不打开新的 active OpenSpec change。
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`：自动 orchestration activation 政策，用来确认本次是单切片文档更新，不启动 durable team。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md`：MCP scope 政策，用来确认 General_2 不应引入 Codex-direct `omx_*` MCP 或 MCP Router 共享治理。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` 与 `codex_user_level_cross_session_durable_state_isolation_plan.md`：active implementation plans，用来确认 native subagents、OMX、LangGraph 和 repo-local durable state 的边界。
- `openspec list --json`：OpenSpec 状态检查命令，本次读取结果为 `changes: []`。

本次补读后的执行结论：

- `D:\PythonProject_General_2` 继续保持 local Git + OpenSpec + native Codex subagents only 模式；不得因为本仓库 LangGraph 或 OMX 能力可用，就把 `oh-my-codex`、`native_omx`、LangGraph runtime、`.omx/state/` 或 durable-team backend 写成 General_2 的当前启用能力。
- 如果 Codex 启动提示、渲染后的 `AGENTS.md`、context-retention canary 或 Trae / Windows PowerShell 输出出现乱码，必须以 UTF-8 读取的 `docs_bilingual/project_startup_summary.md` 与 `.zh-CN.md` 为准；不得把乱码文本复制到模板文件、subagent TOML、`config.toml` 注释或 README。
- 如果 General_2 后续引入上下文保留哨兵，哨兵字面提示词只能放在 `docs_bilingual/project_startup_summary.md` 与 `.zh-CN.md` 这一对启动摘要中；`AGENTS.md`、bootstrap 脚本、checker、native agent TOML 和 Codex `config.toml` 只能引用该规则，不得重复字面提示。
- General_2 不应复制本仓库的具体哨兵标记作为固定模板事实；新项目如需哨兵，应在生成后的项目启动摘要中声明自己的标记，并用 UTF-8 checker 验证。
- `C:\Users\<用户名>\.codex\config.toml` 是 Codex 用户级机器配置文件，可能被 Trae、Codex 或其他工具重写；长期规则必须放在 `AGENTS.md`、启动摘要和 checker 中，不能依赖 TOML 注释保存。

## 1. 目标

创建一个可复制到新电脑继续使用的 Windows 本地开发模板：

- `D:\PythonProject_General_2`：模板根目录，用来承载本地 Git 仓库、OpenSpec 文件、Codex 项目说明和 subagent 配置。
- 本地 Git 仓库：只在本机保存提交历史，不默认配置远程仓库。
- OpenSpec：作为文件化变更治理系统，所有 `openspec/` 文件由本地 Git 管理。
- native Codex subagents：只使用 Codex 原生 subagent TOML 配置，不启用 omx/langgraph durable backend。
- Windows PowerShell 5.1：作为脚本最低兼容目标，因为 Windows 10/11 默认自带 `powershell.exe`。
- Trae 终端：作为新电脑上执行 PowerShell 初始化脚本的常见入口。

## 2. 非目标

本次模板不做以下事情：

- 不配置 GitLab remote：GitLab remote 是远程评审/合并地址，本模板只做本地 Git。
- 不配置 GitHub remote：GitHub remote 是远程镜像/托管地址，本模板只做本地 Git。
- 不创建 `.gitlab-ci.yml`：GitLab CI 配置文件，本模板不使用远程流水线。
- 不创建 `.github/workflows/`：GitHub Actions 工作流目录，本模板不使用远程流水线。
- 不安装 `oh-my-codex`：omx 工作流层，本模板明确不启用。
- 不安装 `langgraph`：LangGraph durable backend，本模板明确不启用。
- 不复制 `.omx/state/`：repo-local durable state 目录，本模板不携带运行时状态。
- 不复制 `.omx/session-claims/`：会话占用声明目录，本模板不携带当前会话状态。
- 不复制 token、`.env`、credential cache：这些是密钥或本机认证状态，不能进入模板。
- 不复制 `.git/`：Git 历史目录，新模板应自己初始化本地 Git。
- 不复制 `.venv/`、`node_modules/`、缓存目录：这些依赖和缓存应在新电脑重新生成。

## 3. OpenSpec 与本地 Git 的关系

OpenSpec 不会替代 Git，也不强制绑定远程仓库。

- `openspec/`：OpenSpec 文件目录，用来保存 specs、changes、archive 等治理文件。
- `git init -b main`：初始化本地 Git 仓库并创建 `main` 分支。
- `git add .`：把模板文件和 OpenSpec 文件加入本地 Git 暂存区。
- `git commit -m "Initialize local Codex OpenSpec template"`：创建本地初始化提交。
- `openspec validate --all` - OpenSpec validation command used to check whether specs and changes are healthy.

结论：OpenSpec 以文件形式存在，Git 负责版本历史；本地 Git 模式下不需要 GitLab/GitHub。

分发状态的模板目录不包含 `.git/`：`.git/` 是本地 Git 仓库元数据目录，不应作为可复制模板内容分发。用户在新电脑运行 `bootstrap-local-project.ps1` 后，本地工作副本可以生成 `.git/`，但不得配置 GitLab/GitHub 或其他远程 remote。

## 4. 新电脑基础工具链

新电脑最小需要以下工具：

- `winget`：Windows 包管理器，用来安装 Git、Python、Node.js；Windows 10/11 新版本通常自带。
- `Git for Windows`：提供 `git` 命令，用来管理本地仓库。
- `Python 3.12`：提供 `python` 和 `pip`，用来运行模板 checker。
- `Node.js LTS`：提供 `node` 和 `npm`，用来安装 Codex CLI 和 OpenSpec CLI。
- `@openai/codex`：Codex CLI 的 npm 包，用来启动 Codex。
- `@fission-ai/openspec`：OpenSpec CLI 的 npm 包，用来运行 OpenSpec。
- `Windows PowerShell 5.1`：Windows 自带脚本运行环境，新电脑不要求 PowerShell 7。

可选工具：

- `ripgrep`：提供 `rg` 搜索命令，提升本地代码搜索体验。
- `PowerShell 7`：提供 `pwsh`，不是模板必需项。

## 5. pip 与 npm 镜像策略

### 5.1 pip 默认使用阿里云镜像

模板初始化脚本可以设置用户级 pip 默认源：

```powershell
python -m pip config --user set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

这条命令把当前 Windows 用户的 pip 默认下载源设置为阿里云 PyPI 镜像。

```powershell
python -m pip config --user set global.timeout 60
```

这条命令把 pip 下载超时时间设置为 60 秒，降低慢网络下失败概率。

说明：默认不设置 `trusted-host`，因为阿里云镜像使用 HTTPS；只有新电脑证书环境异常时再手动处理。

### 5.2 npm 默认不改镜像

模板默认不修改 npm registry：

- `npm`：Node.js 包管理器，用来安装 Codex CLI 和 OpenSpec CLI。
- 官方 npm registry：默认 npm 下载源，通常更容易拿到最新的 Codex/OpenSpec 包。

如网络确实不好，可由用户显式启用 npm 国内镜像：

```powershell
npm config set registry https://registry.npmmirror.com
```

这条命令把 npm 默认下载源设置为 npmmirror 国内镜像；默认不自动执行，避免包同步延迟导致安装旧版本。

## 6. 模板目录结构

确认后创建以下结构：

```text
D:\PythonProject_General_2
├─ AGENTS.md
├─ README.md
├─ TEMPLATE_MANIFEST.md
├─ .gitignore
├─ .codex
│  └─ agents
├─ docs_bilingual
│  ├─ project_startup_summary.md
│  ├─ project_startup_summary.zh-CN.md
│  └─ governance
├─ openspec
│  ├─ changes
│  └─ specs
└─ tools
   ├─ bootstrap-new-pc.ps1
   ├─ bootstrap-local-project.ps1
   ├─ install-subagents-user-level.ps1
   ├─ check_template_health.py
   ├─ check_subagent_only_policy.py
   ├─ check_openspec_local_health.py
   ├─ check_bilingual_pairs.py
   ├─ check_name_clarity_rules.py
   ├─ check_local_git_only_policy.py
   ├─ check-codex-config-rewrite.ps1
   └─ backup-codex-config.ps1
```

目录说明：

- `AGENTS.md`：Codex 项目级启动规则文件，用来声明本模板只使用 local Git + OpenSpec + native subagents。
- `README.md`：模板使用说明文件，用来给新电脑用户按步骤初始化。
- `TEMPLATE_MANIFEST.md`：模板清单文件，用来列出模板包含的目录、脚本、checker、subagent 数量和不包含的状态类文件。
- `.gitignore`：Git 忽略规则文件，用来排除缓存、依赖、密钥和本机状态。
- `.local/`：本机初始化报告和临时检测输出目录，只能由脚本在本机生成，必须被 `.gitignore` 忽略。
- `.codex/agents/`：项目级 Codex subagent 配置目录，用来保存和本机一致的 native subagent TOML。
- `.codex/skills/`：OpenSpec 初始化后生成的 Codex skills 目录，属于 OpenSpec 托管产物；模板初始可不携带，但运行 `openspec init --tools codex --force` 后允许存在。
- `docs_bilingual/project_startup_summary.md`：英文冷启动摘要，用来让无上下文模型恢复项目边界。
- `docs_bilingual/project_startup_summary.zh-CN.md`：中文冷启动摘要，用来让中文会话恢复项目边界。
- `docs_bilingual/governance/`：治理文档目录，用来保存本地 Git、OpenSpec、subagent-only 规则。
- `openspec/changes/`：OpenSpec 变更目录，用来存放 proposal/design/tasks/specs 变更。
- `openspec/specs/`：OpenSpec 稳定规格目录，用来存放已生效能力规格。
- `tools/`：脚本目录，用来保存初始化脚本和检查脚本。

## 6.1 双语文件配对规则

`docs_bilingual/` 和 `openspec/` 下所有人为维护的 Markdown 文档必须成对维护：

- ASCII 主版：不带 `.zh-CN` 后缀的 `.md` 文件，例如 `docs_bilingual/project_startup_summary.md`；这是跨平台、跨工具、跨编码环境的主版本，应尽量只使用 ASCII 字符。
- UTF-8 中文对照版：带 `.zh-CN.md` 后缀的文件，例如 `docs_bilingual/project_startup_summary.zh-CN.md`；这是给中文维护者阅读的对照版本，必须使用 UTF-8 编码。

配对要求：

- 新增 `docs_bilingual/foo.md` 时，必须同步新增 `docs_bilingual/foo.zh-CN.md`。
- 新增 `openspec/.../spec.md`、`proposal.md`、`design.md` 或 `tasks.md` 时，必须同步新增同路径同基名的 `.zh-CN.md` 中文对照版。
- 英文 ASCII 主版和 UTF-8 中文对照版必须表达同一规则、同一验收标准和同一实施边界；允许语言组织不同，但不得出现一边有关键约束、另一边缺失的情况。
- 自动生成、第三方托管、机器输出、缓存、二进制文件、`.yaml`、`.json`、脚本文件和 OpenSpec 工具强制要求的单语元数据文件不适用此规则，除非模板治理文档另行指定。
- 模板 checker 应检查新增 Markdown 文档是否存在对应配对文件，并在缺失时失败。

## 6.2 注释与名称解释规则

当前注释规则应表述为：凡是在 `docs_bilingual/` 或 `openspec/` 下列出脚本、路径、命令、变量、profile 名称、subagent 角色名、配置文件名或其他代码化名称时，不能只写名称本身，必须在同一行或紧邻下一句补充一句简短解释，说明“它是什么、用来做什么”。

正确示例：

- `tools/bootstrap-new-pc.ps1` - New-PC toolchain bootstrap script used to install Git, Python, Node.js, Codex CLI, and OpenSpec CLI.
- `analyst.toml` - Native Codex analyst subagent configuration used for requirements clarification, boundary checks, and ambiguity analysis.
- `openspec validate --all` - OpenSpec validation command used to check whether specs and changes are healthy.
- `PIP_INDEX_URL` - pip index environment variable used to temporarily select a Python package index URL.

错误示例：只写 `tools/bootstrap-new-pc.ps1`、`analyst.toml`、`openspec validate --all` 或 `PIP_INDEX_URL`，但没有说明它是什么、用来做什么。

实施要求：

- 文档中的清单项不能只包含反引号名称；必须追加用途解释。
- 表格中的名称列如果只写名称，必须有相邻说明列解释用途。
- OpenSpec 的 `proposal.md`、`design.md`、`tasks.md` 和 `spec.md` 同样适用此规则。
- 模板 checker 应提供名称解释检查，例如 `tools/check_name_clarity_rules.py`：名称解释检查脚本，用来扫描 `docs_bilingual/` 和 `openspec/` 中缺少用途解释的代码化名称清单项。

## 7. subagent 迁移策略

从当前本机用户级目录复制：

- `C:\Users\lenovo\.codex\agents\*.toml`：当前本机 native Codex subagent 配置文件集合。

复制到模板项目级目录：

- `D:\PythonProject_General_2\.codex\agents\*.toml`：模板内项目级 native Codex subagent 配置副本。

保留的角色包括但不限于：

- `analyst.toml` - Native Codex analyst subagent configuration used for requirements clarification, boundary checks, and ambiguity analysis.
- `architect.toml`：架构设计、模块边界、长期权衡 subagent。
- `planner.toml`：任务拆分、执行顺序、风险排序 subagent。
- `executor.toml`：代码实现和重构 subagent。
- `debugger.toml`：故障定位、失败复现、回归分析 subagent。
- `verifier.toml`：完成度验证、验收检查 subagent。
- `test-engineer.toml`：测试策略和覆盖检查 subagent。
- `security-reviewer.toml`：安全边界和风险审查 subagent。
- `writer.toml`：文档、迁移说明、使用说明 subagent。

可选安装到新电脑用户级：

- `tools/install-subagents-user-level.ps1`：安装脚本，用来把 `.codex\agents\*.toml` 复制到 `%USERPROFILE%\.codex\agents\`。

## 7.1 新电脑排查思路：Trae/Codex 删除 config.toml 注释

如果新电脑上 Trae 每次打开程序或运行 Codex 后都会删除 `C:\Users\<用户名>\.codex\config.toml` 中以 `#` 开头的注释，应按“先定位写入者，再调整模板规则承载位置”的方式排查。`config.toml` 是 Codex 用户级机器配置文件，用来保存 Codex 可读取的配置值，不应作为长期规则说明文档。

### 7.1.1 先备份正式配置

```powershell
Copy-Item "$env:USERPROFILE\.codex\config.toml" "$env:USERPROFILE\.codex\config.toml.bak"
```

这条命令把当前用户级 Codex 配置文件备份成 `.bak` 文件，避免排查时误伤正式配置。

### 7.1.2 添加 sentinel 测试注释

在 `config.toml` 中手动加入：

```toml
# SENTINEL_COMMENT_DO_NOT_DELETE
```

这行 sentinel 注释是排查标记，用来判断 Trae、Codex 或其他工具是否重写并删除 TOML 注释。

### 7.1.3 分步骤缩小触发源

按以下顺序测试，每一步之后都检查 sentinel 注释是否还存在：

1. 只打开 Trae：Trae 是新电脑使用的编辑器入口，用来判断是否编辑器启动时改写配置。
2. 打开 Trae 后运行 Codex：Codex 是本模板要使用的 CLI，用来判断 Trae 集成终端或插件是否触发改写。
3. 不打开 Trae，只在普通 Windows PowerShell 中运行 Codex：Windows PowerShell 是 Windows 10/11 自带终端，用来判断是否 Codex CLI 自己改写。
4. 只运行 `codex --version`：Codex 版本检查命令，用来判断轻量启动是否会改写配置。
5. 运行完整 `codex` 会话：Codex 交互会话入口，用来判断完整启动或登录流程是否会改写配置。

### 7.1.4 用文件哈希确认文件是否变化

```powershell
Get-FileHash "$env:USERPROFILE\.codex\config.toml"
```

这条命令计算 `config.toml` 的文件哈希，用来判断每个测试步骤前后文件内容是否发生变化。

### 7.1.5 用 Process Monitor 查写入进程

如果需要精确定位写入者，使用 Sysinternals Process Monitor。

过滤条件：

- `Path is C:\Users\<用户名>\.codex\config.toml`：只观察 Codex 用户级配置文件。
- `Operation is WriteFile`：观察文件写入事件。
- `Operation is CreateFile`：观察文件打开或创建事件。
- `Operation is SetEndOfFile`：观察文件截断事件。
- `Operation is CloseFile`：观察写入完成后的关闭事件。

判断方式：

- `codex.exe`：Codex CLI 进程，说明 Codex 自己重写配置。
- `trae.exe`：Trae 编辑器进程，说明 Trae 或其插件重写配置。
- `node.exe`：Node.js 进程，可能是 Codex、OpenSpec 或 npm 安装的 CLI 在重写配置。
- `powershell.exe`：Windows PowerShell 进程，可能是初始化脚本或 PowerShell profile 在重写配置。

### 7.1.6 临时只读验证

```powershell
attrib +R "$env:USERPROFILE\.codex\config.toml"
```

这条命令把 `config.toml` 临时设为只读，用来验证哪个程序在启动时尝试写入该文件。

```powershell
attrib -R "$env:USERPROFILE\.codex\config.toml"
```

这条命令取消只读属性，排查完成后必须恢复，避免 Codex 后续无法正常保存机器配置。

### 7.1.7 模板规则承载原则

如果确认 `config.toml` 的注释会被删除，则接受该文件会被工具重写的事实：

- `AGENTS.md`：项目级 Codex 启动规则文件，用来承载项目规则和 read order。
- `docs_bilingual/project_startup_summary.md`：ASCII 主版冷启动摘要，用来承载英文主规则。
- `docs_bilingual/project_startup_summary.zh-CN.md`：UTF-8 中文对照冷启动摘要，用来承载中文规则。
- `tools/check_*.py`：脚本化检查入口，用来强制验证安全边界和模板规则。
- `C:\Users\<用户名>\.codex\config.toml`：Codex 用户级机器配置文件，只保存机器可读配置值，不保存依赖注释的长期规则。

### 7.1.8 模板建议新增保护脚本

建议模板加入以下脚本：

- `tools/check-codex-config-rewrite.ps1`：Codex 配置重写排查脚本，用来备份 `config.toml`、写入 sentinel 注释、提示用户分步骤运行 Trae/Codex，并对比哈希结果。
- `tools/backup-codex-config.ps1`：Codex 配置备份脚本，用来把 `config.toml` 备份到 `%USERPROFILE%\.codex\backups\config.toml.<timestamp>.bak`，且不把 token 或机器配置复制到项目目录。

结论：新电脑模板不能依赖 `config.toml` 注释保存重要规则；重要规则必须进入 AGENTS、启动摘要和 checker，`config.toml` 只保留机器配置值。
## 7.2 版本、认证与安装报告策略

新电脑初始化必须区分“可自动安装的工具链”和“必须人工完成的认证”。

### 7.2.1 版本策略

- `Git for Windows`：Git 命令行工具，用来管理本地仓库；脚本使用 `winget` 安装当前可用稳定版，不在模板中固定旧版本。
- `Python 3.12`：Python 运行时，用来执行模板 checker；脚本优先安装 Python 3.12 系列。
- `Node.js LTS`：Node.js 长期支持版，用来提供 `node` 和 `npm`；脚本优先安装 LTS 版本。
- `@openai/codex`：Codex CLI npm 包，用来运行 Codex；脚本默认安装 npm registry 上的当前版本。
- `@fission-ai/openspec`：OpenSpec CLI npm 包，用来运行 OpenSpec；脚本默认安装 npm registry 上的当前版本。

脚本完成后必须输出实际版本号，而不是只假设安装成功。

### 7.2.2 认证边界

- Codex 登录或 API key 配置必须由用户手动完成；脚本不得保存、复制、打印或提交任何 token。
- OpenSpec 初始化只生成项目文件和 Codex skills，不需要保存远程仓库凭据。
- Git 本地仓库初始化不配置 remote，因此不需要 GitLab/GitHub 凭据。

### 7.2.3 安装报告

`tools/bootstrap-new-pc.ps1` 应在模板目录下生成本地安装报告：

- `.local/bootstrap-report.json`：本地安装报告文件，用来记录 Git、Python、Node.js、npm、Codex CLI、OpenSpec CLI 的检测结果和版本号。

`.local/` 是本机状态目录，必须写入 `.gitignore`，不得提交到本地模板仓库。
## 8. 初始化脚本设计

### 8.1 `tools/bootstrap-new-pc.ps1`

`tools/bootstrap-new-pc.ps1` 是新电脑工具链安装脚本。

脚本职责：

1. 检查 `powershell.exe` 版本，确认至少可在 Windows PowerShell 5.1 运行。
2. 检查 `winget` 是否存在；如果没有，停止并提示用户先安装 App Installer。
3. 安装或检测 `Git.Git`：Git for Windows 安装包 ID。
4. 安装或检测 `Python.Python.3.12`：Python 3.12 winget 安装包 ID。
5. 安装或检测 `OpenJS.NodeJS.LTS`：Node.js LTS winget 安装包 ID。
6. 刷新当前脚本进程 PATH，尽量让新安装的命令立即可用。
7. 运行 `python -m pip config --user set global.index-url https://mirrors.aliyun.com/pypi/simple/`，设置用户级 pip 阿里云镜像。
8. 运行 `python -m pip config --user set global.timeout 60`，设置 pip 下载超时。
9. 运行 `python -m pip install --upgrade pip`，升级 pip。
10. 运行 `npm install -g @openai/codex`，安装 Codex CLI。
11. 运行 `npm install -g @fission-ai/openspec`，安装 OpenSpec CLI。
12. 输出 `git --version`、`python --version`、`node --version`、`npm --version`、`codex --version`、`openspec --version` 的版本检查结果。
13. 生成 `.local/bootstrap-report.json`：本地安装报告文件，用来记录工具版本和检测结果。
14. 提示用户手动运行 `codex` 完成认证；脚本不保存 token。

### 8.2 `tools/bootstrap-local-project.ps1`

`tools/bootstrap-local-project.ps1` 是本地项目初始化脚本。

脚本职责：

1. 确认当前目录是 `D:\PythonProject_General_2` 或用户显式指定的模板根目录。
2. 如果没有 `.git/`，运行 `git init -b main` 初始化本地 Git。
3. 如果没有 `openspec/config.yaml`，运行 `openspec init --tools codex --force` 初始化 OpenSpec。
4. 运行 `openspec update --force` 刷新 OpenSpec 官方托管文件。
5. 运行 `tools/install-subagents-user-level.ps1`，可选安装项目内 subagents 到用户级目录。
6. 运行 `openspec validate --all` 验证 OpenSpec。
7. 运行 `python .\tools\check_template_health.py --root .` 验证模板结构。
8. 运行 `python .\tools\check_subagent_only_policy.py --root .` 验证没有 omx/langgraph durable backend。
9. 如果 `.git/` 是新建的，提示用户运行 `git add .` 和 `git commit -m "Initialize local Codex OpenSpec template"`。

### 8.3 `tools/install-subagents-user-level.ps1`

`tools/install-subagents-user-level.ps1` 是 subagent 用户级安装脚本。

脚本职责：

1. 读取 `.codex\agents\*.toml`：模板内项目级 subagent 配置文件。
2. 创建 `%USERPROFILE%\.codex\agents\`：新电脑用户级 Codex agents 目录。
3. 复制 TOML 文件到用户级目录。
4. 不删除用户级已存在的其他 agents；同名文件覆盖前输出清单。
5. 输出已安装角色列表。

## 9. Checker 设计

### 9.1 `tools/check_template_health.py`

`tools/check_template_health.py` 是模板健康检查脚本。

检查项：

- `AGENTS.md` 是否存在。
- `README.md` 是否存在。
- `.gitignore` 是否存在。
- `.codex/agents/` 是否存在且至少包含一个 `.toml` 文件。
- `docs_bilingual/project_startup_summary.md` 是否存在。
- `docs_bilingual/project_startup_summary.zh-CN.md` 是否存在。
- `openspec/` 是否存在。
- `tools/` 是否存在。

### 9.2 `tools/check_subagent_only_policy.py`

`tools/check_subagent_only_policy.py` 是 subagent-only 策略检查脚本。

检查项：

- 不允许存在 `.omx/state/`：这是 durable state 目录，本模板不应携带。
- 不允许存在 `.omx/state/langgraph/`：这是 LangGraph durable state 目录，本模板不应携带。
- 不允许存在 `tools/langgraph_durable_orchestrator/`：这是 LangGraph repo-local orchestration 源码目录，本模板不使用。
- 不允许在 README/AGENTS 中声明默认使用 `omx team`：这是 durable team 入口，本模板不使用。
- 允许出现“不要使用 omx/langgraph”的否定性说明。

### 9.3 `tools/check_openspec_local_health.py`

`tools/check_openspec_local_health.py` 是 OpenSpec 本地健康检查脚本。

检查项：

- `openspec` 命令是否可用。
- `openspec/config.yaml` 是否存在。
- `openspec validate --all` - OpenSpec validation command used to check whether specs and changes are healthy.
- `openspec/changes/` 是否存在。
- `openspec/specs/` 是否存在。

### 9.4 `tools/check_name_clarity_rules.py`

`tools/check_name_clarity_rules.py` 是名称解释检查脚本。

检查项：

- 扫描 `docs_bilingual/` 和 `openspec/`。
- 识别只包含反引号代码名称的清单项。
- 要求每个脚本、路径、命令、变量、profile 名称、subagent 角色名或配置文件名都有简短用途解释。
- 缺少解释时失败，并提示补充“它是什么、用来做什么”。

### 9.5 `tools/check_bilingual_pairs.py`

`tools/check_bilingual_pairs.py` 是双语文件配对检查脚本。

检查项：

- 扫描 `docs_bilingual/` 和 `openspec/` 下人为维护的 Markdown 文档。
- 对不带 `.zh-CN` 后缀的 ASCII 主版 `.md` 文件，检查是否存在对应 `.zh-CN.md` 中文对照版。
- 对 `.zh-CN.md` 中文对照版，检查是否存在对应 ASCII 主版 `.md` 文件。
- 跳过自动生成、第三方托管、机器输出、缓存、二进制文件、`.yaml`、`.json`、脚本文件和 OpenSpec 工具强制要求的单语元数据文件。
- 缺失配对文件时失败，并输出缺失的主版或中文对照版路径。

### 9.6 `tools/check_local_git_only_policy.py`

`tools/check_local_git_only_policy.py` 是本地 Git-only 策略检查脚本。

检查项：

- 如果 `.git/` 存在，检查 `git remote -v` 不包含 GitLab、GitHub 或其他远程地址。
- 不允许存在 `.gitlab-ci.yml`：GitLab CI 配置文件，本模板不使用远程流水线。
- 不允许存在 `.github/workflows/`：GitHub Actions 工作流目录，本模板不使用远程流水线。
- 检查 `README.md` 和 `AGENTS.md` 不宣称 GitLab-first、GitHub mirror、MR/PR 或 remote-first 工作流。
- 允许出现“不要配置 GitLab/GitHub remote”的否定性说明。
## 9.7 脚本安全与幂等要求

所有初始化脚本和检查脚本必须满足以下要求：

- 幂等：重复运行不会重复破坏文件、重复追加同一配置或重复创建冲突内容。
- 最小写入：只写入模板目录、当前用户级 pip 配置、当前用户级 Codex agents 目录和当前用户级 Codex backup 目录。
- 不写密钥：不得读取、复制、打印或提交 OpenAI token、Codex token、`.env`、credential cache。
- 不写远程：不得自动配置 GitLab/GitHub remote，不得自动推送远程仓库。
- 不安装禁用组件：不得安装 `oh-my-codex`、不得安装 `langgraph`、不得创建 `.omx/state/`。
- 可诊断：每个脚本结束时输出检查摘要，失败时输出下一步人工处理建议。
- Windows PowerShell 5.1 兼容：不得依赖 PowerShell 7-only 语法。
- 路径可移植：新电脑运行时使用 `$env:USERPROFILE`、`%USERPROFILE%` 或脚本参数，不得把 `C:\Users\lenovo` 写成运行时固定路径。
## 10. 实施顺序

确认后按以下顺序实施，避免一次性写入后难以排查：

### Phase 0：创建空模板骨架

- 创建 `D:\PythonProject_General_2`：模板根目录，用来承载本地 Git、OpenSpec、Codex 文档、subagent 配置和初始化脚本。
- 如果 `D:\PythonProject_General_2` 已存在，实施必须停止并输出目录清单；不得覆盖已有目录。
- 写入 `.gitignore`：Git 忽略规则文件，用来排除 `.git/` 以外的缓存、虚拟环境、依赖目录、密钥和本机状态。
- 写入 `README.md`：模板使用说明文件，用来说明新电脑初始化顺序和 subagent-only 边界。
- 写入 `AGENTS.md`：Codex 项目启动规则文件，用来声明本模板只使用 local Git + OpenSpec + native subagents。

### Phase 1：复制 native Codex subagents

- 从 `C:\Users\lenovo\.codex\agents\*.toml` 复制当前本机 24 个 native Codex subagent 配置到 `D:\PythonProject_General_2\.codex\agents\`。
- 复制时只复制 `.toml` 文件，不复制用户级 Codex token、cache、logs 或 `config.toml`。
- 模板运行脚本不得硬编码 `C:\Users\lenovo` 作为新电脑路径；新电脑运行时必须使用 `%USERPROFILE%` 或 `$env:USERPROFILE`。

### Phase 2：写入双语启动文档和治理文档

- 写入 `docs_bilingual/project_startup_summary.md`：ASCII 主版冷启动摘要，用来给无上下文模型提供英文主规则。
- 写入 `docs_bilingual/project_startup_summary.zh-CN.md`：UTF-8 中文对照冷启动摘要，用来给中文维护者提供对照规则。
- 写入 `docs_bilingual/governance/` 下的本地 Git、OpenSpec、subagent-only、双语配对和名称解释治理说明。

### Phase 3：写入初始化脚本和保护脚本

- 写入 `tools/bootstrap-new-pc.ps1`：新电脑工具链安装脚本，用来安装 Git、Python、Node.js、Codex CLI 和 OpenSpec CLI。
- 写入 `tools/bootstrap-local-project.ps1`：本地项目初始化脚本，用来执行 `git init -b main`、OpenSpec 初始化、subagent 安装和模板检查。
- 写入 `tools/install-subagents-user-level.ps1`：subagent 用户级安装脚本，用来把模板内 agents 复制到 `%USERPROFILE%\.codex\agents\`。
- 写入 `tools/backup-codex-config.ps1`：Codex 配置备份脚本，用来备份用户级 `config.toml`，不把机器配置复制到项目目录。
- 写入 `tools/check-codex-config-rewrite.ps1`：Codex 配置重写排查脚本，用来定位 Trae/Codex 是否删除 TOML 注释。

### Phase 4：写入 checker 并本地验证

- 写入 `tools/check_template_health.py`：模板健康检查脚本，用来确认基础目录和关键文件存在。
- 写入 `tools/check_subagent_only_policy.py`：subagent-only 策略检查脚本，用来禁止 `.omx/state/`、LangGraph runtime 和 `omx team` 默认入口。
- 写入 `tools/check_openspec_local_health.py`：OpenSpec 本地健康检查脚本，用来检查 OpenSpec CLI、配置目录和 `openspec validate --all`。
- 写入 `tools/check_bilingual_pairs.py`：双语配对检查脚本，用来检查 ASCII 主版和 UTF-8 中文对照版是否成对。
- 写入 `tools/check_name_clarity_rules.py`：名称解释检查脚本，用来检查代码化名称是否有“是什么、用来做什么”的简短解释。
- 写入 `tools/check_local_git_only_policy.py`：本地 Git-only 检查脚本，用来禁止 GitLab/GitHub remote 和远程 CI 配置。

### Phase 5：最终验收

- 运行所有 checker。
- 确认分发状态不包含 `.git/`、`.omx/state/`、`.venv/`、`node_modules/`、token、`.env`。
- 确认 README 同时包含普通 PowerShell 和 `powershell.exe -NoProfile` 两种启动方式。
- 确认模板不安装、不引用、不默认启用 `oh-my-codex`、`omx team` 或 `langgraph`。
### Phase 6：生成模板清单和实施摘要

- 写入 `TEMPLATE_MANIFEST.md`：模板清单文件，用来列出已创建目录、脚本、checker、subagent 数量、OpenSpec 初始化边界和明确排除项。
- 生成 `.local/bootstrap-report.json`：本地安装报告文件，用来记录当前机器工具版本；该文件必须被 `.gitignore` 忽略。
- 输出最终摘要：说明哪些文件属于模板、哪些文件属于本机状态、哪些认证步骤仍需用户手动完成。
## 11. 新电脑使用步骤

在 Trae 终端中运行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

这条命令允许当前 Windows 用户运行本地 PowerShell 脚本。
如果 Trae 或系统 PowerShell profile 干扰脚本启动，可以改用无 profile 方式执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\bootstrap-new-pc.ps1
```

这条命令用 Windows PowerShell 5.1 的无 profile 模式运行新电脑工具链安装脚本，避免用户 PowerShell profile 影响初始化。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\bootstrap-local-project.ps1
```

这条命令用无 profile 模式运行本地项目初始化脚本，避免 profile 中的编码或启动逻辑干扰模板初始化。

```powershell
cd D:\PythonProject_General_2
```

这条命令进入模板根目录。

```powershell
.\tools\bootstrap-new-pc.ps1
```

这条命令安装 Git、Python、Node.js、Codex CLI、OpenSpec CLI，并配置 pip 阿里云镜像。

```powershell
.\tools\bootstrap-local-project.ps1
```

这条命令初始化本地 Git、OpenSpec、subagents 和模板健康检查。

```powershell
codex
```

这条命令启动 Codex CLI，由用户手动完成认证或配置。

```powershell
git add .
```

这条命令把初始化后的模板文件加入本地 Git 暂存区。

```powershell
git commit -m "Initialize local Codex OpenSpec template"
```

这条命令创建本地 Git 初始化提交。

## 12. 验收标准

确认后实施完成时，需要满足：

- `D:\PythonProject_General_2` 已创建。
- `D:\PythonProject_General_2\TEMPLATE_MANIFEST.md` 存在，并说明模板包含项、排除项和本机状态目录。
- `D:\PythonProject_General_2\.codex\agents\` 包含本机同款 subagent TOML。
- `D:\PythonProject_General_2\tools\bootstrap-new-pc.ps1` 存在且兼容 Windows PowerShell 5.1。
- `D:\PythonProject_General_2\tools\bootstrap-local-project.ps1` 存在且兼容 Windows PowerShell 5.1。
- `D:\PythonProject_General_2\tools\install-subagents-user-level.ps1` 存在且兼容 Windows PowerShell 5.1。
- `D:\PythonProject_General_2\tools\backup-codex-config.ps1` 存在且兼容 Windows PowerShell 5.1。
- `D:\PythonProject_General_2\tools\check-codex-config-rewrite.ps1` 存在且兼容 Windows PowerShell 5.1。
- `D:\PythonProject_General_2\tools\check_template_health.py --root D:\PythonProject_General_2` 通过。
- `D:\PythonProject_General_2\tools\check_subagent_only_policy.py --root D:\PythonProject_General_2` 通过。
- `D:\PythonProject_General_2\tools\check_openspec_local_health.py --root D:\PythonProject_General_2` 通过。
- `D:\PythonProject_General_2\tools\check_bilingual_pairs.py --root D:\PythonProject_General_2` 通过。
- `D:\PythonProject_General_2\tools\check_name_clarity_rules.py --root D:\PythonProject_General_2` 通过。
- `D:\PythonProject_General_2\tools\check_local_git_only_policy.py --root D:\PythonProject_General_2` 通过。
- 分发状态的模板不包含 `.git/`、`.local/`、`.omx/state/`、`.venv/`、`node_modules/`、token、`.env`；运行本地初始化后允许生成 `.git/` 和 `.local/bootstrap-report.json`，但不得配置任何远程 remote。
- 模板文档明确声明不使用 GitLab/GitHub、omx durable team、LangGraph durable backend。
- 模板运行脚本不硬编码 `C:\Users\lenovo`；新电脑路径必须通过 `$env:USERPROFILE`、`%USERPROFILE%` 或脚本参数获得。
- `.local/bootstrap-report.json` 如存在必须被 `.gitignore` 忽略，不得进入本地模板提交。

## 12.1 本地验收命令清单

实施完成后，在 `D:\PythonProject_General_2` 模板根目录运行以下命令：

```powershell
python .\tools\check_template_health.py --root .
```

这条命令运行模板健康检查，确认基础目录、关键文档、subagent 配置和工具脚本存在。

```powershell
python .\tools\check_subagent_only_policy.py --root .
```

这条命令运行 subagent-only 策略检查，确认模板没有启用 omx durable team、LangGraph durable backend 或 `.omx/state/`。

```powershell
python .\tools\check_openspec_local_health.py --root .
```

这条命令运行 OpenSpec 本地健康检查，确认 OpenSpec CLI、OpenSpec 配置目录和 `openspec validate --all` 可用。

```powershell
python .\tools\check_bilingual_pairs.py --root .
```

这条命令运行双语文件配对检查，确认 `docs_bilingual/` 和 `openspec/` 下人为维护的 Markdown 文档有 ASCII 主版和 UTF-8 中文对照版。

```powershell
python .\tools\check_name_clarity_rules.py --root .
```

这条命令运行名称解释检查，确认脚本、路径、命令、变量、profile、subagent 和配置名都有简短用途说明。

```powershell
python .\tools\check_local_git_only_policy.py --root .
```

这条命令运行本地 Git-only 检查，确认模板没有 GitLab/GitHub remote、远程 CI 配置或 remote-first 文档。

```powershell
git status --short
```

这条命令查看本地 Git 工作区状态；在新电脑初始化后可用于确认待提交文件范围。
## 13. 回滚与恢复策略

模板实施和新电脑初始化必须具备可恢复路径：

- 目标目录回滚：如果 `D:\PythonProject_General_2` 创建后发现内容错误，不直接删除；先重命名为 `D:\PythonProject_General_2.backup.<timestamp>`，确认没有需要保留的文件后再人工清理。
- subagent 回滚：`tools/install-subagents-user-level.ps1` 覆盖 `%USERPROFILE%\.codex\agents\*.toml` 前必须备份同名文件到 `%USERPROFILE%\.codex\agents.backup.<timestamp>\`。
- Codex 配置回滚：`tools/backup-codex-config.ps1` 必须能把 `%USERPROFILE%\.codex\config.toml` 备份到 `%USERPROFILE%\.codex\backups\config.toml.<timestamp>.bak`。
- pip 镜像回滚：如果用户不想继续使用阿里云 PyPI 镜像，可运行 `python -m pip config --user unset global.index-url` 取消用户级 pip 默认源。
- pip 超时回滚：如果用户不想保留 pip 超时配置，可运行 `python -m pip config --user unset global.timeout` 取消用户级 pip timeout 设置。
- npm 源回滚：模板默认不修改 npm registry；如果用户手动改过，可运行 `npm config set registry https://registry.npmjs.org/` 恢复官方 npm registry。
- Git 初始化回滚：如果本地 `git init -b main` 后发现不想保留 Git 仓库，只能在确认没有本地提交需要保留后人工删除 `.git/`；脚本不得自动删除 `.git/`。
- OpenSpec 初始化回滚：如果 `openspec init --tools codex --force` 生成内容不符合预期，应先查看 `git status --short`，再按文件清单人工处理；脚本不得自动删除 OpenSpec 产物。
## 14. 风险与防护

- 风险：winget 不存在。防护：脚本停止并提示安装 App Installer，不自动下载未知安装包。
- 风险：npm 国内镜像同步延迟。防护：默认不改 npm registry，只提供可选参数。
- 风险：pip 下载慢。防护：默认设置用户级阿里云 PyPI 镜像。
- 风险：PowerShell 执行策略阻止脚本。防护：README 明确提示 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`。
- 风险：复制旧项目状态。防护：`.gitignore` 和 checker 禁止 `.omx/state/`、`.venv/`、`node_modules/`、`.env`。
- 风险：新电脑误以为启用 omx/langgraph。防护：AGENTS、README、checker 同时声明并验证 subagent-only 模式。
- 风险：模板误带远程 remote。防护：本地 Git-only checker 检查 `git remote -v`、`.gitlab-ci.yml` 和 `.github/workflows/`。
- 风险：脚本重复运行产生重复配置。防护：所有 bootstrap 和 install 脚本必须幂等，写入前先检查目标状态。
- 风险：新电脑脚本硬编码本机用户名。防护：脚本安全要求禁止运行时固定写入 `C:\Users\lenovo`，必须使用用户环境变量或参数。
- 风险：初始化后需要回滚。防护：方案要求目标目录、用户级 subagents、Codex `config.toml`、pip 配置和 npm registry 都有人工可执行的恢复路径。
- 风险：把本机安装报告提交进模板仓库。防护：`.local/` 必须写入 `.gitignore`，`bootstrap-report.json` 只作为本机诊断产物。
- 风险：文档只有中文或只有英文。防护：双语文件配对规则要求 ASCII 主版与 UTF-8 中文对照版同步维护。
- 风险：文档只列名称不解释用途。防护：名称解释规则和 checker 要求脚本、路径、命令、变量、profile、subagent 名称必须附简短说明。

## 15. 待确认事项

请确认以下决策：

1. 是否允许我创建 `D:\PythonProject_General_2` 目录。
2. 是否允许我从 `C:\Users\lenovo\.codex\agents\` 复制本机 subagent TOML 到 `D:\PythonProject_General_2\.codex\agents\`。
3. 是否默认在 `bootstrap-new-pc.ps1` 中配置 pip 用户级阿里云镜像。
4. 是否保持 npm registry 官方默认，不自动切换 npmmirror。
5. 是否由 `bootstrap-local-project.ps1` 自动执行 `git init -b main`。
6. 是否在模板中加入中文为主、英文为辅的双语启动摘要。
7. 是否在模板 checker 中加入双语文件配对检查。
8. 是否在模板 checker 中加入注释与名称解释检查。
9. 是否在模板 checker 中加入本地 Git-only 检查。
10. 是否允许 README 同时给出普通 PowerShell 与 `powershell.exe -NoProfile` 两种执行方式。
11. 是否要求所有初始化脚本保持幂等，并禁止自动安装 `oh-my-codex`、`langgraph` 或创建 `.omx/state/`。
12. 是否要求实施脚本遇到已存在的 `D:\PythonProject_General_2` 时停止而不是覆盖。
13. 是否要求安装用户级 subagents 前备份同名 TOML。
14. 是否生成 `TEMPLATE_MANIFEST.md` 和 `.local/bootstrap-report.json`，并确保 `.local/` 被忽略。

确认后再进入实施。
