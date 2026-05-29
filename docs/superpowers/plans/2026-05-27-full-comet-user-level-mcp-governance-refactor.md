---
change: full-comet-user-level-mcp-governance-refactor
design-doc: docs/superpowers/specs/2026-05-27-full-comet-user-level-mcp-governance-design.md
base-ref: ab5e1c1c3e2f9fd01dc5af5eb30e9d6c5267f802
---

# Full Comet Governance-Plan Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. This is a single document-governance refactor with one owned target document plus Comet evidence artifacts.

**Goal:** Reframe the Chinese user-level MCP/skills/browser/CLI governance plan as a complete `/comet` workflow.

**Architecture:** OpenSpec records WHAT, Superpowers records HOW, and the target plan records the full Open/Design/Build/Verify/Archive gate structure for future governed implementation slices.

**Tech Stack:** Markdown documentation, OpenSpec artifacts, Comet state metadata, repository Python/PowerShell checkers.

---

### Task 1: Update target implementation plan

**Files:**
- Modify: `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md`

- [x] Replace tweak metadata with full Comet metadata.
- [x] Rewrite Section 0.1 to describe full `/comet` evidence.
- [x] Rewrite Sections 16-18 to include full phase gates, implementation order, and verification plan.

### Task 2: Add Comet/OpenSpec evidence

**Files:**
- Create/modify: `openspec/changes/full-comet-user-level-mcp-governance-refactor/proposal.md`
- Create/modify: `openspec/changes/full-comet-user-level-mcp-governance-refactor/design.md`
- Create/modify: `openspec/changes/full-comet-user-level-mcp-governance-refactor/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md`
- Create/modify: `openspec/changes/full-comet-user-level-mcp-governance-refactor/tasks.md`
- Create/modify: `openspec/changes/full-comet-user-level-mcp-governance-refactor/.comet.yaml`
- Create/modify: `openspec/changes/full-comet-user-level-mcp-governance-refactor/management.md`
- Create: `docs/superpowers/specs/2026-05-27-full-comet-user-level-mcp-governance-design.md`
- Create: `docs/superpowers/reports/2026-05-27-full-comet-user-level-mcp-governance-verification.md`

- [x] Record Open, Design, Build, Verify, and archive-deferral evidence.
- [x] Keep runtime mutation out of scope.

### Task 3: Verify and commit

**Files:**
- All changed files in this branch.

- [x] Run implementation-plan and baseline checkers.
- [x] Run precommit update/archive review and OpenSpec guard.
- [x] Run local gate; run local MR review immediately after the feature commit because it requires a clean committed branch.
- [ ] Commit the local feature branch with a Chinese commit subject.
