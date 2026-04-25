## Why

`P0` 控制层已经完成安装与验证，但它目前只做到“持久化状态 + 辅助脚本”。

现在还缺最后一块：把全局 `oh_my_codex` 与 `subagent_routing` 状态真正接到日常 `codex` 启动路径上，同时又不替换原生 Codex 可执行文件。

这套用户级方案只有在普通 PowerShell `codex` 启动能够满足以下条件时才算完整：

- 原生 Codex 仍然存在并可绕过
- `oh_my_codex=on` 时进入 Codex + oh-my-codex 模式
- `oh_my_codex=off` 时保持原生模式
- `subagent_routing=off` 时关闭角色编排
- 启动绑定安装失败时可以安全回滚

## What Changes

- 扩展仓库内安装器，为 PowerShell shell 生成启动绑定 launcher 脚本。
- 增加一个托管的 PowerShell profile block，把 `codex` 路由到 launcher，同时保留原始 `codex-native` 逃生入口。
- 通过 Codex CLI 运行时参数映射 `oh_my_codex` 与 `subagent_routing` 状态，而不是替换原生 `codex` 二进制。
- 明确保持原生 `codex`、`codex.cmd`、`codex.ps1` 不被修改。
- 把安装期备份与回滚覆盖扩展到 PowerShell profile 与 startup-binding 资产。
- 增加测试，验证 launcher 参数映射、profile block 安装以及部分失败时的回滚。

## Capabilities

### New Capabilities

- `codex-user-level-team-mode-startup-binding`
  - 提供一个可回退的 PowerShell 启动绑定，使普通 Codex 启动能够应用用户级 team-mode 状态，而不替换原生可执行文件

### Modified Capabilities

- `codex-user-level-team-mode-controls`
  - 扩展安装器与验证面，使其覆盖 startup-binding 资产与 PowerShell profile block

## Impact

- 影响路径：
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p1-startup-binding/`
- 真实安装时，本变更会向用户 PowerShell profile 加入一个托管 block。
- 本变更不会替换或 patch npm 安装的原生 `codex` 文件。
- 本变更把受支持的启动绑定路径标准化为原生 Windows PowerShell，而不是 `cmd.exe`，也不是 WSL2。

## impact_scope

- 面向 PowerShell 型 Codex 启动的用户级 startup binding
- 从持久化 team-mode 状态到 Codex CLI 运行时覆盖参数的 launcher 映射
- 带备份与回滚的托管 profile 集成
- 保留原生 Codex 二进制路径以及一个 bypass 入口

## explicit_non_goals

- 不替换 `C:\Users\lenovo\AppData\Roaming\npm\codex*`
- 不强制为 `cmd.exe` 提供启动绑定
- 不引入 WSL2 启动路径
- 本阶段不做 mixed-pane compose 编排
- 不修改 OpenClaw runtime 配置

## rollout_sequence

1. 创建 startup binding 的 `P1` OpenSpec 工件。
2. 生成一个 launcher 脚本，读取 `user-level-team-mode.json` 并计算 Codex CLI 覆盖参数。
3. 生成一个托管的 PowerShell profile block，定义 `codex` 与 `codex-native`。
4. 把备份快照与回滚覆盖扩展到 profile 路径和 startup-binding 资产。
5. 在临时环境中验证 profile 安装、launcher 参数映射与回滚行为。
6. 只有在仓库级验证通过后，才重新安装到真实用户 home。

## rollback_plan

- 如果启动绑定被证明不安全或误导，则移除 launcher 与 profile block。
- 保持回滚范围最小：恢复安装前的 PowerShell profile 内容，只删除新增的托管 startup-binding 资产。
- 回滚时绝不触碰 npm 安装的原生 `codex` 文件。

## validation_path

- 运行专用 PowerShell 测试，验证 startup-binding 安装与 launcher 行为
- 验证 launcher 会保留原生可执行文件路径，并暴露原始 bypass 入口
- 验证 `oh_my_codex=off` 会清除 omx 相关启动行为
- 验证 `subagent_routing=off` 会关闭 multi-agent 启动路由
- 验证 startup-binding 安装部分失败时会恢复安装前的 profile 内容
- 运行 `openspec validate --all`
- 运行 `python .\tools\run_openspec_guard.py --root .`
