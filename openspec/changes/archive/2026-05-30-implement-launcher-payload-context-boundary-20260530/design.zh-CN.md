## 设计

### 根因

启动器 payload 边界是架构问题，而不是单纯文本长度问题。删减提示词可以临时降低命令行长度，但稳定修复方式是让生成的指令正文离开 argv，只在命令行上传递可重建的文件引用。

### 决策 1：验证源头生成器，而不是已安装 wrapper

checker 读取 `tools/install-codex-user-level-team-mode.ps1`，因为用户级 Codex bin 目录下的已安装 wrapper 是生成产物。这样可以保持仓库源码作为修复权威，避免把手工编辑已安装文件变成常态。

### 决策 2：要求 UTF-8 文件化启动指令

生成的启动参数必须由 `Get-CodexUserLevelTeamModeStartupArgs` 组装。该函数通过 `Write-CodexUserLevelModelInstructionsFile` 将生成的 model instructions 写入 `user-level-team-mode-model-instructions.md`，并且只传递一个 `model_instructions_file` 覆盖项。

### 决策 3：对内联启动指令正文 fail closed

checker 检查启动参数函数体和 launcher 函数体；如果它们把 `developer_instructions=` 作为命令行覆盖项，或者在构造 `$startupArgs` 时引用 `$DeveloperInstructions` 而不是仅把它传给文件写入器，则检查失败。

### 数据流

1. launcher 根据持久化的用户级 team-mode state 计算生成的启动指令。
2. 启动参数构造器把较大的指令正文写入 UTF-8 状态文件。
3. 命令行只接收短控制参数和一个 `model_instructions_file` 引用。
4. 生成的 launcher 将 `@startupArgs @Arguments` 转发给 native Codex 可执行路径。

### 风险与缓解

- 风险：未来编辑因为方便而重新引入内联 `developer_instructions`。缓解：聚合 guard 现在运行 launcher payload checker。
- 风险：未来编辑使用非 UTF-8 编码写入状态文件。缓解：checker 和回归测试要求 UTF-8 `Set-Content` 调用。
- 风险：测试 manifest 被另一个活跃会话拥有。缓解：将回归用例放入已注册测试文件，并在本包内避免编辑被声明的 CI manifest。