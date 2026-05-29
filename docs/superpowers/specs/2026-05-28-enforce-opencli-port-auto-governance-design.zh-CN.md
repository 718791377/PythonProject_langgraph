---
change: enforce-opencli-port-auto-governance-20260528
status: implemented
---

# 设计：强制 OpenCLI 自动端口治理

## 问题

OpenCLI 已经受按需模式、owner 与 authorization 门禁约束，但 guard 还没有强制执行文档中要求的 `--port auto` 与 `codex-port` 租约 receipt 边界。

## 决策

在 `tools/opencli_governance.py` 中增加不产生运行时副作用的端口策略门禁：

- 默认端口模式是 `auto`；
- 任何硬编码值，例如 `--port 39300`，都会被阻断；
- 必须提供已清洗的 `codex-port` 租约 receipt；
- 租约必须由 `codex` 拥有、已清洗，并位于 `39300-39499` 范围。

## 安全性

该 guard 仍然不会安装 OpenCLI、启动 OpenCLI、绑定端口、打开浏览器、读取 cookie、执行 JavaScript、点击、输入或导航。
