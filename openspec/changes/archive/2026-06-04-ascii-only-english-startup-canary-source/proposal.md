# Change: ASCII-only English Startup Canary Source

## Why

The English startup summary currently embeds the non-ASCII visible context-retention canary markers. Those bytes are valid UTF-8, but an English/ASCII-oriented transport, launcher payload, terminal rendering path, or replay context can decode them through a legacy code page and show mojibake. The Chinese startup summary can safely remain the literal marker source, while the English summary can describe the same markers using ASCII Unicode codepoints.

## What Changes

- Make `docs_bilingual/project_startup_summary.md` ASCII-only by replacing the literal marker text with codepoint descriptions.
- Keep `docs_bilingual/project_startup_summary.zh-CN.md` as the startup summary file that contains the literal visible marker text.
- Update canary placement and startup-mojibake checkers so this storage split is enforced.
- Update tests and stable spec language for the new English-ASCII / Chinese-literal boundary.

## Impact

- No change to the user-visible canonical canary semantics.
- No remote publication is authorized.
- Rollback is a single local feature commit revert plus rerunning the same checker/test commands.
