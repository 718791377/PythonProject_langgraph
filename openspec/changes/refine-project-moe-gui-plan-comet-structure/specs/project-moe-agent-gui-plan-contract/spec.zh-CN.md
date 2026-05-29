## ADDED Requirements

### 需求：Project MOE GUI 方案采用完整 Comet 可执行结构

Project MOE Agent GUI 实施方案必须采用完整 Comet 可执行方案结构，清晰区分文档就绪、目标项目就绪、GUI 运行时完成、本地集成和远端发布授权。

#### 场景：方案结构达到实施切片就绪

- **GIVEN** 实施者打开 `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md`
- **WHEN** 他们在代码实施前复核方案
- **THEN** 方案暴露目标、架构、关系模型、source of truth、安装产物、CLI contract、GUI contract、JSON state model、readiness lanes、安全规则、rollback 规则、验证路径、实施任务、风险决策和自检项
- **AND** 不得在缺少 readiness 证据时声称目标项目已经 GUI-ready。

#### 场景：运行时能力不被夸大

- **GIVEN** 方案结构已经就绪
- **WHEN** 目标项目只有 static Phase 1 证据或仍存在 blocker
- **THEN** 方案必须让目标项目保持在 Ready-candidate 或 Repair Lane
- **AND** 在目标项目 readiness checker 证明 ready 之前，`control_mode_allowed` 必须保持 false。

#### 场景：Comet 脚本证据保持诚实

- **GIVEN** 当前 Windows shell 无法运行 Comet `.sh` 脚本
- **WHEN** change 记录 Comet 状态
- **THEN** 状态记录脚本 blocker，并使用 OpenSpec / 仓库 gate 作为 fallback evidence
- **AND** 不得声称 `comet-state.sh` 或 `comet-guard.sh` 已通过。

### 需求：Project MOE GUI 卸载 apply 只删除已验证受管产物

Project MOE GUI 卸载命令必须支持显式 `--apply` 路径；只有 manifest 路径白名单和 hash 验证通过后，才允许删除 Project MOE GUI 受管产物，并且必须保留目标项目私有提示源、Agent TOML 与 `.omx/state` 运行时状态。

#### 场景：成功 apply 只删除受管 GUI 产物

- **GIVEN** 目标项目包含由本工具链生成的 Project MOE GUI install manifest
- **AND** 每个计划删除的受管文件路径都在 Project MOE GUI managed artifact 白名单内
- **AND** 每个非 manifest 受管文件 hash 都与 manifest 匹配
- **WHEN** 操作员运行 `plan_project_moe_gui_uninstall.py --apply --json`
- **THEN** 命令只删除已验证的 managed GUI 文件
- **AND** JSON payload 返回 `apply_supported=true`、`delete_executed=true`、`applied_file_changes` 和 `uninstall_receipt`
- **AND** 目标项目的 `MOE.md`、`.codex/agents/*.toml` 和 `.omx/state` 保持不变。

#### 场景：不安全 manifest 在删除前 fail closed

- **GIVEN** 目标 install manifest 声明了 Project MOE GUI managed artifact 白名单外路径
- **OR** 非 manifest 受管文件缺失 hash 或 hash 不匹配
- **OR** 受管条目解析为目录
- **WHEN** 操作员运行带 `--apply` 的卸载命令
- **THEN** 命令必须在删除任何文件前 fail closed
- **AND** 返回稳定 blocker，例如 `blocked:uninstall_path_not_in_managed_allowlist`、`blocked:managed_file_hash_missing`、`blocked:managed_file_hash_mismatch` 或 `blocked:managed_path_is_directory`。
