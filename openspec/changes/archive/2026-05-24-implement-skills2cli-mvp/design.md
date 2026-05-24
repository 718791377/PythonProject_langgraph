## Context

`skills2cli` is the second implementation slice from the user-level MCP/skills/browser/CLI governance plan. Its purpose is to provide a compact CLI discovery surface so most skills can remain on-demand rather than always visible in Codex context.

## Design

### Command surface

The MVP exposes these repository-local commands:

```text
python tools/skills2cli.py index --json
python tools/skills2cli.py search <query> --json
python tools/skills2cli.py show <skill-id> --json
python tools/skills2cli.py show <skill-id> --full --json
python tools/skills2cli.py profile suggest --task <text> --json
python tools/skills2cli.py audit warnings --since <duration> --json
```

### Indexing

The helper scans these roots when present:

- repository `.codex/skills`;
- user `~/.codex/skills`;
- user `~/.codex/skills/.system`;
- user `~/.codex/plugins/cache`.

Only metadata is emitted by default: skill id, parsed name, source layer, sanitized path hint, frontmatter validity, availability, short sanitized description summary, and description hash. Full filesystem paths and complete plugin descriptions are not emitted.

### Search and show

`search` matches query tokens against skill names, ids, and summaries. `show` returns one compact metadata record by default. The optional `--full` flag is intentionally explicit and still sanitizes the body; the default remains non-dumping.

### Profile suggestion

`profile suggest` is advisory only. It returns candidate modules/profiles and always reports:

- `mutates_config=false`;
- `profile_apply_performed=false`;
- `approval_required_for_apply=true` to prove profile apply still requires separate approval.

### Warning audit

`audit warnings` scans Codex session log text/JSONL under the supplied Codex home for the 2% skills context budget warning and skipped-loading warnings. It returns counts and sanitized excerpts without raw log paths or full private paths.

### Privacy boundary

The helper redacts Windows, UNC, POSIX private paths, and common token/secret patterns. Repository tests assert that path and token samples are not retained in JSON output.

## Alternatives considered

- Forking `mcp2cli`: rejected because `skills2cli` is a clean-room helper with different privacy and profile-apply boundaries.
- Writing directly to user-level `C:\Users\lenovo\.codex\tools\skills2cli`: deferred to a later installation slice to keep this MVP repository-local and rollback-only.

## Risks

- Real-world plugin SKILL.md frontmatter may be malformed. The helper keeps invalid entries visible as unavailable metadata rather than crashing.
- Session log formats may evolve. The warning audit is intentionally summary-oriented and tolerant of both raw text and JSONL event messages.
