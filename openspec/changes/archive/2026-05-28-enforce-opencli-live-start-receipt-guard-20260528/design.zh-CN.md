# Design: OpenCLI live-start evidence guard

## Approach

在 `tools/opencli_governance.py` 中新增 repo-local `start` preflight。它复用现有 owner-registry lookup 与 port-lease validation，然后用 user-level update receipt 同族字段校验 OpenCLI install/update receipt。

## Safety model

- 命令只做治理检查，绝不启动 OpenCLI。
- 不启动浏览器、不连接 browser target、不读取 cookies、不执行 JavaScript、不 click/type/navigate、不修改用户级 Codex 配置。
- 证据缺失返回 exit code `3` 与 `opencli_live_start_blocked`。
- 证据齐全返回 exit code `4` 与 `live_start_not_implemented_repo_local_mvp`，证明 repo-local MVP 仍推迟真实 live-start。
- 输出中只暴露 install、wrapper、state、rollback path 的 hash。

## Receipt validation

install receipt 必须包含 tool name、installed version、source URL、install path、wrapper path、state path、smoke test command、passing smoke result、updater command、rollback pointer、owner lane 与 redaction status。敏感 key 或 inline secret 必须 fail closed。

## Acceptance evidence

- `python test\cdp_bridge_governance.test.py` - 覆盖 CDP Bridge、OpenCLI 与 CLI-Anything governance fixtures 的 targeted unit coverage。
- `python tools/run_openspec_guard.py --root . --json` - repository OpenSpec 与 governance guard。
- `powershell -NoProfile -File tools/ci/local_gate.ps1 -Json` - shared local CI gate。
- `powershell -NoProfile -File tools/ci/local_mr_review.ps1 -Json` - local MR review 与 merge simulation gate。
