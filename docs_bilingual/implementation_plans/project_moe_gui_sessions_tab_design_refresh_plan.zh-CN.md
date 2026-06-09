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

- [ ] 状态：active 治理包已起草；Stage A 仍需先合入本地 `main`，之后才能开始 runtime 实施。
- [ ] Runtime 实施证据等待 Stage B/C/D 执行后补充。
- [ ] 远端发布不在本计划范围内，除非用户明确要求 GitLab/GitHub 发布。

<!-- CURRENT_STATUS_END -->

## 任务积压
<!-- TASK_BACKLOG_START -->

- [x] 起草双语 implementation plan 并登记 registry。
- [ ] 将治理包合入本地 `main`。
- [ ] 使用 Pencil 或 HTML fallback 生成设计辅助产物。
- [ ] 实现紧凑 Sessions 列表、右侧分区控制、三个 MOE 专家模块、category/lens i18n。
- [ ] 完成测试、视觉渲染检查、A 项目安装与 A 项目 preflight 验证。

<!-- TASK_BACKLOG_END -->

## 证据索引
<!-- EVIDENCE_INDEX_START -->

- Pending implementation evidence is expected after Stage A local integration and Stage B/C/D execution.

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
- [ ] 在 runtime 实施前把 Stage A 治理包合入本地 `main`。

### Stage B：设计辅助工具与设计稿产物

- [ ] 验证 Pencil Desktop 进程或安装路径并记录证据。
- [ ] 如本机未安装 Pencil CLI，则通过 npm 安装或记录无法安装的原因。
- [ ] 尝试通过 Pencil MCP/CLI 生成设计稿并导出 PNG。
- [ ] 如果 Pencil 不可用或未认证，生成 HTML/htmltool2 草图并记录 `fallback_reason`；该字段含义是解释 Pencil 未被使用原因的诊断文本，不会被 GUI runtime 消费。
- [ ] 把设计稿和截图产物保存到 `docs_bilingual/designs/project_moe_sessions_tab/`。

### Stage C：Runtime Sessions 页刷新

- [ ] 将 Project MOE GUI toolchain version 从 `0.2.37` 升到下一个 patch 版本。
- [ ] 左侧 session list 改为每个 session 一行的简洁摘要，并显示清晰的 session 总数。
- [ ] `Session / Created / Updated / Directory / Branch / Conversation` 全量身份字段只保留在右侧详情卡。
- [ ] 右侧拆分为会话详情、MOE 状态/操作、MOE 分类/镜头选择三个独立区域。
- [ ] 镜头选择区独立滚动，并且不需要滚动整个详情区才能看到和操作。
- [ ] 将 MOE 分类重组为三个用户指定的专家模块，同时保留现有 lens id。
- [ ] 为 category/lens 增加中文、英文、中英对照显示标签。
- [ ] 保留 category 到 lens、lens 到 category 的双向 tri-state 联动。

### Stage D：验证与 A 项目验收

- [ ] 增加或更新测试，覆盖 compact list 文本、详情块完整性、三个专家模块、i18n 标签、tri-state 联动。
- [ ] 运行 Project MOE GUI focused tests 和必要的完整 toolchain tests。
- [ ] 对 Sessions 页运行 `1180x720`、`1366x768`、`1440x900` 视觉渲染检查。
- [ ] 将更新后的 toolchain 安装到 `D:/PythonProject_paper_suggest`。
- [ ] 运行 A 项目 `project-moe-gui.cmd --preflight --json` 并确认 `token=ok`。
- [ ] 确认 A 项目仍只显示 5 个真实 target-project session。
- [ ] 使用中文 commit message 提交 A 项目受管理安装产物。

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
