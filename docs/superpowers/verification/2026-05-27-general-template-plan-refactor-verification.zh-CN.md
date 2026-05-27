---
change: refactor-general-template-plans-comet
status: pass
verified_at: 2026-05-27
archived-with: openspec/changes/archive/2026-05-27-refactor-general-template-plans-comet
---

# 验证报告中文对照

## 结果
PASS。两份目标实施计划保持能力层级分离，Comet 被定义为 OpenSpec + Superpowers governance，并且模板默认值不复制 live runtime state。

## 证据
- 目标文档以 UTF-8 和 LF 换行重写。
- OpenSpec stable spec 与 archive spec 记录可复用的 template-plan governance requirements。
- Comet artifacts 记录 proposal、design、tasks、management、Superpowers design、implementation plan 和 verification evidence。
- 最终本地验证命令记录在会话输出中。

## 分支处理
变更提交到本地 feature branch/worktree，不包含远端发布授权。
