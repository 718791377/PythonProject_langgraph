## 新增需求

### 需求：Project MOE Phase 1 Readiness 输出暴露证据摘要

Project MOE Phase 1 readiness 检查器必须为 GUI preflight 和 rollout 决策暴露稳定的顶层证据摘要字段。

#### 场景：Ready Lane 输出包含证据字段

- **假设** 目标项目满足 Phase 1 静态与 read-contract readiness
- **当** 操作者运行 `check_project_moe_phase1_readiness.py --json`
- **那么** payload 包含 `adaptation_lane`、`blockers`、`warnings`、`checked_files`、`redacted_paths` 和 `control_mode_allowed`
- **并且** `adaptation_lane` 为 `ready`
- **并且** `control_mode_allowed` 为 true
- **并且** `checked_files` 包含 agent TOML、private prompt source、Mode CLI、wrappers、startup hooks 和 operator docs 的记录。

#### 场景：Static-only 输出警告缺少 CLI 证据

- **假设** 目标项目满足静态 readiness 表面
- **当** 操作者运行 `check_project_moe_phase1_readiness.py --static-only --json`
- **那么** payload 包含 read-contract CLI execution 被跳过的 warning
- **并且** `control_mode_allowed` 仍为 false。
