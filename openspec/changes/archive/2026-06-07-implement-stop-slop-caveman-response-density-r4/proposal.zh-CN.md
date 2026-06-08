# 变更：实现 Stop-Slop/Caveman 响应密度 R4

## 为什么
当前实施方案要求先提供项目级响应密度 checker、受保护 rewrite runtime 和 R4 smoke receipt 证据，本路线才能声称达到 runtime readiness。

## 变更内容
- 新增确定性的 Stop-Slop/Caveman checker，用于检查 slop 标记、响应密度和受保护的对话/技术片段。
- 新增受保护 runtime，包含 `analyze`、`rewrite --dry-run`、受 `--operator-confirmation` 保护的 `rewrite --apply`，以及有边界的 `smoke-record`。
- 新增 fail-closed 的 R4 smoke receipt checker：接受诚实 blocked receipt，但只有安全的 smoke-tested receipt 计入正向 R4 证据。
- 登记测试、aggregate guard wiring、安全 registry 条目和实施方案证据。

## 影响
- 不启用用户级安装、hook、MCP shrink 或 always-on compression。
- R4 smoke 证据只限显式 receipt 文件和安全的 help/status/dry-run rewrite 动作。
- 未经明确授权不做远端发布。
