---
doc_id: user_level_launcher_payload_policy
lang: en
doc_class: governance
status: active
---

# User-Level Launcher Payload Policy

## 1. Purpose

This document defines how user-level Codex or OMX launchers must avoid Windows command-line length failures while preserving a stable startup contract.

## 2. Problem Statement

The main failure mode is straightforward:

- a user-level launcher generates a large runtime instruction payload
- that payload is passed inline through command-line arguments
- Windows command-line length limits are exceeded
- launcher startup fails before Codex can begin normal work

For this repository, the concrete failure was the launcher passing a very long `-c developer_instructions=...` argument through `codex-ohmy`.

## 3. Hard Rules

- User-level launchers must not pass large generated runtime instructions inline as `-c developer_instructions=...`.
- User-level launchers must not inline large JSON payloads, full policy objects, expanded path lists, or full runtime state into command-line arguments.
- User-level launchers must keep command-line startup arguments short and bounded.
- When large startup instructions are required, launchers must pass a short file reference such as `model_instructions_file`, not the full instruction body.
- User-level launcher state files may carry shared startup payload artifacts, but they must not replace any repository's repo-local canonical durable state.
- Generated installed wrappers under `C:\Users\lenovo\.codex\bin\` are install artifacts, not the source of truth for payload policy fixes.
- Runtime payload assembly belongs in the shared launcher or support-script layer, not in each generated wrapper separately.
- The installer may generate the fixed launcher behavior, but it must not become the place where runtime payload semantics are spread across multiple wrapper-specific branches.
- Do not treat shortening prose or deleting guidance text as the primary long-term mitigation. The transport path must be fixed instead.

## 4. Required Transport Pattern

Use this preferred transport split:

1. command line:
   short control arguments only
2. file or state layer:
   large instruction bodies and structured payloads
3. support-script layer:
   payload generation, file write, and short-reference assembly

For startup instructions specifically:

- write the generated instructions to a managed file under `C:\Users\lenovo\.codex\state\`
- pass only a short config override such as `model_instructions_file="<path>"`

## 5. Layer Ownership

- launcher layer:
  responsible for short startup invocation only
- support-script layer:
  responsible for generating long instructions and writing them to a file
- installer layer:
  responsible for publishing the launcher and support-script implementation
- installed wrapper layer:
  validation target only, not the architectural source of truth
- repository layer:
  remains the authority for repo-local source, repo-local durable state, and any repository-specific runtime truth that launchers may reference

## 6. Recommended Rules

- Prefer passing references over passing content.
- Prefer `thread_id`, `repo_root`, `view`, or file path references over fully expanded state payloads.
- Re-read reconstructible runtime state from disk instead of copying it through the launcher chain.
- Keep payload generation centralized in shared support logic.
- Add regression tests for long-payload launcher scenarios whenever startup argument behavior changes.

## 7. Anti-Patterns

- adding more inline `-c key=value` payloads to work around earlier launcher failures
- shipping large policy text through environment variables or arguments when a file path is available
- hand-editing `C:\Users\lenovo\.codex\bin\codex-ohmy.ps1` or other installed wrappers as the primary fix path
- duplicating temporary-file logic in multiple generated wrappers
- treating one-off prose trimming as a stable architecture solution

## 8. Verification Rules

Any launcher payload change must verify all of the following:

1. `codex-ohmy --version` succeeds on Windows
2. `codex-ohmy exec --help` succeeds on Windows
3. a timed no-argument `codex-ohmy` launch survives the startup boundary instead of failing immediately with a command-line length error
4. repository regression tests cover the file-backed startup-instructions path

## 9. Current Repository Rule

For this repository, the required prevention rule is:

- do not pass the generated user-level orchestration instructions inline as `developer_instructions`
- write them to `user-level-team-mode-model-instructions.md` under the user-level state directory
- pass the short `model_instructions_file` reference instead


## 10. Legacy Resume Launcher Compatibility

Legacy `/resume` use must not force global launcher rewrites or direct MCP removal.

Rules:

- Start `codex-ohmy` normally and enter `/resume` from the temporary session when that path is stable. `codex-ohmy` is the stable wrapped entrypoint for daily Codex orchestration.
- If an old thread requires a temporary startup workaround, use a scoped one-launch override instead of editing installed wrapper files.
- Do not hand-edit `C:\Users\lenovo\.codex\bin\codex-ohmy.ps1` as the primary fix. That file is an installed wrapper artifact, not the source of truth for launcher behavior.
- Long-term fixes must remain in repository-owned source or installer generation logic, with checker coverage before publication.
