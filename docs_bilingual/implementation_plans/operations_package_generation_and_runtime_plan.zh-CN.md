---
doc_id: operations_package_generation_and_runtime_plan
lang: zh-CN
doc_class: implementation_plan
status: final
change: generate-operations-package-runtime-20260620
translation_of: docs_bilingual/implementation_plans/operations_package_generation_and_runtime_plan.md
base_ref: 513788164167bbbb0c22872bcac9dd64de8b2b2b
archived-with: 2026-06-20-generate-operations-package-runtime-20260620
---

# 运营包生成与 Runtime 实施方案

> For agentic workers: use subagent-driven-development or executing-plans to implement this plan task-by-task. Keep Stage A and Stage B as separate local-main integration packages.

**目标：** 为 `Codex CLI 个人开发者生产级持久化团队` 与 `个人级生产级一人公司运营` 两套系统生成受治理的双语运营包，并明确裁剪规则；所有执行层流程采用过程组式 `输入 / 工具与技术 / 输出`。

**架构：** Stage A 只冻结本方案、OpenSpec 契约和 registry 条目。Stage B 按冻结方案新增确定性生成器、检查器、测试、生成的双语运营包文档和 registry 覆盖。

**Tech Stack:** Python CLI helpers, Markdown document generation, YAML registry updates, OpenSpec artifacts, unittest-based repository tests, local-main-first Git workflow.

## Stage A：冻结方案包

Files:

- Create `openspec/changes/generate-operations-package-runtime-20260620/` with proposal, design, tasks, management, and delta spec files.
- Create `docs_bilingual/implementation_plans/operations_package_generation_and_runtime_plan.md` and `.zh-CN.md`.
- Update `docs_bilingual/docs_registry.yaml` with the new implementation plan pair.

Rules:

1. Stage A is documentation/governance only. It does not create runtime scripts, tests, generated package documents, or CI-manifest entries.
2. Stage A freezes the Stage B required output set, tailoring rules, I/T/O contract, and validation commands.
3. Stage A remains leader-owned. Advisory experts may review scope, but durable/persistent team launch waits until the frozen plan exists on local `main`.

Validation:

```powershell
openspec validate generate-operations-package-runtime-20260620 --strict
python .	ools\check_document_pair_policy.py --root . --base-ref main --json
python .	ools\check_precommit_update_archive.py --root . --json
python .	ools
un_openspec_guard.py --root . --tool codex --json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

Commit Stage A with a Chinese commit subject, then integrate it into local `main` through `tools/complete_local_flow_to_remote_gate.py --execute`.

## Stage B：Runtime 与生成运营包

Files:

- Create `tools/generate_operations_package.py`.
- Create `tools/check_operations_package_docs.py`.
- Create `test/operations_package_docs.test.py`.
- Modify `tools/ci/ci_test_manifest.json` to register `operations_package_docs.test.py`.
- Modify `docs_bilingual/docs_registry.yaml` to register generated document pairs.
- Generate Codex durable-team package documents: BRD, PRD, template update policy, core-documents register, responsibility RACI, governed-agent catalog, cross-cutting-module map, reference-books map, virtual-departments operating map, document generation order, and operating slice template.
- Generate one-person-company package documents: operations document system, tailoring decision tree, minimum startup documents, core-documents register, responsibility RACI, governed-agent catalog, cross-cutting-module map, PMI process-group playbook, architecture mode selection guide, and operations metrics/monthly review.

Runtime behavior:

1. `generate_operations_package.py` writes deterministic UTF-8 Markdown and can run repeatedly without changing unchanged output.
2. The generator supports `--root`, `--package codex|one-person-company|all`, `--check`, and `--json`.
3. `check_operations_package_docs.py` validates required files, bilingual companions, required counts, required tailoring mode names, required I/T/O headings, and registry entries.
4. The checker supports `--root` and `--json`; it exits non-zero on validation failure.

## 裁剪契约

| Mode | Use When | Lightweight Scope |
| --- | --- | --- |
| Full architecture | Cross-stage, cross-department, external customer, revenue, compliance, security, publication, rollback, durable-state, or multi-agent work | Whole project is governed end-to-end |
| Whole-project lightweight | Low-risk internal exploration, disposable experiment, no external commitment, no durable-state impact, no publication | Entire project may be lightweight |
| Phase-local lightweight | Overall project matters, but one phase has low uncertainty and limited blast radius | Only that phase is lightweight |
| Module-level lightweight | Single module or document family is low risk while surrounding areas remain governed | Only that module is lightweight |
| Hybrid architecture | Most real work, especially when strategy/risk/revenue/publication remain material but discovery or content work can stay light | Complete governance for critical layers, lightweight treatment for low-risk phases/modules |

Every tailoring decision record must state why the selected mode is not heavier or lighter and list escalation triggers.

## 过程组式 I/T/O 契约

Every execution-facing generated document must include `Inputs`, `Tools And Techniques`, and `Outputs`. Every Chinese companion must include `输入`, `工具与技术`, and `输出`. The checker rejects missing headings in required generated package files.

## 协同计划

- Stage A: leader session plus advisory experts; no durable/persistent team because the frozen plan does not yet exist.
- Stage B: after Stage A is on local `main`, adopt durable/persistent execution when the preflight confirms a ready lane and the work remains split into 2+ independent slices.
- If durable team tooling is blocked, use native subagents with disjoint ownership: runtime/checker/test worker for `tools/` and `test/`; documentation/registry worker for generated docs and registry; leader for fan-in, validation, commit, local-main integration, cleanup, and remote-publication stop.

## Stage B 验证计划

Focused validation:

```powershell
python .	ools\generate_operations_package.py --root . --package all --check --json
python .	ools\check_operations_package_docs.py --root . --json
python .	ools\ci
un_python_tests.py --root . --pattern operations_package_docs.test.py
```

Full local integration gates:

```powershell
openspec validate generate-operations-package-runtime-20260620 --strict
python .	ools\check_document_pair_policy.py --root . --base-ref main --json
python .	ools\check_precommit_update_archive.py --root . --json
python .	ools
un_openspec_guard.py --root . --tool codex --json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

