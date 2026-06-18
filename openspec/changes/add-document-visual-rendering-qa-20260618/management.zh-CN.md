# 管理记录：增加文档视觉渲染 QA

## Open

- [x] 价值：为文档交付物提供诚实的视觉 QA 证据，而不是在渲染依赖缺失时静默降级。
- [x] 成功标准：Stage A 冻结后端/证据契约；Stage B 从 `D:\PythonProject_langgraph` 实现 runtime 与测试，且不触碰 `D:\project`。
- [x] 约束：仅本地集成，不跟踪第三方二进制，默认可选后端缺失时跳过，严格后端缺失时失败。

## Design

- [x] 交付裁剪：两个本地 main 包，先冻结方案，再实现 runtime。
- [x] 风险/假设：`pdf2image` 在 Windows 渲染时包装 Poppler；LibreOffice 可能缺失；测试必须保持 skip-safe。
- [x] 验收证据路径：OpenSpec 验证、文档工具 focused 测试、本地 gate、本地 MR review 与本地 main helper 证据。

## Build

- [x] Stage A 执行模式：隔离 worktree 与 leader-owned 本地集成。
- [x] Stage A 质量证据：本管理清单以及 proposal/design/tasks/spec/plan artifacts。
- [x] 阻塞决策：durable team 等到 Stage A 冻结方案合入且 Stage B 打开 2+ 实现切片后再启动。

## Verify

- [ ] Stage A 验证后的偏差审查。
- [ ] Stage A 验证后的风险/变更影响审查。
- [ ] Stage A 验证后的控制决策。

## Archive

- [ ] Stage B runtime 工作后的价值结果记录。
- [ ] Stage B runtime 工作后的经验记录。
- [ ] Stage B runtime 工作后的 archive/sync 证据记录。

## Monitoring

- [x] 当前事实：Poppler `pdftoppm` 位于被忽略的 `.local`；`pdf2image` 属于 `.venv`；LibreOffice 属于 Windows 程序安装路径。
- [x] Stage A return/no-return 决策：继续本地验证与本地 main 集成；无需返回循环。
