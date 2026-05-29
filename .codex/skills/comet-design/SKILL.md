---
name: comet-design
description: "Comet Phase 2: Deep Design. Invoke with /comet-design. Produce Design Doc and delta spec through brainstorming."
---

# Comet Phase 2: Deep Design (Design)

## Prerequisites

- Active change exists (proposal.md, design.md, tasks.md)
- No Design Doc (no corresponding file under `docs/superpowers/specs/`)

## Steps

### 0. Entry State Verification (Entry Check)

Execute entry verification:

```bash
COMET_SEARCH_ROOTS=("." "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.cursor/skills")
COMET_STATE="${COMET_STATE:-$(find "${COMET_SEARCH_ROOTS[@]}" -path '*/comet/scripts/comet-state.sh' -type f -print -quit 2>/dev/null)}"
COMET_GUARD="${COMET_GUARD:-$(find "${COMET_SEARCH_ROOTS[@]}" -path '*/comet/scripts/comet-guard.sh' -type f -print -quit 2>/dev/null)}"
bash "$COMET_STATE" check <name> design
```

Proceed to Step 1 after verification passes. The script outputs specific failure reasons when verification fails.

### 1a. Read Existing Context

Read `proposal.md` and `design.md` under the active change, organize core content into summaries:
- **Proposal summary**: goals, motivation, scope
- **Design summary**: architectural decisions, high-level design

### 1b. Execute Brainstorming (With Context)

**Immediately execute:** Use the Skill tool to load the `superpowers:brainstorming` skill, ARGUMENTS contains:

```
Change: <change-name>
Proposal summary: <proposal core content>
Design summary: <design.md architectural decisions>
Skip context exploration, proceed directly to design questioning.
```

Skipping this step is prohibited, and continuing without loading this skill is prohibited.

If `superpowers:brainstorming` is unavailable, stop the process and prompt to install or enable Superpowers skills. Do not substitute this step with normal conversation.

After the skill loads, follow its guidance to produce:
- `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` — design document (technical RFC)
- `openspec/changes/<name>/specs/<capability>/spec.md` — capability specification (delta)

### 2. Update Comet State

Record design_doc path, then run guard to auto-transition:

```bash
# Record design_doc path
bash "$COMET_STATE" set <name> design_doc docs/superpowers/specs/YYYY-MM-DD-topic-design.md

# Auto-transition to next phase
bash "$COMET_GUARD" <change-name> design --apply
```

State file is updated automatically. No manual editing of other fields required.

### 3. Management Checklist and Monitoring Return

Before running the guard, update `openspec/changes/<name>/management.md`:

- [ ] Mark delivery approach tailoring as checked.
- [ ] Mark risks and key assumptions as checked.
- [ ] Mark acceptance evidence path as checked.
- [ ] Mark Monitoring current facts and return/no-return decision as checked.

If brainstorming shows the original Open evidence is incomplete, set:

```bash
bash "$COMET_STATE" set <name> monitoring_status blocked
bash "$COMET_STATE" set <name> control_decision return-open
bash "$COMET_STATE" set <name> target_phase open
bash "$COMET_STATE" set <name> rework_reason value-gap
bash "$COMET_STATE" transition <name> monitor-return-open
```

Then re-enter `comet-open` instead of continuing to Build.


### Adaptive Monitoring Control

Monitoring is a cross-cutting focus area, not a sixth Comet phase; do not force waterfall progression when evidence shows an earlier focus area must change.

Forward progression requires both:
- `monitoring_status=clear`
- `control_decision=continue`

If Monitoring returns work, set `monitoring_status=blocked`, set the matching `control_decision`, `target_phase`, and non-null `rework_reason`, then run exactly one matching transition:

| Decision | Transition event | Re-enter skill |
| --- | --- | --- |
| `return-open` | `monitor-return-open` | `comet-open` |
| `return-design` | `monitor-return-design` | `comet-design` |
| `return-build` | `monitor-return-build` | `comet-build` |
| `return-verify` | `monitor-return-verify` | `comet-verify` |

After the return transition, re-enter the target Comet phase and refresh its matching management checklist before moving forward again.

## Exit Conditions

- Design Doc has been created and saved
- Delta spec has been created if there are new capabilities
- `design_doc` written to `.comet.yaml`
- Design management checklist and Monitoring checklist are checked in `management.md`
- **Phase guard**: Run `bash "$COMET_GUARD" <change-name> design --apply`; after all PASS, state advances to `phase: build`

You must use `--apply` before exiting:

```bash
bash "$COMET_GUARD" <change-name> design --apply
```

## Automatic Transition

After exit conditions are met, **proceed immediately to the next phase without waiting for user input**:

> **REQUIRED NEXT SKILL:** Invoke `comet-build` skill to enter the planning and build phase.
