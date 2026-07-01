# 任务

## 1. 受治理的准备

- [x] 1.1 创建隔离 feature worktree 和所有权元数据。
- [x] 1.2 创建 OpenSpec/Comet 变更包。

## 2. 可复用工具

- [x] 2.1 添加可复用 PDF/Poppler 辅助面和本地忽略的 Poppler 缓存。
- [x] 2.2 添加可复用文档流水线核心脚本和示例配置。
- [x] 2.3 添加通用向量/检索工具包和已脱敏的 legacy adapter。

## 3. 验证

- [x] 3.1 添加路径边界和向量工具冒烟行为回归测试。
- [x] 3.2 运行目标测试、OpenSpec 验证和仓库 guard 分项验证。
- [x] 3.3 准备提交和 local-main-first 集成证据。

## 验证说明

- 目标回归测试已通过：`python test/user_level_document_tools.test.py`。
- OpenSpec 严格验证已通过：`openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json`。
- 直接双语配对检查和高风险 guard 分项已通过，包括 `verify_official_openspec`、`check_document_pair_policy`、`check_name_clarity_rules`、`check_context_retention_canary_surface`、`check_startup_instruction_mojibake`、`check_safety_rule_script_backing`、`check_spec_kit_authority_guard`。
- 完整 `local_gate.ps1` 已在 UTF-8 环境和每步 1500 秒预算下重新运行并通过：`powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json`。旧失败报告已由 2026-06-14T14:10:12Z 生成的 `local-gate-report.json` 取代。
