---
change: fix-canary-ascii-marker-mojibake-20260529
design-doc: docs/superpowers/specs/2026-05-29-canary-ascii-marker-mojibake-design.zh-CN.md
base-ref: e81d840af21347047d3f9877b76664f0c17512e1
translation_of: docs/superpowers/plans/2026-05-29-canary-ascii-marker-mojibake.md
archived-with: openspec/changes/archive/2026-05-29-fix-canary-ascii-marker-mojibake-20260529
---

# Canary ASCII Marker Mojibake 实施计划

> **给 agentic worker：** 本计划是单切片修复；按 `executing-plans` 顺序执行，不需要并行写入。

**目标：** 将当前可见 canary 标记改为传输稳定的 ASCII-only 形式，并保留对历史/损坏证据的失败关闭检测。

**架构：** 启动摘要双文件仍是唯一字面来源；检查器和测试中的当前标记用片段组装，历史标记用码点组装。

**技术栈：** Python 标准库检查器、unittest、Markdown/OpenSpec 文档。

---

### 任务 1：检查器常量与诊断

**文件：**
- `tools/check_context_retention_canary_surface.py`
- `tools/check_startup_instruction_mojibake.py`

- [x] 将当前标记改为由 ASCII 片段组装。
- [x] 保留历史标记和旧编码损坏变体检测。
- [x] 确认当前证据报告为 `canonical_present`，历史或损坏证据报告为 `mojibake_canary` 并失败关闭。

### 任务 2：启动摘要与测试

**文件：**
- `docs_bilingual/project_startup_summary.md`
- `docs_bilingual/project_startup_summary.zh-CN.md`
- `test/check_context_retention_canary_surface.test.py`
- `test/check_startup_instruction_mojibake.test.py`

- [x] 更新启动摘要双文件的当前可见标记说明。
- [x] 更新测试，覆盖当前 ASCII 证据、历史非 ASCII 证据、损坏证据以及工具输出不计入响应证据的场景。

### 任务 3：验证与集成

- [x] 运行目标检查器和目标测试。
- [ ] 运行完整本地 gate、本地 MR review。
- [ ] 提交、归档到同一集成包、合入本地 `main`，并停在远端发布审批门前。
