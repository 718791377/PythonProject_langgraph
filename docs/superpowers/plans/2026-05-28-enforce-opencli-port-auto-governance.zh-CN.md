---
change: enforce-opencli-port-auto-governance-20260528
design-doc: docs/superpowers/specs/2026-05-28-enforce-opencli-port-auto-governance-design.md
status: implemented
---

# 计划：强制 OpenCLI 自动端口治理

- [x] 增加 OpenCLI 端口策略校验。
- [x] 要求 `--port auto`。
- [x] 要求 `39300-39499` 范围内已清洗的 `codex-port` 租约 receipt。
- [x] 增加缺失租约、硬编码端口与错误范围的测试。
- [ ] 运行本地验证并归档 OpenSpec change。
