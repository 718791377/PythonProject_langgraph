## ADDED Requirements

### Requirement: Stop-Slop/Caveman response density runtime SHALL be guarded and local
仓库必须提供 repo-local 的 Stop-Slop/Caveman 响应密度 checker 与 runtime，同时不得安装上游工具、修改用户级配置、启用 hook 或激活 always-on compression。

#### Scenario: Analyze reports diagnostics without mutation
- **WHEN** operator 对显式文本或文件运行 response-density runtime 的 analyze 模式
- **THEN** runtime 必须返回 JSON diagnostics
- **AND** 不得 rewrite 或写入输入。

#### Scenario: Rewrite preserves protected spans
- **WHEN** operator 对显式输入运行 rewrite dry-run 或已确认 apply
- **THEN** runtime 必须保留 code fence、inline code、URL、路径、CLI 参数、schema key、OpenSpec/evidence/blocker token、`Routing trace` 与 `Updated Plan`
- **AND** dry-run 不得写文件
- **AND** apply 必须要求 operator confirmation。

#### Scenario: R4 smoke evidence stays bounded
- **WHEN** 记录或检查 R4 smoke evidence
- **THEN** 缺少 R3 install evidence 必须产生 blocked / non-smoke-tested evidence
- **AND** 只有具备 timeout release、rollback readiness 和 redaction evidence 的安全 help、status 或 dry-run rewrite smoke receipt 才能算作正向 smoke-tested evidence
- **AND** write、live、sensitive、user-level mutation、原始私有路径或 secret 标记必须 fail closed。
