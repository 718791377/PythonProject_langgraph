#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


MOJIBAKE_MARKERS = ("????", "\ufffd")


def read_text_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_docs_registry(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in read_text_utf8(path).splitlines():
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


def validate_text_health(path: Path, root: Path, errors: list[str]) -> None:
    text = read_text_utf8(path)
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(marker in line for marker in MOJIBAKE_MARKERS):
            errors.append(
                f"{path.relative_to(root).as_posix()}:{line_number}: contains mojibake or replacement-character marker."
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check implementation-plan registry and bilingual integrity rules.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")

    registry_path = root / "docs_bilingual" / "docs_registry.yaml"
    if not registry_path.exists():
        raise SystemExit("docs_bilingual/docs_registry.yaml is missing.")

    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []

    entries = parse_docs_registry(registry_path)
    impl_entries = [entry for entry in entries if entry.get("doc_class") == "implementation_plan"]
    infos.append(f"Implementation plan registry entries: {len(impl_entries)}")

    for entry in impl_entries:
        doc_id = entry.get("doc_id", "<unknown>")
        status = entry.get("status", "").strip().lower()
        canonical_path = entry.get("canonical_path", "")
        zh_cn_path = entry.get("zh_cn_path", "")

        if not canonical_path:
            errors.append(f"Implementation plan `{doc_id}` is missing canonical_path in docs_registry.yaml.")
            continue
        if not zh_cn_path:
            errors.append(f"Implementation plan `{doc_id}` is missing zh_cn_path in docs_registry.yaml.")
            continue

        canonical_file = root / canonical_path
        zh_file = root / zh_cn_path

        if not canonical_file.exists():
            errors.append(f"Implementation plan `{doc_id}` canonical_path does not exist: {canonical_path}")
        else:
            validate_text_health(canonical_file, root, errors)
        if not zh_file.exists():
            errors.append(f"Implementation plan `{doc_id}` zh_cn_path does not exist: {zh_cn_path}")
        elif zh_file != canonical_file:
            validate_text_health(zh_file, root, errors)

        canonical_is_chinese = canonical_path.endswith(".zh-CN.md")
        zh_is_chinese = zh_cn_path.endswith(".zh-CN.md")
        if not zh_is_chinese:
            errors.append(f"Implementation plan `{doc_id}` zh_cn_path is not a .zh-CN.md file: {zh_cn_path}")

        if status == "active":
            if canonical_is_chinese:
                errors.append(
                    f"Active implementation plan `{doc_id}` uses a Chinese file as canonical_path: {canonical_path}"
                )
            expected_zh = canonical_file.with_name(canonical_file.stem + ".zh-CN.md").relative_to(root).as_posix()
            if zh_cn_path != expected_zh:
                errors.append(
                    f"Active implementation plan `{doc_id}` has mismatched zh_cn_path. Expected `{expected_zh}`, got `{zh_cn_path}`."
                )
        else:
            if canonical_is_chinese:
                warnings.append(
                    f"Draft implementation plan `{doc_id}` still uses a Chinese file as canonical_path: {canonical_path}"
                )
            if canonical_path == zh_cn_path:
                warnings.append(
                    f"Draft implementation plan `{doc_id}` uses the same file for canonical_path and zh_cn_path."
                )

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "implementation_plan_rules",
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": infos,
        "root": str(root),
        "counts": {
            "implementation_plan_entries": len(impl_entries),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "implementation_plan_entries": len(impl_entries),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if errors:
        print("Implementation plan rules check failed:")
        for error in errors:
            print(f"  - {error}")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        return 1

    print("Implementation plan rules check passed.")
    for info in infos:
        print(f"  - {info}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
