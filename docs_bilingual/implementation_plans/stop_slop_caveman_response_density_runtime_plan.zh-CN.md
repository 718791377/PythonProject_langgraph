---
doc_id: stop_slop_caveman_response_density_runtime_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/stop_slop_caveman_response_density_runtime_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B follow-up child plan
phase: 4
batch: 3
confirmation_required: true
---

# Stop-Slop 与 Caveman 响应密度 Runtime 方案

> 给 agentic worker：使用 `superpowers:executing-plans`；只有写入范围互不重叠时才并行使用子代理。本包只记录 checker 加 runtime 目标，不创建脚本。

## 目标

新增 Phase 4 子方案，把 `stop-slop` 与 `caveman` 参考源转成面向 Codex 对话输出的项目级响应密度 checker 和受保护本地 runtime 目标。

## 参考源

| 参考源 | 必须继承的要求 |
| --- | --- |
| https://github.com/hardikpandya/stop-slop | 反 slop 检查：删除 filler，避免套路短语和结构，要求主动语态，禁止 em dash，改变节奏，并评分 directness、rhythm、trust、authenticity、density。 |
| https://github.com/JuliusBrussee/caveman | 输出压缩模式：减少输出 token，同时保持技术准确；rewrite 时保护代码、URL、路径、命令参数和技术 token。 |

## 范围决定

- 层级：先作为 `D:/PythonProject_langgraph` 的项目级治理与项目级 runtime 方案。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`。
- 阶段：Phase 4，因为它影响对话表面质量和输出密度。
- 本包：只更新方案、registry 和父方案索引；不创建 checker、runtime helper、hook、skill 安装、MCP wrapper 或用户级配置变更。
- 后续实现：必须达到 checker 加 runtime 的层级，才能声称 ready。
- 远端发布：除非用户明确要求远端发布，否则不在范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: active child-plan definition; code work is not started.
Stage: documentation package records the checker plus runtime requirement and source links.
Owner session: `plan-stop-slop-caveman-runtime-20260606` only owns this plan-document package.
Current gate: validate implementation-plan rules, OpenSpec guard, precommit update/archive review, local gate, and local MR review before local main integration. Remote publication is not authorized.
Runtime boundary: no Stop-Slop or Caveman runtime is installed, enabled, invoked as a hook, or promoted to user level by this package.
<!-- CURRENT_STATUS_END -->

## Checker 与 Runtime 目标

后续代码包必须先提供这些 repo-local 表面，才能声称达到 R2 ready：

- `tools/check_stop_slop_caveman_response_density.py` 校验回复样本、fixtures 和选定文档片段的 stop-slop 与 density 规则。
- `tools/stop_slop_caveman_runtime.py analyze` 返回 JSON diagnostics，不改写输入。
- `tools/stop_slop_caveman_runtime.py rewrite --dry-run` 给出更短 rewrite 建议，但不写文件。
- `tools/stop_slop_caveman_runtime.py rewrite --apply --operator-confirmation` 只允许处理 operator 显式传入的文件或文本，并且必须保留受保护片段。
- 测试必须覆盖 valid/invalid slop 样例、受保护代码块、受保护 URL、受保护路径、受保护 CLI 参数、受保护 schema key、中文说明文本和对话标签。

未来 checker/runtime 绝不能改写的受保护片段包括：代码块、inline code、URL、文件路径、CLI 参数、JSON/YAML key、OpenSpec requirement 关键词、evidence token、blocker token、`Routing trace` 与 `Updated Plan`。

## Runtime 推广阶梯

| 阶段 | 范围 | 必要证据 |
| --- | --- | --- |
| R0 source preflight | 项目级 | 参考 URL、获取日期、规则映射，并证明没有 install/run。 |
| R1 dry-run runtime | 项目级 | fixture 支持的 `analyze` 与 `rewrite --dry-run`；不改文件。 |
| R2 checker/runtime helper | 项目级 | checker、受保护 helper、测试、OpenSpec guard wiring、CI manifest 登记和 docs registry 登记。 |
| R3 user-level install | 用户级延后 | 明确授权、不可变 source pin、install/update receipt、rollback pointer 和 redaction evidence。 |
| R4 smoke runtime | 用户级延后 | 有边界的 help/status/safe rewrite smoke receipt，带 timeout 与 rollback evidence。 |
| R5 active-candidate | 用户级延后 | 在 hook、全局 skill activation、MCP shrink 或 always-on compression 前，先有明确 active-candidate receipt。 |

## 文件归属

本子方案拥有自身方案文件和上述未来 checker/runtime 名称。它不拥有 canary placement、`Routing trace` 语义、`Updated Plan` 渲染、用户级 skill 安装、MCP Router 配置、消费者项目注入上下文文件或全局 Codex launcher profiles。

## 并行会话契约

同一时间只能有一个 session claim 本 implementation plan。后续代码工作可以和无关 Phase 4 工作并行，但 docs registry、CI manifest、OpenSpec guard wiring 与 conversation-surface fixtures 必须有串行 hotspot owner。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 创建本子方案和中文 companion。
- [x] 记录 Stop-Slop 与 Caveman 参考链接。
- [x] 要求后续实现达到 checker 加 runtime，而不是只做文本治理。
- [ ] 后续实现：新增 `check_stop_slop_caveman_response_density.py`，带 focused fixtures 和 JSON output。
- [ ] 后续实现：新增 `stop_slop_caveman_runtime.py`，包含 `analyze`、`rewrite --dry-run` 与受保护 `rewrite --apply`。
- [ ] 后续实现：登记 focused tests、OpenSpec guard wiring 和 CI manifest 覆盖。
- [ ] 后续 runtime 推广：R3-R5 用户级安装、hook、MCP shrink 和 always-on compression 必须受明确授权以及 receipt/rollback/redaction evidence 约束。
<!-- TASK_BACKLOG_END -->

## 验证门禁

- `python tools/check_implementation_plan_rules.py --root . --json` - 校验 implementation plan registry、双语 companion、parent-plan、体积与 evidence-index 规则。
- `python tools/run_openspec_guard.py --root .` - 校验 OpenSpec 状态和仓库治理 guard wiring。
- `python tools/check_precommit_update_archive.py --root . --json` - 在提交前校验必须的 update/archive review。
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - 在集成前运行共享本地 CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - 在合入本地 main 前运行 local MR review gate。

后续代码工作还必须为 checker 与 runtime helper 添加 focused tests。

## 验收标准

- 本子方案已登记为 active，并链接到父方案。
- 方案记录两个参考源和本项目的 checker/runtime 目标。
- 方案说明本包不创建或启用 runtime 代码。
- R3-R5 用户级激活继续延后，必须先有明确授权和 receipts。
- 未来 runtime 不能改写受保护技术表面和固定对话标签。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 文档包：branch `plan-stop-slop-caveman-runtime-20260606` 创建本 active Phase 4 子方案，记录 `hardikpandya/stop-slop` 与 `JuliusBrussee/caveman` 参考源，并把 checker/runtime 代码留给后续实现包。
<!-- EVIDENCE_INDEX_END -->
