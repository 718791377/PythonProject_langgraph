## 1. OpenSpec 工件

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p1-startup-binding` 的 proposal、design 与 capability spec。
- [x] 1.2 记录“只支持 PowerShell 启动绑定”与“保留原生可执行文件”的范围规则。
- [x] 1.3 记录 launcher 侧的“状态到参数”映射，以及 profile 回滚要求。

## 2. 安装器 / 生成器

- [x] 2.1 扩展安装器，生成 startup-binding launcher 脚本，并保存解析出的原生 Codex 路径。
- [x] 2.2 扩展安装器，托管一个定义包装 `codex` 与 `codex-native` 的 PowerShell profile block。
- [x] 2.3 把 profile 路径与 startup-binding 资产纳入备份快照与回滚覆盖。

## 3. 验证

- [x] 3.1 扩展 PowerShell 测试，使用 fake native Codex 目标验证 profile block 安装与 launcher 参数映射。
- [x] 3.2 验证包装启动在 `oh_my_codex` 与 `subagent_routing` 各模式下的映射行为。
- [x] 3.3 验证 startup-binding 部分失败时的回滚。
- [x] 3.4 运行 `openspec validate --all` 与 `python .\tools\run_openspec_guard.py --root .`。
