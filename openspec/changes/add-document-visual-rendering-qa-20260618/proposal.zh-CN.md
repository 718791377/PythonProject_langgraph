---
change_id: add-document-visual-rendering-qa-20260618
status: proposed
owner: codex
created_at: 2026-06-18
---

# 提案：增加文档视觉渲染 QA

## 为什么

通用文档/PDF/向量工具已经迁移到 `D:\PythonProject_langgraph`，Poppler `pdftoppm` 也已经通过被忽略的本地 Poppler 缓存可用。下一处缺口是文档交付物的视觉渲染 QA：此前消费者项目在 `pdf2image`、`soffice/libreoffice` 或 `pdftoppm` 不可用时，只能降级为 OOXML 结构检查。

共享流水线需要一个持久契约：检测这些视觉 QA 后端，记录实际使用或跳过的后端，并避免在可选工具缺失时错误宣称完成了视觉验证。

## 改动内容

- 在 runtime 修改前冻结 `pdftoppm`、Python `pdf2image` 与 `soffice/libreoffice` 的视觉渲染 QA 契约。
- 明确本地安装/使用位置：Poppler 位于被忽略的 `.local`，`pdf2image` 位于项目虚拟环境，LibreOffice 位于 Windows 程序安装目录。
- 要求为后端可用性、渲染尝试、降级原因与严格后端失败输出结构化 JSON 与 Markdown 证据。
- 默认保持可选后端为可选；严格模式可以要求指定后端，不可用时失败。
- 将 Stage B 实现拆分为 runtime 与测试/文档切片；本方案合入本地 `main` 后可使用 durable team 执行。

## 不在范围内

- 安装 LibreOffice 或把第三方二进制作为仓库源码跟踪。
- 移动或清理 `D:\project` 文件。
- 将消费者配置、受保护源材料、向量索引、embedding 缓存、生成报告或交付物迁入共享源码。
- 远程发布、创建或合并 GitLab MR、同步 GitHub、或修改远程 ref。
