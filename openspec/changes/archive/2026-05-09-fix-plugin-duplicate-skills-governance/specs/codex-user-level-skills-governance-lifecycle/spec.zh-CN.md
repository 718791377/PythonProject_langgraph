## MODIFIED Requirements

### Requirement: Governance checks SHALL classify errors, warnings, and deferred cleanup separately

skills governance 验证表面必须区分 blocking errors、non-blocking warnings 和 deferred cleanup candidates。

Blocking errors 必须包括缺失的仓库必需工件、未被策略覆盖的 user 或 repo-local 同层重复 skill、未知 profile tag，以及损坏的 docs registry 覆盖。Warnings 可以包括已知跨层重复、plugin 层重复 skill 名称、已知 plugin bundle 限制、已知 Vercel 批量加载行为，以及当前阶段刻意不编辑的 user-level 长描述。Deferred cleanup 必须包括需要未来 clean-clone 证据的候选项。

#### Scenario: Validation reports a blocking defect
- **WHEN** 必需的仓库本地工件或 registry entry 缺失
- **THEN** governance check 必须报告 error
- **AND** 受影响 lifecycle phase 在修复前不得被接受

#### Scenario: Validation reports an expected non-blocking issue
- **WHEN** check 检测到已知 user-level 长描述、plugin 层重复 skill 名称，或已知 plugin bundle limitation
- **THEN** governance check 必须报告 warning
- **AND** 不得因为报告该 warning 而改写 user-level 或 plugin-managed 文件

#### Scenario: Validation reports cleanup candidates
- **WHEN** check 检测到需要 OpenSpec regeneration evidence 才能移除的重复文件
- **THEN** governance check 必须把该候选项报告为 deferred cleanup
- **AND** 不得把该候选项当成删除文件的许可
