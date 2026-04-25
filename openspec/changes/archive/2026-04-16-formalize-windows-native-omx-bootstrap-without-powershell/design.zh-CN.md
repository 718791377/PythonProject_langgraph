## Context

用户级 capability-switch 模型现在已经能正常工作：worker-centric flow 选择 `native_omx`，graph-signaled flow 选择 `langgraph`，而且两条 lane 可以在同一套 enabled capability set 下同时存在。剩下的脆弱点已经不在 routing policy，而在全局安装的 `oh-my-codex` runtime。

当前上游 Windows prompt-worker bootstrap 仍通过 `spawnSync('powershell.exe', ...)` 来创建 detached Node controller。而在这个环境里，Node 无法拉起 `powershell.exe` 或 `cmd.exe`，直接得到 `EPERM`。但直接拉起 `node.exe` 仍然是可行的。我们之前的本地实验还证明：child `node.exe` 进程可以在父 shell 退出后继续存活，不一定需要 PowerShell bootstrap。

## Goals / Non-Goals

**Goals:**

- 让 Windows native_omx prompt-worker bootstrap 在正式合同上脱离 `powershell.exe`
- 定义一条 repo-managed 的可重复修复路径，使该修复在 reinstall / upgrade 后仍可恢复
- 把验证聚焦在真实 native_omx worker startup 上

**Non-Goals:**

- 不修改 routing policy 本身
- 不重构 LangGraph 行为
- 除非被证明必要，否则不为了这条修复单独引入新的后台服务

## Decisions

### Decision 1: 当前手工全局 patch 只能作为证据，不能作为最终流程

当前已经打上的全局 `runtime.js` 补丁证明了修复方向是正确的，但它本身不能作为长期交付方式。

考虑过的替代方案：

- 以后需要时继续手工 patch 全局安装
  - 否决，因为它无法跨升级稳定保留，而且也不利于审计

### Decision 2: Windows bootstrap contract 应正式改成直接 Node controller launch

Windows bootstrap contract 应正式定义成“直接由 Node 启动 worker controller”，而不是“通过 PowerShell 中介启动”。

考虑过的替代方案：

- 保留 PowerShell，再继续尝试通过不同参数绕开 EPERM
  - 否决，因为实验已经证明在这个环境里 Node 根本无法拉起 `powershell.exe` 或 `cmd.exe`

### Decision 3: 仓库应拥有一条针对全局安装的 repair / verification 路径

仓库应拥有以下至少一种能力：

- 可重复执行的 repair script
- 可验证并在需要时重打补丁的 verification / reapply script

这样在 `oh-my-codex` reinstall 或 upgrade 后，这条修复仍然能被检查和恢复。

## Risks / Trade-offs

- [Risk] 升级后全局安装结构可能变化。 -> Mitigation: 让修复过程具备版本感知，并在 patch 前先验证目标代码块。
- [Risk] 直接 Node bootstrap 的生命周期边界可能和 PowerShell Start-Process 不完全一致。 -> Mitigation: 真实验证 worker startup、resume 与 shutdown。
- [Risk] 仓库里的 repair 流程可能再次与已安装 runtime 版本漂移。 -> Mitigation: 保持修复范围尽量窄，并锚定在已观察到的 runtime 代码块上。

## Migration Plan

1. 先把已经验证过的 runtime 行为抽象成正式合同。
2. 再实现 repo-managed repair 或 verification script。
3. 再验证修复后 native_omx worker startup 的成功路径。
4. 明确保留 backup 与 rollback 说明。

## Open Questions

- 仓库里的正式方案应自动 patch 已安装 runtime，还是只提供一个在升级后由 operator 显式执行的 verified command？
