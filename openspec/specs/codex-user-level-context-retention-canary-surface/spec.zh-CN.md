# codex-user-level-context-retention-canary-surface 规格

## Purpose

定义上下文保留 canary prompt 允许存在的位置，并要求可执行检查在冷启动会话依赖旧指令或重复指令之前发现漂移。

## Requirements

### Requirement: Canary prompt text SHALL live only in the startup summary pair

仓库 SHALL 只在活动的双语启动摘要中维护上下文保留 canary prompt 的字面文本：

- `docs_bilingual/project_startup_summary.md` - 英文启动摘要和 canary prompt 来源。
- `docs_bilingual/project_startup_summary.zh-CN.md` - 中文启动摘要和 canary prompt 来源。

其他活动指令面 MAY 指向启动摘要 canary，MAY 描述冷启动恢复动作，但 SHALL NOT 复制完整 canary prompt 字面文本。

#### Scenario: Repository instructions refer to the canary without duplicating it

- **WHEN** `AGENTS.md` 记录上下文丢失恢复动作
- **THEN** 它 SHALL 指向启动摘要作为 canary 权威来源
- **AND** 它 SHALL NOT 包含完整 canary prompt 字面文本

### Requirement: Canary placement SHALL have executable enforcement

仓库 SHALL 提供可执行检查器，用于验证活动 canary 放置位置、canary 编码完整性、恢复措辞，以及可选的用户提供响应/session 证据，而不是只依赖模型记忆。

启动摘要双文件中定义的当前可见 canary 标记 SHALL 为 startup-summary-defined non-ASCII/cat-sound marker pair。之前的 ASCII transport-stable markers SHALL NOT 被接受为当前规范响应证据；它们 MAY 仅作为检查器内部的 legacy/stale compatibility inputs 与 replay-filtering signals 保留。

检查器 SHALL 继续强制执行仓库文件的静态放置规则。

当显式提供响应或 session 证据时，检查器 SHALL 只检查用户可见 assistant 响应，SHALL NOT 把工具输出、压缩摘要、推理、developer/system payload、启动摘要文件读取或其他上下文副本算作 canary。

当 session JSONL 证据被缩小到指定 turn 或 latest assistant response 时，检查器 SHALL 只把该选择应用于合格 assistant 消息，并继续忽略非用户可见上下文来源。

#### Scenario: Startup summary defines canonical visible canary markers

- **WHEN** 启动摘要双文件定义当前可见 canary 标记
- **THEN** 这些标记 SHALL 为 startup-summary-defined non-ASCII/cat-sound marker pair
- **AND** 启动摘要双文件之外的活动源文件 SHALL NOT 包含完整字面标记文本

#### Scenario: User-visible assistant response uses legacy ASCII canary text

- **WHEN** 检查器收到包含合格 assistant 响应的 response text 或 session JSONL
- **AND** 该响应包含 legacy ASCII canary marker 而不是启动摘要定义的当前标记
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `legacy_canary`
- **AND** SHALL 将该响应视为 stale compatibility input，而不是 canonical response evidence

#### Scenario: Startup recovery omits repository instructions

- **WHEN** 任一启动摘要描述 canary 恢复动作
- **AND** 恢复动作未提及 `AGENTS.md`
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告对应启动摘要路径

#### Scenario: Repository instructions duplicate the literal prompt

- **WHEN** `AGENTS.md` 包含完整 canary prompt 字面文本
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `AGENTS.md` 必须作为恢复重读目标，而不是字面 prompt 来源

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

#### Scenario: Model-readable replay context contains canary marker copies

- **WHEN** session replay context filtering receives assistant-visible transcript text, tool/function output, raw startup-summary copies, or compacted handoff text
- **AND** candidate model-readable context contains startup-summary-defined canonical marker copies or legacy ASCII marker text
- **THEN** replay filtering helper SHALL block or filter that item before prompt-authority handoff
- **AND** it SHALL report only reason labels and text summaries, not marker literals

#### Scenario: Assistant response contains mojibake canary text

- **WHEN** 合格 assistant 响应包含任一 canary 标记的旧编码损坏渲染
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `mojibake_canary`
- **AND** SHALL 声明 UTF-8 启动摘要双文件为权威来源

### Requirement: OpenSpec guard SHALL run the canary placement checker

仓库 OpenSpec guard SHALL 在标准验证序列中运行 canary placement checker。

#### Scenario: OpenSpec guard runs on a cold-start clone

- **WHEN** `python tools/run_openspec_guard.py --root . --json` 在仓库克隆中运行
- **THEN** 聚合 guard 输出 SHALL 包含 `check_context_retention_canary_surface` 步骤
- **AND** 若检查器报告 canary 放置错误，guard SHALL 失败

### Requirement: Startup instruction surfaces SHALL have mojibake enforcement

仓库 SHALL 提供可执行检查器，通过显式 UTF-8 读取扫描活动启动和指令权威面，并在这些表面包含乱码或有损替换文本时失败。检查器 SHALL 同时支持对显式 response/session 证据进行启动 canary 乱码诊断，而无需把完整 canary 写入其他权威面。

检查器 SHALL 在任何已配置启动或指令权威面出现以下情况时失败关闭：

- 无法按 UTF-8 读取
- 包含 Unicode replacement character
- 包含三个或更多问号组成的有损替换串
- 包含由配置的启动、canary 或 orchestration token 生成的旧编码损坏变体

检查器 MAY 将范围限制在活动启动和治理权威面，并 MAY 排除历史 memory note、已归档 OpenSpec change、生成报告、缓存、运行时状态和广泛文档树。

#### Scenario: Repository instructions contain startup mojibake

- **WHEN** `AGENTS.md` 包含已配置启动 token 的旧编码损坏渲染
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 在 findings 中报告 `AGENTS.md`

#### Scenario: Governance authority contains lossy question replacements

- **WHEN** 活动启动/治理权威面包含由有损替换造成的三个或更多问号串
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告路径和行号

#### Scenario: Startup summary contains replacement characters

- **WHEN** 任一启动摘要包含 Unicode replacement character
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告启动摘要路径

#### Scenario: Response evidence contains mojibake startup canary

- **WHEN** 检查器收到包含合格 assistant 响应的 response text 或 session JSONL
- **AND** 该响应包含启动 canary 的旧编码损坏渲染
- **THEN** 检查器 SHALL 返回非零退出码
- **AND** SHALL 报告 `mojibake_canary`
- **AND** SHALL 建议通过显式 UTF-8 路径重读启动摘要双文件

### Requirement: OpenSpec guard SHALL run the startup instruction mojibake checker

仓库 OpenSpec guard SHALL 在 canary-surface checker 之后，把 startup instruction mojibake checker 作为标准验证序列的一部分运行。

#### Scenario: OpenSpec guard checks instruction encoding integrity

- **WHEN** `python tools/run_openspec_guard.py --root . --json` 在仓库克隆中运行
- **THEN** 聚合 guard 输出 SHALL 包含 `check_startup_instruction_mojibake` 步骤
- **AND** 若检查器报告乱码或有损替换文本，guard SHALL 失败
