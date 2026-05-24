## 1. Scope and Backup

- [x] 1.1 Create this OpenSpec change and define write scope, backup plan, rollback plan, and validation path.
- [x] 1.2 Capture npm and current Comet CLI state before install.
- [x] 1.3 Back up `C:\Users\lenovo\.codex\config.toml` and relevant `.codex` runtime listings.

## 2. Runtime Mutation

- [x] 2.1 Install `@rpamis/comet` globally.
- [x] 2.2 Run `comet --version`, `comet --help`, and `comet init --help`.
- [x] 2.3 Run `comet init` with the safest supported skip-existing/non-interactive options or stop at an interactive prompt with evidence.
- [x] 2.4 Apply the minimal user-level `.codex` configuration update and record the exact diff.

## 3. Validation and Evidence

- [x] 3.1 Run `comet status --json` and `comet doctor --json --scope auto` when available.
- [x] 3.2 Run OpenSpec validation and repository Comet policy checks.
- [x] 3.3 Record runtime evidence, changed paths, backup paths, and remaining manual follow-up.
