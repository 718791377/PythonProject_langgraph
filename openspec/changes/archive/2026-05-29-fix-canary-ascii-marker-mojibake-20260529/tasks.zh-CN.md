## 1. 文档和规格

- [x] 1.1 更新启动摘要双文件，使当前可见 canary 标记为 ASCII 稳定形式，历史非 ASCII 标记仅作为旧证据检测输入。
- [x] 1.2 为 canary surface 能力增加 OpenSpec delta，覆盖 ASCII 当前标记和历史标记拒绝。

## 2. 检查器和测试实现

- [x] 2.1 更新 canary surface 检查器：使用 ASCII 片段组装当前标记，并保留历史/损坏检测失败关闭。
- [x] 2.2 更新 startup mojibake 检查器：接受当前 ASCII 响应证据，拒绝历史/损坏 canary 证据。
- [x] 2.3 更新目标测试，覆盖当前 ASCII 证据以及历史/损坏证据拒绝。

## 3. 验证和集成

- [x] 3.1 运行目标 canary / startup-mojibake 测试和检查器命令。
- [x] 3.2 运行 OpenSpec/precommit/local-gate 验证。
- [ ] 3.3 提交、运行本地 MR review、合入本地 `main`，并停在远端发布审批门前。
