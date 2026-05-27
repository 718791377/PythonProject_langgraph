# 管理检查清单

## Open

- [x] 已检查价值证据：旧方案需要完整 Comet 结构，以避免 readiness 混淆。
- [x] 已检查成功标准：双语方案对、OpenSpec artifact、design record、execution plan 和验证路径。
- [x] 已检查干系人与约束：Codex operator、后续 GUI 维护者、消费项目、本地优先流程。

## Design

- [x] 已检查交付裁剪：仅文档重构、feature worktree 隔离、不写 runtime 或用户级目录。
- [x] 已检查风险与假设：共享 runtime readiness 不得被夸大成消费项目 GUI readiness。
- [x] 已检查验收证据路径：方案结构、显式门禁、OpenSpec validation、本地 gate。

## Build

- [x] 已检查执行模式：在专用 worktree 中按 `executing-plans` 执行。
- [x] 已检查质量证据：双语文件和支持 artifact 必须保持 UTF-8 clean。
- [x] 已检查 blocker 决策：记录 Comet bash 限制，而不是隐藏。

## Verify

- [x] 已检查偏差：不安装、不写目标项目、不启动可见 GUI、不打包、不远端发布。
- [x] 已检查风险/变更影响：仅文档和 OpenSpec 影响。
- [x] 已检查控制决策：验证后继续进入本地 feature commit 与本地集成。

## Monitoring

- [x] 已检查当前事实：feature worktree 已存在；未达到 durable-team 阈值；任务仅限本地。
- [x] 已检查 return/no-return 决策：本范围重构不需要回退到 Open/Design。

## Archive

- [x] 已检查延期价值结果：方案结构达到 implementation-slicing ready。
- [x] 已检查经验教训：没有 bash 时不得声称 `.sh` Comet 脚本已通过。
- [x] 已延期 archive/sync 证据：`.openspec.yaml` 记录 archive deferral 与 follow-up。
