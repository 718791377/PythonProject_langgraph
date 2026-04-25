## 1. OpenSpec 工件

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p3-routing-thresholds` 的 proposal、design 与 capability spec。
- [x] 1.2 记录启动路径语义、仓库级运行态隔离规则，以及角色路由阈值。
- [x] 1.3 记录只读 routing-policy 检查面，并明确普通 `codex` 启动不得自动拉起 durable team 这一 non-goal。

## 2. 安装器 / 生成器

- [x] 2.1 扩展生成的 shared support script，加入结构化 routing-policy 定义、developer-instruction 渲染与 startup-argument helper。
- [x] 2.2 生成 `codex-routing-policy.ps1`，并更新启动器，使其从共享 routing-policy 模型派生 developer instructions。
- [x] 2.3 更新生成的 `team-leader.toml` 与 `docs/team-mode-playbook.md`，使其镜像批准的角色路由阈值与启动/隔离语义。
- [x] 2.4 让新的 routing-policy 资产及更新后的生成文件继续落在现有 additive-only 备份快照与回滚事务之内。

## 3. 验证

- [x] 3.1 扩展 PowerShell 测试，验证 `codex-routing-policy.ps1` 的生成与 JSON 输出。
- [x] 3.2 验证 `auto / manual / off` 三种 routing 状态下的 developer-instructions 注入行为。
- [x] 3.3 验证生成的 playbook 与 leader profile 是否包含路由阈值和启动路径规则。
- [x] 3.4 运行 `openspec validate --all` 与 `python .\tools\run_openspec_guard.py --root .`。
