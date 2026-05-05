## 为什么

当前 user-level team-mode baseline 已经在概念上保护 native Codex，而且 installer 已经具备 backup 和 rollback 行为。缺口是：在任何 release 被标记为 production-ready 之前，还需要一个明确的 release-level gate 来证明这些保护确实存在。

用户要求是：Codex 原生功能必须继续可用，版本发布必须可回退，wrapper 或 user-level team-mode assets 不能破坏日常 Codex 使用。

## 变更内容

- 新增 Codex native preservation and rollback release-gate template。
- 新增 repository checker，用来验证 release-gate template 和静态源码证据。
- 将 checker 接入 `tools/run_openspec_guard.py` —— 这是聚合项目 OpenSpec enforcement checks 的仓库总守卫。
- 在 active team-mode plan 和 long-term production durable-team draft 中补充该 release-gate slice。

## 能力

### 新增能力

- `codex-user-level-team-mode-controls` —— 增加 release gate，用来检查 native Codex preservation、backup snapshots、rollback evidence 和 config rewrite sentinel evidence。
- `codex-user-level-team-mode-startup-binding` —— 增加 startup-binding release checks，用来检查 `codex`、`codex-raw` 和 `codex-ohmy` 这些入口的行为边界。

### 修改能力

- 无。

## 影响

- 影响路径：
  - `tools/codex_native_rollback_release_gate_template.json` —— 描述 native Codex preservation 和 rollback 所需 release evidence 的 JSON template。
  - `tools/check_codex_native_rollback_release_gate_template.py` —— 验证 release-gate template 和 repository evidence 的静态 checker。
  - `tools/run_openspec_guard.py` —— 会运行新增 checker 的 aggregate guard。
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` —— user-level team mode 的英文 active implementation plan。
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` —— user-level team mode 的中文对照 implementation plan。
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` —— long-term production durable-team target 的英文 draft。
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` —— long-term production durable-team target 的中文对照 draft。
- 本变更不会安装或激活 user-level assets。
- 本变更不会修改 `C:\Users\lenovo\.codex\config.toml` —— 这是 Codex 用户配置文件，必须保持显式用户控制。
- 本变更不会替换 native `codex` executable，也不会启动 durable team。

## impact_scope

- 仅限 repository-local release-gate template 和 checker
- native Codex preservation 与 rollback behavior 的静态源码证据
- OpenSpec guard 接入
- 新 release slice 的双语方案对齐

## explicit_non_goals

- 不向真实 user Codex home 做 live installation
- 不修改 `C:\Users\lenovo\.codex\config.toml` —— Codex 用户配置文件
- 不替换、包装或修改 `codex`、`codex.cmd`、`codex.ps1` —— native Codex entrypoint names
- 不启动 durable team，不运行 `omx team`，不激活 LangGraph runtime
- 本 change 自身不做 GitLab 或 GitHub publication action

## rollout_sequence

1. 定义 release-gate template。
2. 增加 checker，检查 required release evidence 和静态源码证据。
3. 将 checker 接入 OpenSpec guard。
4. 更新 active plan 和 long-term draft，写入该 release-gate slice。
5. 使用 checker、OpenSpec validation、installer rollback test 和 aggregate guard 完成验证。

## rollback_plan

- 如果 release gate 过宽或容易误导，删除新增 template 和 checker。
- 从 `tools/run_openspec_guard.py` —— 聚合 OpenSpec guard 脚本中删除新增 guard step。
- 只回退 repository-local 文件；本 slice 不会修改 user-level Codex assets。

## validation_path

- 运行 `python .\tools\check_codex_native_rollback_release_gate_template.py --root . --json` —— 验证 release-gate template 和静态 repository evidence。
- 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1` —— 在临时目录验证 installer backup 和 rollback behavior。
- 运行 `openspec validate --all` —— 验证 OpenSpec artifacts 和 stable specs。
- 运行 `python .\tools\run_openspec_guard.py --root . --tool codex --json` —— 运行仓库聚合 guard。
- production publication 前可选本地 smoke checks：`codex --version`、`codex-raw --version` 和短 `codex-ohmy` help/version check。

## mainline_classification

- bounded release-gate hardening slice
- 不做 runtime activation
- 可在后续 native_omx 或 LangGraph adoption 之前安全实施
