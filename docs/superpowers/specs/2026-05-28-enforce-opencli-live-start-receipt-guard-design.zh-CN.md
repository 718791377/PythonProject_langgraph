# Design: Enforce OpenCLI live-start receipt guard

## Problem

用户级 MCP/skills/browser/CLI 治理方案 Task 5 要求 live start 必须具备 install receipt 与 owner evidence。OpenCLI 已具备 target-action gates，但缺少 repo-local live-start preflight。

## Decision

新增 `opencli_governance.py start` 非变更型 preflight：

- 要求 `--port auto` 与 sanitized codex-port lease evidence；
- 要求 target 与 session 对应的 active browser-owner lease evidence；
- 要求 OpenCLI install/update receipt evidence；
- 证据齐全后返回 `live_start_not_implemented_repo_local_mvp`，因为 repo-local 代码不得启动 OpenCLI。

## Safety

该 guard 不安装 OpenCLI、不启动 OpenCLI、不启动浏览器、不连接 browser target、不读取 cookies、不执行 JavaScript、不 click/type/navigate、不修改用户级 Codex 配置。

## Acceptance

验收证据为单元测试、OpenSpec guard、local gate、local MR review 与本地 main 集成。
