#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_operations_package as generator  # noqa: E402

CHECK_NAME = "operations_package_docs"
EN_HEADINGS = ("## Inputs", "## Tools And Techniques", "## Outputs")
ZH_HEADINGS = ("## 输入", "## 工具与技术", "## 输出")
TAILORING_MODE_NAMES = tuple(mode[0] for mode in generator.TAILORING_MODES)
ZH_TAILORING_MODE_NAMES = tuple(mode[1] for mode in generator.TAILORING_MODES)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def parse_registry(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in read_text(path).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if current:
                entries.append(current)
            current = {}
            stripped = stripped[2:]
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                current[key.strip()] = value.strip()
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def table_number(text: str, label: str, expected: int) -> bool:
    return f"| {label} | {expected} |" in text


def validate_package_counts(root: Path, errors: list[str]) -> None:
    codex_text = read_text(root / "docs_bilingual/product_lifecycle/codex_platform_core_documents_register.md")
    opc_text = read_text(root / "docs_bilingual/product_lifecycle/one_person_company_core_documents_register.md")
    codex_raci = read_text(root / "docs_bilingual/product_lifecycle/codex_platform_responsibility_raci.md")
    opc_raci = read_text(root / "docs_bilingual/product_lifecycle/one_person_company_responsibility_raci.md")
    codex_agents = read_text(root / "docs_bilingual/product_lifecycle/codex_platform_governed_agent_catalog.md")
    opc_agents = read_text(root / "docs_bilingual/product_lifecycle/one_person_company_governed_agent_catalog.md")
    codex_modules = read_text(root / "docs_bilingual/product_lifecycle/codex_platform_cross_cutting_module_map.md")
    opc_modules = read_text(root / "docs_bilingual/product_lifecycle/one_person_company_cross_cutting_module_map.md")
    codex_books = read_text(root / "docs_bilingual/product_lifecycle/codex_platform_reference_books_map.md")
    startup = read_text(root / "docs_bilingual/product_lifecycle/one_person_company_minimum_startup_documents.md")

    count_checks = [
        ("Codex core document rows", len(generator.CORE_48), 8),
        ("One-person-company core document rows", len(generator.CORE_60), 10),
        ("Codex responsibility domains", len(generator.CODEX_DEPARTMENTS) * 6, 24),
        ("One-person-company responsibility domains", len(generator.OPC_DEPARTMENTS) * 6, 30),
        ("Codex agents", len(generator.CODEX_AGENTS), 12),
        ("One-person-company agents", len(generator.OPC_AGENTS), 15),
        ("Codex modules", len(generator.CODEX_MODULES), 18),
        ("One-person-company modules", len(generator.OPC_MODULES), 20),
        ("Codex books", len(generator.CODEX_BOOKS), 12),
        ("One-person-company startup docs", len(generator.STARTUP_DOCS), 12),
    ]
    for label, actual, expected in count_checks:
        if actual != expected:
            errors.append(f"{label} constant count is {actual}; expected {expected}.")

    if not table_number(codex_text, "Core documents", 48):
        errors.append("Codex core-documents register does not preserve the 48 core documents count.")
    if not table_number(opc_text, "Core documents", 60):
        errors.append("One-person-company core-documents register does not preserve the 60 core documents count.")
    if not table_number(codex_raci, "Responsibility domains", 24):
        errors.append("Codex RACI does not preserve the 24 responsibility domains count.")
    if not table_number(opc_raci, "Responsibility domains", 30):
        errors.append("One-person-company RACI does not preserve the 30 responsibility domains count.")
    if not table_number(codex_agents, "Governed AI agents", 12):
        errors.append("Codex governed-agent catalog does not preserve the 12 agent count.")
    if not table_number(opc_agents, "Governed AI agents", 15):
        errors.append("One-person-company governed-agent catalog does not preserve the 15 agent count.")
    if not table_number(codex_modules, "Cross-cutting modules", 18):
        errors.append("Codex module map does not preserve the 18 module count.")
    if not table_number(opc_modules, "Cross-cutting modules", 20):
        errors.append("One-person-company module map does not preserve the 20 module count.")
    if not table_number(codex_books, "Recommended books", 12):
        errors.append("Codex reference-books map does not preserve the 12 book count.")
    if not table_number(startup, "Minimum startup documents", 12):
        errors.append("One-person-company startup document guide does not preserve the 12 minimum startup documents count.")


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    checked_files: list[str] = []

    expected = generator.expected_files("all")
    for rel, expected_text in expected.items():
        path = root / rel
        checked_files.append(rel)
        if not path.exists():
            errors.append(f"Required generated file is missing: {rel}")
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError as exc:
            errors.append(f"{rel} is not valid UTF-8: {exc}")
            continue
        if text != expected_text:
            errors.append(f"{rel} is not current with tools/generate_operations_package.py.")
        if rel.endswith(".zh-CN.md"):
            for heading in ZH_HEADINGS:
                if heading not in text:
                    errors.append(f"{rel} is missing Chinese I/T/O heading `{heading}`.")
            for mode in ZH_TAILORING_MODE_NAMES:
                if mode not in text:
                    errors.append(f"{rel} is missing tailoring mode `{mode}`.")
            if "不更重也不更轻" not in text or "升级触发器" not in text:
                errors.append(f"{rel} is missing the tailoring rationale and escalation trigger language.")
        else:
            try:
                text.encode("ascii")
            except UnicodeEncodeError as exc:
                errors.append(f"{rel} English primary contains non-ASCII text at character index {exc.start}.")
            for heading in EN_HEADINGS:
                if heading not in text:
                    errors.append(f"{rel} is missing English I/T/O heading `{heading}`.")
            for mode in TAILORING_MODE_NAMES:
                if mode not in text:
                    errors.append(f"{rel} is missing tailoring mode `{mode}`.")
            if "not heavier or lighter" not in text or "escalation triggers" not in text:
                errors.append(f"{rel} is missing the tailoring rationale and escalation trigger language.")

    for doc in generator.ALL_DOCS:
        if doc.rel_path not in expected or doc.zh_path not in expected:
            errors.append(f"Generated document pair is incomplete in generator constants: {doc.doc_id}")
        companion = root / doc.zh_path
        if not companion.exists():
            errors.append(f"{doc.rel_path} is missing bilingual companion: {doc.zh_path}")

    codex_expected = set(generator.expected_files("codex"))
    opc_expected = set(generator.expected_files("one-person-company"))
    if len(codex_expected) != 22:
        errors.append(f"Codex package should contain 22 generated files; found {len(codex_expected)}.")
    if len(opc_expected) != 20:
        errors.append(f"One-person-company package should contain 20 generated files; found {len(opc_expected)}.")

    if (root / "docs_bilingual/product_lifecycle/codex_platform_core_documents_register.md").exists():
        codex_core = read_text(root / "docs_bilingual/product_lifecycle/codex_platform_core_documents_register.md")
        if "60-document" in codex_core or "Minimum startup documents" in codex_core:
            errors.append("Codex package appears to mix one-person-company 60-document or minimum-startup language.")
    if (root / "docs_bilingual/product_lifecycle/one_person_company_core_documents_register.md").exists():
        opc_core = read_text(root / "docs_bilingual/product_lifecycle/one_person_company_core_documents_register.md")
        if "48-document durable-team" in opc_core:
            errors.append("One-person-company package appears to mix Codex 48-document durable-team language.")

    registry_path = root / "docs_bilingual/docs_registry.yaml"
    if not registry_path.exists():
        errors.append("docs_bilingual/docs_registry.yaml is missing.")
        registry_entries: list[dict[str, str]] = []
    else:
        registry_entries = parse_registry(registry_path)
    by_doc_id = {entry.get("doc_id", ""): entry for entry in registry_entries}
    for entry in generator.registry_entries_for_generated_docs():
        actual = by_doc_id.get(entry["doc_id"])
        if actual is None:
            errors.append(f"docs_registry.yaml is missing generated doc_id `{entry['doc_id']}`.")
            continue
        for key in ("doc_class", "status", "canonical_path", "zh_cn_path"):
            if actual.get(key) != entry[key]:
                errors.append(
                    f"docs_registry.yaml entry `{entry['doc_id']}` has {key}={actual.get(key)!r}; expected {entry[key]!r}."
                )

    try:
        validate_package_counts(root, errors)
    except FileNotFoundError as exc:
        errors.append(f"Cannot validate package counts because a required file is missing: {exc}")

    out_of_date, _matched = generator.check_expected(root, "all")
    if out_of_date:
        errors.append("Generator --check would report out-of-date files: " + ", ".join(out_of_date))

    info.append("Validated generated operations packages for Codex durable-team and one-person-company targets.")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "checked_files": checked_files,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "required_pairs": len(generator.ALL_DOCS),
            "required_files": len(expected),
            "checked_files": len(checked_files),
            "errors": len(errors),
            "warnings": len(warnings),
            "tailoring_modes": len(TAILORING_MODE_NAMES),
            "codex_expected_files": len(codex_expected),
            "one_person_company_expected_files": len(opc_expected),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check generated operations-package documents and registry coverage.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args(argv)

    payload = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'failed'}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
