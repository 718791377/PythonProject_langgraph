---
doc_id: general_template_phase0_update_patch_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-04-25
phase: 0
---

# D:\PythonProject_General Phase 0 模板更新补丁实施计划

> 冷启动契约：本文是自包含实施计划。一个没有任何聊天上下文的新 Codex 会话，只要读取本文、`README.zh-CN.md`、`AGENTS.md`、`project_startup_summary.zh-CN.md` 和 `docs_bilingual/governance/template_completion_protocol.zh-CN.md`，就可以安全实施 Phase 0 补丁。

## 双语对齐状态

- 英文 ASCII 主版：`docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md` 是 implementation source of truth。
- 中文对照版：本文。
- 对齐规则：范围、安全规则、交付物、验证命令和验收标准必须保持同步。
- 当前结论：Phase 0 是面向模板根目录的安全性与可测试性补丁，不是完整 profile、skills governance、browser、web 或 orchestration 功能 rollout。
- 名称解释规则：凡是列出脚本、路径、命令、变量或 profile 名称，后面都要补一句简短解释，确保冷启动读者知道它是什么、用来做什么。

## 1. 目标

为 `D:\PythonProject_General` 创建一个小型、可 review、可回滚的 Phase 0 补丁，让模板本身在加入更大的 profile、skills、browser、web 或 orchestration 能力之前，先具备更好的维护安全性和可验证性。

该补丁应能让模板在三种状态下更容易验证：

1. master template root：`D:\PythonProject_General`
2. 由 `new-openspec-project.ps1` 新生成的项目
3. 一个只知道生成后仓库文件、没有聊天上下文的新 Codex 会话

## 2. 当前观察到的状态

截至 2026-04-25，模板根目录已经包含：

- OpenSpec 双语仓库 starter 文件
- `AGENTS.md`：Codex 会话进入仓库后优先遵守的仓库级操作契约。
- 英文和中文 startup summary
- OpenSpec governance 文档和 `strict-governance` schema 文件：定义结构化变更流程、review gate 和 approval gate 的规则层。
- GitHub Actions 和 GitLab CI guard surface
- git hook 模板
- `new-openspec-project.ps1`：把该模板复制并 hydrate 成新项目的 PowerShell 生成器。
- Windows Explorer 和 PyCharm launcher helper：从右键菜单或 PyCharm External Tool 调用同一个项目生成器的入口。
- 根目录后台进程入口：`project-background.cmd`、`project-background.ps1`、`project-background.json`，用于启动、检查、查看日志和停止项目本地后台进程。
- `tools/project_background.py`：后台进程入口实际调用的 Python supervisor。
- `tools/background_keepalive.py`：默认 harmless keepalive 进程，用于在真实服务或 daemon 尚不存在时验证后台持久化能力。
- OpenSpec 验证和 enforcement helper

重要发现：

- master template root 目前不是 git 仓库。
- master template root 中保留 raw placeholder 是正常现象，因为它是生成项目的模板源。
- 生成后的测试项目在 hydrate 后不应该再有 unresolved placeholders。
- background-process 支持已经存在，应在生成后项目中做 smoke test。
- 模板根目录 `.gitignore` 对 Python、Node、OpenSpec、Codex 和本地 runtime 产物来说过于简短。

## 3. Phase 0 范围

Phase 0 只处理模板可维护性与安全基线。

范围内：

1. 新增或更新 Phase 0 补丁计划文档。
2. 在 `docs_bilingual/docs_registry.yaml` 中注册本文档。
3. 为 template root 更新更完整的 `.gitignore`，覆盖 local-only runtime 和工具产物。
4. 增加模板 hydration smoke-test 脚本：创建临时生成项目，并验证生成项目而不是 master template root 没有 unresolved placeholders。
5. 文档化 master-template placeholder 与 generated-project placeholder 的区别。
6. 在生成项目 smoke test 中验证根目录 background entry point。
7. 保持补丁足够小，便于 focused review。

Phase 0 不做：

- 不实现 profile-aware project generation
- 不实现 skills inventory 或 skills governance checks
- 不删除、禁用或移动用户级 skills
- 不修改 `C:\Users\lenovo\.codex\config.toml`，这是仓库外的用户级 Codex 配置文件。
- 不修改 Vercel、GitHub、browser 或 OpenSpec plugin 安装
- 不修改真实项目仓库，例如 `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI`、`D:\project` 或 `D:\PythonProject_langgraph`
- 不要求 template root 已经拥有 GitLab 或 GitHub remote
- 不重设计 `strict-governance`，它是当前模板使用的仓库级 OpenSpec review / approval schema。

