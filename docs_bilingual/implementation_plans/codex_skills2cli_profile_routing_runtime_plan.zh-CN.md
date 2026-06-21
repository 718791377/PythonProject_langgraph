---
doc_id: codex_skills2cli_profile_routing_runtime_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.md
translation_of: docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.md
status: active
doc_class: implementation_plan
change: improve-skills2cli-profile-routing
created_at: 2026-06-21
---

# Skills2CLI 场景化 Profile 路由 Runtime 计划

> 给 agentic workers：本方案冻结后，Phase B 可以使用 `subagent-driven-development` 或受保护的 durable-team lane。方案冻结包和 live runtime 实现包必须作为两次独立本地 main 集成包处理。除非后续出现明确 apply receipt，否则 profile apply 不在范围内。

**目标：** 在保留 canonical `target_profile` hard-load 语义的前提下，为 Codex plugin skills 管理增加场景入口和 task module 路由层。

**架构：** Phase A 冻结 OpenSpec 契约与双语实施方案。Phase B 扩展 plugin-modules registry、helper 脚本、`skills2cli.py`、checker 与测试。runtime 只做 advisory：可以建议 soft-load 和 hard-load preview candidate，但不得编辑 `config.toml`、plugin cache 或 hard-load profile。

**技术栈：** JSON profile registry、PowerShell plugin-module helper、Python `skills2cli.py`、仓库 checker、OpenSpec、本地 CI 与 local MR review。

---

## 当前状态

<!-- CURRENT_STATUS_START -->

- Stage A 方案冻结包正在 `freeze-skills2cli-profile-routing-plan-20260621` 中实施。
- OpenSpec change `improve-skills2cli-profile-routing` 是本工作的当前活动契约。
- Phase B runtime 实现等待 Stage A 验证与本地 main 集成后开始。
- 远程发布未授权。

<!-- CURRENT_STATUS_END -->

## 1. 输入与设计原则

本计划使用三个输入：

1. 本地参考视频文件名中的四项原则：场景化描述、分层路由、负样本边界、召回重排机制，用于提升 Agent skill 命中率。
2. `codex_skills_usage_audit` 证据模型：strong evidence 可作为 routing 与 review 输入，但不授权 profile apply。
3. 当前 `target_profile` registry：`core-dev`、`web-saas`、`company-ops`、`market-research`、`customer-comms`、`creative-content`、`pyside6-gui` 和 `full` 继续保持兼容 ID。

## 2. 非目标与安全边界

- Phase B 不重命名现有 `target_profile` ID，只新增 alias 与场景 metadata。
- 不自动 apply 任何 hard-load profile。
- 不修改 `C:\Users\lenovo\.codex\config.toml`。
- 不批量编辑 plugin cache 文件或 vendor `SKILL.md` 文件。
- 不让 `full` 成为普通任务 top-1 suggestion。
- 不把 profile/helper invocation 当成 native expert evidence。
- 本实施流程不推送 GitLab/GitHub。

## 3. 目标模型

registry 必须表达四层：

1. **canonical top-level profile**：现有 `target_profile` hard-load ID，供 `set_plugin_profile.ps1` 与 audit candidate 使用。
2. **scenario profile**：新的 recommendation entrypoint，解析到 canonical `target_profile` 和默认 task modules。
3. **task module**：profile 内部的任务能力块，例如 `web-saas.mobile-app` 或 `core-dev.security-review`。
4. **skill/plugin hints**：可被 soft-load 的 plugin family 与 `SKILL.md` reference。

每个 top-level profile 和每个 task module 都必须定义：

- 场景描述；
- 正向 routing examples 或 `route_when` terms；
- 用于排除误命中的 negative examples；
- load policy：`default-candidate`、`hard-load-preview`、`soft-load`、`repo-local-only` 或 `troubleshooting-only`；
- 适用时提供 plugin hints 与 skill document hints；
- ranking signal 说明，解释 audit evidence 与 warning pressure 如何影响排序。

## 3.1 兼容性约束

