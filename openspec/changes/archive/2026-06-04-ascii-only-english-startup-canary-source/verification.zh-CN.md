# 验证报告

变更：`ascii-only-english-startup-canary-source`
日期：2026-06-04

## 范围

本报告验证拆分后的启动哨兵来源规则：

- 英文启动摘要保持 ASCII-only，并使用 Unicode 码点间接描述。
- 中文启动摘要继续作为字面可见标记来源。
- canary placement、startup mojibake 与双语文档配对检查器会强制执行该拆分。

## 已运行命令

- `python test\check_context_retention_canary_surface.test.py` - 验证 canary-surface 检查器的回归行为。
  - 结果：通过，16 个测试。
- `python test\check_startup_instruction_mojibake.test.py` - 验证 startup mojibake 检查器的回归行为。
  - 结果：通过，10 个测试。
- `python test\check_document_pair_policy.test.py` - 验证双语文档配对策略的回归行为。
  - 结果：通过，6 个测试。
- `python tools\check_context_retention_canary_surface.py --root . --json` - 检查仓库 canary 放置与 response evidence 规则。
  - 结果：通过，`ok: true`。
- `python tools\check_startup_instruction_mojibake.py --root . --json` - 检查启动与指令权威面是否存在 mojibake。
  - 结果：通过，`ok: true`。
- `python tools\check_document_pair_policy.py --root . --json` - 检查变更的双语权威文档是否配对且英文主文件保持 ASCII。
  - 结果：通过，`ok: true`。
- `openspec validate ascii-only-english-startup-canary-source --type change --strict --json` - 在归档前验证 active OpenSpec change 结构。
  - 结果：通过，`valid: true`。

## 归档决策

稳定英文与中文 canary-surface spec 已在归档前作为完整稳定规格手工同步。活动变更中的 delta spec 仍是 OpenSpec 增量工件，因此 archive 已使用 `openspec archive ascii-only-english-startup-canary-source --skip-specs -y` 跳过自动 spec 覆盖，以保留已同步的完整稳定 spec 文件。

Archive path：`openspec/changes/archive/2026-06-04-ascii-only-english-startup-canary-source/`。

归档后的后续 gate：

- `python .\tools\run_openspec_guard.py --root .` - 运行仓库 OpenSpec 与治理 guard 序列。
- `python .\tools\check_precommit_update_archive.py --root . --json` - 在提交前检查 update/archive 就绪状态。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行共享本地 CI gate。
- feature commit
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - 运行本地合并模拟与分支 review gate。
- 项目 local-flow helper 合入本地 `main`，并停在远程发布门前
