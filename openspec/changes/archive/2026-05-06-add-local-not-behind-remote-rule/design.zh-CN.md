# Design: 本地不得落后远端规则

## 规则形态

local-first batching（本地优先批量发布）用于减少远端 pipeline 频率，但不能制造 stale-base work（基于陈旧基线的工作）。新建可写任务、判断发布时机、push、创建 MR 或声明本地已对齐之前，会话必须刷新 `gitlab/main`，并确认本地 `main` 没有落后。

## 陈旧 feature branch 处理

如果 feature branch 基于陈旧基线准备，发布前必须 rebase（变基）或 merge（合并）到刷新后的基线，除非用户明确接受 stale-base risk（陈旧基线风险）。

## 安全边界

该规则不授权破坏性清理。任何 dirty work（脏工作）在 reset、checkout、clean、move 或 delete 前，仍然必须先按 preservation-first（先保存再处理）方式分类。
