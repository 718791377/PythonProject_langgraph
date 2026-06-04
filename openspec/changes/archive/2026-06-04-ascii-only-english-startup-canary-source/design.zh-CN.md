# Design

## Decision

用户可见 assistant response 里的当前可见 canary 标记保持不变。只改变字面标记文本的存放位置：

- 英文启动摘要：ASCII-only prose 和 Unicode codepoint notation。
- 中文启动摘要：继续保存字面可见标记文本。
- 检查器/测试：通过 codepoints 构造标记值，不复制额外字面文本。

## Enforcement

`check_context_retention_canary_surface.py` 变为 path-aware：

- 英文启动摘要必须保持 ASCII-only，且不得包含字面标记文本或 mojibake 变体。
- 中文启动摘要必须包含两个字面标记值，并保持 UTF-8-clean。
- 其他活动文件不得包含字面标记文本、legacy ASCII marker token 或 mojibake 变体。

`check_startup_instruction_mojibake.py` 的 response/session 诊断语义保持不变：规范用户可见响应仍使用可见标记对，legacy ASCII token 仍为 stale evidence，mojibake 变体失败关闭。

## Verification

本地 `main` 集成前运行两个目标 unittest 模块、两个 checker 命令、OpenSpec validation/guard、precommit review、local gate 和 local MR review。
