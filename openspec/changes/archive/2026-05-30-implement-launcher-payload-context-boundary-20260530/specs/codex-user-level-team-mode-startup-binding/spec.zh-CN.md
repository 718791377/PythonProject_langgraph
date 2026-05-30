## ADDED Requirements

### Requirement: Startup launchers SHALL pass generated model instructions through a file reference

用户级 startup launcher 不得把生成的 model-instruction 正文放进命令行启动覆盖项。

当 wrapped Codex startup 需要生成的 instruction body 时，launcher support layer 必须把该正文写入受管理的 UTF-8 状态文件，并且在命令行上只传递较短的 `model_instructions_file` 引用。

startup argument builder 不得为生成的用户级编排指令传递内联 `developer_instructions` 启动覆盖项。

仓库必须保留一个可执行 checker，用于验证源头 launcher generator 是否遵守该文件化传输模式；该 checker 必须纳入聚合 OpenSpec guard。

#### Scenario: Wrapped startup carries generated instructions safely

- **WHEN** generated launcher 需要用户级 team-mode model instructions
- **THEN** 它必须把这些 instructions 写入受管理的 UTF-8 model-instructions 文件
- **AND** 它必须只传递一个较短的 `model_instructions_file` startup override
- **AND** 它必须在用户提供的参数之前转发该 startup override

#### Scenario: Inline generated developer instructions are reintroduced

- **WHEN** startup argument builder 或 generated launcher 试图把 `developer_instructions=` 作为生成启动指令的命令行覆盖项传递
- **THEN** launcher payload context-boundary checker 必须失败
- **AND** 聚合 OpenSpec guard 必须报告 launcher payload boundary violation