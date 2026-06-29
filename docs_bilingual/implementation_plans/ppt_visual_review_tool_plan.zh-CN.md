---
doc_id: ppt_visual_review_tool_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md
change: add-ppt-visual-review-tool-20260629
base_ref: 7c18096e5d0835d504dc6d38875ef88c2e2bd4e8
stage: frozen-governance-package
---

# PPT 可视化修改意见工具实施方案

> 操作说明：按两个本地集成包执行。Stage A 是本治理方案和注册表更新；Stage B 是运行时工具、OpenSpec delta、测试、本地门禁和本地 `main` 合入。除非后续明确授权，否则不做远程发布。

## 目标

部署一个可复用的本地/离线工具：操作者可以对已经渲染出的 PPT 幻灯片 PNG 进行可视化审阅，框选矩形 ROI，记录修改意见，并导出可被后续 PPT 修复工具消费的标准 JSON 证据。

该工具**不修改 PPTX**。它只基于已渲染的幻灯片图片创建旁路审阅会话，并把审阅产物写入消费者项目自己的输出目录，例如 `.local/`、`intermediate/` 或 `result/`。

## 现成方案调研结论

- Microsoft PowerPoint Add-ins 支持 task pane 和 content add-ins，可跨 Windows、Mac、iPad 和浏览器使用，但它们依赖 Office add-in 运行时，定位是在 PowerPoint 内或旁侧运行，不适合作为本仓库默认的离线证据产物。官方文档：https://learn.microsoft.com/en-us/office/dev/add-ins/powerpoint/powerpoint-add-ins
- Label Studio 的 `RectangleLabels` 是成熟的图片矩形框标注模型，能输出 ROI 坐标；但它更适合服务化/团队标注工作流，会引入比本仓库目标更重的服务和配置面。官方文档：https://labelstud.io/tags/rectanglelabels.html
- VGG Image Annotator（VIA）证明了“单 HTML/浏览器离线运行 + JSON 导入导出”的轻量标注方式可行，是本方案最接近的架构参考。官方页面：https://www.robots.ox.ac.uk/~vgg/software/via/
- CVAT 等平台适合大规模计算机视觉标注，但对本任务而言过重；本任务需要一次性、可携带、可追踪的操作者审阅旁路工具，而不是长期运行的标注平台。

决策：实现仓库自有的 stdlib-only Python 会话构建器和静态 HTML/JS viewer。复用“离线浏览器 + JSON ROI”的成熟模式，但 schema、guardrail 和输出边界必须与共享文档工具管线一致。

## Stage A：治理冻结包

文件：

- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md` - English canonical implementation plan for this tool.
- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.zh-CN.md` - Chinese companion implementation plan for this tool.
- `docs_bilingual/docs_registry.yaml` - Registry entry for the bilingual plan pair.

验收标准：

1. 方案必须明确冻结：
   - 输入边界：已渲染幻灯片 PNG，以及可选 PPTX provenance；
   - 输出边界：只能写入消费者拥有的输出目录；
   - 非目标：不修改 PPTX、不部署远程服务、不部署 Office add-in；
   - 交接 schema：标准 comments 列表包含 slide、severity、category、ROI、comment、suggested_fix、status、author、timestamp。
2. 注册表登记双语方案。
3. Stage A 分支必须是 docs-only，并且包含 `docs_bilingual/` 更新。
4. 本地验证命令：
   - `python .\tools\check_document_pair_policy.py --root . --base-ref main --json` - Validates bilingual Markdown pairing.
   - `python .\tools\check_precommit_update_archive.py --root . --json` - Validates pre-commit update and archive readiness.
   - `python .\tools\run_openspec_guard.py --root . --tool codex --json` - Runs repository OpenSpec and governance guard checks.
5. 使用 `tools/complete_local_flow_to_remote_gate.py --stage governance-confirmation --implementation-plan docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md --execute` 将 Stage A 合入本地 `main`。
6. Stage B 收据/claim 必须记录 Stage A commit、`governance_package_merged_to_local_main=true`，并记录当前用户已经用 “Implement the plan.” 确认进入实现。

## Stage B：运行时实现包

文件：

- `tools/user_level_document_tools/viewers/ppt_review/ppt_review_tool.py` - Python CLI and comment normalizer.
- `tools/user_level_document_tools/viewers/ppt_review/__init__.py` - Package marker for the PPT review module.
- `tools/user_level_document_tools/viewers/ppt_review/__main__.py` - python -m entrypoint for the review tool.
- `tools/user_level_document_tools/viewers/ppt_review/static/ppt_review_viewer.html` - Offline browser UI shell.
- `tools/user_level_document_tools/viewers/ppt_review/static/app.js` - Offline viewer interaction and JSON logic.
- `tools/user_level_document_tools/viewers/ppt_review/static/styles.css` - Offline viewer styles.
- `tools/user_level_document_tools/viewers/ppt_review/README.md` - Operator usage notes.
- `tools/user_level_document_tools/viewers/__init__.py` - Shared viewer package marker.
- `test/user_level_document_tools.test.py` - Regression test surface.
- `openspec/changes/add-ppt-visual-review-tool-20260629/` - OpenSpec change package for Stage B.

