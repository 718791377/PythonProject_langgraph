---
doc_id: project_moe_paper_suggest_static_readiness_evidence_2026_05_24
lang: zh-CN
status: active
doc_class: memory_evidence
translation_of: docs_bilingual/memory/project_moe_paper_suggest_static_readiness_evidence_2026-05-24.md
created_at: 2026-05-24
related_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
---

# Project MOE paper_suggest 静态 readiness 证据 - 2026-05-24

## 范围

本证据记录对 `D:\PythonProject_paper_suggest` 的只读 / static-only readiness 检查。检查不读取或复制项目私有 `MOE.md` 正文，也不写入目标项目文件。

## 命令

```powershell
python .\tools\project_moe_gui_toolchain\check_project_moe_phase1_readiness.py --target-project D:\PythonProject_paper_suggest --agent-name thesis-moe-mentor --state-namespace thesis_moe --static-only --json
```

- 退出码：`1`
- 目标项目根目录：`D:\PythonProject_paper_suggest`
- 只读：`True`
- 写入目标项目：`False`
- CLI 执行模式：`static-only`

## 结果

- readiness status：`blocked`
- adaptation lane：`repair`
- control mode allowed：`False`

结论：本次结果是 **static-only no-go / repair-lane**，不是 Ready Lane 控制批准。除非后续修复下列 blocker 并重新通过 readiness 检查，否则 MOE GUI 不得控制 `paper_suggest`。

## 只读 Git preflight 证据

- `git_status.token`：`blocked:dirty_target_project`
- `git_status.dirty`：`True`
- `git_status.dirty_count`：`4`
- `git_status.read_only_git_optional_locks`：`True`
- `git_status.git_optional_locks`：`0`
- dirty 样例：
  - ` M docs_bilingual/operations/cad_fem_api_automation_usage.md` - 目标项目操作文档存在未分类改动。
  - ` M docs_bilingual/operations/cad_fem_api_automation_usage.zh-CN.md` - 目标项目双语操作文档存在未分类改动。
  - ` M test/test_cad_fem_automation_contract.py` - 目标项目自动化契约测试存在未分类改动。
  - ` M tools/cad_fem_automation/cad_fem_orchestrator.py` - 目标项目自动化编排代码存在未分类改动。

## Surface 证据

- Agent TOML 存在：`True`
- Agent TOML 标准 profile 就绪：`False`
- Agent TOML 必填字段 OK：`True`
- 私有提示源存在：`True`
- 私有提示源边界 OK：`True`
- Mode CLI 存在：`True`
- 已看到读命令 token：`project-status, list-sessions, status, assert-on`
- 已看到写命令 token：`project-on, project-off, on, off, assert-on`
- CLI contract 是否跳过执行：`True`
- CLI contract 跳过原因：`static_only_no_exec_cli`
- startup activation hook 找到：`True`
- operator docs 就绪：`True`

| Wrapper | 存在 | 引用 CLI | 引用命令 | 传递 `--json` | 不安全 token |
| --- | --- | --- | --- | --- | --- |
| on | 是 | 是 | 是 | 否 | `>` |
| off | 是 | 是 | 是 | 否 | `>` |

## Blocker codes

- `blocked:dirty_target_project` - 目标项目存在未分类 dirty 文件。
- `blocked:agent_toml_missing_extension_sections` - Agent TOML 缺少 Project MOE 标准扩展区。
- `blocked:agent_project_boundary_invalid` - Agent TOML 的 project 边界字段不符合标准。
- `blocked:agent_state_namespace_mismatch` - Agent TOML 的 state namespace 缺失或不匹配。
- `blocked:agent_moe_boundary_invalid` - Agent TOML 的 MOE 状态边界字段不符合标准。
- `blocked:agent_dispatch_boundary_incomplete` - Agent TOML 的 dispatch mode、禁止列表或 fallback 不完整。
- `blocked:phase1_wrapper_json_output_missing` - wrapper 未传递 `--json`，无法保证机器可读输出。
- `blocked:phase1_wrapper_unsafe_shell_surface` - wrapper 暴露需要移除或解释的不安全 shell-surface token。

## 边界说明

Static-only 证据是保守证据，只证明文件 surface 观察和只读 Git preflight。它不证明目标 CLI read contract 能够无副作用执行，也不授权 GUI 安装或控制。
