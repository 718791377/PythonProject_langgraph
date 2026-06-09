---
doc_id: project_moe_gui_sessions_tab_design_refresh_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_moe_gui_sessions_tab_design_refresh_plan.md
created_at: 2026-06-09
updated_at: 2026-06-09
scope: project_moe_gui_sessions_tab_design_refresh
parent_plan: docs_bilingual/implementation_plans/project_moe_gui_product_ui_function_rebuild_plan.zh-CN.md
related_plans:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
  - docs_bilingual/implementation_plans/project_moe_gui_product_ui_function_rebuild_plan.zh-CN.md
  - docs_bilingual/implementation_plans/project_moe_gui_enhancement_roadmap_plan.zh-CN.md
---

# Project MOE GUI Sessions 页设计刷新计划

## 0. 执行结论

本 active implementation_plan 承接已验收的 `0.2.37` session 身份修复，在 Project MOE GUI 的 Sessions 页继续做一次可视化与交互刷新。下一轮 runtime 切片必须让 Sessions 页更容易扫描和操作：左侧 session list 改为每个会话一行的简洁列表，右侧把会话详情、MOE 状态操作、MOE 分类与镜头选择分开，MOE 分类重组为三个双语专家模块，并让分类和镜头勾选项跟随现有中文 / English / 中英对照语言模式。

本计划优先使用 Pencil 作为设计稿辅助面。当前本机已发现 Pencil Desktop，但 Pencil CLI 可能需要安装和认证；如果 Pencil CLI、Pencil MCP 或 Desktop 连接不可用，则使用 HTML/htmltool2 草图兜底并记录 fallback reason。Pencil/htmltool2 只作为设计确认辅助，不进入 Project MOE GUI 运行时依赖；正式产品 GUI 仍使用 PySide6/QFluentWidgets。

## 当前状态
<!-- CURRENT_STATUS_START -->

- [x] 状态：Stage A 治理包已合入本地 `main`，提交为 `f1bbbefd31922eef729a6d414681df0bbf7212a8`。
- [x] Stage B/C runtime 实现已完成，并已合入 B 本地 `main`，提交为 `8dfe010f13118d3cd4b5aa78cc5869ca4e78bf57`。
- [x] feature worktree `implement-project-moe-sessions-tab-design-refresh-20260609` 已在本地 main 集成后安全清理；回滚 ref 为 `refs/backup/local-main/20260610-014207-before-implement-project-moe-sessions-tab-design-refresh-20260609`。
- [x] Pencil MCP 被 `transport not connected to app: trae_cn` 阻塞；HTML fallback 草图与导出 PNG 已记录到 `docs_bilingual/designs/project_moe_sessions_tab/`。
- [x] Focused toolchain tests 已通过：`python test\project_moe_gui_toolchain.test.py` 返回 101/101 OK。
- [x] B 仓库 Sessions 视觉渲染检查已覆盖 default、long-content、dense-sessions 三组夹具，以及 `1180x720`、`1366x768`、`1440x900` 三个尺寸。
- [x] A 目标项目 `D:/PythonProject_paper_suggest` 安装已完成；受管理安装产物已提交到 A 本地 `main`，提交为 `8d1449f`，toolchain 版本为 `0.2.38`。
- [x] A 目标项目 `project-moe-gui.cmd --preflight --json` 已通过，返回 `token=ok`，Phase 1 readiness 为 `ready`，QFluentWidgets import 为 `ok`，会话数量为 `5`。
- [x] A 目标项目 Sessions 视觉渲染检查已覆盖 `1180x720`、`1366x768`、`1440x900`，返回 `token=ok`。
- [x] 远端发布不在本计划范围内，且未执行。

<!-- CURRENT_STATUS_END -->

## 任务积压
<!-- TASK_BACKLOG_START -->

- [x] 起草双语 implementation plan 并登记 registry。
- [x] 将治理包合入本地 `main`。
- [x] 使用 Pencil 或 HTML fallback 生成设计辅助产物。
- [x] 实现紧凑 Sessions 列表、右侧分区控制、三个 MOE 专家模块、category/lens i18n。
- [x] 在 B 仓库完成 focused tests 与 Sessions 视觉渲染检查。
- [x] 将 runtime 包合入 B 本地 `main` 并清理 feature worktree。
- [x] 将刷新后的受管理 GUI 产物安装到 `D:/PythonProject_paper_suggest` 并运行 A preflight。
- [x] 对已安装到 A 的 Sessions 页运行视觉渲染验收。

<!-- TASK_BACKLOG_END -->

## 证据索引
<!-- EVIDENCE_INDEX_START -->

