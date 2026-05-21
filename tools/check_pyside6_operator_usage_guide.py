#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "pyside6_operator_usage_guide"
EN_GUIDE = Path("docs_bilingual/guides/pyside6_gui_cross_project_usage.md")
ZH_GUIDE = Path("docs_bilingual/guides/pyside6_gui_cross_project_usage.zh-CN.md")
REGISTRY = Path("docs_bilingual/docs_registry.yaml")

REQUIRED_SHARED_SNIPPETS = [
    ("doc_id: pyside6_gui_cross_project_usage", "doc_id"),
    ("doc_class: guide", "doc_class"),
    ("status: active", "active status"),
    ("plugin-modules", "plugin-modules module source"),
    ("pyside6-gui", "pyside6-gui module"),
    ("soft-load", "soft-load boundary"),
    ("-RepoRoot", "repo-root argument"),
    ("skill_docs", "skill-doc output"),
    ("missing_hints", "missing hint blocker"),
    ("ensure-shared-pyside6-runtime.ps1", "shared runtime helper"),
    ("D:\\PythonProject_langgraph\\.shared_runtimes\\pyside6", "shared runtime root"),
    ("shared_runtime_missing", "shared runtime missing blocker"),
    ("-Mode preview", "preview command"),
    ("-RuntimeMode shared", "shared runtime mode"),
    ("-DependencyStyle auto", "dependency-style selection"),
    ("-CreateTemplate", "template preview"),
    ("-Mode apply", "apply command"),
    ("project-local-override", "project-local override boundary"),
    ("applied_file_changes", "apply evidence"),
    ("rollback_note", "rollback note"),
    ("docs/pyside6_gui_rollback.md", "rollback-note path"),
    ("PyInstaller", "PyInstaller packaging option"),
    ("Nuitka", "Nuitka packaging option"),
    ("release_ready", "release-ready non-inference"),
]

REQUIRED_EN_SNIPPETS = [
    ("does not install PySide6", "no PySide6 install during soft-load"),
    ("does not edit `config.toml`", "no config mutation during soft-load"),
    ("does not enable plugin bundles", "no plugin enablement during soft-load"),
    ("visible GUI", "visible GUI boundary"),
    ("packaging", "packaging boundary"),
    ("Never infer `shared_runtime_ready`, `project_gui_verified_with_shared_runtime`, `project_local_override_ready`, `packaged`, or `release_ready`", "state non-inference rule"),
]

REQUIRED_ZH_SNIPPETS = [
    ("不会安装 PySide6", "no PySide6 install during soft-load"),
    ("不会编辑 `config.toml`", "no config mutation during soft-load"),
    ("不会启用 plugin bundle", "no plugin enablement during soft-load"),
    ("可见 GUI", "visible GUI boundary"),
    ("打包", "packaging boundary"),
    ("不得只根据 policy、guide、skill、helper 或 template 文本推断", "state non-inference rule"),
]

FORBIDDEN_PATTERNS = [
    (r"set_plugin_profile\.ps1.*-Apply", "guide must not tell operators to hard-load/apply plugin profiles for the soft-load path"),
    (r"pip\s+install\s+--user\s+PySide6", "guide must not recommend user/global PySide6 installs"),
    (r"pip\s+install\s+PySide6", "guide must not recommend generic global PySide6 installs"),
    (r"Start-Process\s+.*PySide6", "guide must not launch a visible GUI from the soft-load path"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    en_path = root / EN_GUIDE
    zh_path = root / ZH_GUIDE
    registry_path = root / REGISTRY

    texts: dict[str, str] = {}
    for label, path in (("English guide", en_path), ("Chinese guide", zh_path)):
        if not path.exists():
            errors.append(f"Missing {label}: {path.relative_to(root).as_posix()}")
            continue
        text = read_text(path)
        texts[label] = text
        metadata = parse_frontmatter(text)
        if metadata.get("doc_id") != "pyside6_gui_cross_project_usage":
            errors.append(f"{path.relative_to(root).as_posix()} frontmatter doc_id must be pyside6_gui_cross_project_usage.")
        if metadata.get("doc_class") != "guide":
            errors.append(f"{path.relative_to(root).as_posix()} frontmatter doc_class must be guide.")
        if metadata.get("status") != "active":
            errors.append(f"{path.relative_to(root).as_posix()} frontmatter status must be active.")
        if label == "English guide" and metadata.get("lang") != "en":
            errors.append("English guide frontmatter lang must be en.")
        if label == "Chinese guide" and metadata.get("lang") != "zh-CN":
            errors.append("Chinese guide frontmatter lang must be zh-CN.")
        if label == "Chinese guide" and metadata.get("translation_of") != EN_GUIDE.as_posix():
            errors.append("Chinese guide must declare translation_of docs_bilingual/guides/pyside6_gui_cross_project_usage.md.")

    if "English guide" in texts:
        english = texts["English guide"]
        for snippet, label in REQUIRED_SHARED_SNIPPETS + REQUIRED_EN_SNIPPETS:
            if snippet not in english:
                errors.append(f"{EN_GUIDE.as_posix()} missing {label}: {snippet}")
        for pattern, message in FORBIDDEN_PATTERNS:
            if re.search(pattern, english, flags=re.IGNORECASE | re.DOTALL):
                errors.append(f"{EN_GUIDE.as_posix()}: {message}")

    if "Chinese guide" in texts:
        chinese = texts["Chinese guide"]
        for snippet, label in REQUIRED_SHARED_SNIPPETS + REQUIRED_ZH_SNIPPETS:
            if snippet not in chinese:
                errors.append(f"{ZH_GUIDE.as_posix()} missing {label}: {snippet}")
        for pattern, message in FORBIDDEN_PATTERNS:
            if re.search(pattern, chinese, flags=re.IGNORECASE | re.DOTALL):
                errors.append(f"{ZH_GUIDE.as_posix()}: {message}")

    if not registry_path.exists():
        errors.append("docs_bilingual/docs_registry.yaml is missing.")
    else:
        registry = read_text(registry_path)
        for snippet in [
            "doc_id: pyside6_gui_cross_project_usage",
            "doc_class: guide",
            "status: active",
            "canonical_path: docs_bilingual/guides/pyside6_gui_cross_project_usage.md",
            "zh_cn_path: docs_bilingual/guides/pyside6_gui_cross_project_usage.zh-CN.md",
        ]:
            if snippet not in registry:
                errors.append(f"docs_bilingual/docs_registry.yaml missing registry snippet: {snippet}")

    info.append("PySide6 cross-project operator guide keeps soft-load, shared-runtime, preview/apply, override, visible-GUI, and packaging boundaries explicit.")
    return {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "english_guide": str(en_path),
        "chinese_guide": str(zh_path),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "required_english_snippets": len(REQUIRED_SHARED_SNIPPETS) + len(REQUIRED_EN_SNIPPETS),
            "required_chinese_phrases": len(REQUIRED_SHARED_SNIPPETS) + len(REQUIRED_ZH_SNIPPETS),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the PySide6 cross-project operator usage guide contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = validate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 operator usage guide check passed." if payload["ok"] else "PySide6 operator usage guide check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload["warnings"]:
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
