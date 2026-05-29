## Design

### Root cause

The canonical repository files are UTF-8 clean, but the canary's previous visible markers were non-ASCII. When a Windows console, launcher payload, or live session rendering boundary decodes UTF-8 bytes through a legacy code page, those markers can become mojibake and then be copied into assistant-visible output.

### Decision 1: make the visible marker transport-safe

The startup summary pair remains the only literal marker source, but the marker text itself becomes ASCII-only. This makes the user-visible self-check robust across legacy console rendering and launcher/payload transport while preserving the existing startup-summary-only placement boundary.

### Decision 2: keep legacy marker detection fail-closed

The checkers keep the old non-ASCII marker values as internal legacy detection inputs using codepoint construction rather than literal source text. They reject both the old markers and their generated legacy-encoding variants in repository authority surfaces and response/session diagnostics.

### Decision 3: avoid literal marker duplication in code, specs, and plans

Checker/test code assembles the ASCII markers from adjacent fragments so a repository-wide text scan does not see a second literal marker source outside the startup summary pair. OpenSpec and Superpowers artifacts describe the marker class without spelling the marker text.

### Data flow

1. Startup summaries define the literal ASCII start/end markers.
2. `check_context_retention_canary_surface.py` reads the startup summaries through UTF-8, enforces marker placement, and diagnoses response/session evidence.
3. `check_startup_instruction_mojibake.py` scans startup/instruction authority surfaces and response/session evidence for legacy or corrupted canary text.
4. Tests construct the canonical ASCII markers from fragments and the historical markers from codepoints.

### Risks and mitigations

- Risk: The marker literal leaks into tests, specs, or plans and trips placement enforcement. Mitigation: assemble marker constants from fragments and avoid literal marker text outside the startup summary pair.
- Risk: Existing corrupted session logs use the historical marker. Mitigation: keep historical markers and generated mojibake variants as internal invalid evidence.
- Risk: Chinese startup text is damaged while editing from a non-UTF-8 terminal. Mitigation: write through explicit UTF-8 Python paths and run the startup mojibake checker.
