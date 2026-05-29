# 管理清单

## Open

- [x] 价值/原因证据已检查：上一版结构仍需要完整 Comet trace、状态边界说明和支撑 artifacts 修复。
- [x] 成功标准证据已检查：目标文件具备 Comet 结构、OpenSpec artifacts、设计文档、实施计划和验证路径。
- [x] 干系人/约束已检查：Codex operator、未来 Project MOE GUI implementers、目标项目、local-first 发布政策。

## Design

- [x] 交付裁剪已检查：初始切片是文档/治理重构，本延续切片新增一项受保护卸载 `--apply` 工具链行为；不进入 PySide6 安装、user-level 写入或真实目标项目投放。
- [x] 风险/假设已检查：Windows Comet bash 不可用，必须用文件态和仓库 guard 作为 fallback evidence。
- [x] 验收证据路径已检查：proposal、design、tasks、目标方案、Superpowers 设计/计划与本地验证命令。

## Build

- [x] 执行模式已检查：使用 feature worktree 和 `executing-plans` 执行方案重构及受保护卸载 `--apply` 切片。
- [x] 质量证据已检查：目标方案需对齐 Pi sidecar 新结构与 Comet runtime 控制语义，卸载行为需通过工具链定向测试与仓库门禁。
- [x] blocker 决策已检查：Comet bash 缺失不阻断文档重构，但阻断脚本 transition 声明。

## Verify

- [x] 偏差复核已检查：本次包含受保护卸载 `--apply` 的有界 runtime 实现，因此验收同时覆盖文档结构、OpenSpec、卸载安全测试、guard 与 local CI。
- [x] 风险/变更影响已检查：删除行为只限白名单内且 hash 已验证的受管文件；保留 `MOE.md`、`.codex/agents/*.toml` 与 `.omx/state`，不扩大到真实目标项目投放、不改 user-level 目录、不远端发布。
- [x] 控制决策已检查：继续验证；若 guard 或 CI 失败，回到 Build 修复。

## Archive

- [x] 价值结果已检查：方案具备进入后续实现切片的结构，并完成一个受保护卸载运行时切片，待本地集成证据收口。
- [x] 经验教训已检查：Windows 上不能伪造 Comet bash transition；中文 artifacts 必须保持 UTF-8。
- [x] 归档/同步证据已检查：当前先记录 archive deferral，待本地验证与集成完成后再按 Comet/OpenSpec 规则归档。

## Monitoring Loop

- [x] 当前事实：目标是计划结构重构、受保护卸载 `--apply` 实现与本地 main 集成，不包含远端发布。
- [x] 回退/不回退决策：`control_decision=continue`，无需回退到 Open/Design/Build/Verify。
- [x] 证据留存：保留任务清单、management record、设计/计划文档、验证输出摘要与 commit。
