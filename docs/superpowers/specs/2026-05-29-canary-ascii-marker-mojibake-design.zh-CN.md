---
change: fix-canary-ascii-marker-mojibake-20260529
status: archived
translation_of: docs/superpowers/specs/2026-05-29-canary-ascii-marker-mojibake-design.md
archived-with: openspec/changes/archive/2026-05-29-fix-canary-ascii-marker-mojibake-20260529
---

# Canary ASCII Marker Mojibake 设计

## 目标

让上下文保留 canary 的可见标记在 Windows 控制台、启动器 payload 和旧代码页边界中保持稳定，同时不削弱“只允许启动摘要双文件保存字面标记”的约束。

## 摘要

规范文件本身是 UTF-8，但旧的非 ASCII 可见标记在某些渲染链路中会被转码损坏。此变更只把当前可见标记改为 ASCII-only 形式；旧标记仍作为历史/损坏证据由检查器内部按失败关闭处理。

## 决策

1. 启动摘要双文件继续作为唯一的字面标记来源。
2. 当前可见标记使用 ASCII-only 起止 token。
3. 检查器和测试源码通过片段或 Unicode 码点组装常量，避免在启动摘要之外出现完整字面标记。
4. 历史非 ASCII 标记及其旧编码损坏变体继续作为无效证据检测。

## 接受证据

- `python test/check_context_retention_canary_surface.test.py`
- `python test/check_startup_instruction_mojibake.test.py`
- `python tools/check_context_retention_canary_surface.py --root . --json`
- `python tools/check_startup_instruction_mojibake.py --root . --json`
- `python tools/run_openspec_guard.py --root .`
