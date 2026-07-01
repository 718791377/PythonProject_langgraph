---
change: promote-reusable-doc-pdf-vector-tools-20260614
design-doc: docs/superpowers/specs/2026-06-14-reusable-document-tools-design.md
base-ref: 1599c4decaaf583d8dbb4e4a0e420340cf07d65e
---

# 实施计划

提升可复用文档工具，同时保留消费者项目自有状态边界。

## 范围

- 将 PDF/Poppler 辅助面、文档处理流水线核心脚本、向量/检索框架放入用户级编排仓库。
- 只迁移通用执行器、发现器、示例配置和框架代码。
- 不迁移 `D:/project` 的数据、实际配置、权限、来源权威、输出路径或 guard 规则。

## 验证

- 目标测试：`python test/user_level_document_tools.test.py`。
- OpenSpec 验证：`openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json`。
- 仓库 guard：`python ./tools/run_openspec_guard.py --root .`。
- 本地 CI 门禁：`tools/ci/local_gate.ps1`，必要时记录超时原因和更窄验证证据。
