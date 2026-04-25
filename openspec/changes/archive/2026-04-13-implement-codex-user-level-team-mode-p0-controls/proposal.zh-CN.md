## Why

用户级团队模式方案已经稳定，但仓库里仍缺少一个安全的实现面，能够把这份方案真正落成“同一 Windows 用户下、所有 Codex CLI 项目都能复用”的资产。

当前最需要的是一个 `P0` 控制层：它必须可测试、可回退、增量式，并且只能生成用户级状态与辅助资产，不能替换或破坏原生 `codex` 入口。

## What Changes

- 增加一个仓库内安装器/生成器，可把用户级 Codex 团队模式控制资产生成到显式指定的 Codex home 目录。
- 生成以下增量式用户级资产：
  - `team-leader.toml`
  - `codex-omx-on.ps1`
  - `codex-omx-off.ps1`
  - `codex-omx-status.ps1`
  - `codex-subagents-auto.ps1`
  - `codex-subagents-manual.ps1`
  - `codex-subagents-off.ps1`
  - `codex-routing-status.ps1`
- 引入一个全局状态文件，分别记录 `oh_my_codex` 与 `subagent_routing` 两套独立控制。
- 增加安装前备份快照，使失败写入可以自动回滚。
- 保证生成资产是增量式的，并明确禁止创建或替换 `codex`、`codex.cmd`、`codex.ps1`。
- 增加仓库测试，验证资产生成、状态切换、纯净排障模式语义，以及“不破坏原生 Codex”的安全边界。

## Capabilities

### New Capabilities

- `codex-user-level-team-mode-controls`
  - 为用户级 Codex / oh-my-codex 团队模式状态提供可复用的安装器生成控制层

### Modified Capabilities

- None.

## Impact

- 影响路径：
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p0-controls/`
- 本变更不修改 OpenClaw 运行时配置。
- 本变更不 patch oh-my-codex 包内部实现。
- 本变更不得替换、遮蔽或破坏原生 `codex` 的可执行入口。

## impact_scope

- 仅限仓库内安装器与验证面
- 面向显式目标路径的用户级 Codex home 资产生成
- 为 `oh_my_codex` 与 `subagent_routing` 提供增量式控制资产
- 为托管用户级资产提供版本化备份快照与失败自动回滚
- 保证 plain native Codex 可持续使用的安全边界

## explicit_non_goals

- 开发和测试阶段不直接改写 `C:\Users\lenovo\.codex`
- 不替换原生 `codex` 入口、shim、alias 或可执行文件
- 本 `P0` 不实现 mixed persistent pane compose
- 本 `P0` 不实现专家常驻 pane 编排
- 不改变 OpenClaw 仓库特定的 runtime 或 proxy 行为
- 不走 WSL2 路径

## rollout_sequence

1. 先完成 `P0` 控制面的 OpenSpec 工件。
2. 实现一个仓库内安装器/生成器，目标指向显式指定的 Codex home 路径。
3. 生成增量式控制脚本、leader profile 与共享状态文件。
4. 在写入前增加备份快照，并在部分失败后自动回滚。
5. 验证 `on/off/auto/manual`、纯净排障模式与回滚行为。
6. 验证安装器不会创建、替换或修改任何原生 `codex` 命名文件。
7. 更复杂的 hybrid staffing wrapper 与 compose manifest 留到后续阶段。

## rollback_plan

- 如果生成面证明不安全或误导性过强，则删除安装器和对应测试。
- 如果仓库后续采用不同的用户级控制模型，则移除这次新增 capability 与变更工件。
- 回滚要保持窄范围：只回退仓库内生成器与变更工件，不去碰仓库外已经生成的用户 home 资产。

## validation_path

- 运行专用 PowerShell 测试，验证生成、状态切换与回滚
- 验证生成资产全部留在显式指定的 Codex home 目标路径内
- 验证默认会拒绝覆盖非托管冲突文件
- 验证安装失败后会从备份快照恢复安装前的托管状态
- 验证安装器永远不会创建或覆盖 `codex`、`codex.cmd`、`codex.ps1`
- 运行 `openspec validate --all`
- 运行 `python .\tools\run_openspec_guard.py --root .`

## mainline_classification

- 新主线候选
- 面向跨项目复用的 Codex / oh-my-codex 用户级工作流基础设施
- 实际上属于 cross-mainline，因为它横跨可复用工具、验证与治理，但不归属于现有任何 OpenClaw 运行时主线
