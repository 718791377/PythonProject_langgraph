# Runtime Evidence

Generated: 2026-05-24

## Operator request and scope

The operator explicitly requested the runtime mutation:

- install `@rpamis/comet`;
- run `comet init`;
- change user-level `.codex` configuration.

Execution scope was limited to:

- global npm package area for `@rpamis/comet`;
- current repository worktree: `D:\PythonProject_langgraph\.worktrees\upgrade-openspec-comet-superpowers`;
- user-level Codex config: `C:\Users\lenovo\.codex\config.toml`;
- user-level backup path: `C:\Users\lenovo\.codex\backups\comet-adoption-20260524-144223`.

## Pre-install state

```text
node --version => v24.13.1
npm --version  => 11.12.1
npm prefix -g  => C:\Users\lenovo\AppData\Roaming\npm
npm list -g @rpamis/comet --depth=0 => empty before install
```

`npm view @rpamis/comet ... --json` reported version `0.2.7`, description `OpenSpec + Superpowers dual-star development workflow`, and bin entry `comet -> bin/comet.js`.

## Backup

Created before user-level config mutation:

```text
C:\Users\lenovo\.codex\backups\comet-adoption-20260524-144223
```

Backed up:

- `config.toml` - user-level Codex configuration for model, MCP, plugins, hooks, and project trust.
- `hooks.json` - user-level Codex hook definitions referenced by the config trust state.
- listings for `.codex/skills`, `.codex/prompts`, and `.codex/agents`

Config hashes:

```text
backup config.toml SHA256  = 0D90AB415D81101BFDF3FA55E62BB4EB3E925D68D5CD5B6729A0034FD8E17014
current config.toml SHA256 = C85B91327AF70DFA564FB14665C54645714604112154C262018B9EF0E1458D98
```

## Install and CLI verification

Command:

```powershell
npm install -g @rpamis/comet
```

Result:

```text
added 27 packages in 9s
```

CLI verification:

```text
comet --version => 0.2.7
comet --help    => exposes init/status/doctor/update
comet init --help => exposes --yes, --skip-existing, --overwrite, --json
```

## Comet initialization

Command:

```powershell
comet init . --yes --skip-existing --json
```

Result:

```json
{
  "projectPath": "D:\\PythonProject_langgraph\\.worktrees\\upgrade-openspec-comet-superpowers",
  "scope": "project",
  "language": "en",
  "selectedPlatforms": [
    "codex"
  ],
  "results": [
    {
      "platform": "codex",
      "platformName": "Codex",
      "openspec": "skipped",
      "superpowers": "installed",
      "comet": "installed"
    }
  ],
  "workingDirsCreated": true
}
```

Generated or updated repository-local runtime files:

- `.codex/skills/comet/` - main Comet dispatcher skill and guard/state/archive scripts.
- `.codex/skills/comet-open/` - Comet Open phase skill for creating OpenSpec artifacts and Comet state.
- `.codex/skills/comet-design/` - Comet Design phase skill for Superpowers design refinement.
- `.codex/skills/comet-build/` - Comet Build phase skill for implementation planning and execution.
- `.codex/skills/comet-verify/` - Comet Verify phase skill for validation evidence and branch handling.
- `.codex/skills/comet-archive/` - Comet Archive phase skill for spec sync and archive closure.
- `.codex/skills/comet-hotfix/` - Comet preset skill for bounded hotfix workflows.
- `.codex/skills/comet-tweak/` - Comet preset skill for small tweak workflows.
- `.agents/skills/` Superpowers skills
- `skills-lock.json` - Superpowers skill lockfile with source hashes.
- `docs/superpowers/specs/` (`.gitkeep` added so the Comet working directory persists in Git)
- `docs/superpowers/plans/` (`.gitkeep` added so the Comet working directory persists in Git)

Repository guard normalization:

- `.codex/skills/comet-tweak/SKILL.md` - shortened the generated frontmatter description to satisfy the repository skill-description length guard while preserving the full body content.

## User-level `.codex` config mutation

Changed `C:\Users\lenovo\.codex\config.toml` after the backup above.

Minimal config patch:

1. Appended a Comet routing clause to `developer_instructions`:
   - Comet routing clause: `For OpenSpec workflows with Comet skills available, use Comet as the control layer coordinating OpenSpec WHAT and Superpowers HOW; route via $comet/comet-* skills before direct OpenSpec skill use unless explicitly bypassed.`
2. Added a trusted project entry for this adoption worktree:
   - Trusted project table: `[projects."D:\\PythonProject_langgraph\\.worktrees\\upgrade-openspec-comet-superpowers"]`
   - Trusted project value: `trust_level = "trusted"`

Validation:

```text
python tomllib parse => config_toml_parse=ok
comet_clause_added=True
worktree_trust_added=True
```

## Comet status and doctor

Project-scope doctor:

```json
{
  "scope": "project",
  "results": [
    {
      "check": "openspec CLI",
      "status": "pass",
      "message": "installed (1.3.1)"
    },
    {
      "check": "working directories",
      "status": "pass",
      "message": "present"
    },
    {
      "check": "skills: Codex (project)",
      "status": "pass",
      "message": "complete (12 files)"
    },
    {
      "check": "scripts executable",
      "status": "pass",
      "message": "OK (4 scripts)"
    }
  ]
}
```

Auto-scope doctor also passed project checks and warned that global Codex Comet skills are not installed. This was intentionally left as a warning because `comet init --yes --skip-existing --json` selected project scope, and this change avoided broad user-level skill overwrites.

Status:

```json
{
  "changes": []
}
```

The status output is expected for this transitional adoption change because the active OpenSpec change was created before Comet and does not yet contain a `.comet.yaml` state file. Future OpenSpec workflows should be opened through `$comet`/`comet-*` skills so Comet owns `.comet.yaml` state from the beginning.

## Archive

The stable spec was manually synced with the runtime-adoption requirement, then the change was archived with:

```powershell
openspec archive adopt-comet-runtime --skip-specs --yes
```

Result:

```text
Task status: ✓ Complete
Skipping spec updates (--skip-specs flag provided).
Change 'adopt-comet-runtime' archived as '2026-05-24-adopt-comet-runtime'.
```

## Repository validation

Passed:

```powershell
python tools/check_openspec_comet_superpowers_policy.py --root . --json
python test/run_openspec_guard_json.test.py
python tools/check_document_governance_rules.py --root . --json
openspec validate --all
python tools/run_openspec_guard.py --root .
```

Observed results:

- `openspec_comet_superpowers_policy`: `ok: true`
- `run_openspec_guard_json.test.py`: `Ran 6 tests ... OK`
- `document_governance_rules`: `ok: true`
- `openspec validate --all`: `78 passed, 0 failed`
- `run_openspec_guard.py`: `OpenSpec guard passed` after rerunning outside the sandbox for the Windows PySide6 helper subprocess and after shortening the generated `comet-tweak` frontmatter description for the repository skills guard.

## Rollback notes

If rollback is required:

1. Restore `C:\Users\lenovo\.codex\config.toml` from `C:\Users\lenovo\.codex\backups\comet-adoption-20260524-144223\config.toml`.
2. Remove or revert generated repository-local Comet/Superpowers files listed above.
3. Optionally uninstall the global package with `npm uninstall -g @rpamis/comet`.
4. Re-run Comet doctor/status and repository validation.