- 治理包本地 main 合入：`f1bbbefd31922eef729a6d414681df0bbf7212a8`。
- Runtime 本地 main 合入：`8dfe010f13118d3cd4b5aa78cc5869ca4e78bf57`（runtime implementation commit）。
- Runtime 回滚 ref：`refs/backup/local-main/20260610-014207-before-implement-project-moe-sessions-tab-design-refresh-20260609`。
- Runtime 清理证据：completed claim `D:/PythonProject_langgraph/.omx/session-claims/completed/implement-project-moe-sessions-tab-design-refresh-20260609.json` 记录了 cleaned worktree 和 deleted branch。
- 设计 fallback 原因：`docs_bilingual/designs/project_moe_sessions_tab/fallback_reason.md`。
- HTML 草图：`docs_bilingual/designs/project_moe_sessions_tab/sessions_tab_layout.html`。
- HTML 草图截图：`docs_bilingual/designs/project_moe_sessions_tab/sessions_tab_layout.png`。
- Pencil MCP 阻塞证据：`get_editor_state(include_schema=true)` 返回 `transport not connected to app: trae_cn`。
- Pencil CLI/npm 证据：`npm view '@pencil.dev/cli' name version --json` 返回 `@pencil.dev/cli` `0.2.7`；`htmltool2` 包查询返回 npm `E404`。
- Focused tests：`python test\project_moe_gui_toolchain.test.py` -> `Ran 101 tests ... OK`。
- B 仓库 local gate：runtime feature worktree 中运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600 -Json` 通过；`tools/complete_local_flow_to_remote_gate.py --execute` 本地合入后在主目录再次运行 post-merge local gate 通过。
- B 仓库 Sessions 视觉渲染检查：
  - default 夹具：`python tools\project_moe_gui_toolchain\visual_render_check.py --view-model-json .tmp\project_moe_sessions_view_model.json --shell widgets --sections sessions --size 1180x720 --size 1366x768 --size 1440x900 --fixture-profile default --json` -> `token=ok`。
  - long-content 夹具：同命令改为 `--fixture-profile long-content` -> `token=ok`。
  - dense-sessions 夹具：同命令改为 `--fixture-profile dense-sessions` -> `token=ok`。
- A 目标项目安装：`python .\tools\project_moe_gui_toolchain\update_project_moe_gui.py --target-project D:\PythonProject_paper_suggest --json` -> `token=ok`，目标版本 `0.2.38`。
- A 目标项目受管理安装提交：`8d1449f 更新：升级论文 Project MOE GUI 到 0.2.38`。
- A 目标项目 preflight：`D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json` -> `token=ok`，`phase1_readiness_gate.readiness_status=ready`，`session_count.value=5`。
- A 目标项目 Sessions 视觉渲染：`python tools\project_moe_gui_toolchain\visual_render_check.py --target-project D:\PythonProject_paper_suggest --shell widgets --sections sessions --size 1180x720 --size 1366x768 --size 1440x900 --fixture-profile default --json` -> `token=ok`。
- 远端发布：未执行；B 本地 `main` 在明确远端发布授权前有意领先 `gitlab/main`。

<!-- EVIDENCE_INDEX_END -->

## 1. 当前状态

- B 仓库 source of truth：`tools/project_moe_gui_toolchain/`。
- A 目标项目：`D:/PythonProject_paper_suggest`，用于真实安装与验收。
- 当前已接受的 toolchain baseline：`0.2.37`。
- 现有 Sessions list 可能重复显示过多会话详情，导致用户难以快速看清会话数量。
- 右侧区域仍把身份详情、MOE 状态控制、分类选择、镜头选择混在一个滚动区域中。
- 当前 MOE 分类模型仍过粗，不符合用户要求的三个专家模块。
- 产品 i18n 已覆盖主要 UI 标签，但 MOE category 和 lens checkbox 文本也必须支持中文 / English / 中英对照。

## 2. Source of Truth 与边界

- Runtime source of truth 固定在 B 仓库 `tools/project_moe_gui_toolchain/`。
- A 项目只接收受管理安装产物和验收提交。
- Pencil `.pen`、HTML 草图、导出截图统一放在 `docs_bilingual/designs/project_moe_sessions_tab/`。
- Pencil/htmltool2 不得成为目标项目运行时依赖。
- 不把 A 项目的私有 prompt 或 `MOE.md` 内容复制进 B 仓库或设计稿。
- 本计划不触发 GitLab/GitHub 远端发布，除非用户另行明确要求。

## 3. 实施清单

### Stage A：治理包

- [x] 新增本 active implementation_plan 的英文版和中文版。
- [x] 在 `docs_bilingual/docs_registry.yaml` 注册本计划。
- [x] 在 runtime 实施前把 Stage A 治理包合入本地 `main`。证据：`f1bbbefd31922eef729a6d414681df0bbf7212a8`。

### Stage B：设计辅助工具与设计稿产物

- [x] 验证 Pencil Desktop 进程或安装路径并记录证据。证据：Stage B 执行期间本机存在 `Pencil` 进程。
- [x] 如本机未安装 Pencil CLI，则通过 npm 安装或记录无法安装的原因。证据：npm metadata 查询返回 `@pencil.dev/cli` 版本 `0.2.7`；HTML fallback 路径不要求全局 CLI 安装。
- [x] 尝试通过 Pencil MCP/CLI 生成设计稿并导出 PNG。证据：Pencil MCP 返回 `transport not connected to app: trae_cn`，随后使用 HTML screenshot export 兜底。
- [x] 如果 Pencil 不可用或未认证，生成 HTML/htmltool2 草图并记录 `fallback_reason`；该字段含义是解释 Pencil 未被使用原因的诊断文本，不会被 GUI runtime 消费。
- [x] 把设计稿和截图产物保存到 `docs_bilingual/designs/project_moe_sessions_tab/`。

### Stage C：Runtime Sessions 页刷新

- [x] 将 Project MOE GUI toolchain version 从 `0.2.37` 升到下一个 patch 版本：`0.2.38`。
- [x] 左侧 session list 改为每个 session 一行的简洁摘要，并显示清晰的 session 总数。
- [x] `Session / Created / Updated / Directory / Branch / Conversation` 全量身份字段只保留在右侧详情卡。
- [x] 右侧拆分为会话详情、MOE 状态/操作、MOE 分类/镜头选择三个独立区域。
- [x] 镜头选择区独立滚动，并且不需要滚动整个详情区才能看到和操作。
- [x] 将 MOE 分类重组为三个用户指定的专家模块，同时保留现有 lens id。
- [x] 为 category/lens 增加中文、英文、中英对照显示标签。
- [x] 保留 category 到 lens、lens 到 category 的双向 tri-state 联动。

### Stage D：验证与 A 项目验收

- [x] 增加或更新测试，覆盖 compact list 文本、详情块完整性、三个专家模块、i18n 标签、tri-state 联动。
- [x] 运行 Project MOE GUI focused tests 和必要的完整 toolchain tests。证据：`python test\project_moe_gui_toolchain.test.py` 返回 101/101 OK。
- [x] 对 Sessions 页运行 `1180x720`、`1366x768`、`1440x900` 视觉渲染检查，并覆盖 default、long-content、dense-sessions 三组夹具。
- [x] 在 B 本地 `main` 合入后，将更新后的 toolchain 安装到 `D:/PythonProject_paper_suggest`。证据：installer 返回 `token=ok`，目标版本为 `0.2.38`。
- [x] 安装后运行 A 项目 `project-moe-gui.cmd --preflight --json` 并确认 `token=ok`。证据：preflight 返回 `token=ok`，Phase 1 readiness 为 `ready`。
- [x] 安装后确认 A 项目仍只显示 5 个真实 target-project session。证据：preflight `session_count.value=5`。
- [x] 如 A 项目存在受管理安装产物变更，使用中文 commit message 提交。证据：A 本地提交 `8d1449f 更新：升级论文 Project MOE GUI 到 0.2.38`。

## 4. 验收标准

- Sessions list 每个可见 session 只显示紧凑一行，并有明确总数。
- 左侧列表行不再重复完整详情块。
- 右侧详情卡仍包含 `Session`、`Created`、`Updated`、`Directory`、`Branch`、`Conversation`。
- MOE 操作按钮与 lens/category 控件在视觉上与详情卡分离。
- 用户无需滚动详情文本即可进入 lens/category 选择区。
- 显示层 MOE 分类精确为用户要求的三个双语模块。
- Category 与 lens checkbox 标签遵循当前语言模式。
- Category 与 lens 选择保持双向联动。
- 如果 Pencil 可用，则有 Pencil 设计稿或截图；如果不可用，则有 HTML fallback 产物和明确 fallback reason。
- B 仓库本地 `main` 包含 runtime 实施；A 项目本地 `main` 包含刷新后的受管理安装产物。

## 5. 风险控制

- Pencil CLI 安装或认证失败时，使用 HTML/htmltool2 fallback，不阻塞 runtime 实施。
- MCP 无法连接 Pencil Desktop 时，记录 MCP blocker，并继续尝试 CLI 或 HTML fallback。
- 产品 GUI 运行时仅保留 QFluentWidgets/PySide6。
- A 项目写入范围限于 Project MOE GUI 受管理安装产物与验收提交。
- 没有用户明确远端发布授权时，停在本地 main 集成后的 remote-publication gate。
