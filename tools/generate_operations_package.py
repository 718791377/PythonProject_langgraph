#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

CHECK_NAME = "operations_package_generation"
GENERATED_MARKER = "<!-- GENERATED_BY: tools/generate_operations_package.py; DO NOT EDIT BY HAND. -->"

TAILORING_MODES = [
    (
        "Full architecture",
        "完整架构",
        "Use for cross-stage, external-customer, revenue, compliance, security, publication, rollback, durable-state, shared-runtime, or multi-agent work.",
        "适用于跨阶段、外部客户、收入、合规、安全、发布、回滚、持久状态、共享 runtime 或多 Agent 工作。",
        "Govern every affected layer end to end; write full evidence only for the affected risk scope.",
        "对受影响层级进行端到端治理；只为受影响风险范围写足完整证据。",
    ),
    (
        "Whole-project lightweight",
        "整个项目轻量化",
        "Use only for private, reversible, low-risk exploration with no external commitment, durable-state impact, publication, sensitive data, or shared runtime.",
        "仅适用于私有、可逆、低风险探索，且没有外部承诺、持久状态影响、发布、敏感数据或共享 runtime。",
        "The whole project may stay lightweight, but it still records owner, scope, validation, rollback or deletion, and learning.",
        "整个项目可以轻量，但仍需记录 owner、范围、验证、回滚或删除路径以及学习结果。",
    ),
    (
        "Phase-local lightweight",
        "阶段局部轻量化",
        "Use when one discovery, metrics, growth, or retrospective phase is low risk inside a larger governed project.",
        "适用于一个发现、指标、增长或复盘阶段在更大受治理项目内风险较低的情况。",
        "Only that named phase is light; upstream and downstream gates remain explicit.",
        "只有被命名的阶段是轻量的；上游和下游 gate 仍需显式保留。",
    ),
    (
        "Module-level lightweight",
        "模块级轻量化",
        "Use for one bounded document family, helper, prototype, or local module that does not change trust, state, public API, CI, release, or shared runtime behavior.",
        "适用于一个边界清晰的文档族、helper、原型或本地模块，且不改变 trust、状态、公开 API、CI、发布或共享 runtime 行为。",
        "Only the module is light; the surrounding project keeps its full architecture boundary.",
        "只有该模块轻量；外围项目仍保持完整架构边界。",
    ),
    (
        "Hybrid architecture",
        "混合架构",
        "Use for most real work: start light for uncertainty, then freeze fuller controls before customer, production, revenue, trust, durable-state, or release impact.",
        "适用于多数真实工作：不确定阶段先轻量，触达客户、生产、收入、信任、持久状态或发布影响前再冻结更完整的控制。",
        "Critical layers are full; low-risk phases or modules stay light until escalation triggers fire.",
        "关键层级完整治理；低风险阶段或模块保持轻量，直到触发升级条件。",
    ),
]

PROCESS_GROUPS = [
    ("Initiating", "启动", "purpose, value hypothesis, stakeholder signal, scope boundary, initial risks", "目的、价值假设、干系人信号、范围边界、初始风险", "charter-like framing, owner mapping, non-goal review, tailoring pre-check", "类章程 framing、owner 映射、非目标审查、裁剪预检", "authorization to continue, named owner, scope boundary, initial risk log", "继续授权、已命名 owner、范围边界、初始风险日志"),
    ("Planning", "规划", "approved purpose, dependencies, constraints, risk profile, acceptance target", "已批准目的、依赖、约束、风险画像、验收目标", "I/T/O planning, release slicing, validation design, rollback design, role-boundary review", "I/T/O 规划、发布切片、验证设计、回滚设计、角色边界审查", "plan, acceptance criteria, dependency map, validation path, rollback boundary", "计划、验收标准、依赖地图、验证路径、回滚边界"),
    ("Executing", "执行", "approved slice, source evidence, templates, worktree state, role ownership", "已批准切片、来源证据、模板、worktree 状态、角色 ownership", "controlled drafting or implementation, review, testing, documentation update, bounded expert or durable-lane handoff when eligible", "受控起草或实现、评审、测试、文档更新、满足条件时的 bounded expert 或 durable-lane handoff", "drafted artifact, controlled change set, validation work, changed-path evidence", "起草产物、受控变更集、验证工作、变更路径证据"),
    ("Monitoring and Controlling", "监控", "active work products, metrics, issues, review feedback, local gate output", "活动工作产品、指标、问题、评审反馈、本地 gate 输出", "quality checks, change control, variance review, risk response, diff review, gate reruns", "质量检查、变更控制、偏差复核、风险响应、diff 评审、gate 重跑", "issue log, change decisions, metric checks, local-gate evidence, rollback readiness", "问题日志、变更决策、指标检查、本地 gate 证据、回滚就绪度"),
    ("Closing", "收尾", "accepted work, final evidence, archive candidates, lessons, residual risks", "已验收工作、最终证据、归档候选、经验教训、残余风险", "closeout review, archive or sync, release-note update, retrospective, next-cycle triage", "收尾评审、归档或同步、发布说明更新、复盘、下一周期 triage", "final artifact, archive or closeout record, lessons learned, next-cycle input", "最终产物、归档或收尾记录、经验教训、下一周期输入"),
]

