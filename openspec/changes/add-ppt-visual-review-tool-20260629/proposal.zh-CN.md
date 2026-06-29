---
change_id: add-ppt-visual-review-tool-20260629
status: proposed
owner: codex
created_at: 2026-06-29
---

# 提案：新增 PPT 可视化修改意见工具

## 为什么

共享文档工具已经可以渲染 PPTX 并记录视觉 QA 证据，但操作者仍需要一个本地可视化方式提出逐页、区域级 PPT 修改意见，同时不编辑受保护源稿，也不依赖云端协作产品。

## 变更内容

- 在 `tools/user_level_document_tools/viewers/ppt_review/` 下新增本地/离线 PPT 可视化审阅 sidecar。
- 基于已渲染的 slide PNG 和可选源 PPTX provenance 创建审阅 session。
- 规范化评论字段：页码、归一化 ROI、严重级别、类别、问题描述、建议修改和状态。
- 写出可携带 artifact：`session_manifest.json`、`comments.json`、`review_report.json`、`review_report.html` 与静态 viewer assets。
- 默认要求生成的审阅 session 与 slide PNG 留在 Git 跟踪源码之外。

## 不在范围内

- 编辑或重写源 PPTX。
- 向 OOXML 包回写 PowerPoint 原生批注。
- 多人协作、账号、权限或网络服务。
- 将第三方渲染器或 slide 图片作为跟踪源码打包。
- 远程发布、GitLab MR 创建/合并、GitHub 同步或远端 ref 修改。
