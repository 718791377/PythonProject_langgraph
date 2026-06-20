# 管理检查清单

## 打开

- [x] 价值：把 48/60 从登记表数字转换为真实生成的正文文档数量。
- [x] 成功标准：Stage A 冻结方案和契约；Stage B 生成 96 个 Codex 正文文件和 120 个一人公司正文文件。
- [x] 约束：本地 main 优先、无远端发布、不重新抽取原始来源、不编辑无关 runtime。

## 设计

- [x] 交付裁剪：两个串行本地 main 包。
- [x] 风险：Windows 命令行长度、UTF-8/中文损坏、registry 漂移、串包污染、误改无关 runtime surface。
- [x] 验收证据路径：OpenSpec validation、generator/checker JSON、聚焦 unittest、本地 gate、本地 MR review、本地集成 helper receipt。

## 构建

- [x] 执行模式：leader 负责 fan-in，咨询专家辅助；Stage B 可使用 runtime/test 与 docs/registry 两个隔离执行切片。
- [x] 写入所有权：Stage B 限制在 generator、checker、tests、registry 和生成的正文运营包文档。
- [ ] Stage A 验证结果已记录。
- [ ] Stage B 验证结果已记录。

## 验证

- [ ] 48 个 Codex 正文英文主文档和 48 个 zh-CN 伴随文件已验证。
- [ ] 60 个一人公司正文英文主文档和 60 个 zh-CN 伴随文件已验证。
- [ ] I/T/O、裁剪、registry、编码、幂等和串包隔离已验证。
- [ ] 本地 main 集成证据已记录。

## 监控

- [x] 当前决策：继续。
- [x] 监控状态：clear。
- [x] 返工触发器：如果 Stage B 不能证明正文全集数量，必须回到设计阶段，而不是合入 runtime。

## 归档

- [ ] Stage B 后 stable specs 已同步。
- [ ] 验证后完成归档。
- [ ] 保留远端发布门。