LAYERS_EN = [
    (0, "Cognitive narrative", "Why should the platform or company exist"),
    (1, "Business", "Why is it worth maintaining"),
    (2, "Market", "Which users and segments need it"),
    (3, "Strategy", "What to do first and what to refuse"),
    (4, "Metrics", "What evidence changes decisions"),
    (5, "Product", "Which workflows or offers are exposed"),
    (6, "Technical", "How systems stay safe and evolvable"),
    (7, "Organization", "Who owns decisions and permissions"),
    (8, "Execution", "How work ships and rolls back"),
    (9, "Growth", "How adoption or demand compounds"),
    (10, "Operations", "How support and runtime health stay stable"),
    (11, "Retrospective", "How lessons become durable"),
]
LAYERS_ZH = [
    (0, "认知叙事", "平台或公司为什么应该存在"),
    (1, "商业", "为什么值得持续维护"),
    (2, "市场", "哪些用户和细分需要它"),
    (3, "战略", "先做什么以及拒绝什么"),
    (4, "指标", "什么证据会改变决策"),
    (5, "产品", "暴露哪些工作流或 offer"),
    (6, "技术", "系统如何保持安全和可演进"),
    (7, "组织", "谁拥有决策和权限"),
    (8, "执行", "工作如何交付和回滚"),
    (9, "增长", "采用或需求如何形成复利"),
    (10, "运营", "支持和运行健康如何稳定"),
    (11, "复盘", "经验如何沉淀为持久资产"),
]

CODEX_DEPARTMENTS = [
    ("Strategy and Product Office", ["CEO and strategy owner", "Chief of staff", "Business model owner", "Finance owner", "Market intelligence", "Customer research"]),
    ("Engineering and Platform Office", ["Product strategy", "PM and PRD owner", "CLI and UX owner", "Metrics owner", "CTO and architect", "Engineering manager"]),
    ("Agent Governance Office", ["Code quality owner", "DevOps owner", "Platform and toolchain owner", "Security owner", "Privacy and data protection owner", "Data governance owner"]),
    ("Growth and Knowledge Office", ["Agent governance owner", "Agent evaluation owner", "Docs owner", "Support owner", "Brand and trust owner", "Knowledge and review owner"]),
]
OPC_DEPARTMENTS = [
    ("Strategy Office", ["Founder and CEO", "Chief of staff", "Business model owner", "Finance owner", "Risk owner", "Personal operating-system owner"]),
    ("Product and Market Office", ["Market intelligence", "Customer research", "Positioning owner", "Product strategy owner", "Offer owner", "PRD and service-design owner"]),
    ("Revenue and Growth Office", ["Analytics owner", "Growth owner", "Sales owner", "Pricing owner", "Content owner", "Brand and trust owner"]),
    ("Operations Office", ["Partnerships owner", "Customer success owner", "Support owner", "Delivery owner", "Community owner", "Knowledge owner"]),
    ("Governance Office", ["Automation owner", "Security and privacy owner", "Legal and compliance owner", "Data governance owner", "Asset and IP owner", "Agent governance owner"]),
]
DEPT_ZH = {
    "Strategy and Product Office": "战略与产品办公室",
    "Engineering and Platform Office": "工程与平台办公室",
    "Agent Governance Office": "Agent 治理办公室",
    "Growth and Knowledge Office": "增长与知识办公室",
    "Strategy Office": "战略办公室",
    "Product and Market Office": "产品与市场办公室",
    "Revenue and Growth Office": "收入与增长办公室",
    "Operations Office": "运营办公室",
    "Governance Office": "治理办公室",
}

