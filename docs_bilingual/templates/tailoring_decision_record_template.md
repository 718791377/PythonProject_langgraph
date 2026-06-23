---
doc_id: tailoring_decision_record_template
lang: en
doc_class: template
status: active
canonical_path: docs_bilingual/templates/tailoring_decision_record_template.md
zh_cn_path: docs_bilingual/templates/tailoring_decision_record_template.zh-CN.md
---
# Tailoring Decision Record Template

## Purpose

Use this template to record why a one-person-company project with embedded Codex governance uses a full, light, or module-tailored operating mode.

## Required Fields

- id:
- date:
- owner:
- mode: full | light | module-tailored | phased | emergency-contained
- why_not_heavier:
- why_not_lighter:
- escalation_triggers:
- rollback:
- local_main_evidence:
- linked_docs: []

## Inputs

- Project size, customer impact, compliance exposure, revenue impact, code impact, Agent impact, runtime impact, and durable-state impact.
- Current business gate, Codex execution gate, and any two-gate trigger.
- Existing local-main evidence and rollback evidence.

## Tools And Techniques

- Select the lightest mode that still protects business truth and execution truth.
- Explain why-not-heavier and why-not-lighter so the mode is auditable.
- Define escalation triggers before work starts.
- Keep rollback and local-main evidence explicit.

## Outputs

- A recorded tailoring mode and rationale.
- A clear escalation path to fuller architecture or a lighter local-only path.
- Evidence that module-level tailoring is allowed when risk is local to a module, while mixed matters still require two-gate review.
