﻿# ADDED Requirements / 新增要求

### Requirement: Code-class OpenSpec archives SHALL include source or test evidence / 代码类 OpenSpec archive 必须包含源码或测试证据
当 OpenSpec change 以代码类工作归档时，仓库 guard 必须要求同一分支包含 source、executable check、CI 或 test evidence，然后才允许 archive 通过。

#### Scenario: Code-class archive has no code evidence / 代码类 archive 没有代码证据
- **WHEN** 分支归档了一个 artifacts 或 metadata 将其归类为 code、runtime、mixed、tooling 或 CI work 的 OpenSpec change
- **AND** 同一分支在 `docs_bilingual/` 和 `openspec/` 之外没有 source、executable check、CI 或 test file changes
- **THEN** `python tools/run_openspec_guard.py --root .` 必须通过 `tools/check_openspec_code_archive_evidence.py` 失败
- **AND** 失败信息必须要求维护者先落 code/test evidence，再归档；如果确实是 docs-only，则必须显式标记该 change

#### Scenario: Docs-only archive is explicit / docs-only archive 已显式声明
- **WHEN** 已归档 OpenSpec change 声明 `x_change_class: docs`、`spec`、`governance`、`memory`、`research`、`plan` 或 `status`
- **THEN** code evidence checker 不得要求这个 archive 提供 source 或 test changes