- audit candidate 和 hard-load preview 中的 `target_profile` 继续表示现有 canonical profile ID。
- `scenario_profiles` 是新的 recommendation entry layer，不替代 canonical `modules`。
- `task_modules` 可以嵌入 profile 下，并由 runtime 按 `profile.task_module` 解析。
- `set_plugin_profile.ps1` 只接受 canonical top-level profile；scenario 或 task-module 输入必须 fail closed。
- `load_module.ps1` 可以接受 canonical profile、scenario profile 或 `profile.task_module`，但输出必须显式报告 `entry_kind`、`target_profile` 和 `task_module`。

## 4. 顶层 profile 矩阵

| 现有 ID | 场景 alias | 预期 task modules |
| --- | --- | --- |
| `core-dev` | `repo-dev` | `repo-governance`, `code-review`, `security-review`, `openai-dev`, `docs-artifacts`, `browser-verification` |
| `web-saas` | `web-product` | `frontend-build`, `deploy-runtime`, `db-backend`, `payments`, `observability`, `mobile-app`, `design-implementation`, `browser-verification` |
| `company-ops` | `ops-knowledge` | `mail-calendar`, `docs-sheets-slides`, `knowledge-capture`, `crm-workflow`, `team-comms`, `meeting-intel`, `issue-planning` |
| `market-research` | `research-analysis` | `company-research`, `news-library`, `paper-citation`, `model-dataset-inspection`, `science-visuals`, `report-artifacts` |
| `customer-comms` | `customer-comms` | `messaging`, `email-delivery`, `support-comms`, `payment-comms` |
| `creative-content` | `design-media` | `design-generation`, `design-implementation`, `slides-docs`, `video-motion`, `brand-assets`, `media-assets` |
| `pyside6-gui` | `repo-local-gui` | `qt-gui-dev`, `gui-preview-apply`, `gui-packaging-preflight` |
| `full` | `troubleshooting` | 无普通 task module；仅用于 broad discovery 排障 |

Phase B registry 必须确保原先 only-`full` 的插件拥有非 `full` task-module 归属：

- `BioRender` -> `market-research.science-visuals`；
- `ChatGPT Apps` -> `core-dev.openai-dev`，必要时新增 `core-dev.chatgpt-apps`；
- `Cloudinary` -> `creative-content.media-assets`；
- `Expo` -> `web-saas.mobile-app`；
- `Fireflies` -> `company-ops.meeting-intel`；
- `Linear` -> `company-ops.issue-planning`；
- `Temporal` -> `core-dev.workflow-orchestration`，或在证据更偏 Web 工作流时归入 `web-saas.workflow-orchestration`。

## 5. Runtime 行为

`skills2cli.py profile suggest --query <text> --json` 必须：

1. 使用场景文本和 `route_when` terms 给 top-level profiles 评分；
2. 对命中 `negative_examples` 的 profile 做排除或降权；
3. 在保留的 profiles 内继续给 task modules 评分；
4. 可用时用 `codex_skills_usage_audit` strong evidence 做 advisory boost；
5. 对 oversized 或 troubleshooting-only profile 施加 warning-pressure penalty；
6. 返回紧凑且脱敏的 JSON，包含 selected profile、task modules、excluded candidates、soft-load commands、可选 hard-load preview command 与解释文本。

`load_module.ps1` 必须接受 top-level module 和 `profile.task_module` 名称。task-module load 只返回该 module 的 focused hints。

`list_module.ps1` 必须展示 top-level modules，并可选择展示 nested task modules。

`set_plugin_profile.ps1` 保持 top-level only。若传入 task-module ID，必须 fail closed，并解释 task modules 只是 soft-load guidance，hard-load 仅适用于 top-level profiles。

## 6. Checker 与测试

新增或扩展 checker，使仓库在以下场景 fail closed：

- top-level profile 缺少场景描述、route terms、negative examples、ranking signals 或 task modules；
- task module 缺少正向 examples、negative examples、load policy、plugin hints 或 routing explanation fields；
- known plugin 只能通过 `full` 到达且没有明确 allowlist reason；
- 普通 profile suggestion 返回 `full` 作为 top-1；
- user-level installed plugin-modules registry 与 repo source 存在差异但未报告 drift；
- profile suggestion 输出缺少解释、soft/hard boundary 或 excluded-candidate evidence；
- installed `skills2cli` wrapper 只通过 `--help`，但无法执行真实 `profile suggest` smoke；
- 输出将 `mutates_config`、`edits_plugin_cache` 或 `profile_apply_performed` 设为 true；
- 输出把 skill/profile routing 当成 native expert 或 native subagent evidence；
- 当文案涉及 direct MCP handoff 时绕过 paired `mcp2cli` risk-profile / receipt gate。

