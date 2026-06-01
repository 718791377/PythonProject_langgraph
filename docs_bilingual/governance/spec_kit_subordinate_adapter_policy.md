---
doc_id: spec_kit_subordinate_adapter_policy
lang: en
status: active
doc_class: governance
zh_cn_path: docs_bilingual/governance/spec_kit_subordinate_adapter_policy.zh-CN.md
---

# Spec Kit Subordinate Adapter Policy

## Authority Order

1. Native Codex remains the base execution layer for this repository.
2. Comet coordinates OpenSpec WHAT and Superpowers HOW for durable change workflow.
3. OpenSpec remains the repository specification authority.
4. Superpowers remains the implementation-method guidance layer.
5. Spec Kit may be referenced only as an optional subordinate adapter, template source, or documentation reference.

Spec Kit is not a project governance authority for this repository unless a separate active implementation plan explicitly changes that boundary and passes local gates.

## Allowed Uses

- Link to Spec Kit documentation as background when the text names it as a subordinate reference.
- Compare Spec Kit templates with OpenSpec or Comet artifacts without copying authority.
- Reuse a template idea only through a repository plan, checker, or OpenSpec change that preserves the authority order above.

## Blocked Uses Without A Separate Active Plan

- Running `specify init --force` - this command can overwrite or migrate project specification authority.
- Adding `.specify/` - this path is treated as a governance/runtime takeover surface, not an ordinary docs folder.
- Describing Spec Kit as the primary source of truth, primary governance authority, or replacement for Comet/OpenSpec/Superpowers.
- Moving repository workflow ownership from OpenSpec or Comet into Spec Kit by prompt text alone.

## Future `specify` Command Boundary

A future command named `specify` is safe only when a separate active implementation plan names the exact command, target paths, expected outputs, rollback path, and validation gates. The command must run in an isolated feature worktree, its output must be reviewed as subordinate input, and any accepted result must be converted into repository-owned surfaces such as `docs_bilingual/`, `openspec/`, or Superpowers planning artifacts.

If those conditions are missing, stop before running the command and report `blocked:spec_kit_scope_not_authorized`.

## Script Backing

`tools/check_spec_kit_authority_guard.py` - fail-closed checker that scans committed and working-tree surfaces for unsafe Spec Kit initialization, `.specify` path creation, and authority-takeover wording.

`tools/run_openspec_guard.py` - aggregate guard that runs the Spec Kit authority checker as part of the repository local gate.

`tools/ci/ci_test_manifest.json` - local CI manifest that includes the Spec Kit authority guard regression tests.
