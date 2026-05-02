## Design / 设计

wrapper 对 MCP stdio 采用保守策略：`wrapper` 是 Codex 与 MCP Router 之间的本地包装层，目标是记录日志并降低无关 stderr 噪声。

- Child stdout 以 bytes 形式从 child stdout 复制到 wrapper stdout，不解析、不过滤、不按行切分、不插入换行，也不做 encoding replacement。`stdout` 是 MCP 协议通道，必须保持 byte-for-byte 完整。
- Child stdin 以 bytes 形式从 wrapper stdin 复制到 child stdin。`stdin` 是 MCP 请求输入通道，必须保持 byte-for-byte 完整。
- Child stderr 仍可以按文本分类，因为 stderr 不是 Codex 的 MCP 协议通道。`stderr` 是诊断输出通道，benign stderr noise 只写日志，actionable stderr 转发到 wrapper stderr。
- Raw stdout/stderr chunk 写入 `.omx/logs/mcp-router` 下的 timestamped log file；`.omx/logs/mcp-router` 是仓库本地 MCP Router wrapper 日志目录。若传入 `--log-root`，则写入该参数指定的日志根目录。

该设计牺牲 stdout 噪声抑制，换取协议安全。除非 wrapper 实现完整 MCP frame parser，否则不能安全删除 stdout 上的 lifecycle message；因此 stdout 原样保留。主要支持的降噪范围是 stderr filtering。

验证重点是 protocol integrity，而不是 cosmetic stdout filtering。
