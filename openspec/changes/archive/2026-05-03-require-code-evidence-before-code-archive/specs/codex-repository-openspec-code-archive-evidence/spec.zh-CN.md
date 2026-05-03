## ADDED Requirements / 新增要求

### Requirement: Code-affecting OpenSpec archives SHALL include validation evidence / 影响代码的 OpenSpec archive 必须包含验证证据

新归档且会影响仓库代码、可执行脚本、测试、CI、hooks 或 guard 行为的 OpenSpec change，必须包含具体的验证证据：同一分支的新代码证据，或 `.openspec.yaml` 声明的已落地证据路径。

#### Scenario: Archived code-affecting change lacks evidence / 已归档的代码影响 change 缺少证据

- **WHEN** `python tools/check_openspec_code_archive_evidence.py --root . --json` 扫描当前分支或工作区中的 archive diff
- **AND** 某个新归档 change 被分类为 code、runtime、mixed、tooling 或 CI work
- **AND** 同一分支在 `docs_bilingual/` 和 `openspec/` 之外没有 source、executable check、CI 或 test file changes
- **AND** 该 change 没有通过 `x_code_evidence_paths` 声明已存在的 source、executable check、CI 或 test path
- **THEN** checker 必须失败
- **AND** 它必须指出该 change 以及缺失的证据要求

#### Scenario: Archived code-affecting change declares already-landed code evidence / 已归档的代码影响 change 声明已落地代码证据

- **WHEN** checker 扫描一个新归档的 OpenSpec change
- **AND** 该 change 被分类为 code、runtime、mixed、tooling 或 CI work
- **AND** archive 分支没有新的代码 diff，因为 implementation 已经落在 `main`
- **AND** `.openspec.yaml` 通过 `x_code_evidence_paths` 声明了已存在的 source、executable check、CI 或 test path
- **THEN** checker 必须通过

#### Scenario: Documentation-only archived change passes / 纯文档 archived change 可以通过

- **WHEN** checker 扫描一个新归档的 OpenSpec change
- **AND** 该 change 已显式标记为 documentation-only，或没有提到代码或可执行仓库表面
- **THEN** checker 必须通过，且不得要求代码验证证据

### Requirement: OpenSpec guard SHALL enforce code archive evidence / OpenSpec guard 必须执行代码归档证据检查

聚合仓库 OpenSpec guard 必须运行 code archive evidence checker。

#### Scenario: Aggregate guard JSON includes archive evidence step / 聚合 guard JSON 包含归档证据步骤

- **WHEN** `python tools/run_openspec_guard.py --root . --json` 运行
- **THEN** 聚合输出必须包含 `check_openspec_code_archive_evidence` 步骤
- **AND** 如果 checker 报告错误，聚合 guard 必须失败