CORE_48 = [
    ("Strategy and business", ["vision.md", "thesis.md", "business-model.md", "pricing.md", "unit-economics.md", "strategy.md"]),
    ("Market and product", ["user-segments.md", "market-map.md", "research-repository.md", "product-strategy.md", "prd.md", "cli-ux.md"]),
    ("Metrics and data", ["metrics.yaml", "north-star.md", "tracking-plan.md", "data-dictionary.md", "data-quality-checklist.md", "experiment-log.md"]),
    ("Engineering and platform", ["architecture.md", "adr.md", "module-boundaries.md", "tech-stack.md", "delivery-plan.md", "observability.md"]),
    ("Security and risk", ["security-policy.md", "access-control.md", "privacy-policy.md", "incident-response.md", "risk-register.md", "backup-restore.md"]),
    ("Agent governance", ["agent-role-map.md", "agent-permissions.md", "agent-tool-policy.md", "human-review-checklist.md", "agent-evaluation.md", "agent-failure-modes.md"]),
    ("Growth and operations", ["growth-model.md", "docs-plan.md", "support-playbook.md", "faq.md", "trust-page.md", "changelog.md"]),
    ("Retrospective and knowledge", ["decision-log.md", "weekly-review.md", "monthly-review.md", "postmortem.md", "learning-log.md", "template-library.md"]),
]
CORE_60 = [
    ("Company strategy", ["company-thesis.md", "vision.md", "strategy.md", "annual-plan.md", "quarterly-plan.md", "decision-log.md"]),
    ("Business and finance", ["business-model.md", "offer.md", "pricing.md", "unit-economics.md", "finance-model.md", "cashflow.md"]),
    ("Market and user", ["market-map.md", "user-segments.md", "competitor-analysis.md", "alternative-solutions.md", "research-repository.md", "interview-guide.md"]),
    ("Product and service", ["product-strategy.md", "prd.md", "service-blueprint.md", "onboarding.md", "customer-journey.md", "roadmap.md"]),
    ("Metrics and data", ["metrics.yaml", "north-star.md", "funnel-dashboard.md", "tracking-plan.md", "data-dictionary.md", "experiment-log.md"]),
    ("Growth and sales", ["growth-model.md", "channel-map.md", "sales-playbook.md", "landing-page.md", "email-sequences.md", "content-calendar.md"]),
    ("Operations and customer success", ["ops-playbook.md", "customer-success-playbook.md", "support-policy.md", "faq.md", "refund-policy.md", "feedback-triage.md"]),
    ("Technology and automation", ["tech-stack.md", "automation-map.md", "tool-stack.md", "vendor-register.md", "api-dependency-map.md", "backup-restore.md"]),
    ("Governance and risk", ["legal-checklist.md", "terms-of-service.md", "privacy-policy.md", "contract-template.md", "risk-register.md", "compliance-checklist.md"]),
    ("Agent and knowledge", ["agent-governance.md", "agent-role-map.md", "agent-permissions.md", "human-review-checklist.md", "monthly-review.md", "learning-log.md"]),
]

CODEX_MODULES = ["Finance", "Operations", "Engineering management", "Organization design", "Legal and compliance", "Security", "Knowledge management", "Risk management", "Personal productivity", "AI agent governance", "Data governance", "Brand trust", "Toolchain governance", "SLA governance", "Asset and IP governance", "User-research governance", "Channel governance", "Exit governance"]
OPC_MODULES = CODEX_MODULES + ["Vendor governance", "Tax and administration governance"]
CODEX_AGENTS = ["Research Agent", "PM Agent", "Architect Agent", "Code Agent", "Review Agent", "Test Agent", "Security Agent", "DevOps Agent", "Data Agent", "Docs Agent", "Ops Agent", "Risk Agent"]
OPC_AGENTS = ["Strategy Agent", "Research Agent", "Product Agent", "UX and Copy Agent", "Engineering Agent", "QA Agent", "Data Agent", "Growth Agent", "Sales Agent", "Customer Success Agent", "Support Agent", "Finance Agent", "Legal and Risk Agent", "Knowledge Agent", "Chief of Staff Agent"]
CODEX_BOOKS = ["Scaling People", "Working Backwards", "High Output Management", "INSPIRED", "Product Operations", "Team Topologies", "Accelerate", "Shape Up", "Lean Analytics", "Designing Data-Intensive Applications", "Secure by Design", "The Staff Engineer's Path"]
OPC_BOOKS = ["Scaling People", "Working Backwards", "High Output Management", "INSPIRED", "Product Operations", "Measure What Matters", "Lean Analytics", "The Lean Startup", "Obviously Awesome", "Traction", "Deploy Empathy", "Shape Up", "Team Topologies", "Company of One", "The E-Myth Revisited"]
STARTUP_DOCS = ["company-thesis.md", "business-model.md", "offer.md", "pricing.md", "user-segments.md", "growth-model.md", "finance-model.md", "ops-playbook.md", "metrics.yaml", "risk-register.md", "agent-governance.md", "monthly-review.md"]

EXPECTED_COUNTS = {
    "codex": {"trunk_layers": 12, "virtual_departments": 4, "responsibility_domains": 24, "cross_cutting_modules": 18, "core_documents": 48, "governed_ai_agents": 12, "recommended_books": 12},
    "one-person-company": {"trunk_layers": 12, "virtual_departments": 5, "responsibility_domains": 30, "cross_cutting_modules": 20, "core_documents": 60, "governed_ai_agents": 15, "recommended_books": 15, "minimum_startup_documents": 12},
}


@dataclass(frozen=True)
class GeneratedDoc:
    doc_id: str
    rel_path: str
    zh_path: str
    doc_class: str
    package: str
    title_en: str
    title_zh: str
    purpose_en: str
    purpose_zh: str
    body_kind: str


