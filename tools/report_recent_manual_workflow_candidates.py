#!/usr/bin/env python3
"""Report recent repeated manual workflow packaging candidates.

The report is conservative: it reads committed repository evidence, redacts
private/user-level paths, treats Chronicle as discovery-only, and emits
project-level assets plus user-level candidates without installing anything.
The Python source is ASCII-only so Windows shells cannot corrupt Chinese labels;
Chinese output strings use Unicode escapes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


GENERATED_BY = "tools/report_recent_manual_workflow_candidates.py"
DEFAULT_DAYS = 30
MAX_EVIDENCE = 6
MOJIBAKE_MARKERS = (
    "\u951b", "\u7039", "\u93c2", "\u935a", "\u5ee3", "\u7211", "\ufffd", "\u20ac",
    "\u9411", "\u6d93", "\u9e93", "\u9365", "\u93ac", "\u93c8", "\u95c6",
)


@dataclass(frozen=True)
class Evidence:
    source: str
    date: str
    summary: str
    ref: str


WORKFLOW_RULES: list[dict[str, Any]] = [
    {
        "id": "local-main-first-governance-packaging",
        "title": "Plan -> local gate/MR review -> local main integration packaging",
        "title_zh": "\u65b9\u6848 -> \u672c\u5730\u95e8\u7981/MR review -> \u672c\u5730 main \u5408\u5165\u6253\u5305",
        "keywords": ["plan", "local", "merge", "gate", "main", "commit", "workflow", "\u65b9\u6848", "\u8ba1\u5212", "\u5408\u5165", "\u95e8\u7981"],
        "recommended_form": "extend-existing/project-level-skill",
        "frequency_hint": "high",
        "why": "The repository repeatedly freezes plans, validates them, commits, merges to local main, and stops at the remote-publication gate. Existing helpers cover the merge mechanics, but a narrow packaging skill/CLI makes the discovery and decision step repeatable.",
        "why_zh": "\u672c\u4ed3\u5e93\u53cd\u590d\u6267\u884c\u65b9\u6848\u51bb\u7ed3\u3001\u672c\u5730\u9a8c\u8bc1\u3001\u63d0\u4ea4\u3001\u5408\u5165 local main\u3001\u505c\u5728\u8fdc\u7aef\u53d1\u5e03\u95e8\u7981\u7684\u6d41\u7a0b\u3002\u73b0\u6709 helper \u5df2\u8986\u76d6\u5408\u5165\u673a\u68b0\u52a8\u4f5c\uff0c\u4f46\u4ecd\u9700\u8981\u7a84\u8303\u56f4 skill/CLI \u56fa\u5316\u53d1\u73b0\u4e0e\u51b3\u7b56\u6b65\u9aa4\u3002",
        "worth": True,
    },
    {
        "id": "r5-r6-live-runtime-evidence-gates",
        "title": "R5/R6 live runtime evidence receipt gates",
        "title_zh": "R5/R6 \u771f\u5b9e\u8fd0\u884c\u65f6\u8bc1\u636e\u6536\u636e\u95e8\u7981",
        "keywords": ["R5", "R6", "live", "runtime", "receipt", "smoke", "\u771f\u5b9e", "\u8bc1\u636e", "\u95e8\u7981"],
        "recommended_form": "extend-existing/skip-duplicate",
        "frequency_hint": "high",
        "why": "Repeated R5/R6 work is already covered by checker-backed runtime and receipt gates, so the packaging action is to reuse and extend existing gates rather than create a new broad asset.",
        "why_zh": "R5/R6 \u5de5\u4f5c\u5df2\u7531 checker-backed runtime \u4e0e receipt \u95e8\u7981\u8986\u76d6\uff1b\u672c\u8f6e\u53ea\u5e94\u590d\u7528/\u6269\u5c55\u65e2\u6709\u95e8\u7981\uff0c\u907f\u514d\u518d\u5efa\u5bbd\u6cdb\u91cd\u590d\u8d44\u4ea7\u3002",
        "worth": False,
    },
    {
        "id": "skills-usage-audit-cadence",
        "title": "Codex skills usage audit and warning-triage cadence",
        "title_zh": "Codex skills \u4f7f\u7528\u5ba1\u8ba1\u4e0e warning triage \u8282\u594f",
        "keywords": ["Skills", "skills", "audit", "warning", "triage", "weekly", "profile", "\u5ba1\u8ba1"],
        "recommended_form": "extend-existing",
        "frequency_hint": "medium",
        "why": "Weekly summaries and triage files show recurrence, but the repository already has dedicated audit scripts and memory outputs. Keep using those and feed their sanitized signals into this report.",
        "why_zh": "\u5468\u62a5\u548c triage \u6587\u4ef6\u8bf4\u660e\u8be5\u6d41\u7a0b\u91cd\u590d\u51fa\u73b0\uff0c\u4f46\u4ed3\u5e93\u5df2\u6709\u4e13\u7528\u5ba1\u8ba1\u811a\u672c\u548c memory \u8f93\u51fa\u3002\u672c\u8f6e\u5e94\u7ee7\u7eed\u590d\u7528\uff0c\u5e76\u628a\u8131\u654f\u4fe1\u53f7\u63a5\u5165\u672c\u62a5\u544a\u3002",
        "worth": False,
    },
    {
        "id": "gui-browser-wxwork-live-actions",
        "title": "GUI/browser/WXWork live-action governance",
        "title_zh": "GUI/\u6d4f\u89c8\u5668/\u4f01\u4e1a\u5fae\u4fe1\u771f\u5b9e\u52a8\u4f5c\u6cbb\u7406",
        "keywords": ["GUI", "WXWork", "browser", "CLI-Anything", "CloakBrowser", "visual", "\u4f01\u4e1a\u5fae\u4fe1", "\u6d4f\u89c8\u5668", "\u89c6\u89c9"],
        "recommended_form": "needs-more-evidence/separate-plan",
        "frequency_hint": "medium",
        "why": "The work recurs and is costly, but it includes sensitive external live actions. Keep it out of this generic packager and require separate explicit authorization, rollback, smoke, and privacy evidence.",
        "why_zh": "\u8be5\u7c7b\u5de5\u4f5c\u91cd\u590d\u4e14\u6210\u672c\u9ad8\uff0c\u4f46\u6d89\u53ca\u654f\u611f\u5916\u90e8\u771f\u5b9e\u52a8\u4f5c\u3002\u4e0d\u80fd\u7eb3\u5165\u901a\u7528\u6253\u5305\u5668\uff1b\u9700\u8981\u5355\u72ec\u65b9\u6848\u3001\u6388\u6743\u3001rollback\u3001smoke \u4e0e\u9690\u79c1\u8bc1\u636e\u3002",
        "worth": False,
    },
    {
        "id": "general-template-cross-project-sync",
        "title": "General/General_2 template propagation for cross-project reuse",
        "title_zh": "General/General_2 \u6a21\u677f\u6269\u5c55\u4ee5\u652f\u6301\u8de8\u9879\u76ee\u590d\u7528",
        "keywords": ["General", "General_2", "template", "cross-project", "\u6a21\u677f", "\u901a\u7528\u6a21\u677f"],
        "recommended_form": "extend-existing/project-template",
        "frequency_hint": "medium",
        "why": "Template propagation recurs, but it is a project-template concern with existing plans and evidence. This report should list it as a recurring workflow, not mutate template folders.",
        "why_zh": "\u6a21\u677f\u6269\u5c55\u662f\u91cd\u590d\u6d41\u7a0b\uff0c\u4f46\u5c5e\u4e8e\u9879\u76ee\u6a21\u677f\u8fb9\u754c\u5e76\u5df2\u6709\u65b9\u6848/\u8bc1\u636e\uff1b\u672c\u62a5\u544a\u53ea\u5217\u4e3a\u5019\u9009\uff0c\u4e0d\u76f4\u63a5\u4fee\u6539\u6a21\u677f\u76ee\u5f55\u3002",
        "worth": False,
    },
    {
        "id": "recent-manual-workflow-packaging",
        "title": "Recent manual workflow packaging itself",
        "title_zh": "\u8fd1\u671f\u624b\u5de5\u5de5\u4f5c\u6d41\u6253\u5305\u6d41\u7a0b\u672c\u8eab",
        "keywords": ["workflow", "packaging", "manual", "shortlist", "\u6253\u5305", "\u624b\u5de5"],
        "recommended_form": "project-level-skill-and-manual-cli",
        "frequency_hint": "new-but-likely-recurring",
        "why": "The prompt is a reusable meta-workflow with stable evidence order and stopping conditions. The high-confidence missing asset is this project-level skill plus manual CLI.",
        "why_zh": "\u8be5\u63d0\u793a\u662f\u53ef\u590d\u7528\u5143\u5de5\u4f5c\u6d41\uff0c\u8bc1\u636e\u987a\u5e8f\u4e0e\u505c\u6b62\u6761\u4ef6\u7a33\u5b9a\uff1b\u9ad8\u7f6e\u4fe1\u7f3a\u53e3\u8d44\u4ea7\u5c31\u662f\u9879\u76ee\u7ea7 skill \u52a0\u624b\u52a8 CLI\u3002",
        "worth": True,
    },
]

USER_LEVEL_CANDIDATE = {
    "id": "extend-user-level-wrapper",
    "title": "Thin user-level wrapper/config for the project CLI",
    "title_zh": "\u9879\u76ee CLI \u7684\u8584\u7528\u6237\u7ea7 wrapper/config",
    "recommended_form": "user-level-candidate-only",
    "why": "Promote only after the project CLI is stable across two or more projects and has rollback plus smoke evidence. No user-level install is performed by this run.",
    "why_zh": "\u53ea\u6709\u5f53\u9879\u76ee CLI \u5728\u4e24\u4e2a\u4ee5\u4e0a\u9879\u76ee\u7a33\u5b9a\u590d\u7528\u5e76\u5177\u5907 rollback/smoke \u8bc1\u636e\u540e\u624d\u63d0\u5347\uff1b\u672c\u8f6e\u4e0d\u6267\u884c\u7528\u6237\u7ea7\u5b89\u88c5\u3002",
}

DELIBERATE_SKIPS = [
    {
        "id": "custom-subagent-for-packaging",
        "title": "Custom subagent for workflow packaging",
        "title_zh": "\u4e3a\u5de5\u4f5c\u6d41\u6253\u5305\u521b\u5efa custom subagent",
        "reason": "Existing analyst/planner/writer/verifier roles already cover bounded investigation and write-up needs.",
        "reason_zh": "\u73b0\u6709 analyst/planner/writer/verifier \u5df2\u8986\u76d6\u6709\u754c\u8c03\u67e5\u4e0e\u6210\u6587\u9700\u6c42\u3002",
    },
    {
        "id": "scheduled-packaging-audit",
        "title": "Scheduled packaging audit",
        "title_zh": "\u5b9a\u65f6\u5de5\u4f5c\u6d41\u6253\u5305\u5ba1\u8ba1",
        "reason": "Scheduling expands the automation and approval surface; keep this as a manual CLI until a separate scheduled-automation plan exists.",
        "reason_zh": "\u5b9a\u65f6\u6267\u884c\u4f1a\u6269\u5927\u81ea\u52a8\u5316\u4e0e\u6388\u6743\u9762\uff1b\u5728\u5355\u72ec\u5b9a\u65f6\u81ea\u52a8\u5316\u65b9\u6848\u51fa\u73b0\u524d\u4fdd\u6301\u4e3a\u624b\u52a8 CLI\u3002",
    },
    {
        "id": "chronicle-write-integration",
        "title": "Chronicle write or mutation integration",
        "title_zh": "Chronicle \u5199\u5165\u6216\u53d8\u66f4\u96c6\u6210",
        "reason": "Chronicle is discovery-only here. The report records not_enabled or discovery signals but never writes external state.",
        "reason_zh": "Chronicle \u5728\u6b64\u4ec5\u7528\u4e8e\u53d1\u73b0\uff1b\u62a5\u544a\u53ea\u8bb0\u5f55 not_enabled \u6216\u53d1\u73b0\u4fe1\u53f7\uff0c\u4e0d\u5199\u5165\u5916\u90e8\u72b6\u6001\u3002",
    },
    {
        "id": "external-live-action-automation",
        "title": "External live-action automation",
        "title_zh": "\u5916\u90e8\u771f\u5b9e\u52a8\u4f5c\u81ea\u52a8\u5316",
        "reason": "Browser, GUI, WXWork, and similar live actions are sensitive and require their own explicit authorization and receipts.",
        "reason_zh": "\u6d4f\u89c8\u5668\u3001GUI\u3001\u4f01\u4e1a\u5fae\u4fe1\u7b49\u771f\u5b9e\u52a8\u4f5c\u654f\u611f\uff0c\u5fc5\u987b\u6709\u72ec\u7acb\u6388\u6743\u4e0e\u6536\u636e\u3002",
    },
]

BROAD_CATEGORY_RULES: list[dict[str, Any]] = [
    {
        "id": "coding",
        "title": "Coding and implementation",
        "title_zh": "\u7f16\u7801\u4e0e\u5b9e\u73b0",
        "keywords": ["code", "coding", "implementation", "runtime", "fix", "feature", "test", "CLI", "GUI", "\u5b9e\u73b0", "\u4fee\u590d", "\u529f\u80fd", "\u6d4b\u8bd5", "\u8fd0\u884c\u65f6"],
        "candidate_ids": ["r5-r6-live-runtime-evidence-gates", "gui-browser-wxwork-live-actions", "recent-manual-workflow-packaging"],
        "decision": "covered_by_shortlist",
        "why": "Recent implementation work is represented by runtime/receipt gates, GUI/browser governance, and the packager implementation itself.",
        "why_zh": "\u8fd1\u671f\u5b9e\u73b0\u5de5\u4f5c\u5df2\u7531 runtime/receipt \u95e8\u7981\u3001GUI/\u6d4f\u89c8\u5668\u6cbb\u7406\u4ee5\u53ca\u6253\u5305\u5668\u672c\u8eab\u8986\u76d6\u3002",
    },
    {
        "id": "research",
        "title": "Research and source discovery",
        "title_zh": "\u7814\u7a76\u4e0e\u6765\u6e90\u53d1\u73b0",
        "keywords": ["research", "academic", "source", "whitepaper", "PMI", "CloakBrowser", "\u7814\u7a76", "\u5b66\u672f", "\u6765\u6e90", "\u767d\u76ae\u4e66"],
        "candidate_ids": ["gui-browser-wxwork-live-actions"],
        "decision": "separate_plan_required",
        "why": "Research tooling appears in recent work, but browser/live-action pieces remain sensitive and are not packaged by this generic workflow.",
        "why_zh": "\u8fd1\u671f\u5de5\u4f5c\u51fa\u73b0\u7814\u7a76\u5de5\u5177\uff0c\u4f46\u6d4f\u89c8\u5668/\u771f\u5b9e\u52a8\u4f5c\u4ecd\u5c5e\u654f\u611f\u8fb9\u754c\uff0c\u4e0d\u7531\u672c\u901a\u7528\u5de5\u4f5c\u6d41\u6253\u5305\u3002",
    },
    {
        "id": "writing",
        "title": "Writing and documentation",
        "title_zh": "\u5199\u4f5c\u4e0e\u6587\u6863",
        "keywords": ["doc", "docs", "document", "summary", "write", "writing", "plan", "\u6587\u6863", "\u65b9\u6848", "\u6458\u8981", "\u5199\u4f5c", "\u8bb0\u5f55"],
        "candidate_ids": ["local-main-first-governance-packaging", "recent-manual-workflow-packaging"],
        "decision": "covered_by_shortlist",
        "why": "Documentation and planning write-ups recur heavily and are covered by the project-level skill/CLI plus local-main-first packaging candidate.",
        "why_zh": "\u6587\u6863\u4e0e\u65b9\u6848\u5199\u4f5c\u9ad8\u9891\u51fa\u73b0\uff0c\u7531\u9879\u76ee\u7ea7 skill/CLI \u548c local-main-first \u6253\u5305\u5019\u9009\u8986\u76d6\u3002",
    },
    {
        "id": "planning",
        "title": "Planning and roadmap control",
        "title_zh": "\u8ba1\u5212\u4e0e\u8def\u7ebf\u63a7\u5236",
        "keywords": ["plan", "roadmap", "backlog", "proposal", "freeze", "\u65b9\u6848", "\u8ba1\u5212", "\u8def\u7ebf", "\u89c4\u5212", "\u6536\u53e3"],
        "candidate_ids": ["local-main-first-governance-packaging", "recent-manual-workflow-packaging"],
        "decision": "covered_by_shortlist",
        "why": "Plan-first local integration is one of the strongest repeated workflows in the evidence window.",
        "why_zh": "\u8bc1\u636e\u7a97\u53e3\u4e2d\u6700\u5f3a\u7684\u91cd\u590d\u6d41\u7a0b\u4e4b\u4e00\u5c31\u662f\u5148\u65b9\u6848\u540e\u672c\u5730\u5408\u5165\u3002",
    },
    {
        "id": "communication",
        "title": "Communication and messaging",
        "title_zh": "\u6c9f\u901a\u4e0e\u6d88\u606f",
        "keywords": ["WXWork", "WeCom", "message", "communication", "wechat", "\u4f01\u4e1a\u5fae\u4fe1", "\u5fae\u4fe1", "\u7fa4\u804a", "\u6d88\u606f", "\u6c9f\u901a"],
        "candidate_ids": ["gui-browser-wxwork-live-actions"],
        "decision": "separate_plan_required",
        "why": "Messaging work is detected, but it involves external live actions and therefore remains out of scope for this generic packager.",
        "why_zh": "\u5df2\u68c0\u6d4b\u5230\u6d88\u606f\u6c9f\u901a\u5de5\u4f5c\uff0c\u4f46\u5b83\u6d89\u53ca\u5916\u90e8\u771f\u5b9e\u52a8\u4f5c\uff0c\u56e0\u6b64\u4e0d\u7eb3\u5165\u672c\u901a\u7528\u6253\u5305\u5668\u3002",
    },
    {
        "id": "operations",
        "title": "Operations, gates, installs, and releases",
        "title_zh": "\u8fd0\u7ef4\u3001\u95e8\u7981\u3001\u5b89\u88c5\u4e0e\u53d1\u5e03",
        "keywords": ["gate", "CI", "merge", "main", "smoke", "receipt", "install", "release", "runtime", "\u95e8\u7981", "\u5408\u5165", "\u5b89\u88c5", "\u53d1\u5e03", "\u8fd0\u884c\u65f6"],
        "candidate_ids": ["local-main-first-governance-packaging", "r5-r6-live-runtime-evidence-gates", "general-template-cross-project-sync"],
        "decision": "covered_by_shortlist",
        "why": "Operational gates and release discipline recur frequently and map to existing helpers plus shortlist extensions.",
        "why_zh": "\u8fd0\u7ef4\u95e8\u7981\u4e0e\u53d1\u5e03\u7eaa\u5f8b\u9ad8\u9891\u91cd\u590d\uff0c\u5df2\u6620\u5c04\u5230\u65e2\u6709 helper \u548c\u77ed\u540d\u5355\u6269\u5c55\u3002",
    },
    {
        "id": "analysis",
        "title": "Analysis, audit, and triage",
        "title_zh": "\u5206\u6790\u3001\u5ba1\u8ba1\u4e0e triage",
        "keywords": ["analysis", "audit", "triage", "review", "evidence", "verify", "\u5206\u6790", "\u5ba1\u8ba1", "\u8bc1\u636e", "\u9a8c\u8bc1", "\u590d\u6838"],
        "candidate_ids": ["skills-usage-audit-cadence", "r5-r6-live-runtime-evidence-gates"],
        "decision": "covered_by_existing_assets",
        "why": "Audit/triage recurrence is strong, but existing checker-backed assets are adequate, so the packaging decision is extend/skip duplicate.",
        "why_zh": "\u5ba1\u8ba1/triage \u91cd\u590d\u6027\u5f3a\uff0c\u4f46\u65e2\u6709 checker-backed \u8d44\u4ea7\u5df2\u8db3\u591f\uff0c\u56e0\u6b64\u5c01\u88c5\u51b3\u7b56\u662f\u6269\u5c55/\u8df3\u8fc7\u91cd\u590d\u9879\u3002",
    },
    {
        "id": "personal-administration",
        "title": "Personal administration",
        "title_zh": "\u4e2a\u4eba\u884c\u653f\u4e8b\u52a1",
        "keywords": ["personal", "admin", "gmail", "calendar", "notion", "reminder", "schedule", "\u4e2a\u4eba", "\u884c\u653f", "\u65e5\u7a0b", "\u63d0\u9192"],
        "candidate_ids": [],
        "decision": "scanned_no_packaging_candidate",
        "why": "No strong committed recent-work evidence in this repository supports packaging a personal-administration workflow.",
        "why_zh": "\u672c\u4ed3\u5e93\u8fd1\u671f\u5df2\u63d0\u4ea4\u8bc1\u636e\u4e2d\u6ca1\u6709\u8db3\u4ee5\u5c01\u88c5\u4e2a\u4eba\u884c\u653f\u6d41\u7a0b\u7684\u5f3a\u8bc1\u636e\u3002",
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout if result.returncode == 0 else ""


def suspicious_text(text: str) -> bool:
    if not text:
        return False
    if "?" * 4 in text or "\ufffd" in text:
        return True
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        return True
    if text.count("?") >= 3 and re.search(r"[A-Za-z0-9]", text):
        return True
    return False


def redact_unreadable(text: str, ref: str = "") -> str:
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:10]
    ref_part = f":{ref}" if ref else ""
    return f"[REDACTED_UNREADABLE_TEXT:{digest}{ref_part}]"


def redact_non_ascii(text: str, ref: str = "") -> str:
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:10]
    ref_part = f":{ref}" if ref else ""
    return f"[REDACTED_NON_ASCII_TEXT:{digest}{ref_part}:chars={len(text)}]"


def ascii_safe_text(value: Any, *, ref: str = "") -> str:
    text = str(value)
    if all(ord(ch) < 128 for ch in text):
        return text
    return redact_non_ascii(text, ref)


def sanitize_text(value: str, *, ref: str = "", limit: int = 220) -> str:
    text = value.replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(r"[A-Za-z]:[\\/][^\s`'\"]+", "[REDACTED_PATH]", text)
    text = re.sub(r"\\\\[^\s`'\"]+", "[REDACTED_PATH]", text)
    text = re.sub(r"(?i)(api[_-]?key|token|secret|cookie)=\S+", r"\1=[REDACTED_SECRET]", text)
    if suspicious_text(text):
        return redact_unreadable(text, ref)
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "..."
    return text


def parse_git_log(root: Path, days: int) -> list[Evidence]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    raw = run_git(root, ["log", f"--since={since}", "--date=short", "--pretty=format:%h%x09%ad%x09%s"])
    rows: list[Evidence] = []
    for line in raw.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        sha, date, subject = parts
        rows.append(Evidence(source="git", date=date, summary=sanitize_text(subject, ref=sha), ref=sha))
    return rows


def memory_evidence(root: Path, days: int) -> list[Evidence]:
    memory_root = root / "docs_bilingual" / "memory"
    if not memory_root.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows: list[Evidence] = []
    for path in sorted(memory_root.glob("*.md")):
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        ref = path.relative_to(root).as_posix()
        rows.append(Evidence(source="memory", date=mtime.date().isoformat(), summary=sanitize_text(path.stem, ref=ref), ref=ref))
    return rows


def skill_inventory(root: Path) -> dict[str, Any]:
    repo_skills = sorted((root / ".agents" / "skills").glob("*/SKILL.md"))
    repo_codex_skills = sorted((root / ".codex" / "skills").glob("*/SKILL.md")) if (root / ".codex" / "skills").exists() else []
    user_home = Path(os.environ.get("USERPROFILE", str(Path.home())))
    user_skill_names: list[str] = []
    for base in (user_home / ".codex" / "skills", user_home / ".agents" / "skills"):
        if base.exists():
            user_skill_names.extend(sorted({sanitize_text(p.parent.name, ref="user-skill") for p in base.glob("*/SKILL.md")}))
    agent_tomls: list[str] = []
    for base in (root / ".codex" / "agents", user_home / ".codex" / "agents", user_home / ".agents"):
        if base.exists():
            agent_tomls.extend(sorted(sanitize_text(p.name, ref="agent-toml") for p in base.glob("*.toml")))
    tools = sorted(p.name for p in (root / "tools").glob("*.py")) if (root / "tools").exists() else []
    return {
        "repo_agent_skills": [p.parent.name for p in repo_skills],
        "repo_codex_skills": [p.parent.name for p in repo_codex_skills],
        "user_skill_names_redacted": sorted(set(user_skill_names)),
        "custom_agent_toml_names_redacted": sorted(set(agent_tomls)),
        "tool_names": tools,
        "counts": {
            "repo_agent_skills": len(repo_skills),
            "repo_codex_skills": len(repo_codex_skills),
            "user_skills": len(set(user_skill_names)),
            "custom_agent_tomls": len(set(agent_tomls)),
            "repo_python_tools": len(tools),
        },
    }


def chronicle_status(root: Path) -> dict[str, Any]:
    command = shutil.which("chronicle")
    user_home = Path(os.environ.get("USERPROFILE", str(Path.home())))
    candidates = [user_home / ".chronicle", user_home / "AppData" / "Roaming" / "Chronicle", root / ".chronicle"]
    existing = ["[REDACTED_USER_CHRONICLE]" if not str(p).startswith(str(root)) else p.relative_to(root).as_posix() for p in candidates if p.exists()]
    if command or existing:
        return {"status": "available_for_discovery_only", "command_available": bool(command), "data_locations_detected": existing, "mutation_allowed": False}
    return {"status": "not_enabled", "command_available": False, "data_locations_detected": [], "mutation_allowed": False}


def match_evidence(rule: dict[str, Any], evidence: Iterable[Evidence]) -> list[Evidence]:
    keywords = [str(k).lower() for k in rule["keywords"]]
    matches: list[Evidence] = []
    for item in evidence:
        haystack = f"{item.summary} {item.ref}".lower()
        if any(k in haystack for k in keywords):
            matches.append(item)
    return matches


def summarize_frequency(matches: list[Evidence], hint: str) -> tuple[str, str]:
    count = len(matches)
    if count >= 8 or hint == "high":
        return f"{count} evidence hits in the lookback window", "high"
    if count >= 3 or hint == "medium":
        return f"{count} evidence hits in the lookback window", "medium"
    if count >= 2:
        return f"{count} evidence hits in the lookback window", "medium"
    if hint == "new-but-likely-recurring":
        return "new request with stable recurring procedure", "medium"
    return f"{count} evidence hits in the lookback window", "low"


def build_broad_category_scan(evidence: list[Evidence], shortlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    shortlist_ids = {str(row["id"]) for row in shortlist}
    rows: list[dict[str, Any]] = []
    for rule in BROAD_CATEGORY_RULES:
        matches = match_evidence(rule, evidence)
        candidate_ids = [cid for cid in rule["candidate_ids"] if cid in shortlist_ids]
        rows.append(
            {
                "id": rule["id"],
                "category": rule["title"],
                "category_zh": rule["title_zh"],
                "evidence_count": len(matches),
                "supporting_evidence": [item.__dict__ for item in matches[:MAX_EVIDENCE]],
                "mapped_shortlist_ids": candidate_ids,
                "decision": rule["decision"],
                "why": rule["why"],
                "why_zh": rule["why_zh"],
            }
        )
    return rows


def build_report(root: Path, days: int) -> dict[str, Any]:
    all_evidence = parse_git_log(root, days) + memory_evidence(root, days)
    inventory = skill_inventory(root)
    shortlist: list[dict[str, Any]] = []
    for rule in WORKFLOW_RULES:
        matches = match_evidence(rule, all_evidence)
        frequency, confidence = summarize_frequency(matches, str(rule["frequency_hint"]))
        shortlist.append(
            {
                "id": rule["id"],
                "repeated_workflow": rule["title"],
                "repeated_workflow_zh": rule["title_zh"],
                "supporting_evidence": [item.__dict__ for item in matches[:MAX_EVIDENCE]],
                "supporting_evidence_count": len(matches),
                "frequency": frequency,
                "confidence": confidence,
                "recommended_form": rule["recommended_form"],
                "why": rule["why"],
                "why_zh": rule["why_zh"],
                "actionable_now": bool(rule["worth"]),
            }
        )

    broad_category_scan = build_broad_category_scan(all_evidence, shortlist)
    created_or_extended = []
    if (root / ".agents" / "skills" / "recent-workflow-packaging" / "SKILL.md").exists():
        created_or_extended.append({"id": "repo-local-recent-workflow-packaging-skill", "form": "project-level skill", "path": ".agents/skills/recent-workflow-packaging/SKILL.md", "status": "present"})
    if (root / "tools" / "report_recent_manual_workflow_candidates.py").exists():
        created_or_extended.append({"id": "recent-workflow-packaging-cli", "form": "project-level manual CLI", "path": "tools/report_recent_manual_workflow_candidates.py", "status": "present"})

    existing_coverage = {
        "repo_agent_skills": inventory["repo_agent_skills"],
        "repo_codex_skills": inventory["repo_codex_skills"],
        "user_skill_names_redacted_sample": inventory["user_skill_names_redacted"][:40],
        "custom_agent_toml_names_redacted_sample": inventory["custom_agent_toml_names_redacted"][:40],
        "relevant_repo_tools": [name for name in inventory["tool_names"] if any(token in name.lower() for token in ["skill", "workflow", "gate", "openspec", "claim", "receipt", "audit"])][:80],
        "counts": inventory["counts"],
    }
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "generated_by": GENERATED_BY,
        "root": "<repo>",
        "lookback_days": days,
        "evidence_order": [
            "recent_codex_sessions_and_task_summaries_via_git_and_committed_summaries",
            "codex_memories_and_rollout_summaries",
            "chronicle_discovery_only",
            "existing_skills_custom_agents_and_automations",
        ],
        "chronicle": chronicle_status(root),
        "existing_coverage": existing_coverage,
        "broad_category_scan": broad_category_scan,
        "shortlist": shortlist,
        "created_or_extended": created_or_extended,
        "user_level_candidates": [USER_LEVEL_CANDIDATE],
        "deliberately_skipped": DELIBERATE_SKIPS,
        "needs_more_evidence": [
            USER_LEVEL_CANDIDATE,
            {
                "id": "external-action-packagers",
                "title": "Generic browser/GUI/WXWork live-action packagers",
                "title_zh": "\u901a\u7528\u6d4f\u89c8\u5668/GUI/\u4f01\u4e1a\u5fae\u4fe1\u771f\u5b9e\u52a8\u4f5c\u6253\u5305\u5668",
                "recommended_form": "separate-plan-required",
                "why": "Needs per-system authorization, rollback, privacy review, and live smoke evidence before packaging.",
                "why_zh": "\u6253\u5305\u524d\u9700\u8981\u6309\u7cfb\u7edf\u5355\u72ec\u6388\u6743\u3001rollback\u3001\u9690\u79c1\u5ba1\u67e5\u4e0e\u771f\u5b9e smoke \u8bc1\u636e\u3002",
            },
        ],
        "safety": {
            "raw_sessions_read": False,
            "raw_runtime_logs_read": False,
            "chronicle_mutated": False,
            "user_level_config_mutated": False,
            "scheduler_created": False,
            "external_actions_performed": False,
            "path_redaction": "repo-relative paths only; user-level paths reduced to names/counts; unreadable legacy text is hashed",
        },
    }


def evidence_bullets(items: list[dict[str, Any]], lang: str) -> str:
    if not items:
        return "  - none recorded in this sanitized window" if lang == "en" else "  - \u672c\u8131\u654f\u7a97\u53e3\u5185\u672a\u8bb0\u5f55"
    lines: list[str] = []
    for item in items:
        ref = str(item.get("ref", ""))
        if lang == "en":
            date = ascii_safe_text(item.get("date", "n/a"), ref=ref)
            source = ascii_safe_text(item.get("source", "n/a"), ref=ref)
            summary = ascii_safe_text(item.get("summary", ""), ref=ref)
            safe_ref = ascii_safe_text(ref, ref=ref)
        else:
            date = str(item.get("date", "n/a"))
            source = str(item.get("source", "n/a"))
            summary = str(item.get("summary", ""))
            safe_ref = ref
        lines.append(f"  - {date} [{source}] {summary} ({safe_ref})")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any], lang: str) -> str:
    zh = lang.lower().startswith("zh")
    title = "\u8fd1\u671f\u91cd\u590d\u624b\u5de5\u5de5\u4f5c\u6d41\u6253\u5305\u77ed\u540d\u5355" if zh else "Recent Manual Workflow Packaging Shortlist"
    lines: list[str] = [
        "---",
        "doc_id: recent_manual_workflow_packaging_shortlist_2026_06_13",
        f"lang: {'zh-CN' if zh else 'en'}",
        "status: active",
        "doc_class: memory",
    ]
    lines.append("translation_of: docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md" if zh else "zh_cn_path: docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md")
    lines.extend(["---", "", f"# {title}", ""])
    if zh:
        lines.extend([
            f"\u751f\u6210\u65f6\u95f4\uff1a`{report['generated_at']}`",
            f"\u56de\u770b\u7a97\u53e3\uff1a`{report['lookback_days']}` \u5929",
            f"Chronicle\uff1a`{report['chronicle']['status']}`\uff08\u4ec5\u53d1\u73b0\uff0c\u4e0d\u5199\u5165\uff09",
            "",
            "## \u5c01\u88c5\u5224\u65ad",
            "",
            "- \u9879\u76ee\u7ea7\uff1a\u672c\u8f6e\u5df2\u5b9e\u73b0\u3002\u539f\u56e0\uff1a\u8f93\u5165\u4f9d\u8d56\u672c\u4ed3\u5e93 Git\u3001memory\u3001implementation plans \u4e0e\u672c\u5730\u95e8\u7981\uff0c\u672c\u4ed3\u5e93\u662f source of truth\u3002",
            "- \u7528\u6237\u7ea7\uff1a\u53ea\u8bb0\u5f55\u5019\u9009\uff0c\u4e0d\u5b89\u88c5\u3002\u6761\u4ef6\uff1a\u8de8\u4e24\u4e2a\u4ee5\u4e0a\u9879\u76ee\u590d\u7528\u3001\u8f93\u51fa\u8131\u654f\u3001\u5177\u5907 rollback/smoke \u8bc1\u636e\u5e76\u6709\u5355\u72ec\u6388\u6743\u3002",
            "- \u4e0d\u5c01\u88c5\uff1acustom subagent\u3001scheduler\u3001Chronicle \u5199\u5165\u3001\u5916\u90e8\u771f\u5b9e\u52a8\u4f5c\uff1b\u539f\u56e0\u662f\u5df2\u6709\u89d2\u8272\u8986\u76d6\u6216\u6743\u9650/\u9690\u79c1\u9762\u8fc7\u5927\u3002",
            "",
            "## \u5e7f\u6cdb\u7c7b\u522b\u626b\u63cf",
            "",
            "\u4ee5\u4e0b\u7c7b\u522b\u5bf9\u5e94 `reference_files/5.md` \u8981\u6c42\u7684 coding/research/writing/planning/communication/operations/analysis/personal administration \u5e7f\u6cdb\u56de\u770b\u8303\u56f4\u3002",
            "",
        ])
        for row in report["broad_category_scan"]:
            mapped = ", ".join(f"`{item}`" for item in row["mapped_shortlist_ids"]) or "\u65e0"
            lines.append(f"- **{row['category_zh']}** (`{row['id']}`): decision=`{row['decision']}`, evidence_count=`{row['evidence_count']}`, mapped={mapped}. {row['why_zh']}")
        lines.extend([
            "",
            "## \u77ed\u540d\u5355",
        ])
    else:
        lines.extend([
            f"Generated at: `{report['generated_at']}`",
            f"Lookback window: `{report['lookback_days']}` days",
            f"Chronicle: `{report['chronicle']['status']}` (discovery only; no writes)",
            "",
            "## Packaging Decision",
            "",
            "- Project-level: implemented in this run because inputs depend on this repository's Git history, memory, implementation plans, and local gates.",
            "- User-level: candidate only; install requires cross-project proof, redaction, rollback, smoke evidence, and separate authorization.",
            "- Do not package: custom subagent, scheduler, Chronicle writes, and external live actions are skipped because existing roles cover them or the privilege/privacy surface is too large.",
            "",
            "## Broad Category Scan",
            "",
            "These categories correspond to the broad review scope requested by `reference_files/5.md`: coding, research, writing, planning, communication, operations, analysis, and personal administration.",
            "",
        ])
        for row in report["broad_category_scan"]:
            mapped = ", ".join(f"`{item}`" for item in row["mapped_shortlist_ids"]) or "none"
            lines.append(f"- **{row['category']}** (`{row['id']}`): decision=`{row['decision']}`, evidence_count=`{row['evidence_count']}`, mapped={mapped}. {row['why']}")
        lines.extend([
            "",
            "## Shortlist",
        ])
    for row in report["shortlist"]:
        row_title = row["repeated_workflow_zh"] if zh else row["repeated_workflow"]
        why = row["why_zh"] if zh else row["why"]
        lines.extend([
            "",
            f"### {row['id']}: {row_title}",
            "",
            f"- {'\u63a8\u8350\u5f62\u5f0f' if zh else 'Recommended form'}: `{row['recommended_form']}`",
            f"- {'\u9891\u7387/\u7f6e\u4fe1\u5ea6' if zh else 'Frequency/confidence'}: {row['frequency']} / `{row['confidence']}`",
            f"- {'\u672c\u8f6e\u53ef\u884c\u52a8' if zh else 'Actionable now'}: `{str(row['actionable_now']).lower()}`",
            f"- {'\u7406\u7531' if zh else 'Why'}: {why}",
            f"- {'\u652f\u6301\u8bc1\u636e' if zh else 'Supporting evidence'}:",
            evidence_bullets(row["supporting_evidence"], "zh" if zh else "en"),
        ])
    lines.extend(["", "## " + ("\u5df2\u521b\u5efa\u6216\u6269\u5c55" if zh else "Created Or Extended"), ""])
    for row in report["created_or_extended"] or []:
        lines.append(f"- `{row['id']}` - {row['form']} - `{row['path']}` - `{row['status']}`")
    if not report["created_or_extended"]:
        lines.append("- none detected yet" if not zh else "- \u5c1a\u672a\u68c0\u6d4b\u5230")
    lines.extend(["", "## " + ("\u7528\u6237\u7ea7\u5019\u9009" if zh else "User-Level Candidates"), ""])
    for row in report["user_level_candidates"]:
        lines.append(f"- `{row['id']}` - {row['title_zh'] if zh else row['title']} - `{row['recommended_form']}` - {row['why_zh'] if zh else row['why']}")
    lines.extend(["", "## " + ("\u523b\u610f\u8df3\u8fc7" if zh else "Deliberately Skipped"), ""])
    for row in report["deliberately_skipped"]:
        lines.append(f"- `{row['id']}` - {row['title_zh'] if zh else row['title']}: {row['reason_zh'] if zh else row['reason']}")
    lines.extend(["", "## " + ("\u9700\u8981\u66f4\u591a\u8bc1\u636e" if zh else "Needs More Evidence"), ""])
    for row in report["needs_more_evidence"]:
        lines.append(f"- `{row['id']}` - {row.get('title_zh') if zh else row.get('title')}: {row.get('why_zh') if zh else row.get('why')}")
    lines.extend(["", "## " + ("\u5b89\u5168\u4e0e\u8131\u654f" if zh else "Safety And Redaction"), ""])
    for key, value in report["safety"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def emit_stdout(text: str) -> None:
    data = text.encode("utf-8", errors="strict")
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write(data)
        stream.flush()
    else:
        sys.stdout.write(text)
        sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Report repeated manual workflow packaging candidates.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Lookback window in days.")
    parser.add_argument("--output", help="Optional Markdown output path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown to stdout.")
    parser.add_argument("--json-output", help="Optional JSON artifact path.")
    parser.add_argument("--language", choices=("en", "zh-CN"), default="en", help="Markdown language.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = build_report(root, args.days)
    if args.json_output:
        json_path = Path(args.json_output)
        if not json_path.is_absolute():
            json_path = root / json_path
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(report, args.language), encoding="utf-8", newline="\n")
    if args.json:
        emit_stdout(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    elif not args.output:
        emit_stdout(render_markdown(report, args.language) + "\n")
    else:
        print(f"Wrote Markdown report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
