# Receipt redaction guard 设计

## 决策

实现 repo-local 通用 guard，用于校验 authorization receipts、update receipts、rollback pointers 与 redaction 边界；在任何用户级安装 lane 被标记为 active 前，先提供可测试的本地治理门禁。

## 边界

- 不修改用户级 Codex 配置。
- 不调用外部 MCP、不控制浏览器、不读取 browser data。
- 默认输出对私有路径与 rollback pointer 做 hash。
- 对 raw secrets、cookies、tokens、message contents、browser data、plugin description dumps fail closed。

