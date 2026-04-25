## ADDED Requirements

### Requirement: 仓库必须提供一条可重复的 Windows native_omx bootstrap repair 路径

仓库必须针对全局安装的 `oh-my-codex` runtime 提供一条可重复的 repair 或 verification 路径，使 Windows native_omx prompt-worker bootstrap 不再依赖 `powershell.exe`。

#### Scenario: 升级后 operator 重新应用 Windows bootstrap fix

- **WHEN** 全局安装的 `oh-my-codex` runtime 已被 upgrade 或 reinstall
- **THEN** 仓库必须提供一种可重复的方法来验证或重新应用 Windows bootstrap fix
- **AND** 这条流程必须保持可审计且可回滚
