# 变更：实现 wecom-cli 受治理 dry-run 防线

## 为什么
用户级 MCP / skills / browser / CLI 治理方案仍把 `wecom-cli` 标为 planned。企业微信 / WeCom / WXWork 自动化属于高敏感通道，因为 GUI attach 可能暴露消息、联系人、token 或用户桌面状态。

## 变更内容
- 新增 repo-local `tools/wecom_cli_governance.py` guard。
- 新增 fixture tests，覆盖 API/Webhook 优先、GUI dry-run 规划、缺 receipt fail closed、有效 receipt 仅允许 dry-run dispatch。
- 将测试登记到共享 CI manifest，并通过 baseline checker 要求该测试存在。
- 更新双语实施方案与稳定 spec，将 `wecom-cli` 标记为 implemented-local，而不是 active 用户级自动化。

## 影响
- 不探测或控制真实 `WXWork.exe` 进程。
- 不修改用户级 Codex 配置。
- 不执行远端发布。