def _doc(path: str, doc_class: str, package: str, title_en: str, title_zh: str, purpose_en: str, purpose_zh: str, body_kind: str) -> GeneratedDoc:
    p = Path(path)
    return GeneratedDoc(p.stem, path, p.with_name(p.stem + ".zh-CN.md").as_posix(), doc_class, package, title_en, title_zh, purpose_en, purpose_zh, body_kind)


CODEX_DOCS = [
    _doc("docs_bilingual/business/codex_cli_durable_team_brd.md", "business", "codex", "Codex CLI Durable Team BRD", "Codex CLI 持久化团队 BRD", "Defines the business need, user value, constraints, and acceptance logic for the personal production durable-team platform.", "定义个人生产级持久化团队平台的业务需要、用户价值、约束与验收逻辑。", "codex_brd"),
    _doc("docs_bilingual/product/codex_cli_durable_team_prd.md", "product", "codex", "Codex CLI Durable Team PRD", "Codex CLI 持久化团队 PRD", "Defines operator workflows, package generation behavior, validation requirements, and release boundaries for the durable-team platform.", "定义持久化团队平台的 operator 工作流、运营包生成行为、验证要求和发布边界。", "codex_prd"),
    _doc("docs_bilingual/templates/template_update_policy.md", "template", "codex", "Template Update Policy", "模板更新策略", "Defines how reusable templates are proposed, reviewed, validated, released, and retired without losing local-main-first governance.", "定义可复用模板如何在不丢失本地 main 优先治理的前提下提出、评审、验证、发布和退役。", "template_policy"),
    _doc("docs_bilingual/product_lifecycle/codex_platform_core_documents_register.md", "product_lifecycle", "codex", "Codex Platform Core Documents Register", "Codex 平台核心文档登记表", "Registers the 48-document durable-team platform target as eight six-document families.", "把持久化团队平台的 48 个核心文档目标登记为 8 个六文档家族。", "codex_core_docs"),
    _doc("docs_bilingual/product_lifecycle/codex_platform_responsibility_raci.md", "product_lifecycle", "codex", "Codex Platform Responsibility RACI", "Codex 平台责任 RACI", "Maps the 4 virtual departments and 24 responsibility domains to accountable, consulted, and informed surfaces.", "把 4 个虚拟部门和 24 个责任域映射到 accountable、consulted 和 informed 责任面。", "codex_raci"),
    _doc("docs_bilingual/product_lifecycle/codex_platform_governed_agent_catalog.md", "product_lifecycle", "codex", "Codex Platform Governed Agent Catalog", "Codex 平台受治理 Agent 目录", "Defines the 12 governed AI-agent lanes, human gates, and validation responsibilities.", "定义 12 条受治理 AI Agent 通道、人类 gate 与验证责任。", "codex_agents"),
    _doc("docs_bilingual/product_lifecycle/codex_platform_cross_cutting_module_map.md", "product_lifecycle", "codex", "Codex Platform Cross-Cutting Module Map", "Codex 平台横切模块地图", "Defines the 18 cross-cutting modules that keep platform work aligned across lifecycle layers.", "定义 18 个横切模块，使平台工作跨生命周期层级保持对齐。", "codex_modules"),
    _doc("docs_bilingual/product_lifecycle/codex_platform_reference_books_map.md", "product_lifecycle", "codex", "Codex Platform Reference Books Map", "Codex 平台推荐书籍地图", "Maps the 12 recommended books to the durable-team operating model without treating books as copied source text.", "把 12 本推荐书籍映射到持久化团队 operating model，但不复制书籍正文。", "codex_books"),
    _doc("docs_bilingual/product_lifecycle/codex_platform_virtual_departments_operating_map.md", "product_lifecycle", "codex", "Codex Platform Virtual Departments Operating Map", "Codex 平台虚拟部门运行地图", "Defines how the 4 virtual departments operate the 12-layer platform and hand off work.", "定义 4 个虚拟部门如何运行 12 层平台并交接工作。", "codex_departments"),
    _doc("docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_document_generation_order.md", "product_lifecycle", "codex", "Codex CLI Durable Team Document Generation Order", "Codex CLI 持久化团队文档生成顺序", "Defines the recommended sequence for generating and expanding the 48-document durable-team package.", "定义生成和扩展 48 文档持久化团队运营包的推荐顺序。", "codex_generation_order"),
    _doc("docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_operating_slice_template.md", "product_lifecycle", "codex", "Codex CLI Durable Team Operating Slice Template", "Codex CLI 持久化团队运行切片模板", "Provides a repeatable slice template for applying the platform lifecycle to concrete local-main-first work.", "为把平台生命周期应用到具体本地 main 优先工作提供可重复切片模板。", "codex_slice_template"),
]