## 4. 安全规则

1. 除 smoke test 创建的临时目录外，不编辑生成后的子项目。
2. 不删除 user-level Codex skills 或 plugin cache。
3. 不修改全局 Codex、Git、npm、Python 或 PowerShell 配置。
4. 不假设 master template root 应该通过 placeholder check；只有生成后项目应该通过 placeholder check。
5. 不在没有收尾或隔离到 `.project-runtime/` 的情况下启动长期后台进程。
6. 不把 `D:\PythonProject_langgraph` 的项目事实写进通用模板。
7. 英文 implementation plan 文件必须保持 ASCII-only。
8. 中文 companion 文件必须注册，并随英文主版同步更新。

## 5. 交付物

### 5.1 文档

创建并维护：

- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md`：英文 ASCII Phase 0 实施 source of truth。
- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md`：中文对照版，用来解释同一套实施范围和安全规则。

更新：

- `docs_bilingual/docs_registry.yaml`：双语文档注册表，用于让冷启动会话和检查脚本找到这份计划。

如果实际补丁触及相关表面，可选更新：

- `README.md`：英文模板概览和操作者使用入口。
- `README.zh-CN.md`：中文模板概览和操作者使用入口。
- `docs_bilingual/governance/template_completion_protocol.md`：英文模板补完规则，说明如何把模板默认值替换成真实项目事实。
- `docs_bilingual/governance/template_completion_protocol.zh-CN.md`：模板补完规则的中文对照版。

### 5.2 模板 ignore 规则

更新 `.gitignore`，至少忽略：

```gitignore
.omx/
.tmp/
__pycache__/
*.pyc
.pytest_cache/
.venv/
node_modules/
openspec-guard-report.json
.project-runtime/
```

ignore 条目含义：

- `.omx/`：仓库本地 durable orchestration state，不应提交。
- `.tmp/`：模板 hydration 测试和其他临时输出使用的 scratch 目录。
- `__pycache__/` 和 `*.pyc`：Python 本地运行生成的字节码缓存。
- `.pytest_cache/`：pytest 生成的本地测试缓存。
- `.venv/`：项目本地 Python 虚拟环境。
- `node_modules/`：Node.js 依赖安装目录。
- `openspec-guard-report.json`：本地或 CI 生成的 guard 报告。
- `.project-runtime/`：后台进程的 pid、日志和 heartbeat 状态目录。

### 5.3 模板 hydration smoke test

新增脚本，例如：

- `tools/test_template_hydration.py`：建议新增的 smoke-test runner，用于生成临时项目并验证生成结果。

最低行为要求：

1. 定位 master template root
2. 在 `.tmp/` 下创建临时输出目录；`.tmp/` 是模板本地 scratch 目录，应被 git ignore。
3. 运行 `new-openspec-project.ps1 -ProjectName TemplateSmokeTest -DestinationRoot <temp> -SkipOfficialOpenSpecBootstrap`；该命令生成测试项目，但不刷新官方 OpenSpec managed files。
4. 在生成项目中运行 `python tools/check_placeholders.py .`；该命令验证模板 hydrate 后已经替换 raw placeholders。
5. 断言生成项目中的 `tools/project_background.py` 存在且非空；该文件是每个新项目必须携带的后台 supervisor。
6. 运行 `project-background.cmd doctor` 或等价的安全检查；该命令检查后台入口可用性，但不留下长期后台进程。
7. 除非传入 `--keep-temp`，否则清理临时输出；`--keep-temp` 用于调试失败的 smoke test。
8. 失败时返回非零 exit code
9. 支持 `--json` 输出；该参数让 CI 或 Codex 会话读取机器可解析报告。

推荐命令：

```powershell
python tools/test_template_hydration.py --root . --json
```

这条命令会在当前模板根目录上运行 hydration smoke test，并输出 JSON 报告。

### 5.4 Guard surface 兼容性记录

Phase 0 应记录但不一定修复本模板和 `D:\PythonProject_langgraph` guard helper 能力之间的差异。

已知后续需要检查的差异：

