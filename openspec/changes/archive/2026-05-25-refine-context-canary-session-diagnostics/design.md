## Context

The static canary placement contract already exists. This design adds a runtime-evidence diagnostic mode without changing the canary storage rule.

## Decisions

- Keep the literal canary prompt only in `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md`.
- Do not inject the canary into generated wrappers or model-instruction payloads.
- Treat missing or mojibake canary in a complete assistant response as evidence that the current model context is unsafe and must cold-start reread.
- Treat missing or mojibake canary immediately after reading as a read-path failure, especially when tool output showed mojibake.
- Session evidence parsing only examines user-visible assistant messages. Tool outputs, compaction summaries, developer/system payloads, function calls, and reasoning are ignored.
- The checker reports diagnostics and recovery instructions; it does not edit transcripts or enforce a response gate.

## Data Flow

1. Operator passes response text, response file, or session JSONL to a checker.
2. The checker extracts only eligible assistant final/output messages, optionally narrowing session JSONL evidence to the selected turn and/or the latest assistant response.
3. The checker checks for canonical markers and known mojibake variants.
4. The checker emits JSON with `canonical_present`, `missing_canary`, `mojibake_canary`, or `not_applicable_no_assistant_response`.

## Failure Modes

- No eligible assistant response: return ok with `not_applicable_no_assistant_response` so static checks can still pass.
- Missing marker: return non-zero for response/session diagnostic mode.
- Mojibake marker: return non-zero and report UTF-8 canonical reread recovery.
- Tool output contains canonical markers but assistant response does not: return missing, proving context copies are filtered.
