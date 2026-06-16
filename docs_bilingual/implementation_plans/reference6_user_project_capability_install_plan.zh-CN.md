---
doc_id: reference6_user_project_capability_install_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/reference6_user_project_capability_install_plan.md
---

# Reference 6 用户级/项目级能力安装计划

## 目标

按分层模型安装或登记 `reference_files/6.md` 中列出的能力，并把可复用入口同步到 `D:\PythonProject_General` 和 `D:\PythonProject_General_2`。

参考清单：

- `https://github.com/nexu-io/open-design` - open design-to-code 能力参考，用于可复用 UI/设计转换。
- `https://github.com/nexu-io/html-anything` - HTML 结构化输出转换能力参考。
- `https://github.com/browserbase/skills` - Browserbase skills 集合参考，用于浏览器自动化 skill 包装。
- `https://github.com/pymupdf/pymupdf` - PyMuPDF 源码参考，用于 PDF 解析与渲染能力。
- `https://github.com/opendatalab/MinerU` - MinerU 源码参考，用于文档智能与抽取能力。
- `https://mineru.net/apiManage/limit` - MinerU API 配额页参考，用于 live-service readiness 与 blocker receipt。
- `https://mineru.net/` - MinerU 服务首页参考，用于账号/API 能力发现。
- `https://github.com/virgiliojr94/book-to-skill` - book-to-skill 源码参考，用于从长文档生成可复用 skill。
- `https://github.com/mattpocock/skills` - 可复用 skill 示例参考，用于 Codex/Superpowers 兼容 skill 包装。

## 当前状态

<!-- CURRENT_STATUS_START -->

- 2026-06-16：已从 `reference_files/6.md` 打开计划；实施计划已提交并合入本地 `main`。
- 2026-06-17：runtime/checker/test 实现已完成；真实用户级安装 receipt 已在用户 Codex home 下重新生成；General 与 General_2 模板同步提交已合入各自本地 `main`。
- 默认决策：分层安装、复用 Codex provider `env_key` 名称、redacted receipts / 脱敏 receipt、不做远端发布。

<!-- CURRENT_STATUS_END -->

## 任务 backlog

<!-- TASK_BACKLOG_START -->

- [x] 创建用户级 reference6 manifest、installer、smoke script 和 receipt writer。
- [x] 安装或登记七个参考能力；可用时记录 pinned version 或 commit evidence。
- [x] 运行用户级 smoke，并为缺失外部前置条件记录明确补全方法。
- [x] 更新 `D:\PythonProject_General`：active reusable policy/checker/example config。
- [x] 更新 `D:\PythonProject_General_2`：inert upgrade policy/checker/example manifest。
- [ ] 验证源仓库、用户级、General 和 General_2 门禁；合入本地 main 并停在远端发布门禁。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

| 证据项 | 预期路径或命令 | 状态 |
| --- | --- | --- |
| 计划登记 | `docs_bilingual/docs_registry.yaml` | 已纳入本次变更 |
| 参考源清单 | `reference_files/6.md` | 已纳入本计划 |
| 用户级安装 receipt | `C:\Users\<user>\.codex\state\reference6-capability-install\receipts\*.json` | live receipts 已重新生成；PyMuPDF 与 mineru package 已安装；MinerU service key 仍记录为 redacted blocker |
| 源仓库验证 | `python tools\run_openspec_guard.py --root . --json` | 待最终 gate |
| General 验证 | `tools\ci\local_gate.ps1 -Root D:\PythonProject_General -Json` | 合入本地 main 前已通过；commit `f0a5e94` |
| General_2 验证 | `tools\ci\local_gate.ps1 -Root D:\PythonProject_General_2 -Json` | 合入本地 main 前已通过；commit `01aaff4` |

<!-- EVIDENCE_INDEX_END -->

## 分层决策

- 用户级：安装或登记可复用 CLI、Python 包、Node/GitHub 源、skills、smoke 脚本、manifest 和 receipt。
- `D:\PythonProject_General`：提供 active 可复用项目模板入口、policy、checker 和 example config；不得提交凭据、账号状态、缓存、浏览器会话或外部动作证据。
- `D:\PythonProject_General_2`：仅提供保守 inert 升级入口；默认不得启用 live/API/runtime 行为。

## API key 策略

- 尽可能复用 Codex `C:\Users\lenovo\.codex\config.toml` 的 provider/key 形态。
- 只按环境变量名称复用 provider `env_key`，绝不复制或写入 secret value。
- 需要专用 key 的外部服务只读取现有环境变量存在性，并用脱敏 receipt 记录。
- receipt、manifest、template、test output 和 log 都不得包含密钥明文。

## 阻塞协议

实现不得把未解决阻塞当作完成。每个阻塞必须记录：

1. 缺少什么；
2. 不泄露密钥的补全命令；
3. 脱敏验证命令；
4. 下一步恢复位置。

已知前置风险：

- 本机 GitHub HTTPS 可能出现 Windows Schannel 凭据错误；在声明 GitHub source installed 失败前，应改用 SSH remote 或修复 Git TLS/credential。
- `uv` 与 `pnpm` 可能缺失；除非上游包强依赖，否则优先使用 Python venv/pip 和 npm/npx。
- `mineru` 与 `browserbase` API smoke 可能需要服务专用环境变量。

## Runtime 实现说明

- 仓库内 runtime 入口：`tools/reference6_capability_install.py`。
- 仓库内 checker：`tools/check_reference6_capability_install.py`。
- CI 测试：`test/reference6_capability_install.test.py`。
- runtime 使用 `utf-8-sig` 读取 Codex config，只记录 `env_key` 名称和是否存在，不复制 secret value。
- receipt 使用便于人工确认的标签，同时对 install、wrapper、state、rollback 位置做 hash 脱敏。

## 验证门禁

- 源仓库：`python tools\run_openspec_guard.py --root . --json`、相关 checker/test、`tools\ci\local_gate.ps1`、`tools\ci\local_mr_review.ps1`。
- 用户级：manifest parse、receipt redaction check、按可用 key 执行 import/help/API-smoke。
- General：新增 reference6 checker、`tools\ci\local_gate.ps1 -Root . -Json`、local MR review。
- General_2：inert checker、`tools\ci\local_gate.ps1 -Root . -Json`、local MR review。

## 完成标准

- 源仓库计划与实现提交均合入本地 `main`。
- 用户级 reference6 安装有脱敏 receipts 和 smoke 证据，或有明确补全命令与恢复步骤。
- General 与 General_2 已更新到本地 `main`、状态干净并通过本地验证。
- 未收到明确远端发布指令前不执行远端发布。

## Live execution evidence

- 用户级 artifacts 已通过 `python tools\reference6_capability_install.py apply --apply --operator-confirmation --resolve-git-refs --codex-home C:\Users\<user>\.codex --json` 写入用户 Codex home。
- PyMuPDF 用户级 package smoke 通过，`fitz` 可 import，版本 `1.27.2.3`。
- MinerU 用户级 package smoke 可 import `mineru`，版本 `3.3.1`；live service smoke 仅因缺少 `MINERU_API_KEY` 阻塞，已记录 `setx MINERU_API_KEY <secret-value>` 与脱敏恢复命令。
- `D:\PythonProject_General` 本地 `main` 已包含 active reusable Reference 6 模板表面，commit `f0a5e94`。
- `D:\PythonProject_General_2` 本地 `main` 已包含 inert Reference 6 升级样例，commit `01aaff4`。
