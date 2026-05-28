# 变更：加固 Project MOE Phase 1 CLI envelope schema

## 为什么

Project MOE GUI 方案要求 Phase 1 readiness checker 在目标项目只读 Mode CLI 返回不支持的 JSON envelope schema 时 fail-closed。当前公共 envelope 校验已经检查必填字段、命令回显、ok/token、CLI contract 与私有字段泄露，但尚未显式拒绝与本工具链 `SCHEMA_VERSION` 不一致的 `schema_version`。

## 变更内容

- 为 Mode CLI envelope `schema_version` 不匹配增加稳定 blocker。
- 通过 Phase 1 readiness checker 的 read-contract 路径覆盖该负向场景。
- 保持 static-only 与静态 blocker 行为不变：static-only 永不执行目标 CLI，read-contract 仍只执行安全读命令。
- 只勾选已有测试和新增测试真实覆盖的 Project MOE GUI 实施方案事项。

## 影响范围

- `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py` - Project MOE GUI 工具链共享校验器源码。
- `test/project_moe_gui_toolchain.test.py` - Project MOE GUI 工具链回归测试套件。
- `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` - 中文实施方案与证据勾选清单。
- 本 OpenSpec change 包。

## 非目标

- 不写入真实目标项目。
- 不把 `D:\PythonProject_paper_suggest` 或其他消费项目推进到 GUI 控制态。
- 不推送 GitLab/GitHub。
- 不改变目标 Mode CLI 写命令合同。

## 推出顺序

1. 增加 OpenSpec change 与管理清单。
2. 增加 schema-version mismatch blocker 与 remediation 元数据。
3. 增加 unsupported read-contract envelope schema 定向测试。
4. 仅根据证据更新实施方案勾选项。
5. 运行定向测试、OpenSpec validation、precommit update/archive review、local gate 与 local MR review。
6. 本地验证通过后才合入本地 `main`。

## 回滚计划

- 回滚 feature branch 或本地 main merge commit。
- 如果本地 main 已推进，则使用合并前创建的 rollback ref。
- 本切片不写目标项目状态，因此没有外部目标项目回滚事项。

## 验证路径

- `python test\project_moe_gui_toolchain.test.py` - 运行 Project MOE GUI 工具链回归测试套件。
- `openspec validate harden-project-moe-cli-envelope-schema-20260528 --strict` - 验证本次有界 OpenSpec change 包。
- `python .\tools\check_precommit_update_archive.py --root . --json` - 运行提交前 update/archive review。
- `python .\tools\run_openspec_guard.py --root .` - 运行仓库 OpenSpec 与治理 guard。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行共享本地 CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - 本地 main 集成前运行 local MR review。

## 主线分类

- 所属主线：Codex 用户级编排仓库中的 Project MOE GUI 工具链实施。
- 相关主线：用户级编排控制面安全与 local-first 发布治理。
