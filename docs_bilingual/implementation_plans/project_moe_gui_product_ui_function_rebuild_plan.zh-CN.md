---
doc_id: project_moe_gui_product_ui_function_rebuild_plan
lang: zh-CN
status: active
doc_class: implementation_plan
created_at: 2026-06-08
source_plan: project_moe_gui_product_ui_function_rebuild_confirmed
related_plans:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
  - docs_bilingual/implementation_plans/project_moe_gui_enhancement_roadmap_plan.zh-CN.md
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md
---

# Project MOE GUI 产品级 UI / 功能 / Session 对账重构实施方案

## 0. 执行结论

本方案已将 Project MOE GUI 从原 `0.2.31` 的 QML Material 工程控制台升级并验收为 `0.2.32` 产品级本地 GUI。目标是让每个项目拥有只显示和控制自身 session 的 MOE 控制台，每个 session 可以独立开关 MOE，并通过具体 MOE / MOE 分类联动选择最终生效的专家镜头。GUI 需要支持 English / 中英对照 / 中文三种语言，默认中英对照。

本方案同时增强 Expert Workbench：它仍然是安全交接台，不直接启动 Codex、subagent、durable team、LangGraph workflow 或模型 API；它只生成、保存、复制、导出 handoff package，并提供执行前检查建议。

本方案新增 session identity / discovery / reconciliation 能力：GUI 必须显示完整 session id，尝试只读发现本机 Codex 已有会话并与项目 MOE state 做映射，禁止仅凭 session 名称包含 `smoke`、`test`、`fixture`、`generated` 等词就隐藏或降级普通会话。`smoke-session-final` 这类没有显式测试元数据的普通会话必须默认显示。

## 1. 当前状态与问题

### 1.1 当前已具备

