#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def read_text_utf8_strict(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def parse_docs_registry(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in read_text_utf8_strict(path).splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
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
        if current is None:
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()

    if current:
        entries.append(current)

    return entries


def governance_pairs(root: Path) -> tuple[list[Path], list[Path]]:
    governance_root = root / "docs_bilingual" / "governance"
    english = sorted(
        path
        for path in governance_root.glob("*.md")
        if not path.name.endswith(".zh-CN.md")
    )
    chinese = sorted(governance_root.glob("*.zh-CN.md"))
    return english, chinese


def validate_governance_pairs(root: Path, errors: list[str], infos: list[str]) -> None:
    english_files, chinese_files = governance_pairs(root)

    for english_path in english_files:
        chinese_path = english_path.with_name(english_path.stem + ".zh-CN.md")
        if not chinese_path.exists():
            errors.append(f"Missing Chinese governance companion for {english_path.relative_to(root).as_posix()}.")

    for chinese_path in chinese_files:
        english_name = chinese_path.name.replace(".zh-CN.md", ".md")
        english_path = chinese_path.with_name(english_name)
        if not english_path.exists():
            errors.append(f"Missing English governance primary for {chinese_path.relative_to(root).as_posix()}.")

    infos.append(f"Governance English primaries: {len(english_files)}")
    infos.append(f"Governance Chinese companions: {len(chinese_files)}")


def validate_governance_ascii(root: Path, errors: list[str]) -> None:
    english_files, _ = governance_pairs(root)
    for english_path in english_files:
        text = read_text_utf8_strict(english_path)
        try:
            text.encode("ascii")
        except UnicodeEncodeError as exc:
            errors.append(
                f"{english_path.relative_to(root).as_posix()} contains non-ASCII text at character index {exc.start}."
            )


def validate_governance_utf8(root: Path, errors: list[str]) -> None:
    _, chinese_files = governance_pairs(root)
    for chinese_path in chinese_files:
        try:
            read_text_utf8_strict(chinese_path)
        except UnicodeDecodeError as exc:
            errors.append(
                f"{chinese_path.relative_to(root).as_posix()} is not readable through explicit UTF-8: {exc}."
            )


def validate_registry_consistency(root: Path, errors: list[str], infos: list[str]) -> None:
    registry_path = root / "docs_bilingual" / "docs_registry.yaml"
    if not registry_path.exists():
        errors.append("docs_bilingual/docs_registry.yaml is missing.")
        return

    entries = parse_docs_registry(registry_path)
    governance_entries = [entry for entry in entries if entry.get("doc_class") == "governance"]
    indexed_doc_ids = {entry.get("doc_id", "") for entry in governance_entries}

    english_files, chinese_files = governance_pairs(root)
    expected_doc_ids = {path.stem for path in english_files}

    missing_entries = sorted(expected_doc_ids - indexed_doc_ids)
    unexpected_entries = sorted(indexed_doc_ids - expected_doc_ids)

    for doc_id in missing_entries:
        errors.append(f"docs_registry.yaml is missing governance doc_id `{doc_id}`.")
    for doc_id in unexpected_entries:
        errors.append(f"docs_registry.yaml contains unknown governance doc_id `{doc_id}`.")

    for entry in governance_entries:
        doc_id = entry.get("doc_id", "<unknown>")
        canonical_path = entry.get("canonical_path", "")
        zh_cn_path = entry.get("zh_cn_path", "")
        if not canonical_path:
            errors.append(f"Governance registry entry `{doc_id}` is missing canonical_path.")
            continue
        if not zh_cn_path:
            errors.append(f"Governance registry entry `{doc_id}` is missing zh_cn_path.")
            continue
        canonical_file = root / canonical_path
        zh_file = root / zh_cn_path
        if not canonical_file.exists():
            errors.append(f"Governance canonical_path for `{doc_id}` does not exist: {canonical_path}")
        if not zh_file.exists():
            errors.append(f"Governance zh_cn_path for `{doc_id}` does not exist: {zh_cn_path}")
        expected_zh = canonical_file.with_name(canonical_file.stem + ".zh-CN.md").relative_to(root).as_posix()
        if zh_cn_path != expected_zh:
            errors.append(
                f"Governance registry entry `{doc_id}` has mismatched zh_cn_path. Expected `{expected_zh}`, got `{zh_cn_path}`."
            )

    infos.append(f"Governance registry entries: {len(governance_entries)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check governance document bilingual and encoding rules.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")

    errors: list[str] = []
    infos: list[str] = []

    validate_governance_pairs(root, errors, infos)
    validate_governance_ascii(root, errors)
    validate_governance_utf8(root, errors)
    validate_registry_consistency(root, errors, infos)
    english_files, chinese_files = governance_pairs(root)
    registry_entries = 0
    registry_path = root / "docs_bilingual" / "docs_registry.yaml"
    if registry_path.exists():
        registry_entries = len(
            [entry for entry in parse_docs_registry(registry_path) if entry.get("doc_class") == "governance"]
        )
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "document_governance_rules",
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": [],
        "info": infos,
        "root": str(root),
        "counts": {
            "governance_english_primaries": len(english_files),
            "governance_chinese_companions": len(chinese_files),
            "governance_registry_entries": registry_entries,
            "errors": len(errors),
        },
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if errors:
        print("Document governance rules check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Document governance rules check passed.")
    for info in infos:
        print(f"  - {info}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
