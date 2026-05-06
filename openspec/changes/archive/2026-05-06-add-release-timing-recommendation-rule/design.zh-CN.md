# Design: 发布时机建议规则

## 决策边界

发布时机建议应由当前会话模型提出，因为当前会话模型掌握本地上下文：validation results（验证结果）、active OpenSpec state（active OpenSpec 状态）、review scope（评审范围）、rollback boundary（回退边界）和 runner-budget value（runner 配额价值）。

用户仍然是 release decision authority（发布决策权威）。模型只提出建议，用户负责确认。

## 建议输入

发布建议应考虑：

- local validation state（本地验证状态）
- active-change state（active change 状态）
- review scope（评审范围）
- rollback boundary（回退边界）
- runner-budget value（runner 配额价值）
- 是否马上还会有同主题补充变更

## 放置位置

该规则应放在启动和发布治理表面，让冷启动会话知道推送前必须先提出建议。
