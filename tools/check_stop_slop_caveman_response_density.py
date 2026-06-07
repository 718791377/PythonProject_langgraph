#!/usr/bin/env python3
"""Repo-local Stop-Slop/Caveman response-density checker."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CHECK_NAME = "stop_slop_caveman_response_density"
SCRIPT = Path("tools/check_stop_slop_caveman_response_density.py")
RUNTIME = Path("tools/stop_slop_caveman_runtime.py")
SMOKE_CHECKER = Path("tools/check_stop_slop_caveman_smoke_receipts.py")
PLAN_EN = Path("docs_bilingual/implementation_plans/stop_slop_caveman_response_density_runtime_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/stop_slop_caveman_response_density_runtime_plan.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")
TEST_NAME = "check_stop_slop_caveman_response_density.test.py"


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


@dataclass(frozen=True)
class Span:
    kind: str
    start: int
    end: int
    text: str


PROTECTED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("code_fence", re.compile(r"```.*?```", re.DOTALL)),
    ("inline_code", re.compile(r"`[^`\n]+`")),
    ("url", re.compile(r"https?://[^\s`\]>)\"';]+")),
    ("windows_path", re.compile(r"(?i)\b[A-Z]:\\[^\s`]+")),
    ("posix_path", re.compile(r"(?<!\w)/(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+")),
    ("repo_path", re.compile(r"\b(?:tools|test|docs_bilingual|openspec|docs|\.omx)/(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+")),
    ("cli_arg", re.compile(r"(?<!\w)--[A-Za-z0-9][A-Za-z0-9_-]*")),
    ("schema_key", re.compile(r"\b[A-Za-z][A-Za-z0-9_]*(?=\s*:)")),
    ("openspec_keyword", re.compile(r"\b(?:Requirement|Scenario|WHEN|THEN|AND|SHALL|MAY|MUST)\b")),
    ("evidence_token", re.compile(r"\b(?:evidence|blocker|blockers|threshold_not_met|blocked:[A-Za-z0-9_-]+)\b", re.IGNORECASE)),
)
LABELS = ("Routing trace", "Updated Plan")
THROAT_CLEARING = (
    re.compile(r"(?i)\bSure!?\b"),
    re.compile(r"(?i)\bCertainly[,!]?\b"),
    re.compile(r"(?i)\bI(?:'|’)d be happy to help\b"),
    re.compile(r"(?i)\bHere(?:'|’)s what(?: you need to do| happened| changed| this means)?\b"),
)
BINARY_CONTRAST = re.compile(r"(?i)\b(?:not just|not only|it(?:'|’)s not|this is not just)\b.{0,120}\b(?:but|it(?:'|’)s)\b")
VAGUE_DECLARATIVES = (
    re.compile(r"(?i)\bthe implications are significant\b"),
    re.compile(r"(?i)\bthis is (?:important|significant|crucial)\b"),
    re.compile(r"(?i)\bvarious|several things|a number of\b"),
)
FILLER_WORDS = {"basically", "actually", "just", "very", "really", "quite", "simply", "clearly"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError:
        errors.append(f"missing_or_unreadable_json:{path.as_posix()}")
    except json.JSONDecodeError:
        errors.append(f"invalid_json:{path.as_posix()}")
    return None


def protected_spans(text: str) -> list[Span]:
    spans: list[Span] = []
    occupied: list[tuple[int, int]] = []

    def overlaps(start: int, end: int) -> bool:
        return any(start < used_end and end > used_start for used_start, used_end in occupied)

    for label in LABELS:
        idx = text.find(label)
        while idx >= 0:
            end = idx + len(label)
            if not overlaps(idx, end):
                spans.append(Span("label", idx, end, label))
                occupied.append((idx, end))
            idx = text.find(label, end)

    for kind, pattern in PROTECTED_PATTERNS:
        for match in pattern.finditer(text):
            start, end = match.span()
            if overlaps(start, end):
                continue
            spans.append(Span(kind, start, end, match.group(0)))
            occupied.append((start, end))
    spans.sort(key=lambda item: (item.start, item.end))
    return spans


def mask_protected(text: str, spans: list[Span]) -> str:
    chars = list(text)
    for span in spans:
        for index in range(span.start, span.end):
            chars[index] = " "
    return "".join(chars)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, max(index, 0)) + 1


def span_summary(spans: list[Span]) -> dict[str, Any]:
    by_kind: dict[str, int] = {}
    labels: list[str] = []
    for span in spans:
        by_kind[span.kind] = by_kind.get(span.kind, 0) + 1
        if span.kind == "label" and span.text not in labels:
            labels.append(span.text)
    return {"counts_by_kind": by_kind, "labels": labels, "total": len(spans)}


def add_finding(findings: list[dict[str, Any]], *, sample: str, finding_id: str, message: str, text: str, index: int, severity: str = "error") -> None:
    findings.append({"id": finding_id, "severity": severity, "sample": sample, "line": line_number(text, index), "message": message})


def analyze_text(text: str, *, sample_name: str = "<text>") -> dict[str, Any]:
    spans = protected_spans(text)
    check_text = mask_protected(text, spans)
    findings: list[dict[str, Any]] = []
    for pattern in THROAT_CLEARING:
        for match in pattern.finditer(check_text):
            add_finding(findings, sample=sample_name, finding_id="throat_clearing", message="Remove conversational throat-clearing or assistant boilerplate.", text=text, index=match.start())
    for match in re.finditer("—", check_text):
        add_finding(findings, sample=sample_name, finding_id="em_dash", message="Replace em dash with a shorter sentence boundary or colon.", text=text, index=match.start())
    for match in BINARY_CONTRAST.finditer(check_text):
        add_finding(findings, sample=sample_name, finding_id="binary_contrast", message="Avoid formulaic not-just/but contrast structures.", text=text, index=match.start())
    for pattern in VAGUE_DECLARATIVES:
        for match in pattern.finditer(check_text):
            add_finding(findings, sample=sample_name, finding_id="vague_declarative", message="Replace vague significance claims with concrete impact.", text=text, index=match.start(), severity="warning")
    words = re.findall(r"\b[A-Za-z][A-Za-z'’-]*\b", check_text)
    filler_count = sum(1 for word in words if word.lower().strip("'’-") in FILLER_WORDS)
    if words and filler_count / max(len(words), 1) > 0.08:
        add_finding(findings, sample=sample_name, finding_id="low_density_filler_ratio", message="Filler ratio is too high for dense operator output.", text=text, index=0, severity="warning")
    sentence_lengths = [len(re.findall(r"\b\w+\b", sentence)) for sentence in re.split(r"[.!?。！？]+", check_text) if sentence.strip()]
    if len(sentence_lengths) >= 4 and len(set(sentence_lengths)) <= 2:
        add_finding(findings, sample=sample_name, finding_id="flat_rhythm", message="Vary sentence rhythm or compress repeated structure.", text=text, index=0, severity="warning")
    errors = sum(1 for item in findings if item["severity"] == "error")
    warnings = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "sample": sample_name,
        "ok": errors == 0,
        "findings": findings,
        "counts": {"errors": errors, "warnings": warnings, "findings": len(findings)},
        "protected_spans": span_summary(spans),
        "metrics": {"chars": len(text), "words_unprotected": len(words), "filler_words": filler_count, "sentence_lengths_unprotected": sentence_lengths},
    }


def check_repo_surfaces(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    surface = {
        "checker_exists": (root / SCRIPT).exists(),
        "runtime_exists": (root / RUNTIME).exists(),
        "smoke_checker_exists": (root / SMOKE_CHECKER).exists(),
        "ci_manifest_has_test": False,
        "safety_registry_has_rule": False,
        "safety_registry_has_scripts": False,
        "safety_registry_has_guard_steps": False,
        "openspec_guard_references_checker": False,
        "plan_markers_present": False,
    }
    for key, rel in (("checker_exists", SCRIPT), ("runtime_exists", RUNTIME), ("smoke_checker_exists", SMOKE_CHECKER)):
        if not surface[key]:
            errors.append(f"missing_surface:{rel.as_posix()}")
    manifest = read_json(root / CI_MANIFEST, errors)
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        surface["ci_manifest_has_test"] = TEST_NAME in manifest["python_unittest"]
    if not surface["ci_manifest_has_test"]:
        errors.append(f"ci_manifest_missing:{TEST_NAME}")
    registry = read_json(root / SAFETY_REGISTRY, errors)
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "stop-slop-caveman-response-density-runtime":
                surface["safety_registry_has_rule"] = True
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                surface["safety_registry_has_scripts"] = {SCRIPT.as_posix(), RUNTIME.as_posix(), SMOKE_CHECKER.as_posix()}.issubset(scripts)
                surface["safety_registry_has_guard_steps"] = {CHECK_NAME, "stop_slop_caveman_smoke_receipts"}.issubset(steps)
    if not surface["safety_registry_has_rule"]:
        errors.append("safety_registry_missing:stop-slop-caveman-response-density-runtime")
    if not surface["safety_registry_has_scripts"]:
        errors.append("safety_registry_missing_stop_slop_caveman_scripts")
    if not surface["safety_registry_has_guard_steps"]:
        errors.append("safety_registry_missing_stop_slop_caveman_guard_steps")
    try:
        guard_text = (root / GUARD_SCRIPT).read_text(encoding="utf-8-sig")
        surface["openspec_guard_references_checker"] = CHECK_NAME in guard_text and "check_stop_slop_caveman_smoke_receipts" in guard_text
    except OSError:
        errors.append(f"missing_or_unreadable:{GUARD_SCRIPT.as_posix()}")
    if not surface["openspec_guard_references_checker"]:
        errors.append("openspec_guard_missing_stop_slop_caveman_checks")
    required_markers = (SCRIPT.as_posix(), RUNTIME.as_posix(), SMOKE_CHECKER.as_posix(), TEST_NAME, "blocked receipts", "smoke-tested")
    plan_ok = True
    for rel in (PLAN_EN, PLAN_ZH):
        try:
            plan_text = (root / rel).read_text(encoding="utf-8-sig").lower()
        except OSError:
            errors.append(f"missing_or_unreadable:{rel.as_posix()}")
            plan_ok = False
            continue
        for marker in required_markers:
            if marker.lower() not in plan_text:
                errors.append(f"{rel.as_posix()}:missing_marker:{marker}")
                plan_ok = False
    surface["plan_markers_present"] = plan_ok
    return {"ok": not errors, "surface": surface, "errors": errors}


def load_samples(args: argparse.Namespace) -> list[tuple[str, str]]:
    samples: list[tuple[str, str]] = []
    for path_text in args.sample_file:
        path = Path(path_text)
        samples.append((path.name, read_text(path)))
    for index, text in enumerate(args.sample_text, start=1):
        samples.append((f"inline-{index}", text))
    return samples


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check Stop-Slop/Caveman response-density samples.")
    parser.add_argument("--root", default=".", help="Repository root for surface validation.")
    parser.add_argument("--sample-file", action="append", default=[], help="Explicit sample file to check.")
    parser.add_argument("--sample-text", action="append", default=[], help="Explicit sample text to check.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    samples = load_samples(args)
    if not samples:
        surface_payload = check_repo_surfaces(root)
        payload = {"schema_version": 1, "check_name": CHECK_NAME, "ok": surface_payload["ok"], "mode": "repo-surfaces", **surface_payload}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1
    sample_results = [analyze_text(text, sample_name=name) for name, text in samples]
    findings = [finding for result in sample_results for finding in result["findings"]]
    errors = sum(result["counts"]["errors"] for result in sample_results)
    warnings = sum(result["counts"]["warnings"] for result in sample_results)
    labels: list[str] = []
    total_spans = 0
    by_kind: dict[str, int] = {}
    for result in sample_results:
        protected = result["protected_spans"]
        total_spans += int(protected["total"])
        for label in protected["labels"]:
            if label not in labels:
                labels.append(label)
        for kind, count in protected["counts_by_kind"].items():
            by_kind[kind] = by_kind.get(kind, 0) + int(count)
    payload = {
        "schema_version": 1,
        "check_name": CHECK_NAME,
        "ok": errors == 0,
        "mode": "samples",
        "samples": sample_results,
        "findings": findings,
        "counts": {"samples": len(sample_results), "errors": errors, "warnings": warnings, "findings": len(findings)},
        "protected_spans": {"labels": labels, "total": total_spans, "counts_by_kind": by_kind},
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