After Stage B passes and is locally integrated, archive the OpenSpec change only if the stable spec sync and archive validation pass; otherwise record an explicit archive deferral.

## 假设

- The existing refreshed Business Management/PMP synthesis is sufficient for this operations-package runtime; Stage B does not re-extract raw PDFs/EPUBs.
- The first Stage B package uses registers and operating maps rather than fully writing all 48 or 60 future document bodies.
- Remote publication is not authorized by this plan.
- Generated documents are source-controlled Markdown, not ignored runtime cache.

## 当前状态

<!-- CURRENT_STATUS_START -->
- Stage A 方案冻结包已合入本地 `main`: `459b28ad14f7d26f0a837d51318f006affc3c01f`.
- Stage B runtime/运营包实现已合入本地 `main`: `7863c4dd8daaa3b113b57e83b5252e68220446b9`.
- OpenSpec 收尾正通过本地-only closeout 分支归档到 `openspec/changes/archive/2026-06-20-generate-operations-package-runtime-20260620/`.
- 远程发布仍未授权.
<!-- CURRENT_STATUS_END -->

## 任务积压

<!-- TASK_BACKLOG_START -->
- Stage A: 已完成并合入本地 `main`.
- Stage B: 已完成并合入本地 `main`.
- Archive: 完成 OpenSpec 归档/sync 收尾, 然后停在远程发布门.
<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- `docs_bilingual/implementation_plans/operations_package_generation_and_runtime_plan.md` - 冻结实施方案与收尾证据索引.
- `tools/generate_operations_package.py` - 确定性运营包生成器.
- `tools/check_operations_package_docs.py` - 生成包/裁剪/I/T/O/registry 检查器.
- `test/operations_package_docs.test.py` - 已登记到本地 CI 的聚焦回归测试.
- `openspec/changes/archive/2026-06-20-generate-operations-package-runtime-20260620/` - 收尾后的 OpenSpec 归档证据.
- `refs/backup/local-main/20260620-042238-before-ops-package-runtime-20260620` - Stage B 本地 main 集成前保留的 rollback ref.
<!-- EVIDENCE_INDEX_END -->

> zh-CN companion note: this file is the Chinese companion for the frozen implementation plan; Stage B must keep tailoring modes and process-group I/T/O rules aligned with the English primary.
