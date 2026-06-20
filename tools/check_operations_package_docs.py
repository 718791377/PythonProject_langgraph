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
EN_HEADINGS = (
    "## Purpose",
    "## Authority Boundary",
    "## Lifecycle Placement",
    "## Tailoring Rules",
    "## Inputs",
    "## Tools And Techniques",
    "## Outputs",
    "## Process Group Operating Table",
    "## Closeout And Registry",
)
ZH_HEADINGS = (
    "## 目的",
    "## 权威边界",
    "## 生命周期落点",
    "## 裁剪规则",
    "## 输入",
    "## 工具与技术",
    "## 输出",
    "## 过程组运行表",
    "## 收尾与登记",
)
EN_ITO = ("## Inputs", "## Tools And Techniques", "## Outputs")
ZH_ITO = ("## 输入", "## 工具与技术", "## 输出")
TAILORING_MODE_NAMES = tuple(mode[0] for mode in generator.TAILORING_MODES)
ZH_TAILORING_MODE_NAMES = tuple(mode[1] for mode in generator.TAILORING_MODES)
ZH_READABLE_SNIPPETS = (
    "## 目的",
    "## 输入",
    "## 工具与技术",
    "## 输出",
    "## 裁剪规则",
    "默认裁剪模式",
    "为什么不更重也不更轻",
    "升级触发器",
)
ZH_MOJIBAKE_SENTINELS = (
    "\u9429",  # common UTF-8-as-GBK artifact for `目`
    "\u9428",  # common UTF-8-as-GBK artifact for `的`
    "\u6748\u64b3",  # common artifact for `输`
    "\u5bb8\u30e5",  # common artifact for `工具`
    "\u7441\u4f78",  # common artifact for `裁`
    "\u93c9",  # common artifact for `权`
    "\u935b",  # common artifact for `命`
    "\u7f01",  # common artifact for `组`
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def parse_front_matter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def parse_registry(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    if not path.exists():
        return entries
    for raw_line in read_text(path).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("- doc_id:"):
            if current:
                entries.append(current)
            current = {"doc_id": stripped.split(":", 1)[1].strip()}
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def section_body(text: str, heading: str, following: tuple[str, ...]) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    candidates = [text.find(next_heading, start) for next_heading in following if text.find(next_heading, start) >= 0]
    end = min(candidates) if candidates else len(text)
    return text[start:end].strip()


def headings_in_order(text: str, headings: tuple[str, ...]) -> bool:
    position = -1
    for heading in headings:
        index = text.find(heading)
        if index <= position:
            return False
        position = index
    return True


def validate_front_matter(doc: generator.GeneratedDoc, rel: str, text: str, zh: bool, errors: list[str]) -> None:
    fm = parse_front_matter(text)
    required = {
        "doc_id": doc.doc_id,
        "doc_class": "operations_package",
        "status": "active",
        "package": doc.package,
        "body_kind": doc.body_kind,
        "generated_by": "tools/generate_operations_package.py",
        "lang": "zh-CN" if zh else "en",
    }
    if zh:
        required["translation_of"] = doc.rel_path
    for key, value in required.items():
        if fm.get(key) != value:
            errors.append(f"{rel} front matter {key}={fm.get(key)!r}; expected {value!r}.")
    if not zh and "translation_of" in fm:
        errors.append(f"{rel} English primary must not contain translation_of.")


def validate_zh_readability(rel: str, text: str, errors: list[str]) -> None:
    missing = [snippet for snippet in ZH_READABLE_SNIPPETS if snippet not in text]
    if missing:
        errors.append(f"{rel} is missing readable Chinese snippets: {', '.join(missing)}.")
    for sentinel in ZH_MOJIBAKE_SENTINELS:
        if sentinel in text:
            errors.append(f"{rel} contains Chinese mojibake sentinel U+{ord(sentinel[0]):04X}.")
            break


def validate_body_doc(root: Path, doc: generator.GeneratedDoc, rel: str, expected: str, zh: bool, errors: list[str]) -> None:
    path = root / rel
    if not path.exists():
        errors.append(f"Required generated body file is missing: {rel}")
        return
    try:
        text = read_text(path)
    except UnicodeDecodeError as exc:
        errors.append(f"{rel} is not valid UTF-8: {exc}")
        return
    if "\ufffd" in text:
        errors.append(f"{rel} contains Unicode replacement character.")
    if text != expected:
        errors.append(f"{rel} is not current with tools/generate_operations_package.py.")
    if generator.GENERATED_MARKER not in text:
        errors.append(f"{rel} is missing generated marker.")
    validate_front_matter(doc, rel, text, zh, errors)

    headings = ZH_HEADINGS if zh else EN_HEADINGS
    ito = ZH_ITO if zh else EN_ITO
    modes = ZH_TAILORING_MODE_NAMES if zh else TAILORING_MODE_NAMES
    if not headings_in_order(text, headings):
        errors.append(f"{rel} required headings are missing or out of order.")
    if not headings_in_order(text, ito):
        errors.append(f"{rel} I/T/O headings are missing or out of order.")
    for idx, heading in enumerate(ito):
        body = section_body(text, heading, ito[idx + 1 :] + headings[headings.index("## Process Group Operating Table" if not zh else "## 过程组运行表") :])
        if not body:
            errors.append(f"{rel} I/T/O section `{heading}` is empty.")
    for mode in modes:
        if mode not in text:
            errors.append(f"{rel} is missing tailoring mode `{mode}`.")
    if zh:
        validate_zh_readability(rel, text, errors)
        if "不更重也不更轻" not in text or "升级触发器" not in text:
            errors.append(f"{rel} is missing Chinese tailoring rationale and escalation trigger language.")
    else:
        try:
            text.encode("ascii")
        except UnicodeEncodeError as exc:
            errors.append(f"{rel} English primary contains non-ASCII text at character index {exc.start}.")
        if "not heavier or lighter" not in text or "Escalate to a heavier tailoring mode" not in text:
            errors.append(f"{rel} is missing English tailoring rationale and escalation trigger language.")


def validate_registry(root: Path, errors: list[str]) -> None:
    registry_path = root / "docs_bilingual" / "docs_registry.yaml"
    if not registry_path.exists():
        errors.append("docs_bilingual/docs_registry.yaml is missing.")
        return
    entries = parse_registry(registry_path)
    by_doc_id: dict[str, dict[str, str]] = {}
    duplicate_doc_ids: set[str] = set()
    canonical_paths: dict[str, str] = {}
    zh_paths: dict[str, str] = {}
    duplicate_paths: set[str] = set()
    for entry in entries:
        doc_id = entry.get("doc_id", "")
        canonical = entry.get("canonical_path", "")
        zh_path = entry.get("zh_cn_path", "")
        if doc_id in by_doc_id:
            duplicate_doc_ids.add(doc_id)
        by_doc_id[doc_id] = entry
        if canonical in canonical_paths:
            duplicate_paths.add(canonical)
        canonical_paths[canonical] = doc_id
        if zh_path in zh_paths:
            duplicate_paths.add(zh_path)
        zh_paths[zh_path] = doc_id
    for doc_id in sorted(duplicate_doc_ids):
        errors.append(f"docs_registry.yaml has duplicate doc_id `{doc_id}`.")
    for path in sorted(duplicate_paths):
        errors.append(f"docs_registry.yaml has duplicate path `{path}`.")
    for entry in generator.registry_entries_for_generated_docs("all"):
        actual = by_doc_id.get(entry["doc_id"])
        if actual is None:
            errors.append(f"docs_registry.yaml is missing generated doc_id `{entry['doc_id']}`.")
            continue
        for key, value in entry.items():
            if actual.get(key) != value:
                errors.append(
                    f"docs_registry.yaml entry `{entry['doc_id']}` has {key}={actual.get(key)!r}; expected {value!r}."
                )


def validate_package_isolation(root: Path, errors: list[str]) -> None:
    codex_forbidden = ("solo business", "offer, customers, cashflow", "monthly keep, stop, pivot")
    opc_forbidden = ("expert routing", "durable execution", "OpenSpec state")
    for doc in generator.CODEX_DOCS:
        path = root / doc.rel_path
        if path.exists():
            text = read_text(path)
            for term in codex_forbidden:
                if term in text:
                    errors.append(f"{doc.rel_path} contains one-person-company-only language `{term}`.")
    for doc in generator.OPC_DOCS:
        path = root / doc.rel_path
        if path.exists():
            text = read_text(path)
            for term in opc_forbidden:
                if term in text:
                    errors.append(f"{doc.rel_path} contains Codex-only language `{term}`.")


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    checked_files: list[str] = []

    if len(generator.CODEX_DOCS) != 48:
        errors.append(f"Codex generated body primary count is {len(generator.CODEX_DOCS)}; expected 48.")
    if len(generator.OPC_DOCS) != 60:
        errors.append(f"One-person-company generated body primary count is {len(generator.OPC_DOCS)}; expected 60.")
    if len(generator.ALL_DOCS) != 108:
        errors.append(f"Generated body pair count is {len(generator.ALL_DOCS)}; expected 108.")
    if len(generator.expected_files("codex")) != 96:
        errors.append(f"Codex generated body file count is {len(generator.expected_files('codex'))}; expected 96.")
    if len(generator.expected_files("one-person-company")) != 120:
        errors.append(
            f"One-person-company generated body file count is {len(generator.expected_files('one-person-company'))}; expected 120."
        )
    if len(generator.expected_files("all")) != 216:
        errors.append(f"Generated body file count is {len(generator.expected_files('all'))}; expected 216.")

    expected = generator.expected_files("all")
    docs_by_path = {doc.rel_path: doc for doc in generator.ALL_DOCS}
    docs_by_path.update({doc.zh_path: doc for doc in generator.ALL_DOCS})
    for rel, expected_text in expected.items():
        checked_files.append(rel)
        validate_body_doc(root, docs_by_path[rel], rel, expected_text, rel.endswith(".zh-CN.md"), errors)

    for doc in generator.ALL_DOCS:
        primary = root / doc.rel_path
        companion = root / doc.zh_path
        if primary.exists() and not companion.exists():
            errors.append(f"{doc.rel_path} is missing bilingual companion: {doc.zh_path}.")
        if companion.exists():
            try:
                fm = parse_front_matter(read_text(companion))
            except UnicodeDecodeError as exc:
                errors.append(f"{doc.zh_path} is not valid UTF-8: {exc}")
                continue
            if fm.get("translation_of") != doc.rel_path:
                errors.append(f"{doc.zh_path} translation_of={fm.get('translation_of')!r}; expected {doc.rel_path!r}.")

    validate_registry(root, errors)
    validate_package_isolation(root, errors)
    out_of_date, _matched = generator.check_expected(root, "all")
    if out_of_date:
        errors.append("Generator --check would report out-of-date files: " + ", ".join(out_of_date))

    info.append("Validated generated full-body operations packages for Codex durable-team and one-person-company targets.")
    return {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "checked_files": checked_files,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "codex_body_primaries": len(generator.CODEX_DOCS),
            "codex_body_files": len(generator.expected_files("codex")),
            "one_person_company_body_primaries": len(generator.OPC_DOCS),
            "one_person_company_body_files": len(generator.expected_files("one-person-company")),
            "required_pairs": len(generator.ALL_DOCS),
            "required_files": len(expected),
            "checked_files": len(checked_files),
            "tailoring_modes": len(generator.TAILORING_MODES),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate generated full-body operations-package documents.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    payload = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'fail'}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