代表性 routing tests 必须覆盖：

- GitLab CI 修复加安全审查 -> `core-dev`，包含 `code-review` 与 `security-review`；
- Expo 移动端构建加 Sentry 观测 -> `web-saas`，包含 `mobile-app` 与 `observability`；
- Twilio WhatsApp 客户通知 -> `customer-comms`，包含 `messaging`；
- 会议纪要和 CRM 跟进 -> `company-ops`，包含 `meeting-intel` 或 `crm-workflow`；
- BioRender 科学图 -> `market-research.science-visuals`；
- Cloudinary 素材管线 -> `creative-content.media-assets`；
- 未知 broad troubleshooting 请求 -> 只有当 query 明确要求排障全部插件时，才允许 `full` 成为 top-1。

## 7. Phase A 任务

<!-- TASK_BACKLOG_START -->

- [x] 创建本双语 implementation plan。
- [x] 创建 OpenSpec change `improve-skills2cli-profile-routing`。
- [x] 添加 delta spec，覆盖 profile routing、task modules、negative examples、recall/rerank 输出和安全边界。
- [x] 更新 `codex_skills_usage_audit_plan.md` 与 `.zh-CN.md`，声明 audit evidence 仅作为 advisory routing/rerank 输入。
- [x] 在 `docs_bilingual/docs_registry.yaml` 登记本双语方案。
- [x] 运行 plan-level validation 并提交 plan-freeze package。
- [ ] 通过 local-main-first helper 将 Phase A 集成到本地 `main` 并清理 worktree/branch。

## 8. Phase B 任务

- [ ] 扩展 `profiles.json`，加入场景 metadata 与 task modules，同时保留现有 profile IDs。
- [ ] 扩展 plugin-modules 脚本，支持 nested `profile.task_module` soft-load 和 top-level-only hard-load。
- [ ] 添加 `skills2cli.py profile suggest`，输出 positive/negative/rerank evidence 与紧凑脱敏结果。
- [ ] 添加 checker 与测试，覆盖 schema、only-`full` coverage、普通任务不得 `full` top-1、installed-copy drift reporting。
- [ ] 如果新增 checker/test 文件需要登记，同步更新 CI manifest 与 guard registration。
- [ ] 通过 checker、代表性 suggestions、OpenSpec guard、local gate 与 local MR review 验证 Phase B。
- [ ] runtime validation 通过后 archive OpenSpec change，再集成到本地 `main`。

<!-- TASK_BACKLOG_END -->

## 9. 验收标准

- `profiles.json` 为所有非 `full` profile 包含 scenario fields 与 task modules。
- 每个 known plugin 都有非 `full` route，或有明确 allowlist reason。
- `skills2cli.py profile suggest --query ... --json` 返回确定、脱敏、可解释的 recommendations。
- 普通用户任务不会让 `full` 成为 top-1。
- Profile suggestion 继续保持 advisory，绝不 apply config。
- `skills2cli` 聚焦测试、`mcp2cli` risk/receipt 测试、agent/skill/profile 边界测试，以及严格 user-level install/smoke 检查，都属于最终 runtime 验证集合。
- 本地 `main` 集成前，OpenSpec validation、repository guard、本地 CI 和 local MR review 均通过。

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- `docs_bilingual/implementation_plans/codex_skills2cli_profile_routing_runtime_plan.md` - Stage A 冻结实施方案与 runtime 验证契约。
- `docs_bilingual/docs_registry.yaml` - active 双语方案登记。
- `openspec/changes/improve-skills2cli-profile-routing/` - 当前 OpenSpec change，包含 proposal、design、tasks、management record 与 delta spec。
- `docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md` - advisory audit 输入关联；profile apply 仍未授权。
- Stage A 验证证据：`openspec validate improve-skills2cli-profile-routing --strict`、`tools/run_openspec_guard.py --root . --tool codex --json`、`tools/check_precommit_update_archive.py --root . --json` 与 `tools/check_worktree_task_receipt.py --root . --json` 已在 plan-freeze commit 前通过。

<!-- EVIDENCE_INDEX_END -->
