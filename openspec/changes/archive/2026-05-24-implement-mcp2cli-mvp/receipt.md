# mcp2cli MVP Local Receipt

- status: implemented-local
- user_level_install_performed: false
- mutates_config: false
- edits_user_codex_config: false
- invokes_live_mcp_servers: false
- full_schema_default_output: false
- rollback: revert the repository commit or reset local main to the pre-merge rollback ref

## Smoke commands

```text
python tools/mcp2cli.py list --profile core-readonly --json
python tools/mcp2cli.py search browser --profile browser-readonly --json
python tools/mcp2cli.py show browser.tabs.list --profile browser-readonly --json
python tools/mcp2cli.py call browser.tabs.list --profile browser-readonly --json --args {}
python test/mcp2cli.test.py
```

## Deferred to later slices

- user-level `C:\Users\lenovo\.codex\tools\mcp2cli` wrapper installation;
- live MCP server invocation adapters;
- user-level tool update receipts;
- port allocator integration for any local listener.