OPC_DOCS = [
    _doc("docs_bilingual/product_lifecycle/one_person_company_operations_document_system.md", "product_lifecycle", "one-person-company", "One-Person Company Operations Document System", "一人公司运营文档系统", "Defines the governed 60-document operating system and its relationship to the minimum startup set.", "定义受治理的 60 文档运营系统及其与最小启动集合的关系。", "opc_document_system"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_tailoring_decision_tree.md", "product_lifecycle", "one-person-company", "One-Person Company Tailoring Decision Tree", "一人公司裁剪决策树", "Defines when to use full, lightweight, phase-local, module-level, or hybrid architecture for solo business work.", "定义一人公司何时采用完整、轻量、阶段局部、模块级或混合架构。", "opc_tailoring_tree"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_minimum_startup_documents.md", "product_lifecycle", "one-person-company", "One-Person Company Minimum Startup Documents", "一人公司最小启动文档", "Defines the 12-document startup path before expanding into the complete 60-document operating system.", "定义在扩展为完整 60 文档运营系统前的 12 文档启动路径。", "opc_startup_docs"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_core_documents_register.md", "product_lifecycle", "one-person-company", "One-Person Company Core Documents Register", "一人公司核心文档登记表", "Registers the 60-document operating-system target as ten six-document families.", "把 60 文档运营系统目标登记为 10 个六文档家族。", "opc_core_docs"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_responsibility_raci.md", "product_lifecycle", "one-person-company", "One-Person Company Responsibility RACI", "一人公司责任 RACI", "Maps the 5 virtual departments and 30 responsibility domains to solo-owner and AI-agent collaboration surfaces.", "把 5 个虚拟部门和 30 个责任域映射到 solo owner 与 AI Agent 协同责任面。", "opc_raci"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_governed_agent_catalog.md", "product_lifecycle", "one-person-company", "One-Person Company Governed Agent Catalog", "一人公司受治理 Agent 目录", "Defines the 15 governed AI-agent lanes that support a solo operator without replacing human accountability.", "定义支持 solo operator 但不取代人类责任的 15 条受治理 AI Agent 通道。", "opc_agents"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_cross_cutting_module_map.md", "product_lifecycle", "one-person-company", "One-Person Company Cross-Cutting Module Map", "一人公司横切模块地图", "Defines the 20 cross-cutting modules that keep strategy, delivery, support, finance, trust, and administration aligned.", "定义 20 个横切模块，使战略、交付、支持、财务、信任和行政保持对齐。", "opc_modules"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_pmi_process_group_playbook.md", "product_lifecycle", "one-person-company", "One-Person Company PMI Process Group Playbook", "一人公司 PMI 过程组 Playbook", "Translates PMBOK, Process Groups, Agile, program, portfolio, and PMO overlays into a solo operating cadence.", "把 PMBOK、过程组、敏捷、项目集、项目组合和 PMO 叠加层转化为 solo operating cadence。", "opc_pmi_playbook"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_architecture_mode_selection_guide.md", "product_lifecycle", "one-person-company", "One-Person Company Architecture Mode Selection Guide", "一人公司架构模式选择指南", "Explains when the whole project is lightweight and when only a phase or module is lightweight.", "说明何时整个项目轻量，何时只有阶段或模块轻量。", "opc_architecture_modes"),
    _doc("docs_bilingual/product_lifecycle/one_person_company_operations_metrics_and_monthly_review.md", "product_lifecycle", "one-person-company", "One-Person Company Operations Metrics And Monthly Review", "一人公司运营指标与月度复盘", "Defines metrics, review cadence, stop or expand triggers, and learning outputs for the one-person-company system.", "定义一人公司系统的指标、复盘节奏、停止或扩展触发器与学习输出。", "opc_metrics_review"),
]

ALL_DOCS = CODEX_DOCS + OPC_DOCS


