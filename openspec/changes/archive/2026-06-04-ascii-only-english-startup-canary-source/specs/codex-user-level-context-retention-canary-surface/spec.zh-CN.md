## MODIFIED Requirements

### Requirement: Canary prompt text SHALL live only in the startup summary pair

仓库 SHALL 只在活动的双语启动摘要中维护上下文保留 canary 权威：

- `docs_bilingual/project_startup_summary.md` - 英文启动摘要和 ASCII-only 恢复/来源描述。
- `docs_bilingual/project_startup_summary.zh-CN.md` - 中文启动摘要和字面可见标记来源。

英文启动摘要 SHALL NOT 包含非 ASCII 字符、字面可见 canary 标记文本、legacy ASCII marker token，或可见标记的 mojibake 变体。它 SHALL 通过 ASCII-only Unicode 码点写法或等效 ASCII-only 间接描述来说明当前可见标记。

中文启动摘要 SHALL 包含字面可见标记文本，并 SHALL 保持 UTF-8-clean。

其他活动指令面 MAY 指向 startup-summary canary，MAY 描述 cold-start recovery action，但 SHALL NOT 复制字面 canary prompt text。

#### Scenario: English startup summary uses ASCII-only marker indirection

- **WHEN** canary placement checker 扫描 `docs_bilingual/project_startup_summary.md`
- **THEN** 它 SHALL 要求该文件保持 ASCII-only
- **AND** 如果该文件包含字面可见 canary 标记或其 mojibake 变体，则 SHALL 失败

#### Scenario: Chinese startup summary remains the literal marker source

- **WHEN** canary placement checker 扫描 `docs_bilingual/project_startup_summary.zh-CN.md`
- **THEN** 它 SHALL 要求两个字面可见标记值都存在
- **AND** 如果该文件包含 mojibake marker text，则 SHALL 失败

### Requirement: Canary placement SHALL have executable enforcement

仓库 SHALL 提供可执行检查器，用于验证活动 canary 放置位置、canary 编码完整性、恢复措辞，以及可选的用户提供 response/session evidence，而不是只依赖模型记忆。

可见启动 canary 标记 SHALL 继续为 startup-summary-defined non-ASCII/cat-sound marker pair。字面标记文本 SHALL 存放在中文启动摘要中，而英文启动摘要 SHALL 使用 ASCII-only codepoint indirection。Previous ASCII transport-stable markers SHALL NOT 被接受为当前 canonical response evidence；它们 MAY 仅作为检查器内部 legacy/stale compatibility inputs 和 replay-filtering signals 保留。

检查器 SHALL 继续强制执行仓库文件的静态放置规则。

当显式提供 response 或 session evidence 时，检查器 SHALL 只检查用户可见 assistant responses，SHALL NOT 把 tool output、compaction summaries、reasoning、developer/system payload、startup-summary file reads 或其他 context copies 算作 canary。

#### Scenario: User-visible assistant response uses the canonical visible marker pair

- **WHEN** 检查器收到包含 eligible assistant response 的 response text 或 session JSONL
- **AND** 该响应包含两个 startup-summary-defined visible markers
- **THEN** 检查器 SHALL 报告 `canonical_present`
