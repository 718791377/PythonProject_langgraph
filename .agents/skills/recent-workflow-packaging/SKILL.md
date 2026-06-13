---
name: recent-workflow-packaging
description: Use when asked to review recent Codex work and identify repeated manual workflows worth packaging as repo-local skills, user-level candidates, subagents, automations, extensions, or skips.
---

# Recent Workflow Packaging

Use this skill to turn repeated manual work into a narrow, evidence-first packaging shortlist.

## Boundary

This is a project-level workflow first. It may record user-level wrapper/config candidates, but it must not install user-level skills, mutate user config, create scheduled tasks, write to Chronicle, or perform browser/GUI/external actions without a separate explicit plan and authorization.

## Evidence Order

1. Recent Codex sessions and task summaries, represented by committed Git history, committed memory, implementation-plan status, and runnable audit summaries.
2. Codex Memories and rollout summaries under `docs_bilingual/memory/`.
3. Chronicle discovery signals only. If Chronicle is unavailable, record `Chronicle: not_enabled`.
4. Existing skills, custom agents, and automations, so you extend or skip instead of duplicating existing coverage.

Do not read or commit raw transcripts, raw runtime logs, raw Chronicle payloads, or full private user paths.

## Broad Review Categories

The CLI must record a `broad_category_scan` so the broad search requested by
`reference_files/5.md` is explicit and auditable. It covers coding, research,
writing, planning, communication, operations, analysis, and personal
administration. A category with weak or absent evidence should be recorded as
`scanned_no_packaging_candidate` or `separate_plan_required`, not silently
omitted.

## Procedure

1. Run the repo CLI from the repository root:

   ```powershell
   python .\tools\report_recent_manual_workflow_candidates.py --root . --days 30 --output docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_YYYY-MM-DD.md
   ```

2. For a Chinese companion, run:

   ```powershell
   python .\tools\report_recent_manual_workflow_candidates.py --root . --days 30 --language zh-CN --output docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_YYYY-MM-DD.zh-CN.md
   ```

3. Review each shortlist item against the candidate gate:
   - repeated at least twice, or clearly likely to recur and costly to repeat;
   - stable inputs, repeatable procedure, and clear output/stopping condition;
   - materially improves speed, quality, consistency, or reliability;
   - not already adequately covered.

4. Review the `broad_category_scan` and ensure every broad category has a
   decision, evidence count, and either mapped shortlist items or an explicit
   no-package/separate-plan reason.

5. Choose the smallest form:
   - Skill: reusable workflow/playbook.
   - Custom subagent: bounded specialist role suitable for delegation.
   - Automation: scheduled/recurring check, report, reminder, or monitor.
   - Extend existing: existing asset covers most of the need.
   - Skip: one-off, sensitive, weakly evidenced, too broad, or already covered.

## Packaging Split

- Project-level now: repo-local skill, repo CLI, sanitized memory shortlist, and implementation-plan evidence.
- User-level candidate only: thin wrapper/config around this CLI after cross-project evidence, rollback, and smoke evidence exist.
- Do not package now: custom subagent when existing roles cover it, scheduler, Chronicle write integration, or external live actions.

## Validation

Before claiming completion, verify:

```powershell
python .\tools\report_recent_manual_workflow_candidates.py --root . --days 30 --json
python .\tools\report_recent_manual_workflow_candidates.py --root . --days 30 --output .omx/test-artifacts/recent-workflow-packaging-smoke.md
```

The CLI stdout path is UTF-8 forced for JSON and Markdown so subprocess
consumers can parse output reliably on Windows shells whose console code page is
not UTF-8.

Then run the repository precommit/update/archive, OpenSpec guard, local gate if not blocked by unrelated active worktrees, and local MR review according to the local-main-first workflow.
