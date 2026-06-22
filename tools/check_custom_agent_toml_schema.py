#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "custom_agent_toml_schema"
REQUIRED_FIELDS = ("name", "description", "developer_instructions")
ALLOWED_MODEL_VALUES = frozenset(("gpt-5.4", "gpt-5.5"))


def default_user_agents_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "agents"
    return Path.home() / ".codex" / "agents"


def load_toml(path: Path) -> dict[str, Any] | None:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return data if isinstance(data, dict) else None


def validate_agent_file(path: Path, source: str, errors: list[str]) -> dict[str, Any]:
    rel = str(path)
    file_errors: list[str] = []
    fields: dict[str, Any] = {}
    try:
        data = load_toml(path)
    except tomllib.TOMLDecodeError as exc:
        message = f"{source} agent TOML is not parseable: {rel}: {exc}"
        errors.append(message)
        file_errors.append(message)
        data = None
    except OSError as exc:
        message = f"{source} agent TOML is not readable: {rel}: {exc}"
        errors.append(message)
        file_errors.append(message)
        data = None

    if data is not None:
        for field in REQUIRED_FIELDS:
            value = data.get(field)
            fields[field] = value
            if not isinstance(value, str) or not value.strip():
                message = f"{source} agent TOML missing non-empty top-level `{field}` string: {rel}"
                errors.append(message)
                file_errors.append(message)
        model = data.get("model")
        if model is not None and model not in ALLOWED_MODEL_VALUES:
            message = (
                f"{source} agent TOML has unsupported top-level `model` value: {rel}: "
                f"{model!r}; expected one of {sorted(ALLOWED_MODEL_VALUES)!r}"
            )
            errors.append(message)
            file_errors.append(message)

    return {
        "source": source,
        "path": rel,
        "ok": not file_errors,
        "required_fields": list(REQUIRED_FIELDS),
        "allowed_model_values": sorted(ALLOWED_MODEL_VALUES),
        "present_fields": [field for field in REQUIRED_FIELDS if isinstance(fields.get(field), str) and fields[field].strip()],
        "errors": file_errors,
    }


def collect_agent_files(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted(path for path in directory.glob("*.toml") if path.is_file())


def run_check(root: Path, user_agents_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    user_dir = (user_agents_dir or default_user_agents_dir()).expanduser().resolve()
    repo_dir = (root / ".codex" / "agents").resolve()

    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    scan_dirs = [
        ("repo", repo_dir),
        ("user", user_dir),
    ]
    for source, directory in scan_dirs:
        if not directory.exists():
            warnings.append(f"{source} agents directory is missing; no custom agent TOMLs checked there: {directory}")
            continue
        if not directory.is_dir():
            errors.append(f"{source} agents path is not a directory: {directory}")
            continue
        files = collect_agent_files(directory)
        if not files:
            warnings.append(f"{source} agents directory contains no *.toml files: {directory}")
            continue
        for path in files:
            checked.append(validate_agent_file(path, source, errors))

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "scan_directories": {"repo": str(repo_dir), "user": str(user_dir)},
        "checked": checked,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "checked_files": len(checked),
            "errors": len(errors),
            "warnings": len(warnings),
            "required_fields": len(REQUIRED_FIELDS),
            "allowed_model_values": len(ALLOWED_MODEL_VALUES),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate standalone native Codex custom agent TOML files.")
    parser.add_argument("--root", default=".", help="Repository root; repo-local agents are read from <root>/.codex/agents.")
    parser.add_argument("--user-agents-dir", default=None, help="Override the user-level Codex agents directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root), Path(args.user_agents_dir) if args.user_agents_dir else None)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
        if payload["ok"]:
            print(
                f"custom_agent_toml_schema: ok ({payload['counts']['checked_files']} TOML file(s) checked)"
            )
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
