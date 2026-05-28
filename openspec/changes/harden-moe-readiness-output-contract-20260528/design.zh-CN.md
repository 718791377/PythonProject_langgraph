# 设计：Project MOE Readiness 输出契约

## 当前状态

`check_phase1_readiness()` 已经计算 adaptation lane、blockers 和 `control_mode_allowed`。它也会把已检查的表面放入嵌套对象，例如 `agent_toml`、`mode_cli_surface`、wrappers、startup hooks 和 operator docs。

## 缺口

GUI preflight 和 rollout 证据需要稳定的顶层 checked files 与脱敏路径别名摘要。没有这些字段时，调用方必须从嵌套实现细节中推断证据。

## 决策

在 readiness payload 上增加一个小的派生契约层：

- `warnings`：机器可读 warning 记录；没有 warning 时为空数组。
- `checked_files`：Phase 1 readiness 检查过的每个目标项目文件候选项的稳定记录。
- `redacted_paths`：适合日志和 UI 证据展示的稳定别名与相对路径。

新增字段是增量字段，不移除既有面向操作者的绝对路径字段。

## 安全说明

- 检查器保持只读。
- 仍然不读取或复制 private prompt 正文。
- `checked_files` 中的路径是目标项目相对值或脱敏别名，不包含 private prompt 正文。
- static-only 执行仍然不会执行目标 CLI。

## 验证重点

- Ready Lane 输出包含所有必需契约字段。
- Static-only 输出包含 warning，且仍然阻止 control。
- 既有 readiness lane 行为保持不变。
