# codex-user-level-response-density-runtime 规范

## 目的
本规范记录 Stop-Slop/Caveman 响应密度 runtime 的仓库级约束。该 runtime 只提供本地 checker、受保护 rewrite helper 与 R4 smoke receipt 验证；不得在未授权时安装上游工具、修改用户级配置、启用 hook 或开启 always-on compression。

## 需求
### 需求：Stop-Slop/Caveman response density runtime 必须受守护且保持本地化
仓库必须提供 repo-local Stop-Slop/Caveman 响应密度 checker 与 runtime，并且不得安装上游工具、修改用户级配置、启用 hook 或激活 always-on compression。

#### 场景：Analyze 在不修改输入的情况下报告 diagnostics
- **WHEN** operator 针对显式文本或文件运行 response-density runtime 的 analyze 模式
- **THEN** runtime 必须返回 JSON diagnostics
- **AND** 不得 rewrite 或写入输入。

#### 场景：Rewrite 保留受保护片段
- **WHEN** operator 针对显式输入运行 rewrite dry-run 或已确认 apply
- **THEN** runtime 必须保留 code fence、inline code、URL、路径、CLI 参数、schema key、OpenSpec/evidence/blocker token、`Routing trace` 与 `Updated Plan`
- **AND** dry-run 不得写文件
- **AND** apply 必须要求 operator confirmation。

#### 场景：R4 smoke evidence 保持有边界
- **WHEN** 记录或检查 R4 smoke evidence
- **THEN** 缺少 R3 install evidence 必须产生 blocked/non-smoke-tested evidence
- **AND** 只有带 timeout release、rollback readiness 与 redaction evidence 的安全 help、status 或 dry-run rewrite smoke receipt 才能计为正向 smoke-tested evidence
- **AND** write、live、sensitive、user-level mutation、原始私有路径或 secret 标记必须 fail closed。