运行时行为：

1. Python CLI 构建审阅会话：
   - `--slides-dir` 指向已渲染的幻灯片 PNG；
   - `--input` 仅记录可选 PPTX provenance；
   - `--output-dir` 写入复制后的 slide 图片、`session_manifest.json`、`comments.json`、`review_report.json`、`review_report.html` 和静态 viewer 资源；
   - `--comments-json` 导入已有审阅意见或 viewer 导出的 JSON。
2. 静态 viewer：
   - 加载本地 PNG；
   - 绘制归一化矩形 ROI；
   - 记录 severity/category/comment/suggested_fix；
   - 导入和导出 Python CLI 可接受的同一 JSON schema。
3. Schema 与校验：
   - severity 集合：`info`、`low`、`medium`、`high`、`critical`；
   - 可兼容旧别名：`minor -> low`、`major -> high`、`warning -> medium`、`error -> high`；
   - ROI 使用 `[0,1]` 区间内的归一化 `x`、`y`、`w`、`h`；
   - 导入非法或越界 ROI 时必须 fail closed，不能静默 clamp 成“看似有效”的证据。
4. 输出安全：
   - 默认拒绝把生成会话写入被跟踪的共享工具源码目录；
   - `--allow-source-output` 只用于明确的测试 fixture。
5. 本地/离线约束：
   - 不调用远程 API；
   - 不新增 Python stdlib 和浏览器原生 HTML/CSS/JS 之外的重量级依赖；
   - 不修改源 PPTX。

## Stage B 测试

Focused 测试必须覆盖：

- 必要文件和静态资源存在；
- 被跟踪共享工具源码中没有消费者/项目绝对路径；
- CLI `--help`；
- 从 PNG 构建 manifest/session；
- comment 标准化和坏 ROI 拒绝；
- viewer export schema 能被后端接受；
- viewer severity 选项与后端 severity 契约一致；
- viewer import 对 ROI fail closed，而不是静默 clamp；
- 带 `--comments-json` 的 CLI 成功路径；
- slides 目录缺失或 comment JSON 损坏时的 CLI 错误路径；
- 生成会话会复制 HTML/CSS/JS 静态 viewer 资源。

## 验证与集成

Stage A 治理包已经在本地 `main` 后，并且实现收据已经确认后，在 Stage B worktree 运行：

```powershell
python test\user_level_document_tools.test.py -k ppt_review
python -m py_compile tools\user_level_document_tools\viewers\ppt_review\ppt_review_tool.py
openspec validate add-ppt-visual-review-tool-20260629 --strict
python .\tools\run_openspec_guard.py --root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -StepTimeoutSeconds 3600 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

验证后本地合入：

```powershell
python .\tools\complete_local_flow_to_remote_gate.py --root D:\PythonProject_langgraph --worktree D:\PythonProject_langgraph\.worktrees\add-ppt-visual-review-tool-20260629 --branch add-ppt-visual-review-tool-20260629 --stage implementation --implementation-plan docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md --local-gate-step-timeout-seconds 3600 --execute
```

到远程发布门停止。

## 协同计划

- Leader 负责 Stage A 治理冻结、Stage B fan-in、验证、提交、本地 main 合入和远程发布边界。
- Researcher 负责复核现成方案并确认本地/离线模式合理。
- Test-engineer/verifier 在平台线程容量允许时复核 schema round-trip 和 gate 证据。
- Stage A 后 Stage B 至少有两个执行切片（runtime/static viewer 与 tests/OpenSpec/gates），满足 durable/persistent 协同阈值；如果平台线程上限阻止新增 worker，则记录 main-session takeover，并保留已有 expert findings 作为 review 证据。

## 当前状态

<!-- CURRENT_STATUS_START -->
- Stage A 治理方案正在 `docs/add-ppt-visual-review-tool-plan-20260629` 分支冻结。
- Stage B 实现 worktree 已在 `.worktrees/add-ppt-visual-review-tool-20260629`，最终集成前必须 rebase 到 Stage A 本地 `main` commit。
- 未授权远程发布。
<!-- CURRENT_STATUS_END -->

## 任务积压

<!-- TASK_BACKLOG_START -->
- Stage A：验证双语方案和注册表更新，提交 docs-only 包，并合入本地 `main`。
- Stage B：将运行时分支 rebase 到 Stage A 本地 `main` commit，并在 receipt/claim 中记录实现确认。
- Stage B：修复 expert 已识别问题：OpenSpec delta 文件无 BOM、后端/viewer schema 对齐、ROI 导入 fail closed、源码输出目录 guard、补齐缺失测试。
- Stage B：运行 focused tests、OpenSpec validate、OpenSpec guard、local gate、local MR review，然后合入本地 `main`。
<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- `docs_bilingual/docs_registry.yaml` - Registry entry for the bilingual plan pair.
- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md` - English canonical implementation plan for this tool.
- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.zh-CN.md` - Chinese companion implementation plan for this tool.
- `test/user_level_document_tools.test.py` - Regression test surface.
<!-- EVIDENCE_INDEX_END -->
