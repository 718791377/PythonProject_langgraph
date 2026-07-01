#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

CHECK_NAME = "operations_package_generation"
GENERATED_MARKER = "<!-- GENERATED_BY: tools/generate_operations_package.py; DO NOT EDIT BY HAND. -->"

TAILORING_MODES = [
    (
        "Full architecture",
        "完整架构",
        "Cross-stage, external-customer, revenue, compliance, security, publication, "
        "rollback, durable-state, shared-runtime, or multi-agent work.",
        "跨阶段、外部客户、收入、合规、安全、发布、回滚、持久状态、共享运行时或多 Agent 工作。",
        "Govern every affected risk layer end to end.",
        "端到端治理所有受影响的风险层。",
    ),
    (
        "Whole-project lightweight",
        "全项目轻量",
        "Private, reversible, low-risk exploration with no external commitment, "
        "durable-state impact, publication, sensitive data, or shared runtime.",
        "私有、可逆、低风险探索，并且没有外部承诺、持久状态影响、发布、敏感数据或共享运行时影响。",
        "The whole project may stay light while still recording owner, validation, "
        "rollback, and learning.",
        "整个项目可以保持轻量，但仍记录负责人、验证、回滚和学习。",
    ),
    (
        "Phase-local lightweight",
        "阶段局部轻量",
        "One discovery, metrics, growth, or retrospective phase is low risk inside a "
        "larger governed project.",
        "更大受治理项目中的某个发现、指标、增长或复盘阶段风险较低。",
        "Only that named phase is light; upstream and downstream gates stay explicit.",
        "只有被命名的阶段轻量；上下游门禁保持显式。",
    ),
    (
        "Module-level lightweight",
        "模块级轻量",
        "One bounded document family, helper, prototype, or local module does not "
        "change trust, state, public API, CI, release, or shared runtime behavior.",
        "单个有边界的文档族、helper、原型或本地模块不改变信任、状态、公共 API、CI、发布或共享运行时行为。",
        "Only that module is light; the surrounding project keeps its full boundary.",
        "只有该模块轻量；周边项目保留完整边界。",
    ),
    (
        "Hybrid architecture",
        "混合架构",
        "Most real work, where low-risk phases can start light but production, "
        "customer, revenue, trust, durable-state, or release impact needs fuller control.",
        "多数真实工作；低风险阶段可先轻量，但生产、客户、收入、信任、持久状态或发布影响需要更完整控制。",
        "Critical layers are full; low-risk phases or modules stay light until "
        "escalation triggers fire.",
        "关键层完整；低风险阶段或模块在升级触发前保持轻量。",
    ),
]

CORE_48 = [
    ("Strategy and business", ["vision.md", "thesis.md", "business-model.md", "pricing.md", "unit-economics.md", "strategy.md"]),
    ("Market and product", ["user-segments.md", "market-map.md", "research-repository.md", "product-strategy.md", "prd.md", "cli-ux.md"]),
    ("Metrics and data", ["metrics.md", "north-star.md", "tracking-plan.md", "data-dictionary.md", "data-quality-checklist.md", "experiment-log.md"]),
    ("Engineering and platform", ["architecture.md", "adr.md", "module-boundaries.md", "tech-stack.md", "delivery-plan.md", "observability.md"]),
    ("Security and risk", ["security-policy.md", "access-control.md", "privacy-policy.md", "incident-response.md", "risk-register.md", "backup-restore.md"]),
    ("Agent governance", ["agent-role-map.md", "agent-permissions.md", "agent-governance.md", "human-review-checklist.md", "agent-evaluation.md", "agent-failure-modes.md"]),
    ("Growth and operations", ["growth-model.md", "docs-plan.md", "support-playbook.md", "faq.md", "trust-page.md", "changelog.md"]),
    ("Retrospective and knowledge", ["decision-log.md", "weekly-review.md", "monthly-review.md", "postmortem.md", "learning-log.md", "template-library.md"]),
]

