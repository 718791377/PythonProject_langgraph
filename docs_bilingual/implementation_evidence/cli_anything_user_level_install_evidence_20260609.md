# CLI-Anything User-Level Install Evidence - 2026-06-09

## Summary

- Source: `https://github.com/HKUDS/CLI-Anything`.
- Installed user-level Codex skills: `cli-anything` and `cli-hub-meta-skill`.
- Installed Python package: `cli-anything-hub==0.3.0`.
- Smoke command: `cli-hub --help`.
- Version command: `cli-hub --version` returned `cli-hub 0.3.0`.
- Receipt: ignored local receipt `.omx/cli-anything/cli-anything.lock.json`.
- Receipt status: `installed-user-level`.
- Remote publication mutated: `false`.

## Receipt Validation

`python tools\cli_anything_governance.py validate --receipt .omx\cli-anything\cli-anything.lock.json --json` passed with:

- `install_performed=true` - the receipt records that the user-level CLI-Anything install has already been performed.
- `network_fetch_performed=true` - the receipt records that the install used a network-backed fetch/install step.
- `user_level_config_mutated=false` - the install did not mutate the user-level Codex configuration file.
- `wxwork_cli_installed=false` - this repository package did not install the WXWork_CLI surface.
- `wxwork_cli_controlled=false` - this repository package did not start or control WXWork_CLI or WXWork.exe.
- `source_url=https://github.com/HKUDS/CLI-Anything` - the source URL remains visible because it is not a private path.
- Smoke result: pass - the bounded `cli-hub --help` smoke evidence completed successfully.

Redacted receipt hashes:

- receipt path hash: `c48f3b6f51f0a146`
- install path hash: `9c9e532db9c4773c`
- wrapper path hash: `ba63c2f93d4be132`
- state path hash: `f0744b4573cbb903`
- rollback pointer hash: `5fd81dfe573883dd`

## WXWork_CLI Boundary

`WXWork_CLI` is not installed, started, or controlled by this repository package. Future `WXWork_CLI` integration is delegated to `D:\PythonProject_OpenClaw` / PythonProject_OpenClaw. No `WXWork.exe` start/control/send action occurred in this package.

## Official Codex Skill Installation Supplement

- Official source commit used for the follow-up install: `0a19072f8810afea6f00089226f9f7d06bd2de04`.
- Official Codex installer used: `codex-skill/scripts/install.ps1` from `https://github.com/HKUDS/CLI-Anything`.
- Official Codex skill destination confirmed: `C:\Users\lenovo\.codex\skills\cli-anything`.
- Official CLI-Hub meta-skill destination confirmed: `C:\Users\lenovo\.codex\skills\cli-hub-meta-skill`.
- Compatibility copies remain under `C:\Users\lenovo\.agents\skills`, but `.codex\skills` is the current Codex user-level skill surface.
- Git for Windows `bash` is available at `D:\Program Files\Git\bin\bash.exe`, matching the upstream Windows workflow note.
- WXWork_CLI remains delegated to `D:\PythonProject_OpenClaw`; this repository package still does not install, start, control, or send through WXWork_CLI.
