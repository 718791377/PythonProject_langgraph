# codex-user-level-team-mode-startup-binding Specification

## ??

?? user-level team-mode startup binding?PowerShell wrapper?native bypass?backup rollback ? release smoke evidence ????

## Requirements

### Requirement: The installer SHALL generate a PowerShell startup-binding launcher

installer ???? launcher script????????? user-level team-mode state????? PowerShell ? `codex` launches ?? Codex CLI runtime overrides?

launcher ???? native Codex executable path????????

#### Scenario: Startup-binding assets are generated into the target Codex home

- **WHEN** installer ? startup binding ??
- **THEN** ???? target Codex home ??? launcher asset
- **AND** launcher ???????? native Codex command path ????

### Requirement: The installer SHALL add a managed PowerShell profile block without replacing the native executable

installer ????? PowerShell profile path ?? managed block?? block ?? wrapped `codex` function ? raw `codex-native` bypass function?

????? npm-installed `codex`?`codex.cmd` ? `codex.ps1` files?

#### Scenario: A new PowerShell session loads the startup binding

- **WHEN** PowerShell session ?? managed profile block
- **THEN** ?? `codex` ???? generated launcher
- **AND** ?? `codex-native` ?????? native Codex command
- **AND** native Codex installation files ??????

### Requirement: The launcher SHALL map `oh_my_codex` state to startup behavior

launcher ??? persisted state file ?? `oh_my_codex`??????? Codex CLI runtime overrides?

?????

- `oh_my_codex=on` SHALL keep omx startup behavior enabled
- `oh_my_codex=off` SHALL disable omx-specific startup behavior for the wrapped launch

#### Scenario: Wrapped launch runs in native mode when omx is off

- **WHEN** wrapped `codex` launch ?? `oh_my_codex=off`
- **THEN** ?????? launch ?? omx-specific MCP startup surfaces
- **AND** ????? native-mode developer-instruction preset

### Requirement: The launcher SHALL map `subagent_routing` state to multi-agent availability

launcher ??? persisted state file ?? `subagent_routing`??????? Codex CLI routing behavior?

?????

- `auto` SHALL keep multi-agent available and use automatic-routing instructions
- `manual` SHALL keep multi-agent available and use manual-routing instructions
- `off` SHALL disable multi-agent for the wrapped launch

#### Scenario: Wrapped launch disables multi-agent in no-routing mode

- **WHEN** wrapped `codex` launch ?? `subagent_routing=off`
- **THEN** ???????? `--disable multi_agent`
- **AND** ????? no-routing developer-instruction preset

### Requirement: Startup-binding installation SHALL be covered by backup snapshots and rollback

installer ??? PowerShell profile path ? startup-binding launcher assets ????? timestamped backup-and-rollback transaction?? transaction ??? team-mode assets ????????

#### Scenario: A partial startup-binding install restores the previous profile content

- **WHEN** startup-binding installation ??? profile ? launcher ???
- **THEN** installer ??????? PowerShell profile content
- **AND** ???? startup-binding assets ?????? pre-install state
- **AND** ????? backup metadata ? diagnostics ??

### Requirement: Startup-binding surfaces SHALL avoid duplicating project canary prompts

Startup-binding?launcher ? repository instruction surfaces ??? project startup summary pair ???? project-level context-retention canary prompt?

?????? project startup summary ?? source of truth?????? cold-start recovery path?

#### Scenario: Launcher or instruction text refers to context-loss recovery

- **WHEN** startup-binding ? repository instruction text ?? context-loss recovery
- **THEN** ???????? project startup summary ?? canary prompt
- **AND** ???? launcher payloads?generated wrappers ? `AGENTS.md` ??? literal canary prompt text

### Requirement: Startup-binding release gates SHALL include native, raw, and wrapped launcher smoke evidence

? startup-binding changes ???? production-ready ???release gate ???? native Codex entrypoint?stable raw bypass entrypoint ? stable wrapped entrypoint ????? smoke evidence?

required release evidence ???????

- `codex --version` as the native Codex smoke command
- `codex-raw --version` as the stable raw bypass smoke command
- a short `codex-ohmy` help or version check as the stable wrapped launcher smoke command

?? repository checker ??????? evidence fields ?????? CI ?????? Codex sessions?

#### Scenario: Wrapped launcher changes but raw bypass is not proven

- **WHEN** startup-binding release candidate ?? `codex-ohmy` wrapper behavior
- **AND** release evidence ??? `codex-raw --version`
- **THEN** release ?????? production-ready
- **AND** operator ???? raw bypass ?? recovery path

#### Scenario: CI validates the release-gate template

- **WHEN** CI ?? release-gate template checker
- **THEN** ????? native?raw bypass ? wrapped launcher smoke evidence fields ??
- **AND** ????? long-running Codex session

### Requirement: Startup launchers SHALL pass generated model instructions through a file reference

User-level startup launchers ?????? model-instruction bodies ?? command-line startup overrides?

? wrapped Codex startup ?? generated instruction body ??launcher support layer ???? body ?????? UTF-8 state file???? command line ????? `model_instructions_file` reference?

startup argument builder ??? generated user-level orchestration instructions ???? `developer_instructions` startup overrides?

repository ???? executable checker????? source launcher generator ??? file-backed transport pattern?? checker ???? aggregate OpenSpec guard?

#### Scenario: Wrapped startup carries generated instructions safely

- **WHEN** generated launcher ?? user-level team-mode model instructions
- **THEN** ?????? instructions ?????? UTF-8 model-instructions file
- **AND** ????????? `model_instructions_file` startup override
- **AND** ???? user-supplied arguments ????? startup override

#### Scenario: Inline generated developer instructions are reintroduced

- **WHEN** startup argument builder ? generated launcher ??? `developer_instructions=` ?? generated startup instructions ? command-line override ??
- **THEN** launcher payload context-boundary checker ????
- **AND** aggregate OpenSpec guard ???? launcher payload boundary violation
