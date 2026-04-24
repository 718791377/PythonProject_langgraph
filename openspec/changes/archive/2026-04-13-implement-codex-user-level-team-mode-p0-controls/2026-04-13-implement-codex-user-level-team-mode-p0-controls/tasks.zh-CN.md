## 1. OpenSpec 工件

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p0-controls` 的 proposal、design 与 capability spec。
- [x] 1.2 固化 `P0` 边界：只做增量式用户级控制资产，不替换 native `codex`。
- [x] 1.3 记录 `oh_my_codex` 与 `subagent_routing` 的独立控制语义，以及 pure debugging mode。

## 2. 安装器 / 生成器

- [x] 2.1 增加一个仓库内安装器，把 `P0` 控制资产生成到显式指定的 Codex home。
- [x] 2.2 生成共享 support script、leader profile、状态文件，以及 omx / routing 控制脚本。
- [x] 2.3 默认拒绝覆盖非托管冲突文件，并保留所有原生 `codex` 命名文件。
- [x] 2.4 在写入前创建时间戳备份快照，并在安装失败时自动恢复托管路径。

## 3. 验证

- [x] 3.1 增加专用 PowerShell 测试，验证生成、状态切换与非托管冲突拒绝。
- [x] 3.2 验证 pure debugging mode 语义与“仅增量、不破坏原生 Codex”的安全保证。
- [x] 3.3 验证备份快照创建以及部分安装失败后的自动回滚。
- [x] 3.4 运行 `openspec validate --all` 与 `python .\tools\run_openspec_guard.py --root .`。
