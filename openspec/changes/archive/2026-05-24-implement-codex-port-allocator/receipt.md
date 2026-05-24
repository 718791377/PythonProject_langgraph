# codex-port Allocator Local Receipt

- status: implemented-local
- user_level_install_performed: false
- mutates_config: false
- edits_user_codex_config: false
- process_kill_performed: false
- default_runtime_state_modified: false
- rollback: revert the repository commit or reset local main to the pre-merge rollback ref

## Smoke commands

```text
python tools/codex_port.py --state-dir <temp> lease reserve --owner codex --project pythonproject-langgraph --tool mcp2cli --range codex-helper --purpose smoke --ttl 300 --owner-session smoke --json
python tools/codex_port.py --state-dir <temp> lease list --owner codex --json
python tools/codex_port.py --state-dir <temp> lease gc --dry-run --json
python test/codex_port.test.py
```

## Deferred to later slices

- user-level `C:\Users\lenovo\.codex\tools\codex-port` wrapper installation;
- OpenCLI `--port auto` integration;
- browser owner registry and `chrome-devtools-mcp` wrapper integration;
- user-level smoke evidence and update receipts.