- 一部分 `D:\PythonProject_langgraph` helper scripts 支持 `--json`
- 一部分 `D:\PythonProject_General` helper scripts 当前还不支持 `--json`

Phase 0 可以先记录 inventory note；后续阶段再统一增加 JSON 输出。

## 6. 实施步骤

1. 如果缺少 `docs_bilingual/implementation_plans/`，先创建目录；该目录用于保存非 OpenSpec change artifact 的实施计划。
2. 新增英文与中文 Phase 0 plan 文件。
3. 将这组 plan 注册到 `docs_bilingual/docs_registry.yaml`；该文件是双语文档索引。
4. 更新 `.gitignore`，加入 local runtime 和工具产物规则，避免日志、缓存和临时目录进入提交。
5. 新增 `tools/test_template_hydration.py`；该脚本负责测试生成项目的 hydrate 结果。
6. 运行模板 hydration smoke test。
7. 对新 plan 文件做定向检查：
   - 英文文件 non-ASCII 数量为 0。
   - 两个文件都没有 trailing whitespace。
   - 两个文件都已注册到 `docs_bilingual/docs_registry.yaml`，即文档检查使用的 registry。
8. 通过 smoke test 运行生成项目的 placeholder check。
9. 如果 template root 已初始化为 git 仓库，则在 feature branch 上提交 Phase 0 补丁。

## 7. 验证命令

除非特别说明，均在 `D:\PythonProject_General` 下运行。

```powershell
python tools/test_template_hydration.py --root . --json
python tools/check_placeholders.py .
```

预期解释：

- `tools/test_template_hydration.py` 应该对生成项目通过。
- 在 master template root 直接运行 `tools/check_placeholders.py .` 可能会报告 raw placeholders；在 checker 具备 template-root 模式之前，这是预期结果，或者应只对生成项目运行该检查。
- `--root .` 表示把当前目录作为模板根目录。
- `--json` 表示输出机器可解析报告，而不是只输出人类可读文本。

可选检查：

```powershell
python tools/verify_official_openspec.py --root .
python tools/enforce_openspec_policy.py --root .
python tools/run_openspec_guard.py --root .
```

可选命令含义：

- `tools/verify_official_openspec.py`：检查官方 OpenSpec managed files 和基础验证面是否存在。
- `tools/enforce_openspec_policy.py`：检查仓库本地 OpenSpec policy 是否满足。
- `tools/run_openspec_guard.py`：运行 hooks 或 CI 使用的组合 guard 流程。

如果 official OpenSpec bootstrap 改写了 managed files，必须显式检查并提交这些 managed files，不要隐藏 drift。

## 8. 验收标准

Phase 0 满足以下条件才算完成：

- 双语 Phase 0 plan 文件存在
- plan 文件已注册到 `docs_bilingual/docs_registry.yaml`，从而让文档检查能找到中英文版本。
- `.gitignore` 覆盖常见 local-only runtime 和 tooling artifacts，避免这些本地文件被提交。
- 模板 hydration smoke test 存在，并能生成测试项目
- 生成的测试项目通过 placeholder scanning
- 生成项目的 background entry files 存在且非空
- 英文 implementation plan 文件保持 ASCII-only
- 没有修改 user-level Codex skills、plugin cache 或全局配置文件
- 没有修改任何现有真实项目仓库

## 9. 回滚计划

如果 Phase 0 引入问题：

1. revert Phase 0 commit 或 patch
2. 只删除 `.tmp/` 下由测试创建的临时目录
3. 不删除 user-level skills 或 plugin cache
4. 除非用户明确指出某个生成项目只是测试输出，否则不删除真实生成项目
5. 回滚后重新运行一次干净的 template hydration smoke test

## 10. 后续阶段交接

Phase 0 之后，后续阶段可以继续实现：

- profile-aware project generation：`core` 表示默认非 Web 项目，`browser` 表示浏览器自动化项目，`web` 表示前端和部署项目，`python-cli` 表示 Python 命令行工具，`agent-service` 表示 daemon 或 worker 服务，`orchestration` 表示 Codex 或 durable-team 编排仓库，`full` 表示临时广泛发现模式。
- skills governance inventory 和 profile registry
- 为 `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 等项目保留 browser automation profile
- 所有 guard helper 的 JSON 输出对齐
- 发布流程 profile：GitLab-first、GitHub-PR、local-only
- OMX 和 LangGraph 的 repo-local durable state 隔离默认规则
