#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DOC_ID = "openspec_comet_superpowers_workflow_policy"
EN_POLICY = Path("docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md")
ZH_POLICY = Path("docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md")
REGISTRY = Path("docs_bilingual/docs_registry.yaml")
ACTIVE_SPEC = Path(
    "openspec/changes/upgrade-openspec-comet-superpowers/"
    "specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md"
)
STABLE_SPEC = Path("openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md")

EN_REQUIRED_TERMS = [
    "Comet-controlled OpenSpec + Superpowers",
    "OpenSpec is the WHAT layer",
    "Superpowers is the HOW layer",
    "Comet is the control layer",
    "Open -> Design -> Build -> Verify -> Archive",
    ".openspec.yaml",
    ".comet.yaml",
    "comet init",
    "explicit operator approval",
    "Skills remain workflow instruction surfaces",
    "not native subagent evidence",
]

ZH_REQUIRED_TERMS = [
    "Comet 控制",
    "OpenSpec",
    "Superpowers",
    "WHAT",
    "HOW",
    "Comet 管 WHEN & NEXT",
    "Open -> Design -> Build -> Verify -> Archive",
    ".openspec.yaml",
    ".comet.yaml",
    "显式操作员批准",
    "不是 native subagent 证据",
]

SPEC_REQUIRED_TERMS = [
    "Comet-controlled workflow SHALL preserve layer boundaries",
    "five-phase pipeline",
    "decoupled state",
    "guard phase transitions",
    "archive evidence",
    "explicit and repository-local",
    "checker-backed",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def parse_registry_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
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


def require_file(root: Path, relative: Path, errors: list[str]) -> Path | None:
    path = root / relative
    if not path.exists():
        errors.append(f"Missing required file: {relative.as_posix()}")
        return None
    if not path.is_file():
        errors.append(f"Required path is not a file: {relative.as_posix()}")
        return None
    return path


def check_terms(label: str, text: str, terms: list[str], errors: list[str]) -> list[str]:
    missing = [term for term in terms if term not in text]
    for term in missing:
        errors.append(f"{label} is missing required term: {term}")
    return missing


def build_report(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    checked_files: list[str] = []

    en_path = require_file(root, EN_POLICY, errors)
    zh_path = require_file(root, ZH_POLICY, errors)
    registry_path = require_file(root, REGISTRY, errors)

    en_missing: list[str] = []
    zh_missing: list[str] = []
    spec_missing: list[str] = []

    if en_path:
        try:
            en_text = read_text(en_path)
            checked_files.append(EN_POLICY.as_posix())
            try:
                en_text.encode("ascii")
            except UnicodeEncodeError as exc:
                errors.append(f"{EN_POLICY.as_posix()} contains non-ASCII text at character index {exc.start}.")
            en_missing = check_terms("English policy", en_text, EN_REQUIRED_TERMS, errors)
        except UnicodeDecodeError as exc:
            errors.append(f"{EN_POLICY.as_posix()} is not valid UTF-8: {exc}")

    if zh_path:
        try:
            zh_text = read_text(zh_path)
            checked_files.append(ZH_POLICY.as_posix())
            if "\ufffd" in zh_text or "??" in zh_text:
                errors.append(
                    f"{ZH_POLICY.as_posix()} appears to contain mojibake or placeholder question marks; "
                    "read and maintain it as UTF-8 Chinese text."
                )
            zh_missing = check_terms("Chinese policy", zh_text, ZH_REQUIRED_TERMS, errors)
        except UnicodeDecodeError as exc:
            errors.append(f"{ZH_POLICY.as_posix()} is not valid UTF-8: {exc}")

    if registry_path:
        try:
            registry_text = read_text(registry_path)
            checked_files.append(REGISTRY.as_posix())
            entries = parse_registry_entries(registry_text)
            matching = [entry for entry in entries if entry.get("doc_id") == DOC_ID]
            if not matching:
                errors.append(f"docs registry is missing governance doc_id `{DOC_ID}`.")
            else:
                entry = matching[0]
                expected = {
                    "doc_class": "governance",
                    "status": "active",
                    "canonical_path": EN_POLICY.as_posix(),
                    "zh_cn_path": ZH_POLICY.as_posix(),
                }
                for key, value in expected.items():
                    if entry.get(key) != value:
                        errors.append(
                            f"docs registry entry `{DOC_ID}` has wrong {key}: expected `{value}`, got `{entry.get(key)}`."
                        )
        except UnicodeDecodeError as exc:
            errors.append(f"{REGISTRY.as_posix()} is not valid UTF-8: {exc}")

    spec_path = root / ACTIVE_SPEC
    spec_kind = "active_delta"
    if not spec_path.exists():
        spec_path = root / STABLE_SPEC
        spec_kind = "stable"
    if not spec_path.exists():
        errors.append(
            "Missing Comet/OpenSpec/Superpowers spec; expected active delta or stable spec at "
            f"{ACTIVE_SPEC.as_posix()} or {STABLE_SPEC.as_posix()}."
        )
    else:
        try:
            spec_text = read_text(spec_path)
            checked_files.append(str(spec_path.relative_to(root).as_posix()))
            spec_missing = check_terms("OpenSpec capability", spec_text, SPEC_REQUIRED_TERMS, errors)
            info.append(f"Spec source: {spec_kind}")
        except UnicodeDecodeError as exc:
            errors.append(f"{spec_path.relative_to(root).as_posix()} is not valid UTF-8: {exc}")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "openspec_comet_superpowers_policy",
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "checked_files": checked_files,
        "required_terms": {
            "english_policy": EN_REQUIRED_TERMS,
            "chinese_policy": ZH_REQUIRED_TERMS,
            "spec": SPEC_REQUIRED_TERMS,
        },
        "missing_terms": {
            "english_policy": en_missing,
            "chinese_policy": zh_missing,
            "spec": spec_missing,
        },
        "counts": {
            "checked_files": len(checked_files),
            "english_terms": len(EN_REQUIRED_TERMS),
            "chinese_terms": len(ZH_REQUIRED_TERMS),
            "spec_terms": len(SPEC_REQUIRED_TERMS),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Comet-controlled OpenSpec + Superpowers governance policy.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_report(root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        if report["ok"]:
            print("OpenSpec Comet/Superpowers policy check passed.")
        else:
            print("OpenSpec Comet/Superpowers policy check failed:")
            for error in report["errors"]:
                print(f"  - {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
