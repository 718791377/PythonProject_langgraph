# Design: Startup Canary Mojibake Detection

## Context

The canonical canary text lives only in `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md`. `AGENTS.md` must remain a recovery reread target and must not contain the literal canary. The observed failure is not a bad canonical file; it is a startup payload or console-encoding boundary that can render the same UTF-8 bytes as Windows ANSI/GBK-style mojibake.

## Decisions

### Decision 1: Generate mojibake variants from the canonical markers

The checker will derive bad variants by encoding the canonical start/end markers as UTF-8 and decoding those bytes through likely legacy Windows encodings such as `gbk`, `gb18030`, `cp936`, and `latin-1`, ignoring undecodable fragments when necessary. This avoids storing the literal corrupted prompt as another authority surface.

### Decision 2: Fail active text surfaces that contain corrupted marker variants

The checker will scan active text candidates that it already inspects for literal canary duplication. It will fail if a mojibake canary variant appears in `AGENTS.md`, a startup summary, or another active non-archived text file. Immutable archives and ignored runtime artifacts remain out of scope.

### Decision 3: Document the runtime recovery rule in `AGENTS.md`

`AGENTS.md` will state that when injected startup instructions or AGENTS-rendered context shows mojibake, maintainers must trust the UTF-8 startup summaries, discard the corrupted runtime copy, and fix the launcher/payload encoding boundary. This keeps runtime recovery explicit without duplicating the literal canary prompt.

## Non-Goals

- Do not move the canonical canary out of the startup summary pair.
- Do not duplicate the literal canary in `AGENTS.md` or tests.
- Do not patch installed user-level wrappers in this repository change.
- Do not treat console-rendering issues as evidence that the repository file is corrupted until UTF-8 file reads prove it.

## Risks

- The checker could flag historical mojibake in archived evidence. Mitigation: keep the existing archive and ignored-path exclusions.
- More mojibake forms could exist. Mitigation: generate variants from multiple likely encodings and keep the implementation small enough to extend.