def table(headers: list[str], rows: list[tuple[Any, ...]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def inventory_table(package: str, zh: bool) -> str:
    c = EXPECTED_COUNTS[package]
    if zh:
        rows = [("主干层级", c["trunk_layers"], "0-11 的 12 层模型"), ("虚拟部门", c["virtual_departments"], "每个部门 6 个责任域"), ("责任域", c["responsibility_domains"], "用于 owner 与 RACI 映射"), ("横切模块", c["cross_cutting_modules"], "用于跨层风险和能力控制"), ("核心文档", c["core_documents"], "以六文档家族组织"), ("受治理 AI Agent", c["governed_ai_agents"], "每条通道保留人类 gate"), ("推荐书籍", c["recommended_books"], "作为主题地图而非复制来源文本")]
        if package == "one-person-company":
            rows.append(("最小启动文档", c["minimum_startup_documents"], "启动时的最小运营集合"))
        return table(["清单元素", "数量", "运行含义"], rows)
    rows = [("Trunk layers", c["trunk_layers"], "0-11 twelve-layer model"), ("Virtual departments", c["virtual_departments"], "six responsibility domains per department"), ("Responsibility domains", c["responsibility_domains"], "used for owner and RACI mapping"), ("Cross-cutting modules", c["cross_cutting_modules"], "used for cross-layer risk and capability control"), ("Core documents", c["core_documents"], "organized as six-document families"), ("Governed AI agents", c["governed_ai_agents"], "each lane keeps a human gate"), ("Recommended books", c["recommended_books"], "used as a topic map, not copied source text")]
    if package == "one-person-company":
        rows.append(("Minimum startup documents", c["minimum_startup_documents"], "smallest operating set for launch"))
    return table(["Inventory element", "Count", "Operating meaning"], rows)


def tailoring_table(zh: bool) -> str:
    if zh:
        return table(["模式", "何时使用", "轻量范围"], [(m[1], m[3], m[5]) for m in TAILORING_MODES])
    return table(["Mode", "Use when", "Lightweight scope"], [(m[0], m[2], m[4]) for m in TAILORING_MODES])


def process_table(zh: bool) -> str:
    if zh:
        return table(["过程组", "输入", "工具与技术", "输出"], [(p[1], p[3], p[5], p[7]) for p in PROCESS_GROUPS])
    return table(["Process group", "Inputs", "Tools And Techniques", "Outputs"], [(p[0], p[2], p[4], p[6]) for p in PROCESS_GROUPS])


def layers_table(zh: bool) -> str:
    return table(["#", "层级", "核心问题"], LAYERS_ZH) if zh else table(["#", "Layer", "Primary question"], LAYERS_EN)


def core_docs_table(package: str, zh: bool) -> str:
    data = CORE_48 if package == "codex" else CORE_60
    return table(["文档家族", "数量", "规范文档"] if zh else ["Document family", "Count", "Canonical documents"], [(family, len(items), ", ".join(items)) for family, items in data])


def departments_table(package: str, zh: bool) -> str:
    source = CODEX_DEPARTMENTS if package == "codex" else OPC_DEPARTMENTS
    rows: list[tuple[Any, ...]] = []
    index = 1
    for dept, domains in source:
        for domain in domains:
            rows.append((index, DEPT_ZH.get(dept, dept) if zh else dept, domain))
            index += 1
    return table(["#", "虚拟部门", "责任域"] if zh else ["#", "Virtual department", "Responsibility domain"], rows)


def list_table(items: list[str], zh: bool, kind: str) -> str:
    return table(["#", kind, "治理用途"] if zh else ["#", kind, "Governance use"], [(i, item, "映射到 owner、gate、证据与复盘" if zh else "Mapped to owner, gate, evidence, and retrospective") for i, item in enumerate(items, 1)])


def special(g: GeneratedDoc, zh: bool) -> str:
    if g.body_kind in {"codex_core_docs", "codex_generation_order", "opc_document_system", "opc_core_docs"}:
        return ("## 文档登记\n\n" if zh else "## Document Register\n\n") + core_docs_table(g.package, zh)
    if g.body_kind in {"codex_raci", "codex_departments", "opc_raci"}:
        return ("## 部门与责任域\n\n" if zh else "## Departments And Responsibility Domains\n\n") + departments_table(g.package, zh)
    if g.body_kind in {"codex_agents", "opc_agents"}:
        return ("## Agent 目录\n\n" if zh else "## Agent Catalog\n\n") + list_table(CODEX_AGENTS if g.package == "codex" else OPC_AGENTS, zh, "Agent")
    if g.body_kind in {"codex_modules", "opc_modules"}:
        return ("## 横切模块\n\n" if zh else "## Cross-Cutting Modules\n\n") + list_table(CODEX_MODULES if g.package == "codex" else OPC_MODULES, zh, "Module")
    if g.body_kind == "codex_books":
        return ("## 推荐书籍\n\n" if zh else "## Recommended Books\n\n") + list_table(CODEX_BOOKS, zh, "Book")
    if g.body_kind == "opc_startup_docs":
        return ("## 12 个最小启动文档\n\n" if zh else "## 12 Minimum Startup Documents\n\n") + list_table(STARTUP_DOCS, zh, "Document")
    if g.body_kind in {"opc_tailoring_tree", "opc_architecture_modes"}:
        return ("## 架构模式选择\n\n完整架构用于真实外部风险；整个项目轻量只允许在全部低风险条件同时成立时使用；阶段局部和模块级轻量只缩小被命名的范围；混合架构是默认的真实工作路径。\n\n" if zh else "## Architecture Mode Selection\n\nFull architecture is used for real external risk. Whole-project lightweight is allowed only when all low-risk conditions hold. Phase-local and module-level lightweight narrow only the named scope. Hybrid architecture is the default path for real work.\n\n") + tailoring_table(zh)
    if g.body_kind == "opc_pmi_playbook":
        return ("## PMI 叠加层\n\nPMBOK 8 是价值与裁剪主叠加层；Process Groups 提供执行语法；Agile 支持探索和反馈；项目集、项目组合与 PMO 只在多 initiative、容量取舍或共享治理服务出现时进入。\n\n" if zh else "## PMI Overlay\n\nPMBOK 8 is the primary value and tailoring overlay. Process Groups provide execution grammar. Agile supports discovery and feedback. Program, portfolio, and PMO overlays enter only for multiple initiatives, capacity tradeoffs, or shared governance services.\n\n") + process_table(zh)
    if g.body_kind == "opc_metrics_review":
        return "## 指标与月度复盘\n\n- 北极星：验证当前 offer 是否持续创造可付费价值。\n- 护栏：现金流、支持负载、质量、风险、合规和 operator 时间。\n- 月度输出：保留、停止、转向、扩展或重新裁剪。\n" if zh else "## Metrics And Monthly Review\n\n- North Star: prove whether the current offer keeps creating payable value.\n- Guardrails: cashflow, support load, quality, risk, compliance, and operator time.\n- Monthly outputs: keep, stop, pivot, expand, or re-tailor.\n"
    if g.body_kind == "codex_slice_template":
        return "## 运行切片模板\n\n1. 命名受影响层级、部门、责任域、横切模块、核心文档家族和 Agent gate。\n2. 写明裁剪模式以及为什么不更重也不更轻。\n3. 以输入、工具与技术、输出定义执行流程。\n4. 本地验证、提交、合入 local main，并停在远端发布门。\n" if zh else "## Operating Slice Template\n\n1. Name affected layer, department, responsibility domain, cross-cutting module, core-document family, and agent gate.\n2. State the tailoring mode and why it is not heavier or lighter.\n3. Define the execution flow with Inputs, Tools And Techniques, and Outputs.\n4. Validate, commit, integrate local main, and stop at the remote-publication gate.\n"
    if g.body_kind == "template_policy":
        return "## 模板变更策略\n\n模板变更必须说明适用范围、非目标、版本兼容、回滚路径、示例更新和下游项目迁移边界。共享模板不得绕过 OpenSpec、local gate 或本地 MR review。\n" if zh else "## Template Change Policy\n\nTemplate changes must state scope, non-goals, version compatibility, rollback path, example updates, and downstream migration boundary. Shared templates must not bypass OpenSpec, local gate, or local MR review.\n"
    if g.body_kind in {"codex_brd", "codex_prd"}:
        return "## 需求摘要\n\n该平台面向个人开发者的生产级 Codex CLI 持久化团队，核心价值是在一人操作下保持专家路由、持久执行、证据门禁、本地 main 集成和远端发布审批边界。\n" if zh else "## Requirements Summary\n\nThe platform serves a personal developer running a production-grade Codex CLI durable team. Its value is to keep expert routing, durable execution, evidence gates, local-main integration, and remote-publication approval boundaries operable for a solo operator.\n"
    return ""


def front_matter(g: GeneratedDoc, zh: bool) -> str:
    rows = ["---", f"doc_id: {g.doc_id}", f"doc_class: {g.doc_class}", "status: active", f"package: {g.package}", "generated_by: tools/generate_operations_package.py", "lang: zh-CN" if zh else "lang: en"]
    if zh:
        rows.append(f"translation_of: {g.rel_path}")
    rows.append("---")
    return "\n".join(rows) + "\n\n"


def render_doc(g: GeneratedDoc, zh: bool = False) -> str:
    authority_en = "This generated package uses tracked repository authorities refreshed from Business Management, product lifecycle, and PMP synthesis: codex_platform_inventory_map.md, one_person_company_inventory_map.md, durable_team_process_group_contract.md, lifecycle_tailoring_rules.md, pmi_project_management_reference_map.md, and the two current white papers. Stage B operationalizes those tracked authorities and does not re-extract raw PDF, EPUB, or Markdown source libraries."
    authority_zh = "本生成包使用已跟踪的仓库权威文档，这些文档来自 Business Management、product lifecycle 与 PMP 综合刷新：codex_platform_inventory_map.md、one_person_company_inventory_map.md、durable_team_process_group_contract.md、lifecycle_tailoring_rules.md、pmi_project_management_reference_map.md 以及两份当前白皮书。Stage B 只把这些已跟踪权威运行化，不重新抽取原始 PDF、EPUB 或 Markdown source libraries。"
    if zh:
        sections = [
            front_matter(g, True),
            GENERATED_MARKER,
            f"\n\n# {g.title_zh}\n",
            f"## 目的\n\n{g.purpose_zh}\n",
            special(g, True),
            "## 权威边界\n\n" + authority_zh + "\n",
            "## 规范清单\n\n" + inventory_table(g.package, True),
            "## 12 层主干\n\n" + layers_table(True),
            "## 裁剪规则\n\n裁剪不是在心智模型中删除层级，而是选择最小充分治理深度。每个裁剪记录都必须说明为什么所选模式不更重也不更轻，并列出升级触发器。\n\n" + tailoring_table(True),
            "## 输入\n\n- 当前白皮书、北极星、清单地图、PMI map 与 lifecycle tailoring rules。\n- 目标项目或平台切片的风险、耦合、owner、证据和约束。\n- 本地 main 优先工作流、OpenSpec 状态、验证路径和远端发布边界。\n",
            "## 工具与技术\n\n- 12 层落点分析、责任域映射、RACI、过程组 I/T/O、裁剪评分卡。\n- PMBOK 8 价值与裁剪叠加、Process Groups 执行语法、Agile 反馈循环、PMO 治理服务按需进入。\n- 生成器、检查器、本地 CI、本地 MR review、回滚引用与 lessons learned。\n",
            "## 输出\n\n- 双语受治理运营包文档、registry 条目、验证报告和变更路径证据。\n- 明确的裁剪决策、升级触发器、owner、验证和 closeout 记录。\n- 停在远端发布门，除非用户显式授权远端发布。\n",
            "## 过程组运行表\n\n" + process_table(True),
        ]
    else:
        sections = [
            front_matter(g, False),
            GENERATED_MARKER,
            f"\n\n# {g.title_en}\n",
            f"## Purpose\n\n{g.purpose_en}\n",
            special(g, False),
            "## Authority Boundary\n\n" + authority_en + "\n",
            "## Canonical Inventory\n\n" + inventory_table(g.package, False),
            "## 12 Trunk Layers\n\n" + layers_table(False),
            "## Tailoring Rules\n\nTailoring does not delete layers from the mental model. It chooses the minimum sufficient governance depth. Every tailoring record must explain why the selected mode is not heavier or lighter and list escalation triggers.\n\n" + tailoring_table(False),
            "## Inputs\n\n- Current white paper, North Star, inventory map, PMI map, and lifecycle tailoring rules.\n- Target project or platform slice risk, coupling, owner, evidence, and constraints.\n- Local-main-first workflow state, OpenSpec state, validation path, and remote-publication boundary.\n",
            "## Tools And Techniques\n\n- Twelve-layer landing analysis, responsibility-domain mapping, RACI, process-group I/T/O, and tailoring scorecard.\n- PMBOK 8 value and tailoring overlay, Process Groups execution grammar, Agile feedback loop, and PMO governance service when needed.\n- Generator, checker, local CI, local MR review, rollback reference, and lessons learned.\n",
            "## Outputs\n\n- Bilingual governed operations-package documents, registry entries, validation reports, and changed-path evidence.\n- Explicit tailoring decision, escalation triggers, owner, validation, and closeout record.\n- Stop point at the remote-publication gate unless the user explicitly authorizes remote publication.\n",
            "## Process Group Operating Table\n\n" + process_table(False),
        ]
    return "\n".join(part.strip() for part in sections if part).strip() + "\n"


def selected_docs(package: str) -> list[GeneratedDoc]:
    if package == "codex":
        return CODEX_DOCS
    if package == "one-person-company":
        return OPC_DOCS
    return ALL_DOCS


def expected_files(package: str = "all") -> dict[str, str]:
    files: dict[str, str] = {}
    for g in selected_docs(package):
        files[g.rel_path] = render_doc(g, False)
        files[g.zh_path] = render_doc(g, True)
    return files


def registry_entries_for_generated_docs() -> list[dict[str, str]]:
    return [{"doc_id": g.doc_id, "doc_class": g.doc_class, "status": "active", "canonical_path": g.rel_path, "zh_cn_path": g.zh_path} for g in ALL_DOCS]


def write_expected(root: Path, package: str) -> list[str]:
    changed: list[str] = []
    for rel, content in expected_files(package).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != content:
            path.write_text(content, encoding="utf-8", newline="\n")
            changed.append(rel)
    return changed


def check_expected(root: Path, package: str) -> tuple[list[str], list[str]]:
    out_of_date: list[str] = []
    matched: list[str] = []
    for rel, content in expected_files(package).items():
        path = root / rel
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            out_of_date.append(rel)
        else:
            matched.append(rel)
    return out_of_date, matched


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate governed bilingual operations-package Markdown documents.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--package", choices=["codex", "one-person-company", "all"], default="all", help="Package to generate or check.")
    parser.add_argument("--check", action="store_true", help="Check whether generated files are current without writing them.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.check:
        out_of_date, matched = check_expected(root, args.package)
        payload = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "check_name": CHECK_NAME, "ok": not out_of_date, "root": str(root), "package": args.package, "mode": "check", "changed_or_missing": out_of_date, "counts": {"expected_files": len(expected_files(args.package)), "matched_files": len(matched), "changed_or_missing": len(out_of_date)}}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'out-of-date'}")
            for rel in out_of_date:
                print(f"OUT_OF_DATE: {rel}")
        return 0 if payload["ok"] else 1

    changed = write_expected(root, args.package)
    payload = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "check_name": CHECK_NAME, "ok": True, "root": str(root), "package": args.package, "mode": "write", "changed_files": changed, "counts": {"expected_files": len(expected_files(args.package)), "changed_files": len(changed)}}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: wrote {len(changed)} changed files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
