## 1. OpenSpec Artifacts

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p4-burst-review-agents` 的 proposal、design 与 capability specs。
- [x] 1.2 记录 burst-review agent profiles，以及其 leader 侧默认只读使用规则。
- [x] 1.3 记录 routing-policy 增量要求，使其暴露“已安装、可调用”的 burst-review 角色。

## 2. Installer / Generator

- [x] 2.1 扩展安装器，在目标用户级 `agents/` 目录中生成 `bug-finder.toml`、`bug-rebutter.toml`、`bug-judge.toml`。
- [x] 2.2 扩展共享 support runtime 与 `codex-routing-policy.ps1` 输出，加入 burst-role 安装元数据和可调用角色可见性。
- [x] 2.3 更新生成出来的 `team-leader.toml` 与 `docs/team-mode-playbook.md`，使其把 triad 描述为真实生成的 leader 侧角色。
- [x] 2.4 将新增 agent 文件纳入现有的 additive-only 备份快照与失败回滚事务。

## 3. Validation

- [x] 3.1 扩展 PowerShell 安装器测试，验证 burst-role 文件生成和备份清单覆盖。
- [x] 3.2 针对 fresh install 与 existing install 的失败路径，验证新增 agent 文件的回滚行为。
- [x] 3.3 验证 `codex-routing-policy.ps1 -Json` 会暴露已安装的 burst-review 角色。
- [x] 3.4 运行 `test/install-codex-user-level-team-mode.test.ps1`。
- [x] 3.5 运行 `openspec validate --all` 与 `python .\tools\run_openspec_guard.py --root .`。
- [x] 3.6 重装到真实用户 Codex home，并验证 `omx agents list --scope user` 中出现 `bug-finder`、`bug-rebutter`、`bug-judge`。
