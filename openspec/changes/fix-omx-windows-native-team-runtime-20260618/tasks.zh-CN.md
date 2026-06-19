# 任务：修复 OMX Windows 原生团队运行时

## Stage A：冻结方案

- [x] 创建 OpenSpec change 以及双语 proposal/design/tasks/management。
- [x] 创建 `docs_bilingual/implementation_plans/` 下的双语 canonical 实施方案。
- [x] 固化四层模型和 Windows runtime backend 词汇。
- [x] 固化 readiness 与真实 launchability 的区别。
- [x] 修正 active team-mode plan，把 P6 重新标记为运行时目标，而不是已完成能力。
- [x] 验证、提交并把 Stage A 合入本地 `main`。

## Stage B：实现 live runtime

- [x] 为 Windows 无 tmux、无 live runtime evidence 的 native OMX false-ready 投影添加失败测试。
- [x] 为 Windows backend selection 与 `omx-team-auto.ps1 -Apply` preflight fail-closed 行为添加失败测试。
- [x] 增加 `runtime_backend`、`preflight_passed`、`operational_ready`、`blockers` 字段。
- [x] 实现 Windows 原生 prompt/process controller 后端，或在不能启动时用命名 blocker fail closed。
- [x] 让自动 helper 的 launch/reuse/switch/shutdown 都经过 operational preflight。
- [x] 增加 launch、status、await、resume、shutdown 和跨项目 cwd 的生命周期证据。
- [ ] 验证、提交并把 Stage B 合入本地 `main`，然后停在远程发布门。
