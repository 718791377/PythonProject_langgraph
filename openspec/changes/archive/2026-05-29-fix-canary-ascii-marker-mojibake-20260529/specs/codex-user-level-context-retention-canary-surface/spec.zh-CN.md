## MODIFIED Requirements

### Requirement: Canary placement SHALL have executable enforcement

仓库 SHALL 提供可执行检查器，用于验证活动 canary 放置位置、canary 编码完整性、恢复措辞，以及可选的用户提供响应/session 证据，而不是只依赖模型记忆。

启动摘要双文件中定义的当前可见 canary 标记 SHALL 为 ASCII-only token。历史非 ASCII canary 标记 SHALL NOT 被接受为当前规范响应证据；它们 MAY 仅作为检查器内部的历史/损坏检测输入保留。

检查器 SHALL 继续强制执行仓库文件的静态放置规则。

当显式提供响应或 session 证据时，检查器 SHALL 只检查用户可见 assistant 响应，SHALL NOT 把工具输出、压缩摘要、推理、developer/system payload、启动摘要文件读取或其他上下文副本算作 canary。

当 session JSONL 证据被缩小到指定 turn 或 latest assistant response 时，检查器 SHALL 只把该选择应用于合格 assistant 消息，并继续忽略非用户可见上下文来源。

#### Scenario: Startup summary defines transport-stable canary markers

- **WHEN** 启动摘要双文件定义当前可见 canary 标记
- **THEN** 这些标记 SHALL 为 ASCII-only，并能安全通过旧 Windows 控制台或启动器 payload 边界渲染
- **AND** 启动摘要双文件之外的活动源文件 SHALL NOT 包含完整字面标记文本

#### Scenario: User-visible assistant response uses historical non-ASCII canary text

- **WHEN** 检查器收到包含合格 assistant 响应的 response text 或 session JSONL
- **AND** 该响应包含历史非 ASCII canary 标记而不是启动摘要定义的当前标记
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 将该响应报告为无效 canary 证据并要求冷启动恢复

#### Scenario: Startup recovery omits repository instructions

- **WHEN** 任一启动摘要描述 canary 恢复动作
- **AND** 恢复动作未提及 `AGENTS.md`
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告对应启动摘要路径

#### Scenario: Repository instructions duplicate the literal prompt

- **WHEN** `AGENTS.md` 包含完整 canary prompt 字面文本
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `AGENTS.md` 只能作为恢复重读目标，而不是字面 prompt 来源

#### Scenario: Repository instructions contain mojibake canary text

- **WHEN** `AGENTS.md` 包含任一 canary 标记的旧编码损坏渲染
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告包含损坏标记的路径和行号

#### Scenario: Startup summary contains mojibake canary text

- **WHEN** 任一启动摘要包含任一 canary 标记的旧编码损坏渲染
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告启动摘要 canary 来源不是 UTF-8-clean

#### Scenario: User-visible assistant response is missing the canary

- **WHEN** 检查器收到包含合格 assistant 响应的 response text 或 session JSONL
- **AND** 该 assistant 响应不包含启动摘要定义的当前 canary 标记
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `missing_canary`
- **AND** SHALL 建议按冷启动顺序重读启动摘要双文件和必需文件

#### Scenario: Tool output contains canary text but assistant response omits it

- **WHEN** session JSONL 中工具输出或文件读取输出包含 canary 标记
- **AND** 合格 assistant 响应遗漏这些标记
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `missing_canary`
- **AND** SHALL NOT 把工具输出视为满足响应诊断

#### Scenario: Selected turn assistant response is the canonical evidence source

- **WHEN** 检查器收到 session JSONL 证据以及指定 turn id 或 latest-assistant selector
- **AND** 被选择的 assistant 响应包含启动摘要定义的当前 canary 标记
- **THEN** 检查器 SHALL 报告 `canonical_present`
- **AND** SHALL 忽略其他 turn 的上下文副本和选择范围外的 assistant 消息

#### Scenario: Assistant response contains mojibake canary text

- **WHEN** 合格 assistant 响应包含任一 canary 标记的旧编码损坏渲染
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `mojibake_canary`
- **AND** SHALL 声明 UTF-8 启动摘要双文件为权威来源
