# 设计：wecom-cli 受治理 dry-run

## 边界
`wecom-cli` 首先是 repo-local 治理 guard。helper 只报告未来 GUI 动作是否满足证据门禁，不执行真实 GUI 自动化。

## 决策
- API/Webhook status 是默认低风险通道。
- 拒绝内联 webhook secret，只接受引用。
- GUI 动作必须同时具备 operator authorization receipt 和 global WXWork lease receipt。
- 有效 receipt 在本仓库 MVP 中只允许 `dry_run_only` dispatch eligibility。
- 输出使用 hash 或布尔值，不输出原始私有路径或消息内容。

## 风险
- 把 dry-run eligibility 当作真实授权会不安全；输出明确报告 `gui_control_performed=false`。
- 如果缺 CI 登记，guard 可能漂移；baseline checker 现在要求测试登记和 helper 文件存在。