- B 仓库 source of truth：`tools/project_moe_gui_toolchain/`。
- A 目标项目：`D:\PythonProject_paper_suggest` 已安装并验收 Project MOE GUI `0.2.32`。
- A 安装检查显示 installed/source toolchain 版本一致。
- 当前 GUI 已有：项目默认开关、session 开关、session lens/category 字段保存、Workbench handoff package 草稿/导出、多尺寸视觉渲染检查，以及 QFluentWidgets / Qt Widgets 产品级主界面。
- 共享 PySide6 runtime 位于 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`，消费项目默认不安装 PySide6。
- QFluentWidgets runtime 检查和 GPLv3/商业双许可 manifest 已存在；当前 primary shell 是 `qfluentwidgets-qtwidgets`，QML Material 仅作为显式 fallback。

### 1.2 当前问题

- 当前主界面仍是 QML Material 工程控制台，视觉变化不明显，不满足产品级 UI 目标。
- 当前 `Projects` 页面容易让目标项目 GUI 被误解为可跨项目控制。
- 当前界面基本全英文，没有语言切换。
- 当前 MOE 分类与具体 lens 是两个独立选择区，分类勾选不会自动联动具体 lens。
- 当前 Workbench 更像文本包生成器，缺少更明确的 session 绑定、历史复用、执行前检查和最终生效 MOE 解释。
- 当前 Sessions 列表只显示 MOE state 中已登记 session，不等于所有 Codex 已有会话；缺少会话映射、完整 id、来源解释和对账信息。
- 当前不得用名称启发式隐藏 session；`smoke-session` / `smoke-session-final` 可能是普通真实会话。


## 当前状态
<!-- CURRENT_STATUS_START -->

- [x] 需求已冻结：产品级 Fluent Widgets 主界面、默认中英对照、项目内 session 范围、session 对账、MOE 分类三态联动、Workbench 安全交接台。
- [x] 0.2.31 基线已确认：A 项目曾安装 QML 主体验。
- [x] B runtime 产品级重构已在源码完成、验证并合入本地 main：`e041f59`。
- [x] A 目标项目安装与可见启动验收已完成：A 本地 main 提交 `b4c5333`。

<!-- CURRENT_STATUS_END -->

## 任务积压
<!-- TASK_BACKLOG_START -->

- [x] Slice 0：新建本产品级重构方案。
- [x] Slice 1：Fluent Widgets 主界面骨架。
- [x] Slice 2：i18n 与语言切换。
- [x] Slice 3：项目边界与默认页面收敛。
- [x] Slice 4：Session 列表、Codex 发现与对账。
- [x] Slice 5：MOE lens/category 三态联动。
- [x] Slice 6：Workbench 安全交接台增强。
- [x] Slice 7：视觉与自动化验证。
- [x] Slice 8：A 目标项目安装验收。

<!-- TASK_BACKLOG_END -->

## 证据索引
<!-- EVIDENCE_INDEX_START -->

- B source of truth：`tools/project_moe_gui_toolchain/`。
- A 目标项目：`D:/PythonProject_paper_suggest`。
- A 目标项目 Slice 8 前安装基线：`0.2.31`。
- A 目标项目 Slice 8 后安装版本：`0.2.32`，A 本地 main 提交 `b4c5333`。
- B 源码 runtime Slice 1-7 后版本：`0.2.32`，B 本地 main 提交 `e041f59`。
- Slice 1-7 后默认源码 shell：QFluentWidgets / Qt Widgets (`qfluentwidgets-qtwidgets`)；QML Material 保留为显式 fallback。
- B 定向测试证据：`python .\test\project_moe_gui_toolchain.test.py` -> `Ran 91 tests ... OK`。
- B 视觉证据：`visual_render_check.py` product Widgets shell，profiles `long-content` 与 `dense-sessions`，尺寸 `1180x720`、`1366x768`、`1440x900`，页面 `overview sessions workbench diagnostics settings` -> `ok=true`。
- Slice 8 安装检查：`python tools\project_moe_gui_toolchain\check_project_moe_gui_install.py --target-project D:\PythonProject_paper_suggest --json` -> `ok=true`、`status=up_to_date`、installed/target version 均为 `0.2.32`。
- Slice 8 launcher preflight：`D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json` -> `ok=true`、`product_shell_contract=project-moe-gui-product-widgets-v1`、`primary_shell=qfluentwidgets-qtwidgets`、`qfluentwidgets_status.ok=true`、Phase1 readiness `ready`。
- Slice 8 A 视觉证据：`visual_render_check.py --target-project D:\PythonProject_paper_suggest --shell widgets`，profiles `long-content` 与 `dense-sessions`，尺寸 `1180x720`、`1366x768`、`1440x900`，页面 `overview sessions workbench diagnostics settings` -> `ok=true`；截图目录 `.tmp/paper_suggest_moe_visual_long/` 与 `.tmp/paper_suggest_moe_visual_dense/`。
- Slice 8 可见启动 smoke：`PROJECT_MOE_GUI_VISIBLE_SMOKE_EXIT_MS=3000` + `D:\PythonProject_paper_suggest\project-moe-gui.cmd --allow-visible` -> exit code `0`。
- Slice 8 A Git 状态：`git -C D:\PythonProject_paper_suggest status --short --branch` -> `## main`，无脏文件。
- 当前主体验：QFluentWidgets / Qt Widgets (`qfluentwidgets-qtwidgets`)；QML Material 仅为显式 fallback。
- 关键验收会话：`smoke-session-final` 必须默认显示，除非存在显式测试元数据。

<!-- EVIDENCE_INDEX_END -->

## 2. 目标与非目标

### 2.1 目标

1. 每个项目 GUI 默认只显示和控制自己项目的 session。
2. 每个 session 可独立开启/关闭 MOE。
3. 每个 session 可选择具体 MOE 或 MOE 分类；分类与具体 MOE 必须三态联动。
4. session 运行时根据 GUI 写入的 MOE 状态自行选择合适的 MOE 范围。
5. GUI 支持 English / 中英对照 / 中文，默认中英对照。
6. MOE 分类升级为更清晰的产品级分类，并展示说明和包含 lens。
7. Workbench 升级为安全交接台：生成、保存、复制、导出 handoff package，并提供执行前检查。
8. Sessions 页支持和 Codex 已有会话的只读发现/映射/对账。
9. 安装到 A 项目，运行 preflight、视觉截图、可见启动验证，并提交 A 本地 git。

### 2.2 非目标

