---
doc_id: reference6_user_project_capability_install_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/reference6_user_project_capability_install_plan.md
---

# Reference 6 用户级/项目级能力安装计划

## 目标

按分层模型安装或登记 `reference_files/6.md` 中的能力，并同步可复用入口到 `D:\PythonProject_General` 和 `D:\PythonProject_General_2`。

参考清单：

- `https://github.com/nexu-io/open-design` - open design-to-code 能力参考，用于可复用 UI/设计转换。
- `https://github.com/nexu-io/html-anything` - HTML 结构化转换能力参考。
- `https://github.com/browserbase/skills` - Browserbase skills 集合参考，用于浏览器自动化 skill 包装。
- `https://github.com/pymupdf/pymupdf` - PyMuPDF 源码参考，用于 PDF 解析与渲染能力。
- `https://github.com/opendatalab/MinerU` - MinerU 源码参考，用于文档智能与抽取能力。
- `https://mineru.net/apiManage/limit` - MinerU API 配额页参考，用于 live-service readiness 与 blocker receipt。
- `https://mineru.net/` - MinerU 服务首页参考，用于账号/API 能力发现。
- `https://github.com/virgiliojr94/book-to-skill` - book-to-skill 源码参考，用于从长文档生成可复用 skill。
- `https://github.com/mattpocock/skills` - 可复用 skill 示例参考，用于 Codex/Superpowers 兼容 skill 包装。

## 当前状态

<!-- CURRENT_STATUS_START -->

- 2026-06-16：从 `reference_files/6.md` 打开计划；实现尚未运行。
- 默认决策：分层安装、复用 Codex provider env-key、脱敏 receipt、不做远端发布。

<!-- CURRENT_STATUS_END -->

## 任务 backlog

<!-- TASK_BACKLOG_START -->

- [ ] 创建用户级 reference6 manifest、installer、smoke script 和 receipt writer。
- [ ] 安装或登记七个参考能力；可用时记录 pinned version 或 commit evidence。
- [ ] 运行用户级 smoke，并为缺失外部前置条件记录明确补全方法。
- [ ] 更新 `D:\PythonProject_General`：active reusable policy/checker/example config。
- [ ] 更新 `D:\PythonProject_General_2`：inert upgrade policy/checker/example manifest。
- [ ] 验证源仓库、用户级、General 和 General_2 门禁；合入本地 main 并停在远端发布门禁。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

| 证据项 | 预期路径或命令 | 状态 |
| --- | --- | --- |
| 计划登记 | `docs_bilingual/docs_registry.yaml` | 本次变更计划内 |
| 参考源清单 | `reference_files/6.md` | 已纳入本计划 |
| 用户级安装 receipt | 用户级 reference6 receipt JSON | 待实现 |
| 源仓库验证 | `python tools\run_openspec_guard.py --root . --json` | 待实现 |
| General 验证 | `tools\ci\local_gate.ps1 -Root D:\PythonProject_General -Json` | 待实现 |
| General_2 验证 | `tools\ci\local_gate.ps1 -Root D:\PythonProject_General_2 -Json` | 待实现 |

<!-- EVIDENCE_INDEX_END -->

## 分层决策

- 用户级：安装或登记可复用 CLI、Python 包、Node/GitHub 源、skills、smoke 脚本、manifest 和 receipt。
- `D:\PythonProject_General`：提供 active 可复用项目模板入口、policy、checker 和 example config；不提交凭据、账号状态、缓存或外部动作证据。
- `D:\PythonProject_General_2`：只提供保守 inert 升级入口，默认不启用 live/API/runtime 行为。

## API key 策略

- 尽可能复用 Codex `C:\Users\lenovo\.codex\config.toml` 的 provider/key 形态。
- 只按环境变量名复用 provider `env_key`，绝不复制或写入 secret value。
- 需要专用 key 的外部服务只读取现有环境变量，并用脱敏 receipt 验证存在性。
- receipt、manifest、template、test output 和 log 不得包含密钥明文。

## 阻塞协议

实现不得把未解决阻塞当作完成。每个阻塞必须记录：

1. 缺少什么；
2. 不泄露密钥的补全命令；
3. 脱敏验证命令；
4. 下一步恢复位置。

## 实施任务

1. 创建用户级 reference6 manifest、installer、smoke 脚本和 receipt writer。
2. 安装/登记 PyMuPDF、MinerU、book-to-skill、open-design、html-anything、Browserbase skills 和 mattpocock skills。
3. 运行用户级 smoke，并记录结果或可恢复阻塞。
4. 更新 General 与 General_2 模板并验证。

## 验证门禁

- 源仓库：`python tools\run_openspec_guard.py --root . --json`、local gate 和 local MR review。
- 用户级：manifest 可解析、receipt 脱敏检查、import/help/API-smoke。
- General 与 General_2：各自 checker、local gate 和 local MR review。

## 完成标准

- 源仓库计划与实现提交均合入本地 `main`。
- 用户级 reference6 安装有脱敏 receipts 和 smoke 证据，或有明确补全命令与恢复步骤。
- General 与 General_2 已更新到本地 `main`、状态干净并通过本地验证。
- 未收到明确远端发布指令前不执行远端发布。