CORE_60 = [
    ("Company strategy", ["thesis.md", "vision.md", "strategy.md", "annual-plan.md", "quarterly-plan.md", "decision-log.md"]),
    ("Business and finance", ["business-model.md", "offer.md", "pricing.md", "unit-economics.md", "finance-model.md", "cashflow.md"]),
    ("Market and user", ["market-map.md", "user-segments.md", "competitor-analysis.md", "alternative-solutions.md", "research-repository.md", "interview-guide.md"]),
    ("Product and service", ["product-strategy.md", "prd.md", "service-blueprint.md", "onboarding.md", "customer-journey.md", "roadmap.md"]),
    ("Metrics and data", ["metrics.md", "north-star.md", "funnel-dashboard.md", "tracking-plan.md", "data-dictionary.md", "experiment-log.md"]),
    ("Growth and sales", ["growth-model.md", "channel-map.md", "sales-playbook.md", "landing-page.md", "email-sequences.md", "content-calendar.md"]),
    ("Operations and customer success", ["ops-playbook.md", "customer-success-playbook.md", "support-playbook.md", "faq.md", "refund-policy.md", "feedback-triage.md"]),
    ("Technology and automation", ["tech-stack.md", "automation-map.md", "tool-stack.md", "vendor-register.md", "api-dependency-map.md", "backup-restore.md"]),
    ("Governance and risk", ["legal-checklist.md", "terms-of-service.md", "privacy-policy.md", "contract-template.md", "risk-register.md", "compliance-checklist.md"]),
    ("Agent and knowledge", ["agent-governance.md", "agent-role-map.md", "agent-permissions.md", "human-review-checklist.md", "monthly-review.md", "learning-log.md"]),
]

FAMILY_ZH = {
    "Strategy and business": "战略与商业",
    "Market and product": "市场与产品",
    "Metrics and data": "指标与数据",
    "Engineering and platform": "工程与平台",
    "Security and risk": "安全与风险",
    "Agent governance": "Agent 治理",
    "Growth and operations": "增长与运营",
    "Retrospective and knowledge": "复盘与知识",
    "Company strategy": "公司战略",
    "Business and finance": "商业与财务",
    "Market and user": "市场与用户",
    "Product and service": "产品与服务",
    "Growth and sales": "增长与销售",
    "Operations and customer success": "运营与客户成功",
    "Technology and automation": "技术与自动化",
    "Governance and risk": "治理与风险",
    "Agent and knowledge": "Agent 与知识",
}

LAYER_EN = {
    0: "Cognitive narrative",
    1: "Business",
    2: "Market",
    3: "Strategy",
    4: "Metrics",
    5: "Product",
    6: "Technical",
    7: "Organization",
    8: "Execution",
    9: "Growth",
    10: "Operations",
    11: "Retrospective",
}
LAYER_ZH = {
    0: "认知叙事",
    1: "商业",
    2: "市场",
    3: "战略",
    4: "指标",
    5: "产品",
    6: "技术",
    7: "组织",
    8: "执行",
    9: "增长",
    10: "运营",
    11: "复盘",
}

FAMILY_META = {
    "Strategy and business": ([0, 1, 3], ["Initiating", "Planning"], "Strategy and Product Office", "Hybrid architecture"),
    "Market and product": ([2, 3, 5], ["Initiating", "Planning", "Monitoring and Controlling"], "Strategy and Product Office", "Hybrid architecture"),
    "Metrics and data": ([4, 8, 11], ["Planning", "Monitoring and Controlling", "Closing"], "Engineering and Platform Office", "Phase-local lightweight"),
    "Engineering and platform": ([6, 8], ["Planning", "Executing", "Monitoring and Controlling"], "Engineering and Platform Office", "Hybrid architecture"),
    "Security and risk": ([6, 7, 8], ["Initiating", "Planning", "Executing", "Monitoring and Controlling", "Closing"], "Agent Governance Office", "Full architecture"),
    "Agent governance": ([7, 8], ["Planning", "Executing", "Monitoring and Controlling"], "Agent Governance Office", "Full architecture"),
    "Growth and operations": ([9, 10], ["Executing", "Monitoring and Controlling", "Closing"], "Growth and Knowledge Office", "Hybrid architecture"),
    "Retrospective and knowledge": ([11], ["Monitoring and Controlling", "Closing"], "Growth and Knowledge Office", "Phase-local lightweight"),
    "Company strategy": ([0, 1, 3], ["Initiating", "Planning", "Closing"], "Strategy Office", "Hybrid architecture"),
    "Business and finance": ([1, 4, 10], ["Planning", "Monitoring and Controlling", "Closing"], "Strategy Office", "Hybrid architecture"),
    "Market and user": ([2, 3, 4], ["Initiating", "Planning", "Monitoring and Controlling"], "Product and Market Office", "Phase-local lightweight"),
    "Product and service": ([5, 8, 10], ["Planning", "Executing", "Monitoring and Controlling"], "Product and Market Office", "Hybrid architecture"),
    "Growth and sales": ([9, 8], ["Planning", "Executing", "Monitoring and Controlling"], "Revenue and Growth Office", "Hybrid architecture"),
    "Operations and customer success": ([10, 8], ["Executing", "Monitoring and Controlling", "Closing"], "Operations Office", "Hybrid architecture"),
    "Technology and automation": ([6, 8, 10], ["Planning", "Executing", "Monitoring and Controlling"], "Operations Office", "Module-level lightweight"),
    "Governance and risk": ([6, 7, 8], ["Initiating", "Planning", "Executing", "Monitoring and Controlling", "Closing"], "Governance Office", "Full architecture"),
    "Agent and knowledge": ([7, 11], ["Planning", "Executing", "Closing"], "Governance Office", "Hybrid architecture"),
}