- GUI 不直接启动 Codex、subagent、durable team、LangGraph workflow 或任何模型 API。
- A 项目 GUI 不写其他项目状态。
- 不再把多项目运营页放进普通目标项目 GUI 默认导航。
- 不按 session 名称启发式隐藏普通 session。
- 不把 QFluentWidgets 做公开商业分发；GPLv3 本地使用边界之外必须另开许可证/打包方案。
- 不推送 GitLab/GitHub；远端发布必须另有当前用户明确授权。

## 3. 运行时边界

### 3.1 项目边界

- 目标项目 GUI 只读写当前目标项目的 `.omx/state/<namespace>/`。
- A 项目 GUI 只读写 `D:\PythonProject_paper_suggest\.omx\state\thesis_moe\`。
- 默认不显示 `Projects` 页面；如保留多项目扫描能力，只能通过 B 仓库维护台或隐藏诊断入口展示只读结果。
- 每次写操作必须通过目标项目 Phase 1 CLI contract，不直接改 JSON。

### 3.2 Session 边界

- session MOE 开关只影响选中的 session。
- 项目默认状态和 session override 必须分开展示。
- `enabled=false` 时，该 session 不使用 MOE。
- `enabled=true` 且无 lens/category 选择时，表示全部 MOE 可用。
- `enabled=true` 且有 lens/category 选择时，只使用最终展开后的 lens 集合。

### 3.3 Workbench 边界

- Workbench 只生成 carrier-shaped handoff package。
- handoff target 可以是 `main-session`、`subagent`、`durable-team`、`langgraph-workflow`。
- handoff target 只是结构化元数据，不代表 GUI 执行该 carrier。
- Workbench 不读取或复制私有 `MOE.md` 全文，只使用公开 lens metadata 和用户输入 brief。

## 4. UI 技术路线

### 4.1 默认路线

- 采用 QFluentWidgets / Qt Widgets 全量重写主 GUI。
- 旧 QML 保留为 fallback，但不作为默认主体验。
- launcher 默认启动 Fluent Widgets GUI；若 QFluentWidgets 缺失则 fail closed，并输出清晰 preflight blocker。
- 共享 runtime 中使用 `PySide6-Fluent-Widgets`，不在消费项目内安装 PySide6/QFluentWidgets。

### 4.2 许可证边界

- QFluentWidgets 以 GPLv3 / commercial dual-license 记录。
- 本方案只授权本地个人工具链使用。
- 商业闭源分发、公开二进制安装包、客户交付前必须另开许可证审查。

### 4.3 产品级页面

- Overview：当前项目、readiness、项目默认 MOE 状态、最近 session 摘要。
- Sessions：session 列表、详情、开关、lens/category 联动、Codex 映射、最终生效 MOE。
- Workbench：安全 handoff package 工作台、历史、草稿、导出、执行前检查。
- Diagnostics：preflight、blockers、runtime、QFluentWidgets、session discovery、被排除/未映射诊断。
- Settings：语言、主题、session discovery 设置、显示字段设置。

普通目标项目 GUI 默认不展示多项目 Projects 页。

## 5. i18n 契约

- 新增 i18n 字典或资源模块，至少支持 `en`、`zh`、`bilingual`。
- 默认语言：`bilingual`。
- 所有核心页面、按钮、标签、错误、状态、Workbench package 说明进入 i18n。
- 中英对照格式统一：`中文 / English`。
- 语言设置写入目标项目 GUI runtime 配置或用户本地 runtime preference，不写入业务 MOE state。

## 6. MOE 分类与联动模型

### 6.1 推荐分类

A 论文项目默认分类升级为：

- `review`：盲审、导师追问、创新性、结构表达。
- `evidence`：文献、证据链、引用覆盖。
- `risk`：AIGC 风险、过度断言、阻塞风险。
- `thinking`：苏格拉底提问、思维模型调度。

### 6.2 三态联动

- 分类勾选：勾选该分类下全部 lens。
- 分类取消：取消该分类下全部 lens，除非该 lens 仍被其他已选分类包含且用户选择保持交集保护。
- lens 手动勾选/取消：分类状态自动更新为全选、半选或未选。
- UI 必须展示最终展开后的 `effective_lenses`。
- 保存时继续兼容现有字段，并在字段表中定义语义：

| 字段 | 用途 |
| --- | --- |
| `selected_lenses` | 保存当前 session 显式选择的具体 MOE lens id 列表。 |
| `selected_categories` | 保存当前 session 显式选择的 MOE 分类 id 列表。 |
| `effective_lens_mode` | 保存当前 session 的生效模式；`all` 表示全部 lens，`selected` 表示按选择后的 lens 集合生效。 |

- 读回时根据 `selected_lenses` / `selected_categories` 重建三态显示。

### 6.3 校验

- 非法 lens/category 必须 fail closed。
- 分类为空但 lens 非空合法。
- lens 为空但分类非空合法。
- lens/category 都空且 session enabled=true 表示 all。

## 7. Session identity / discovery / reconciliation

### 7.1 显示规则

- 默认显示所有未显式隐藏的 MOE session。
- 显示完整 session id。
- 禁止仅凭名称包含 `smoke`、`test`、`fixture`、`generated` 判定为测试会话。
- 只有显式字段可以让 session 进入诊断/隐藏视图，例如：
  - `session_kind: test|smoke|fixture|diagnostic` - operator 可见的 session 类型字段。
  - `is_test_session: true` - 明确声明该 session 是测试会话的布尔字段。
  - `hidden_from_default_view: true` - 明确从默认 Sessions 列表隐藏的显示门字段。
  - `created_by: visual_render_check|launcher_preflight|test_fixture` - 说明 session 状态由哪个工具或 fixture 创建。
- `smoke-session-final` 没有显式测试元数据时必须默认显示。

### 7.2 Codex 会话发现

- 只读扫描可用 Codex 会话来源：
  - `C:\Users\lenovo\.codex\session_index.jsonl` - Codex 会话索引候选来源。
  - `C:\Users\lenovo\.codex\sessions\**` - Codex 会话文件候选来源。
  - 其他已知只读索引或日志文件，必须避免读取凭据和大文件全文。
- 输出 discovered Codex sessions，并和 MOE session state 进行映射。
- 映射置信度：`exact`、`strong`、`weak`、`unmatched`。
- 映射不上时仍显示 MOE session，并说明 `Codex session mapping unavailable`。

### 7.3 Session 详情字段

每个 session 详情至少显示：

- full session id
- optional Codex resume/thread id
- mapping confidence
- session id source
- override origin
- enabled / effective enabled
- project default source
- first_seen_at / last_seen_at / updated_at
- branch / worktree
- state file path
- selected lenses / selected categories
- effective lenses
- why this session is shown
- why mapping is unavailable or weak

## 8. Expert Workbench 增强

- 选择 session 后生成绑定该 session 的 package。
- 展示当前 session 的 MOE 开关、选择和最终生效 lens。
- 支持 handoff target 选择：main session / subagent / durable team / LangGraph workflow。
- 支持保存草稿、复制、导出、历史筛选、历史复用。
- 增加执行前检查：
  - 是否缺目标；
  - 是否缺输入材料；
  - 是否缺验收标准；
  - 是否更适合 subagent；
  - 是否达到 durable team 或 LangGraph 的建议阈值。
- 检查结果只是建议，不自动执行。

## 9. 实施切片

### Slice 0：方案落地

- [x] 新建本方案文件。
- [x] 更新既有 Project MOE GUI 方案索引，指向本方案为 0.2.31 后续产品级重构方案。
- [x] 本地提交。
- [x] 合入 B 本地 main。

### Slice 1：Fluent Widgets 主界面骨架

- [x] 新增 Widgets GUI shell。
- [x] launcher 默认启动 Widgets shell。
- [x] QML shell 保留为 fallback。
- [x] 增加 QFluentWidgets fail-closed preflight。
- [x] 增加基础页面导航和主题。

### Slice 2：i18n

- [x] 新增 i18n 字典。
- [x] 默认中英对照。
- [x] Settings 页面可切换 English / 中英对照 / 中文。
- [x] 核心页面文案接入 i18n。

### Slice 3：项目边界与页面收敛

- [x] 目标项目 GUI 隐藏 Projects 多项目页。
- [x] 保留多项目扫描能力为 B 维护台或诊断-only 非默认入口。
- [x] 所有写操作显示当前 target project root。

### Slice 4：Session 列表与对账

- [x] 新增 Codex session discovery 只读模块。
- [x] 读取 MOE session state 与 Codex session index/files 做映射。
- [x] 显示完整 session id 和映射置信度。
- [x] 禁止名称启发式隐藏 session。
- [x] `smoke-session-final` 默认显示。
- [x] 增加 session 详情页和 why-shown 解释。

### Slice 5：MOE lens/category 三态联动

- [x] 新增 lens/category selection model。
- [x] 分类勾选联动具体 lens。
- [x] 具体 lens 变化反向更新分类三态。
- [x] 展示最终生效 lens 列表。
- [x] 保存/读回兼容现有 `selected_lenses`、`selected_categories`。

### Slice 6：Workbench 安全交接台

- [x] Workbench 绑定当前 session。
- [x] package 包含最终生效 lens。
- [x] 增加历史筛选和复用。
- [x] 增加执行前检查建议。
- [x] 保持不执行 carrier。

### Slice 7：视觉与自动化验证

- [x] 更新 visual render checker 支持 Widgets shell。
- [x] 覆盖 1180x720、1366x768、1440x900。
- [x] 覆盖中英对照、中文、英文。
- [x] 覆盖长 session id、长 lens 名、多 session、多分类。

### Slice 8：A 目标项目安装验收

- [x] 安装/更新到 `D:\PythonProject_paper_suggest`。
- [x] 运行 install check。
- [x] 运行 launcher preflight。
- [x] 运行视觉截图验证。
- [x] 运行可见启动验证。
- [x] 提交 A 项目本地 git。
- [x] 合入 A 本地 main。

## 10. 验证计划

B 仓库验证：

- `python tools/project_moe_gui_toolchain/check_project_moe_gui_install.py --target-project D:\PythonProject_paper_suggest --json` - 检查 A 目标项目安装产物与 B source toolchain 是否一致。
- QFluentWidgets runtime import/preflight。
- Session discovery 单测。
- i18n 文案单测。
- lens/category 三态联动单测。
- Workbench package schema 单测。
- visual render checker 多尺寸、多语言、多 session fixture。
- `python .\tools\check_precommit_update_archive.py --root . --json` - 本地提交前检查已有文件更新与 archive 要求。
- `python .\tools\run_openspec_guard.py --root .` - 运行仓库 OpenSpec 与文档治理 guard。
- 本地 gate / local MR review。

A 项目验证：

- `D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json` - A 目标项目 launcher 机器可读 preflight。
- 安装检查 `ok=true`。
- `smoke-session-final` 出现在默认 Sessions 列表。
- 目标项目 GUI 不显示其他项目 session。
- GUI 可见启动显示 Fluent 产品级界面。
- 视觉截图无明显截断、重叠或空白页。

## 11. 风险与默认处理

| 风险 | 默认处理 |
| --- | --- |
| QFluentWidgets GPLv3 边界不清 | 只授权本地个人工具链；商业/公开分发另开方案 |
| Widgets 全量重写回归大 | 保留 QML fallback，先接入相同 CLI/view-model |
| Codex session discovery 误匹配 | 只读发现，显示置信度，不自动写映射 |
| session 名称误判 | 禁止名称启发式隐藏，必须依赖显式字段 |
| 多项目页误导跨项目控制 | 普通目标项目 GUI 默认隐藏 Projects 页 |
| Workbench 被误当执行器 | 所有 package 标明 generated-only，GUI 不执行 carrier |

## 12. 完成定义

截至 2026-06-08，本方案所有 Slice 已完成并通过 A/B 两仓本地验证；远端发布不在本方案授权范围内。

- 本方案文件已提交并合入 B 本地 main。
- B runtime 实现已提交并合入 B 本地 main。
- A 项目已安装更新并提交本地 main。
- A GUI 默认只显示 A 项目 session。
- `smoke-session-final` 正常显示。
- 每个 session 可独立开关 MOE。
- lens/category 三态联动可用。
- 语言切换可用且默认中英对照。
- Workbench 安全交接台增强可用。
- preflight、视觉截图、可见启动验证通过。
