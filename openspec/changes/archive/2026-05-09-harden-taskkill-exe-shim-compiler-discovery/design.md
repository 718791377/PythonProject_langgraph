## Design

### Root cause

The leaked lines are localized `taskkill` success output. The scoped `taskkill.cmd` and `taskkill.ps1` shims suppress ordinary `taskkill` invocations, but explicit `taskkill.exe` invocations require an executable shim. The installed user-level directory did not contain `C:\Users\lenovo\.codex\bin\win-shims\taskkill.exe`, so native cleanup could still resolve to the real Windows executable.

The repository installer source already had an optional executable shim path, but the default compile path remained brittle:

- `csc.exe` can exist under `C:\Windows\Microsoft.NET\Framework64\...` or `Framework\...` without being on PATH.
- compiler stdout/stderr capture used the ambient temp directory, which can fail under constrained/sandboxed execution even when the generated shim directory is writable.

### Approach

Keep the existing scoped wrapper design and make the executable shim reliably available by default:

1. Resolve the compiler from PATH first, then from both Framework64 and Framework Windows directories.
2. Capture compiler stdout/stderr in the generated shim directory using unique local filenames.
3. Keep the executable shim semantics unchanged: exit code 0 suppresses stdout/stderr entirely; non-zero exit forwards captured diagnostics and returns the original exit code.
4. Extend the checker with source markers for compiler fallback, local compiler temp files, and success-output suppression.
5. Add regression coverage for the Chinese success line class reported by the operator.

### Local plugin cache hotfix

The Twilio cache patch is deliberately tactical:

- `twilio-agent-connect` gets missing YAML frontmatter.
- `twilio-enterprise-knowledge` keeps its body but shortens the frontmatter description under the loader limit.

Because those files are plugin-managed cache artifacts, the durable fix remains upstream/plugin refresh. This change only removes current local startup warning noise.

### Risks

- Executable shim generation depends on a local Windows C# compiler. If neither PATH nor Framework compiler locations exist, the installer still reports unavailable shim status and falls back to cmd/ps1 shims.
- Plugin cache edits may be overwritten by plugin updates.