OWNER_ZH = {
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

PROCESS_GROUPS_EN = [
    ("Initiating", "source need, owner signal, scope boundary, first risk", "charter framing, stakeholder scan, tailoring pre-check", "authorized operating slice, named owner, initial risk log"),
    ("Planning", "approved purpose, dependencies, constraints, acceptance target", "I/T/O planning, RACI mapping, validation design, rollback design", "document plan, validation path, rollback boundary"),
    ("Executing", "approved slice, templates, evidence, local state", "controlled drafting, review, test, evidence capture", "updated operating artifact, change evidence, handoff record"),
    ("Monitoring and Controlling", "active artifact, metrics, issues, review feedback", "quality checks, variance review, change control, gate rerun", "issue log, decision record, gate evidence"),
    ("Closing", "accepted artifact, final evidence, residual risk", "closeout review, archive or registry sync, retrospective", "final body doc, registry entry, lessons learned"),
]
PROCESS_GROUPS_ZH = [
    ("启动", "来源需求、负责人信号、范围边界、首轮风险", "章程式界定、干系人扫描、裁剪预检", "获准继续的运营切片、已命名负责人、初始风险日志"),
    ("规划", "已批准目的、依赖、约束、验收目标", "I/T/O 规划、RACI 映射、验证设计、回滚设计", "文档计划、验证路径、回滚边界"),
    ("执行", "已批准切片、模板、证据、本地状态", "受控起草、评审、测试、证据捕获", "已更新运营产物、变更证据、交接记录"),
    ("监控", "活动产物、指标、问题、评审反馈", "质量检查、偏差复核、变更控制、门禁重跑", "问题日志、决策记录、门禁证据"),
    ("收尾", "已验收产物、最终证据、剩余风险", "收尾评审、归档或登记同步、复盘", "最终正文文档、登记条目、经验教训"),
]


@dataclass(frozen=True)
class GeneratedDoc:
    doc_id: str
    rel_path: str
    zh_path: str
    doc_class: str
    package: str
    body_kind: str
    source_name: str
    slug: str
    family: str
    title_en: str
    title_zh: str
    purpose_en: str
    purpose_zh: str
    primary_layers: tuple[int, ...]
    process_groups: tuple[str, ...]
    owner_surface_en: str
    owner_surface_zh: str
    default_mode: str


def _slug(source_name: str) -> str:
    stem = source_name.rsplit(".", 1)[0]
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def _title(slug: str) -> str:
    overrides = {"prd": "PRD", "faq": "FAQ", "adr": "ADR", "api": "API", "ux": "UX"}
    return " ".join(overrides.get(part, part.capitalize()) for part in slug.split("-"))


def _body_kind(family: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", family.lower()).strip("_") + "_body"


def _doc(package: str, family: str, source_name: str) -> GeneratedDoc:
    slug = _slug(source_name)
    layers, groups, owner, mode = FAMILY_META[family]
    if package == "codex":
        doc_id = f"codex_cli_durable_team_{slug.replace('-', '_')}"
        folder = "codex_cli_durable_team"
        title_en = f"Codex CLI Durable Team {_title(slug)} Body Document"
        title_zh = f"Codex CLI 持久化团队 {_title(slug)} 正文运营文档"
        purpose_en = (
            f"Defines how the personal production command-line team system operates "
            f"the {source_name} artifact inside the {family.lower()} family with "
            f"evidence gates, expert routing discipline, and approval boundaries."
        )
        purpose_zh = (
            f"定义个人生产级命令行团队系统如何在{FAMILY_ZH[family]}文档族中运行 "
            f"{source_name} 产物，并保留证据门禁、专家路由纪律和审批边界。"
        )
    else:
        doc_id = f"one_person_company_{slug.replace('-', '_')}"
        folder = "one_person_company"
        title_en = f"One-Person Company {_title(slug)} Body Document"
        title_zh = f"一人公司 {_title(slug)} 正文运营文档"
        purpose_en = (
            f"Defines how the solo production business operating system uses the "
            f"{source_name} artifact inside the {family.lower()} family to make "
            f"decisions, collect evidence, and select the right tailoring depth."
        )
        purpose_zh = (
            f"定义单人生产级业务运营系统如何在{FAMILY_ZH[family]}文档族中使用 "
            f"{source_name} 产物，以支持业务决策、证据收集和合适裁剪深度选择。"
        )
    return GeneratedDoc(
        doc_id=doc_id,
        rel_path=f"docs_bilingual/operations_packages/{folder}/{slug}.md",
        zh_path=f"docs_bilingual/operations_packages/{folder}/{slug}.zh-CN.md",
        doc_class="operations_package",
        package=package,
        body_kind=_body_kind(family),
        source_name=source_name,
        slug=slug,
        family=family,
        title_en=title_en,
        title_zh=title_zh,
        purpose_en=purpose_en,
        purpose_zh=purpose_zh,
        primary_layers=tuple(layers),
        process_groups=tuple(groups),
        owner_surface_en=owner,
        owner_surface_zh=OWNER_ZH[owner],
        default_mode=mode,
    )


def _build_docs() -> tuple[list[GeneratedDoc], list[GeneratedDoc]]:
    codex = [_doc("codex", family, name) for family, names in CORE_48 for name in names]
    opc = [_doc("one-person-company", family, name) for family, names in CORE_60 for name in names]
    return codex, opc


CODEX_DOCS, OPC_DOCS = _build_docs()
ALL_DOCS = CODEX_DOCS + OPC_DOCS

STALE_LEGACY_FILES = {
    "codex": (
        "docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.md",
        "docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.zh-CN.md",
    ),
    "one-person-company": (
        "docs_bilingual/operations_packages/one_person_company/company-thesis.md",
        "docs_bilingual/operations_packages/one_person_company/company-thesis.zh-CN.md",
        "docs_bilingual/operations_packages/one_person_company/support-policy.md",
        "docs_bilingual/operations_packages/one_person_company/support-policy.zh-CN.md",
    ),
}

STALE_LEGACY_DOC_IDS = (
    "codex_cli_durable_team_agent_tool_policy",
    "one_person_company_company_thesis",
    "one_person_company_support_policy",
)


def stale_legacy_files(package: str = "all") -> list[str]:
    if package == "codex":
        return list(STALE_LEGACY_FILES["codex"])
    if package == "one-person-company":
        return list(STALE_LEGACY_FILES["one-person-company"])
    return list(STALE_LEGACY_FILES["codex"] + STALE_LEGACY_FILES["one-person-company"])


def stale_legacy_doc_ids(package: str = "all") -> list[str]:
    if package == "codex":
        return ["codex_cli_durable_team_agent_tool_policy"]
    if package == "one-person-company":
        return ["one_person_company_company_thesis", "one_person_company_support_policy"]
    return list(STALE_LEGACY_DOC_IDS)


def selected_docs(package: str) -> list[GeneratedDoc]:
    if package == "codex":
        return CODEX_DOCS
    if package == "one-person-company":
        return OPC_DOCS
    return ALL_DOCS


def table(headers: list[str], rows: list[tuple[str, ...]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def front_matter(g: GeneratedDoc, zh: bool) -> str:
    rows = [
        "---",
        f"doc_id: {g.doc_id}",
        f"doc_class: {g.doc_class}",
        "status: active",
        f"package: {g.package}",
        f"body_kind: {g.body_kind}",
        "generated_by: tools/generate_operations_package.py",
        "lang: zh-CN" if zh else "lang: en",
    ]
    if zh:
        rows.append(f"translation_of: {g.rel_path}")
    rows.append("---")
    return "\n".join(rows)


def tailoring_table(zh: bool) -> str:
    if zh:
        rows = [(zh_name, use_zh, scope_zh) for _en, zh_name, _use_en, use_zh, _scope_en, scope_zh in TAILORING_MODES]
        return table(["模式", "使用时机", "轻量范围"], rows)
    rows = [(en, use_en, scope_en) for en, _zh, use_en, _use_zh, scope_en, _scope_zh in TAILORING_MODES]
    return table(["Mode", "Use when", "Lightweight scope"], rows)


def lifecycle_text(g: GeneratedDoc, zh: bool) -> str:
    if zh:
        layers = ", ".join(f"L{idx} {LAYER_ZH[idx]}" for idx in g.primary_layers)
        return (
            f"- 主生命周期层级：{layers}\n"
            f"- 主过程组：{', '.join(g.process_groups)}\n"
            f"- 负责人界面：{g.owner_surface_zh}\n"
            f"- 文档族：{FAMILY_ZH[g.family]}；源清单项：`{g.source_name}`。\n"
        )
    layers = ", ".join(f"L{idx} {LAYER_EN[idx]}" for idx in g.primary_layers)
    return (
        f"- Primary lifecycle layers: {layers}\n"
        f"- Primary process groups: {', '.join(g.process_groups)}\n"
        f"- Owner surface: {g.owner_surface_en}\n"
        f"- Document family: {g.family}; source list item: `{g.source_name}`.\n"
    )


def authority_text(g: GeneratedDoc, zh: bool) -> str:
    if g.package == "codex":
        if zh:
            return (
                "- 权威来源：团队白皮书、北极星、product lifecycle 清单、PMI 过程组合同、"
                "OpenSpec 变更和本地优先发布规则。\n"
                "- 本文档只运行化本包的受治理命令行团队运营规则。\n"
                "- Codex owns execution truth for agents, OpenSpec, worktrees, durable state, "
                "validation gates, local-main evidence, rollback, and release boundaries.\n"
                "- Codex is an embedded execution capability inside a one-person company; "
                "it is not a peer business authority and must not redefine business truth.\n"
                "- 任何远端发布仍需要当前用户消息显式授权。\n"
            )
        return (
            "- Authority sources: team white paper, North Star, product lifecycle registers, "
            "PMI process-group contract, OpenSpec change, and local-first publication rules.\n"
            "- This document operationalizes only this governed command-line team package.\n"
            "- Codex owns execution truth for agents, OpenSpec, worktrees, durable state, "
            "validation gates, local-main evidence, rollback, and release boundaries.\n"
            "- Codex remains an embedded execution capability inside a one-person company; "
            "it is not a peer business authority and must not redefine business truth.\n"
            "- Any remote publication still requires explicit approval in the current user message.\n"
        )
    if zh:
        return (
            "- 权威来源：运营白皮书、北极星、Business Management 综合、product lifecycle 清单、"
            "PMI 过程组合同和裁剪规则。\n"
            "- 本文档只运行化本包的单人业务运营规则。\n"
            "- The one-person company owns business truth for customers, revenue, pricing, "
            "contracts, legal posture, cashflow, support, delivery commitments, and business learning.\n"
            "- Embedded Codex supplies governed execution truth for agents, worktrees, durable state, "
            "validation gates, rollback, and release boundaries; it is not a peer business authority and must not redefine business truth.\n"
            "- 任何外部承诺、收入、合同、隐私或合规影响都必须进入更完整的治理深度。\n"
        )
    return (
        "- Authority sources: operations white paper, North Star, Business Management synthesis, "
        "product lifecycle registers, PMI process-group contract, and tailoring rules.\n"
        "- This document operationalizes only this solo business operations package.\n"
        "- The one-person company owns business truth for customers, revenue, pricing, "
        "contracts, legal posture, cashflow, support, delivery commitments, and business learning.\n"
        "- Embedded Codex supplies governed execution truth for agents, worktrees, durable state, "
        "validation gates, rollback, and release boundaries; it is not a peer business authority and must not redefine business truth.\n"
        "- Any external commitment, revenue, contract, privacy, or compliance impact must enter a fuller governance depth.\n"
    )


def package_terms(g: GeneratedDoc, zh: bool) -> tuple[str, str, str]:
    title = _title(g.slug)
    if g.package == "codex":
        if zh:
            return (
                f"- 当前本地工作区、OpenSpec、registry、验证门禁和 {g.owner_surface_zh} 的 owner 约束。\n"
                f"- `{g.source_name}` 所属文档族、风险画像、依赖、回滚或退休路径。\n"
                "- 专家路由、持久执行和本地优先证据的最新边界。",
                "- 12 层落点、RACI、Agent gate、过程组 I/T/O 和裁剪评分卡。\n"
                "- 确定性生成器、检查器、聚焦测试、本地 CI、本地评审与回滚引用。\n"
                "- 仅在所有权隔离时使用 expert 或 durable lane，并由 leader 负责 fan-in。",
                f"- `{title}` 的受治理正文、配套 zh-CN companion 和 registry 条目。\n"
                "- owner、裁剪模式、升级触发器、验证路径和发布审批边界记录。\n"
                "- 可供后续实施、验证、复盘或归档使用的运营证据。",
            )
        return (
            f"- Current local workspace, OpenSpec state, registry state, validation gates, and {g.owner_surface_en} owner constraints.\n"
            f"- The `{g.source_name}` document family, risk profile, dependencies, rollback path, or retirement path.\n"
            "- Latest boundaries for expert routing, durable execution, and local-first evidence.",
            "- Twelve-layer placement, RACI, agent gates, process-group I/T/O, and tailoring scorecard.\n"
            "- Deterministic generator, checker, focused tests, local CI, local review, and rollback reference.\n"
            "- Expert or durable lane handoff only when ownership is isolated, with leader-owned fan-in.",
            f"- Governed `{title}` body document, zh-CN companion, and registry entry.\n"
            "- Owner, tailoring mode, escalation triggers, validation path, and publication approval boundary record.\n"
            "- Operating evidence for later implementation, verification, retrospective, or archive work.",
        )
    if zh:
        return (
            f"- 当前产品、客户、现金流、交付容量、风险、合规和 {g.owner_surface_zh} 的 owner 约束。\n"
            f"- `{g.source_name}` 所属文档族、业务假设、证据来源、依赖和停止或扩展条件。\n"
            "- 单人 operator 的时间预算、自动化边界和月度复盘输入。",
            "- 12 层落点、责任域映射、PMI 过程组 I/T/O、敏捷反馈循环和裁剪评分卡。\n"
            "- 客户发现、财务检查、渠道实验、服务交付复盘和合规核对。\n"
            "- 只在外部承诺、收入或风险扩大时升级治理深度。",
            f"- `{title}` 的受治理正文、配套 zh-CN companion 和 registry 条目。\n"
            "- 产品、价格、渠道、支持、财务、合规或知识库中的下一步更新。\n"
            "- 可在月度复盘中使用的保留、停止、转向、扩展或重新裁剪证据。",
        )
    return (
        f"- Current offer, customers, cashflow, delivery capacity, risk, compliance, and {g.owner_surface_en} owner constraints.\n"
        f"- The `{g.source_name}` document family, business assumptions, evidence sources, dependencies, and stop or expand conditions.\n"
        "- Solo-operator time budget, automation boundary, and monthly review inputs.",
        "- Twelve-layer placement, responsibility-domain mapping, PMI process-group I/T/O, agile feedback loops, and tailoring scorecard.\n"
        "- Customer discovery, finance checks, channel experiments, service delivery review, and compliance checks.\n"
        "- Governance depth escalates only when external commitment, revenue, or risk expands.",
        f"- Governed `{title}` body document, zh-CN companion, and registry entry.\n"
        "- Next update for offer, pricing, channel, support, finance, compliance, or knowledge base.\n"
        "- Evidence for monthly keep, stop, pivot, expand, or re-tailor decisions.",
    )


def process_table(g: GeneratedDoc, zh: bool) -> str:
    if zh:
        rows = [(group, f"{inputs}；文档 `{g.source_name}`", tools, outputs) for group, inputs, tools, outputs in PROCESS_GROUPS_ZH]
        return table(["过程组", "输入", "工具与技术", "输出"], rows)
    rows = [(group, f"{inputs}; document `{g.source_name}`", tools, outputs) for group, inputs, tools, outputs in PROCESS_GROUPS_EN]
    return table(["Process group", "Inputs", "Tools And Techniques", "Outputs"], rows)


def render_doc(g: GeneratedDoc, zh: bool = False) -> str:
    input_text, tool_text, output_text = package_terms(g, zh)
    if zh:
        mode_zh = {en: zh_name for en, zh_name, *_rest in TAILORING_MODES}[g.default_mode]
        escalation = (
            "当范围、信任、合规、收入暴露、恢复难度或跨边界协同超出当前模式记录的假设时，必须升级到更重的裁剪模式。 "
            f"针对 `{g.source_name}`，如果 owner 无法确认、证据不可复现、验证路径失效或输出影响外部承诺，也必须升级。"
        )
        parts = [
            front_matter(g, True),
            "",
            GENERATED_MARKER,
            "",
            f"# {g.title_zh}",
            "",
            "## 目的",
            "",
            g.purpose_zh,
            "",
            "## 权威边界",
            "",
            authority_text(g, True).rstrip(),
            "",
            "## 生命周期落点",
            "",
            lifecycle_text(g, True).rstrip(),
            "",
            "## 裁剪规则",
            "",
            f"默认裁剪模式：{mode_zh}。该选择必须说明为什么不更重也不更轻，并保留升级触发器。",
            "",
            tailoring_table(True).rstrip(),
            "",
            "### 为什么不更重也不更轻",
            "",
            f"`{g.source_name}` 默认采用上述模式，因为 {FAMILY_ZH[g.family]} 的风险需要被治理，"
            "但只有触及外部承诺、敏感信息、共享状态或恢复困难时才需要扩大到更重模式。",
            "",
            "### 升级触发器",
            "",
            escalation,
            "",
            "## 输入",
            "",
            input_text,
            "",
            "## 工具与技术",
            "",
            tool_text,
            "",
            "## 输出",
            "",
            output_text,
            "",
            "## 过程组运行表",
            "",
            process_table(g, True).rstrip(),
            "",
            "## 收尾与登记",
            "",
            f"- Registry 中的 `doc_id` 必须保持唯一：`{g.doc_id}`。\n"
            f"- 英文主文件 `{g.rel_path}` 与中文 companion `{g.zh_path}` 必须成对更新。\n"
            "- 收尾时确认 owner、裁剪模式、升级触发器、输出证据和下一周期输入。",
            "",
        ]
        return "\n".join(parts)

    escalation = (
        "Escalate to a heavier tailoring mode when scope, trust, compliance, revenue exposure, "
        "recovery difficulty, or cross-boundary coordination exceeds the assumptions recorded "
        f"for the current mode. For `{g.source_name}`, also escalate when the owner cannot "
        "confirm evidence, validation is no longer repeatable, or outputs affect an external commitment."
    )
    parts = [
        front_matter(g, False),
        "",
        GENERATED_MARKER,
        "",
        f"# {g.title_en}",
        "",
        "## Purpose",
        "",
        g.purpose_en,
        "",
        "## Authority Boundary",
        "",
        authority_text(g, False).rstrip(),
        "",
        "## Lifecycle Placement",
        "",
        lifecycle_text(g, False).rstrip(),
        "",
        "## Tailoring Rules",
        "",
        f"Default tailoring mode: {g.default_mode}. This choice must explain why it is not heavier or lighter and must keep escalation triggers visible.",
        "",
        tailoring_table(False).rstrip(),
        "",
        "### Why this mode is not heavier or lighter",
        "",
        f"`{g.source_name}` uses the default mode because the {g.family.lower()} family needs governed evidence, "
        "but a heavier mode is reserved for external commitment, sensitive information, shared state, or difficult recovery.",
        "",
        "### Escalation triggers",
        "",
        escalation,
        "",
        "## Inputs",
        "",
        input_text,
        "",
        "## Tools And Techniques",
        "",
        tool_text,
        "",
        "## Outputs",
        "",
        output_text,
        "",
        "## Process Group Operating Table",
        "",
        process_table(g, False).rstrip(),
        "",
        "## Closeout And Registry",
        "",
        f"- Registry `doc_id` remains unique: `{g.doc_id}`.\n"
        f"- English primary `{g.rel_path}` and zh-CN companion `{g.zh_path}` stay paired.\n"
        "- Closeout confirms owner, tailoring mode, escalation triggers, output evidence, and next-cycle input.",
        "",
    ]
    return "\n".join(parts)


def expected_files(package: str = "all") -> dict[str, str]:
    files: dict[str, str] = {}
    for doc in selected_docs(package):
        files[doc.rel_path] = render_doc(doc, False)
        files[doc.zh_path] = render_doc(doc, True)
    return files


def registry_entries_for_generated_docs(package: str = "all") -> list[dict[str, str]]:
    return [
        {
            "doc_id": doc.doc_id,
            "doc_class": doc.doc_class,
            "status": "active",
            "canonical_path": doc.rel_path,
            "zh_cn_path": doc.zh_path,
        }
        for doc in selected_docs(package)
    ]


def parse_registry(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- doc_id:"):
            if current:
                entries.append(current)
            current = {"doc_id": stripped.split(":", 1)[1].strip()}
        elif current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def render_registry_entry(entry: dict[str, str]) -> list[str]:
    return [
        f"  - doc_id: {entry['doc_id']}",
        f"    doc_class: {entry['doc_class']}",
        f"    status: {entry['status']}",
        f"    canonical_path: {entry['canonical_path']}",
        f"    zh_cn_path: {entry['zh_cn_path']}",
    ]


def update_registry(root: Path, package: str) -> list[str]:
    path = root / "docs_bilingual" / "docs_registry.yaml"
    entries = parse_registry(path)
    generated = registry_entries_for_generated_docs(package)
    generated_ids = {entry["doc_id"] for entry in generated}
    stale_ids = set(stale_legacy_doc_ids(package))
    stale_paths = set(stale_legacy_files(package))
    updated = [
        entry
        for entry in entries
        if entry.get("doc_id") not in generated_ids
        and entry.get("doc_id") not in stale_ids
        and entry.get("canonical_path") not in stale_paths
        and entry.get("zh_cn_path") not in stale_paths
    ] + generated
    lines = ["version: 1", "documents:"]
    for entry in updated:
        lines.append("")
        lines.extend(render_registry_entry(entry))
    text = "\n".join(lines) + "\n"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return ["docs_bilingual/docs_registry.yaml"]
    return []


def write_expected(root: Path, package: str) -> list[str]:
    changed: list[str] = []
    for rel, content in expected_files(package).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != content:
            path.write_text(content, encoding="utf-8", newline="\n")
            changed.append(rel)
    for rel in stale_legacy_files(package):
        path = root / rel
        if path.exists():
            path.unlink()
            changed.append(rel)
    changed.extend(update_registry(root, package))
    return sorted(dict.fromkeys(changed))


def check_expected(root: Path, package: str) -> tuple[list[str], list[str]]:
    out_of_date: list[str] = []
    matched: list[str] = []
    for rel, content in expected_files(package).items():
        path = root / rel
        try:
            actual = path.read_text(encoding="utf-8") if path.exists() else None
        except UnicodeDecodeError:
            actual = None
        if actual == content:
            matched.append(rel)
        else:
            out_of_date.append(rel)
    for rel in stale_legacy_files(package):
        if (root / rel).exists():
            out_of_date.append(rel)
    registry_entries = parse_registry(root / "docs_bilingual" / "docs_registry.yaml")
    by_doc_id = {entry.get("doc_id", ""): entry for entry in registry_entries}
    stale_ids = set(stale_legacy_doc_ids(package))
    stale_paths = set(stale_legacy_files(package))
    if any(
        entry.get("doc_id") in stale_ids
        or entry.get("canonical_path") in stale_paths
        or entry.get("zh_cn_path") in stale_paths
        for entry in registry_entries
    ):
        out_of_date.append("docs_bilingual/docs_registry.yaml")
    for entry in registry_entries_for_generated_docs(package):
        actual = by_doc_id.get(entry["doc_id"])
        if actual is None or any(actual.get(key) != value for key, value in entry.items()):
            out_of_date.append("docs_bilingual/docs_registry.yaml")
            break
    return sorted(dict.fromkeys(out_of_date)), matched


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate governed bilingual operations-package body Markdown documents.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--package", choices=["codex", "one-person-company", "all"], default="all", help="Package to generate or check.")
    parser.add_argument("--check", action="store_true", help="Check whether generated files and registry entries are current without writing them.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.check:
        out_of_date, matched = check_expected(root, args.package)
        payload = {
            "schema_version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "check_name": CHECK_NAME,
            "ok": not out_of_date,
            "root": str(root),
            "package": args.package,
            "mode": "check",
            "changed_or_missing": out_of_date,
            "counts": {
                "expected_pairs": len(selected_docs(args.package)),
                "expected_files": len(expected_files(args.package)),
                "matched_files": len(matched),
                "changed_or_missing": len(out_of_date),
            },
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'out-of-date'}")
            for rel in out_of_date:
                print(f"OUT_OF_DATE: {rel}")
        return 0 if payload["ok"] else 1

    changed = write_expected(root, args.package)
    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": True,
        "root": str(root),
        "package": args.package,
        "mode": "write",
        "changed_files": changed,
        "counts": {
            "expected_pairs": len(selected_docs(args.package)),
            "expected_files": len(expected_files(args.package)),
            "changed_files": len(changed),
        },
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: wrote {len(changed)} changed files")
        for rel in changed:
            print(f"CHANGED: {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
