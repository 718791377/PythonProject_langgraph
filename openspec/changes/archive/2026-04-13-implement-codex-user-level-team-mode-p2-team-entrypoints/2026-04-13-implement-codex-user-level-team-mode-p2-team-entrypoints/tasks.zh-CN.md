## 1. OpenSpec 工件

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p2-team-entrypoints` 的 proposal、design 与 capability spec。
- [x] 1.2 记录“保留原生 `omx`”规则，以及新的 wrapper / playbook 生成资产。
- [x] 1.3 记录 hybrid staffing bridge 与 verification-plan 语义。

## 2. 安装器 / 生成器

- [x] 2.1 扩展安装器，解析原生 `omx` 命令路径，并生成新的 wrapper 资产与 playbook。
- [x] 2.2 扩展 shared support script，加入 team name 发现、ops 分发、hybrid planning 与 verification planning 帮助函数。
- [x] 2.3 让新资产继续落在既有 additive-only 备份快照与回滚事务之内。

## 3. 验证

- [x] 3.1 扩展 PowerShell 测试，使用 fake `omx` 目标验证 wrapper 生成与命令分发。
- [x] 3.2 验证 `omx-team-dev`、`omx-team-debug`、`omx-team-ops`、`omx-team-hybrid` 的行为。
- [x] 3.3 验证 `omx-team-verify` 输出的是 leader 侧 verification plan，而不是持久 verifier 启动。
- [x] 3.4 运行 `openspec validate --all` 与 `python .\tools\run_openspec_guard.py --root .`。
