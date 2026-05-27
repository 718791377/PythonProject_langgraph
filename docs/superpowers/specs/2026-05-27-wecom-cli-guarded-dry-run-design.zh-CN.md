---
change: implement-wecom-cli-guarded-dry-run
status: archived-with-local-implementation
---

# 设计：wecom-cli 受治理 dry-run

本实现把 `wecom-cli` 保持为 repo-local guard，而不是真实 live adapter。低风险路径是 API/Webhook 规划；高风险路径是 WXWork GUI action precheck。

关键不变式：即使 receipt 有效，本仓库也只报告 dry-run dispatch eligibility，绝不控制 `WXWork.exe`。
