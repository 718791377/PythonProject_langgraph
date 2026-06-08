# 设计

## 边界
本变更只实现 repo-local 代码；不安装上游 Stop-Slop 或 Caveman，不修改用户级 Codex 配置，也不启用全局压缩。

## Checker
`tools/check_stop_slop_caveman_response_density.py` 对显式 sample file 或文本输出 JSON diagnostics。它把参考源启发的规则映射为确定性本地 findings：

- throat-clearing 和 filler phrases
- em dash 使用
- 套路化 binary contrast
- vague declaratives
- 弱 density 与重复 rhythm

checker 同时报告受保护片段，确保 runtime rewrite 保留 code fence、inline code、URL、路径、CLI 参数、schema key、OpenSpec/evidence/blocker token、`Routing trace` 与 `Updated Plan`。

## Runtime
`tools/stop_slop_caveman_runtime.py` 包装 checker：

- `analyze` 只报告 diagnostics。
- `rewrite --dry-run` 返回更短建议，绝不写文件。
- `rewrite --apply` 必须有 `--operator-confirmation` 和显式文件目标。
- `smoke-record` 写入 sanitized R4 receipt；缺少 R3 install receipt 时只写 blocked evidence，不写正向 smoke evidence。

## R4 receipt checker
`tools/check_stop_slop_caveman_smoke_receipts.py` 接受 blocked / not-installed receipt 作为诚实证据，并拒绝包含写入、live action、敏感 action、原始私有路径或 secret 的正向 receipt。
