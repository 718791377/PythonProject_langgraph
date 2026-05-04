## Context

The operator wants to keep the `codex-ohmy` flow where a temporary Codex session opens first and `/resume` is typed inside the TUI. Disabling `omx_*` MCP servers proves the noise source but is not acceptable because those servers are part of the long-term `subagent / omx / langgraph` orchestration baseline.

The repair therefore belongs at the Windows cleanup-output boundary. The wrapper must keep full `omx_*` capability, scope any shim to the wrapped launch, and avoid global `config.toml` mutation.

## Decisions

### Add a scoped Windows cleanup shim directory

The installer will generate a `win-shims` directory under the user-level Codex bin directory. `win-shims` is a generated directory containing Windows command shims used only by wrapped Codex launches.

The directory will contain:

- `taskkill.cmd`: a CMD shim that invokes the real `taskkill.exe` and suppresses success output.
- `taskkill.ps1`: a PowerShell shim with the same success-suppression contract for PowerShell-based callers.
- `taskkill-shim-source.cs`: a C# source file for an optional `taskkill.exe` shim when a local C# compiler is available.
- optionally `taskkill.exe`: a compiled executable shim; this catches callers that invoke `taskkill.exe` explicitly instead of `taskkill`.

### Scope the shim to `codex-ohmy` child processes

The generated startup launcher will prepend the `win-shims` directory to `$env:Path` immediately before invoking the native Codex command and restore the previous PATH afterwards. This makes the shim visible to the native Codex child process tree, including `/resume` cleanup inside the temporary session, without changing the operator's global shell state.

### Preserve errors and log evidence

The shim will call the real `%SystemRoot%\System32\taskkill.exe`. On exit code 0 it suppresses stdout and stderr. On non-zero exit it forwards captured output to stderr and returns the same exit code.

The first implementation will keep the visible channel clean and deterministic. If later evidence shows operators need full cleanup logs, a follow-up can add a bounded log path without changing the success-suppression contract.

### Keep `omx_*` MCP direct and enabled

The launcher continues to pass `mcp_servers.omx_state.enabled=true`, `mcp_servers.omx_memory.enabled=true`, `mcp_servers.omx_code_intel.enabled=true`, and `mcp_servers.omx_trace.enabled=true` when `oh_my_codex=on`.

## Alternatives Considered

- Disable `omx_*` MCP servers: rejected because it removes long-term orchestration capabilities.
- Require `codex-ohmy resume <session-id>`: rejected because the operator explicitly wants temporary-session-first `/resume`.
- Use MCP Router for `omx_*`: rejected because Codex-private `omx_*` MCP servers belong in direct Codex config.
- Pipe/filter the entire Codex TUI output: rejected because it risks breaking interactive terminal behavior.

## Risks and Mitigations

- Exact `taskkill.exe` callers may bypass a CMD-only shim. Mitigation: generate optional `taskkill.exe` from C# source when a compiler is available and include checker/test evidence that the installer owns this path.
- PATH scoping could accidentally affect the parent shell. Mitigation: wrap native Codex invocation in `try/finally` and restore the original PATH after the child returns.
- Shim could hide real failures. Mitigation: non-zero exit returns the original code and forwards captured output to stderr.

## Validation

- Installer test confirms shim files are generated.
- Installer test confirms wrapped launch prepends `win-shims` to PATH while forwarding user arguments.
- Checker test confirms the installer still enables `omx_*` MCP when `oh_my_codex=on` and has a cleanup-output control layer.
- OpenSpec validation confirms the requirement contract.
