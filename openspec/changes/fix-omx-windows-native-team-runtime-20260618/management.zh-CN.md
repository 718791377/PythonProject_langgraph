# 管理记录：修复 OMX Windows 原生团队运行时

## Open

- [x] 价值：移除“Unix/tmux-only runtime 足以代表 Windows native_omx durable team”的错误假设。
- [x] 成功标准：Stage A 冻结契约；Stage B 证明 Windows 运行态 launchability，或给出命名 fail-closed blocker。
- [x] 约束：本地集成，不远程发布；Windows 默认路径不要求 WSL2/tmux；repo-local durable state 按项目隔离。

## Design

- [x] 交付裁剪：两个 local-main 包，先方案冻结，再 runtime 实现。
- [x] 风险/假设：readiness/selected 容易被误当作 launchability；Stage B 必须先写失败测试。
- [x] 验收证据路径：OpenSpec validation、聚焦 PowerShell 测试、local gate、local MR review、本地 main helper。

## Build

- [x] Stage A 执行模式：隔离 worktree，专家 advisory，leader 负责本地集成。
- [x] Stage A 质量证据：management、proposal、design、tasks、spec、plan。
- [x] blocker 决策：persistent team 等 Stage A 冻结且 Stage B 安全切片后再启动；当前 bug 场景不能把 tmux pane 当证据。
- [x] Stage B 实现：Windows 原生 preflight 现在区分 runtime backend、preflight、operational readiness 与 blockers；生成 wrapper 默认不再走 tmux-only 路径。
- [x] Stage B 生命周期 replay patch：prompt runtime/controller shutdown 与 child-exec status patcher 已由 Node 测试和 official-install replay 测试覆盖。

## Verify

- [x] Stage A 验证后的偏差复核：Stage A 已落入本地 `main`；Stage B 继续使用同一个 change，未扩大到远程发布。
- [x] Stage B 聚焦验证后的风险/影响复核：tmux 仍是显式 opt-in backend；不可用时 fail closed；Windows 默认走 prompt/process controller 路径。
- [x] Stage B 聚焦验证后的控制决策：继续进入仓库 gate、local MR review 与本地 main 集成；未授权远程发布。

## Archive

- [x] Stage B runtime 完成后记录价值结果：Windows 原生 OMX team launchability 不再由 selected/ready 状态单独推断，而必须有 operational preflight 证据。
- [x] Stage B runtime 完成后记录经验：prompt/process controller patch replay 必须同时覆盖 startup evidence、child exec status 和 shutdown cleanup。
- [ ] Stage B 本地 main 集成后记录 archive/sync 证据。

## Monitoring

- [x] 当前事实：本机没有可用的 `tmux` team pane 环境，因此 Stage A 不能声称已有真实 persistent team launchability。
- [x] Stage A 决策：继续本地验证与本地 main 集成，不需要返回 earlier phase。
- [x] Stage B 监控决策：persistent-team 证据必须使用 Windows prompt/process controller 生命周期面或命名 blockers，不能只看旧 compatibility team record。
