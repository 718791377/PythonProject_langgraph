# skills2cli MVP Local Receipt

- status: implemented-local
- user_level_install_performed: false
- mutates_config: false
- edits_plugin_cache: false
- full_skill_body_default_output: false
- rollback: revert the repository commit or reset local main to the pre-merge rollback ref

## Smoke commands

```text
python tools/skills2cli.py index --json
python tools/skills2cli.py search plugin --json
python tools/skills2cli.py show <skill-id> --json
python tools/skills2cli.py profile suggest --task "debug chrome skills warning" --json
python tools/skills2cli.py audit warnings --since 7d --json
python test/skills2cli.test.py
```

## Deferred to later slices

- user-level `C:\Users\lenovo\.codex\tools\skills2cli` wrapper installation;
- user-level state index persistence;
- profile apply or hard-load behavior.
