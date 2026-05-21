#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "pyside6_gui_skill_contract"
SKILL_PATH = Path(".codex/skills/pyside6-gui/SKILL.md")
MAX_DESCRIPTION_LENGTH = 180
REQUIRED_FRONTMATTER = {
    "name": "pyside6-gui",
    "description": None,
}
REQUIRED_SNIPPETS = [
    "ProjectRoot",
    "-Mode preview",
    "-Mode apply",
    "RuntimeMode shared",
    "project-local-override",
    "D:\\PythonProject_langgraph\\.shared_runtimes\\pyside6",
    "ensure-shared-pyside6-runtime.ps1",
    "pyside6_runtime_contract.json",
    "shared_runtime_missing",
    "DependencyStyle auto",
    "requirements-gui.txt",
    "pyproject.toml",
    "dependency group",
    "project-local",
    "Do not install PySide6 globally",
    "do not launch a visible GUI window",
    "applied_file_changes",
    "rollback_note",
    "docs/pyside6_gui_rollback.md",
    "candidate",
    "shared_runtime_declared",
    "shared_runtime_ready",
    "project_gui_template_ready",
    "project_gui_verified_with_shared_runtime",
    "project_local_override_ready",
    "packaged",
    "Do not infer `shared_runtime_ready`, `project_gui_verified_with_shared_runtime`, `project_local_override_ready`, or `packaged`",
]
FORBIDDEN_SNIPPETS = [
    "pip install --user",
    "--global",
    "global Python installation by default",
    "plugin/vendor cache edits without explicit approval",
    "git push",
    "Start-Process",
    "app.exec() during automated verification",
]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, text, ["SKILL.md must start with YAML frontmatter delimited by ---."]
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text, ["SKILL.md frontmatter must end with a standalone --- delimiter."]
    raw = text[4:end]
    body = text[end + len("\n---\n") :]
    parsed: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"Unsupported frontmatter line: {line!r}")
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")
    return parsed, body, errors


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    skill = root / SKILL_PATH
    frontmatter: dict[str, str] = {}
    body = ""

    if not skill.exists():
        errors.append(f"Missing PySide6 GUI skill: {SKILL_PATH}")
    else:
        text = skill.read_text(encoding="utf-8", errors="replace")
        frontmatter, body, fm_errors = parse_frontmatter(text)
        errors.extend(fm_errors)
        for key, expected in REQUIRED_FRONTMATTER.items():
            if key not in frontmatter:
                errors.append(f"{SKILL_PATH} frontmatter missing required key: {key}")
            elif expected is not None and frontmatter[key] != expected:
                errors.append(f"{SKILL_PATH} frontmatter key {key} must be {expected!r}, got {frontmatter[key]!r}")
        description = frontmatter.get("description", "")
        if not description:
            errors.append(f"{SKILL_PATH} frontmatter description must be non-empty.")
        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"{SKILL_PATH} description length {len(description)} exceeds {MAX_DESCRIPTION_LENGTH} characters.")
        for snippet in REQUIRED_SNIPPETS:
            if snippet not in text:
                errors.append(f"{SKILL_PATH} missing required snippet: {snippet}")
        for snippet in FORBIDDEN_SNIPPETS:
            if snippet in text:
                errors.append(f"{SKILL_PATH} contains forbidden snippet: {snippet}")
        if re.search(r"(?i)install\s+PySide6\s+globally", body) and "Do not install PySide6 globally" not in body:
            errors.append(f"{SKILL_PATH} must not allow global PySide6 installation.")

    info.append("PySide6 GUI skill guidance is shared-runtime-first, preview-first, override-gated, and evidence-based.")
    return {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "skill": str(skill),
        "frontmatter": frontmatter,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "required_snippets": len(REQUIRED_SNIPPETS),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repo-local PySide6 GUI skill contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()
    payload = validate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 GUI skill contract check passed." if payload["ok"] else "PySide6 GUI skill contract check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload["warnings"]:
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
