---
doc_id: north_star_plan
lang: zh-CN
canonical: docs_bilingual/north_star_plan.md
translation_of: docs_bilingual/north_star_plan.md
doc_class: north_star_plan
status: draft
---

# 北极星计划：Codex CLI 个人生产级持久化团队平台

## 文档身份

本文是 Codex CLI 个人生产级持久化团队平台的指标层北极星计划。它把白皮书叙事、MRD 需求和产品生命周期清单地图转化为可度量的方向。它不是运行时证据，不能证明当前已经有 durable team 或 persistent team 正在运行。

本次刷新使用的新鲜来源证据来自 `2026-06-13T22:50:48Z` 生成、但因体积和原文版权边界而未提交的 `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260613/` 抽取产物：`fresh_source_manifest.json`、`fresh_source_synthesis.json`、本地 raw `fresh_source_items.jsonl`。抽取覆盖 54 个来源，其中 31 个来自 `Business Management/`、23 个来自 `PMP/`；格式包括 31 个 PDF / 9,280 页、9 个 EPUB / 362 个 spine item、14 个 Markdown 全文文件，合计 18,492,044 个抽取文本字符。Git 跟踪文档只记录综合结论；源文本、逐项抽取流和抽取日志保留在本地忽略目录中。

## 主要北极星指标

**安全冷启动延续成功率**：新建或恢复的 Codex 会话能够继续项目任务，且不需要用户反复解释、不发生跨项目状态泄漏、不虚假宣称 durable/persistent team 已运行、不执行不安全 Git/worktree 操作、不作出未经验证完成声明的比例。

## 输入指标

| 输入指标 | 为什么重要 | 示例证据 |
| --- | --- | --- |
| 启动上下文恢复率 | 新会话必须能找到正确读取顺序和当前主线 | 启动摘要、`AGENTS.md`、文档注册表 |
| 路由证据完整性 | experts、`native_omx`、LangGraph 必须基于具体理由被选择或拒绝 | 包含 phase、backend readiness、thresholds、blockers 的 routing trace |
| 持久状态隔离质量 | 共享 user-level helper 不能变成跨项目 durable truth | repo-local `.omx/state/`、selector 状态、state-status 输出 |
| 冻结计划质量 | durable team 执行只应在目标和切片清晰后启动 | frozen plan、scope、owner map、validation、rollback boundary |
| 验证新鲜度 | 完成声明必须有近期证据支撑 | local gates、OpenSpec guard、diff review、test output |

## 护栏指标

- 没有 selector、manifest、heartbeat、worker record 或 closed-agent evidence 时，虚假宣称 durable/persistent team 已运行的次数为 0。
- 当任务要求 fresh reading 时，把旧 extraction cache 当作事实来源的次数为 0。
- 未授权 remote publication、protected-branch mutation 或跨项目 Git commit 的次数为 0。
- Codex 平台 durable state 与下游业务 runtime truth 混用的次数为 0。

## 目标架构清单

| 目标 | 清单 | 权威边界 |
| --- | --- | --- |
| Codex CLI 个人生产级持久化团队 | 12 层主干层级 + 4 个虚拟部门 + 24 个责任域 + 18 个横切模块 + 48 个核心文档 + 12 个受治理 AI Agent + 12 本推荐书籍 | 本仓库拥有平台治理、helper 源码、文档、检查器、模板和 repo-local 平台 durable state |
| 个人级生产级一人公司 | 12 层主干层级 + 5 个虚拟部门 + 30 个责任域 + 20 个横切模块 + 60 个核心文档 + 15 个受治理 AI Agent + 15 本推荐书籍 + 12 个最小启动文档 | 下游仓库拥有客户证据、收入、财务、法务、支持、发布、durable state 和经验复盘 |

## 过程组式运营模型

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 白皮书、MRD、来源综合证据、启动痛点、路由失败、持久状态风险 | 价值框定、干系人/责任人映射、非目标审查、风险框定 | 北极星指标、护栏、范围边界、初始风险 |
| 规划 | 北极星指标、输入指标、生命周期地图、PMI 裁剪规则、当前能力状态 | 指标分解、阈值设计、裁剪、发布切片规划、验证设计 | 输入指标计划、决策阈值、发布切片指标、验证计划 |
| 执行 | 已批准计划、worktree ownership、docs/templates/checkers、抽取证据 | 文档更新、检查器更新、合格时的 expert fan-out、本地验证 | 更新后的文档、模板、检查器、发布证据、changed-path list |
| 监控与控制 | 当前指标、路由证据、selectors、gates、review findings、issue logs | Diff review、OpenSpec guard、local CI、durable evidence checks、变更控制 | 接受的变更、缺陷、延期风险、回滚就绪度、路由修正 |
| 收尾 | 已接受 artifacts、验证输出、archive candidates、经验教训 | 收尾审查、docs registry/spec sync、复盘、下一周期分诊 | 稳定文档、已归档 change 或延期说明、经验教训、下一增量 |

## 决策阈值

- 当变更影响 orchestration、subagent routing、`native_omx`、LangGraph、worktree safety、OpenSpec governance、launcher、checker、release safety 或跨项目 template 时，采用完整平台架构。
- 仅当事项是低风险私有 spike 或本地 note，且没有外部用户、金钱、信任边界、敏感数据、共享 runtime entrypoint、durable-state 变更或发布承诺时，才允许整个项目轻量化。
- 当一个有界切片低风险且可逆，而相邻高风险阶段或模块仍保持完整架构路径时，采用阶段局部轻量或模块级轻量。
- 当仍需要 discovery、但最终交付可能影响用户、信任、收入、合规、runtime behavior 或 release safety 时，采用混合架构。
