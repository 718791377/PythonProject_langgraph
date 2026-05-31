#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "capability_switch_chain"
ALLOWED_SUBAGENT_ROUTING = {"auto", "manual", "off"}
ALLOWED_ON_OFF = {"on", "off"}
ALLOWED_DURABLE_BACKENDS = {"langgraph", "native_omx", "none", ""}
READY_BACKEND_STATUSES = {"ready", "running", "selected", "ok"}
UNREADY_BACKEND_STATUSES = {"blocked", "failed", "error", "unavailable", "missing"}
READINESS_FIELDS = ("installed", "enabled", "selected", "ready")
READINESS_BACKENDS = ("native_omx", "langgraph")


def default_state_file() -> Path:
    explicit = os.environ.get("CODEX_USER_LEVEL_TEAM_MODE_STATE") or os.environ.get("CODEX_TEAM_MODE_STATE")
    if explicit:
        return Path(explicit)
    codex_home = os.environ.get("CODEX_HOME")
    base = Path(codex_home) if codex_home else Path.home() / ".codex"
    return base / "state" / "user-level-team-mode.json"


def default_backend_file(root: Path) -> Path:
    return root / ".omx" / "state" / "langgraph" / "backend.json"


def load_json(path: Path, errors: list[str], warnings: list[str], label: str, *, required: bool) -> dict[str, Any] | None:
    if not path.exists():
        message = f"{label} JSON file is missing: {path}"
        if required:
            errors.append(message)
        else:
            warnings.append(message)
        return None
    if not path.is_file():
        errors.append(f"{label} JSON path is not a file: {path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} JSON is not parseable: {path}: {exc}")
        return None
    except OSError as exc:
        errors.append(f"{label} JSON is not readable: {path}: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{label} JSON must be an object: {path}")
        return None
    return data


def as_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key, "")
    return value.strip() if isinstance(value, str) else str(value).strip() if value is not None else ""


def add_value_error(errors: list[str], field: str, value: str, allowed: set[str]) -> None:
    errors.append(f"Invalid `{field}` value `{value}`; expected one of: {', '.join(sorted(allowed - {''}))}.")


def validate_state(data: dict[str, Any], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    subagent = as_string(data, "subagent_routing")
    oh_my_codex = as_string(data, "oh_my_codex")
    langgraph = as_string(data, "langgraph")
    durable_backend = as_string(data, "durable_orchestration_backend")

    if not subagent:
        errors.append("Missing required capability switch `subagent_routing`.")
    elif subagent not in ALLOWED_SUBAGENT_ROUTING:
        add_value_error(errors, "subagent_routing", subagent, ALLOWED_SUBAGENT_ROUTING)

    if not oh_my_codex:
        errors.append("Missing required capability switch `oh_my_codex`.")
    elif oh_my_codex not in ALLOWED_ON_OFF:
        add_value_error(errors, "oh_my_codex", oh_my_codex, ALLOWED_ON_OFF)

    if not langgraph:
        errors.append("Missing required capability switch `langgraph`.")
    elif langgraph not in ALLOWED_ON_OFF:
        add_value_error(errors, "langgraph", langgraph, ALLOWED_ON_OFF)

    if durable_backend and durable_backend not in ALLOWED_DURABLE_BACKENDS:
        add_value_error(errors, "durable_orchestration_backend", durable_backend, ALLOWED_DURABLE_BACKENDS)

    if subagent == "off":
        if oh_my_codex != "off":
            errors.append("Capability chain violation: subagent_routing=off requires oh_my_codex=off.")
        if langgraph != "off":
            errors.append("Capability chain violation: subagent_routing=off requires langgraph=off.")
        if durable_backend == "langgraph":
            errors.append("Capability chain violation: durable_orchestration_backend=langgraph is invalid when subagent_routing=off.")

    if oh_my_codex == "off":
        if langgraph == "on":
            errors.append("Capability chain violation: oh_my_codex=off requires langgraph=off.")
        if durable_backend == "langgraph":
            errors.append("Capability chain violation: durable_orchestration_backend=langgraph requires oh_my_codex=on.")

    if langgraph == "on":
        if subagent == "off":
            errors.append("Capability chain violation: langgraph=on requires subagent_routing!=off.")
        if oh_my_codex != "on":
            errors.append("Capability chain violation: langgraph=on requires oh_my_codex=on.")

    if durable_backend == "langgraph":
        if langgraph != "on":
            errors.append("Capability chain violation: durable_orchestration_backend=langgraph requires langgraph=on.")
        if subagent == "off":
            errors.append("Capability chain violation: durable_orchestration_backend=langgraph requires subagent_routing!=off.")
        if oh_my_codex != "on":
            errors.append("Capability chain violation: durable_orchestration_backend=langgraph requires oh_my_codex=on.")

    langgraph_ready_value = data.get("langgraph_ready")
    langgraph_ready = bool(langgraph_ready_value) if isinstance(langgraph_ready_value, bool) else None
    if langgraph_ready is True and durable_backend and durable_backend != "langgraph":
        errors.append("Capability chain violation: langgraph_ready=true requires durable_orchestration_backend=langgraph when a durable backend is selected.")
    if langgraph_ready is True and langgraph != "on":
        errors.append("Capability chain violation: langgraph_ready=true requires langgraph=on.")

    effective_backend_default = "langgraph" if durable_backend == "langgraph" and langgraph == "on" and subagent != "off" and oh_my_codex == "on" else (durable_backend or "none")
    if durable_backend == "" and langgraph == "on":
        warnings.append("LangGraph is enabled but `durable_orchestration_backend` is unset; backend default cannot be proven from user-level state alone.")

    return {
        "subagent_routing": subagent,
        "oh_my_codex": oh_my_codex,
        "langgraph": langgraph,
        "durable_orchestration_backend": durable_backend,
        "langgraph_ready": langgraph_ready,
        "effective_backend_default": effective_backend_default,
    }


def validate_backend_context(
    backend_data: dict[str, Any] | None,
    state_summary: dict[str, Any] | None,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any] | None:
    if backend_data is None:
        return None
    backend = as_string(backend_data, "backend")
    status = as_string(backend_data, "status")
    phase = as_string(backend_data, "phase")
    if backend and backend != "langgraph":
        warnings.append(f"Repo-local LangGraph backend context reports backend={backend}; expected `langgraph` for this context file.")
    if state_summary and state_summary.get("durable_orchestration_backend") == "langgraph":
        if backend and backend != "langgraph":
            errors.append("Capability chain violation: user-level durable_orchestration_backend=langgraph conflicts with repo-local backend context.")
        if status in UNREADY_BACKEND_STATUSES:
            errors.append(f"Capability chain violation: repo-local LangGraph backend status is not ready: {status}.")
    return {
        "backend": backend,
        "status": status,
        "phase": phase,
        "ready_hint": status in READY_BACKEND_STATUSES if status else None,
    }


def as_bool_field(data: dict[str, Any], key: str, errors: list[str], label: str) -> bool | None:
    if key not in data:
        errors.append(f"{label} missing required boolean field `{key}`.")
        return None
    value = data.get(key)
    if type(value) is not bool:
        errors.append(f"{label} field `{key}` must be boolean, not {type(value).__name__}.")
        return None
    return value


def validate_capability_readiness_projection(
    data: dict[str, Any] | None,
    errors: list[str],
    warnings: list[str],
    *,
    label: str,
) -> dict[str, Any] | None:
    if data is None:
        return None

    readiness = data.get("capability_readiness") if isinstance(data.get("capability_readiness"), dict) else data
    if not isinstance(readiness, dict):
        errors.append(f"{label} must be an object or contain an object-valued `capability_readiness` field.")
        return None

    readiness_fields = readiness.get("readiness_fields")
    normalized_fields: list[str] = []
    if not isinstance(readiness_fields, list):
        errors.append(f"{label} must publish `readiness_fields` as an array.")
    else:
        normalized_fields = [str(item) for item in readiness_fields]
        for field in READINESS_FIELDS:
            if field not in normalized_fields:
                errors.append(f"{label} readiness_fields missing required distinct state field `{field}`.")

    selected_backend = as_string(readiness, "selected_backend")
    if selected_backend and selected_backend not in (ALLOWED_DURABLE_BACKENDS - {""}):
        add_value_error(errors, "capability_readiness.selected_backend", selected_backend, ALLOWED_DURABLE_BACKENDS)

    backends: dict[str, Any] = {}
    for backend_name in READINESS_BACKENDS:
        record = readiness.get(backend_name)
        record_label = f"{label}.{backend_name}"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object with installed/enabled/selected/ready booleans.")
            continue
        values: dict[str, bool | None] = {}
        for field in READINESS_FIELDS:
            values[field] = as_bool_field(record, field, errors, record_label)

        if all(values[field] is not None for field in READINESS_FIELDS):
            expected_ready = bool(values["installed"] and values["enabled"] and values["selected"])
            if values["ready"] is not expected_ready:
                errors.append(
                    f"{record_label}.ready must equal installed && enabled && selected; "
                    f"got installed={values['installed']}, enabled={values['enabled']}, "
                    f"selected={values['selected']}, ready={values['ready']}."
                )
            if selected_backend == backend_name and values["selected"] is not True:
                errors.append(
                    f"{label}.selected_backend={backend_name} requires {record_label}.selected=true."
                )

        backends[backend_name] = {
            field: values.get(field) for field in READINESS_FIELDS
        }

    return {
        "selected_backend": selected_backend,
        "readiness_fields": normalized_fields,
        "backends": backends,
    }


def run_check(
    root: Path,
    state_file: Path | None = None,
    backend_file: Path | None = None,
    readiness_file: Path | None = None,
    *,
    require_state: bool = False,
    require_backend: bool = False,
    require_readiness: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    state_path = (state_file or default_state_file()).expanduser()
    backend_path = backend_file or default_backend_file(root)
    readiness_path = readiness_file.expanduser() if readiness_file is not None else None
    errors: list[str] = []
    warnings: list[str] = []

    state_data = load_json(state_path, errors, warnings, "user-level capability state", required=require_state)
    state_summary = validate_state(state_data, errors, warnings) if state_data is not None else None
    backend_data = load_json(backend_path, errors, warnings, "repo-local LangGraph backend context", required=require_backend)
    backend_summary = validate_backend_context(backend_data, state_summary, errors, warnings)
    readiness_data = (
        load_json(readiness_path, errors, warnings, "durable capability readiness projection", required=require_readiness)
        if readiness_path is not None
        else None
    )
    if readiness_data is None and require_readiness and readiness_path is None:
        errors.append("durable capability readiness projection JSON file is required but no --readiness-file was provided.")
    readiness_source = readiness_data
    readiness_label = "durable capability readiness projection"
    if readiness_source is None and backend_data is not None and isinstance(backend_data.get("capability_readiness"), dict):
        readiness_source = backend_data
        readiness_label = "repo-local backend capability_readiness"
    if readiness_source is None and state_data is not None and isinstance(state_data.get("capability_readiness"), dict):
        readiness_source = state_data
        readiness_label = "user-level state capability_readiness"
    readiness_summary = validate_capability_readiness_projection(
        readiness_source,
        errors,
        warnings,
        label=readiness_label,
    ) if readiness_source is not None else None

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "state_file": str(state_path),
        "backend_file": str(backend_path),
        "readiness_file": str(readiness_path) if readiness_path is not None else None,
        "state": state_summary,
        "backend_context": backend_summary,
        "capability_readiness": readiness_summary,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "state_loaded": 1 if state_data is not None else 0,
            "backend_context_loaded": 1 if backend_data is not None else 0,
            "capability_readiness_loaded": 1 if readiness_source is not None else 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Codex user-level orchestration capability-switch dependency chain.")
    parser.add_argument("--root", default=".", help="Repository root; repo-local LangGraph backend context defaults under <root>/.omx/state/langgraph/backend.json.")
    parser.add_argument("--state-file", default=None, help="Override the user-level team-mode capability state JSON file.")
    parser.add_argument("--backend-file", default=None, help="Override the repo-local LangGraph backend context JSON file.")
    parser.add_argument("--readiness-file", default=None, help="Validate a durable capability readiness projection JSON file.")
    parser.add_argument("--require-state", action="store_true", help="Fail when the capability state JSON file is missing.")
    parser.add_argument("--require-backend", action="store_true", help="Fail when the repo-local LangGraph backend context JSON file is missing.")
    parser.add_argument("--require-readiness", action="store_true", help="Fail when no durable capability readiness projection is loaded.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(
        Path(args.root),
        Path(args.state_file) if args.state_file else None,
        Path(args.backend_file) if args.backend_file else None,
        Path(args.readiness_file) if args.readiness_file else None,
        require_state=args.require_state,
        require_backend=args.require_backend,
        require_readiness=args.require_readiness,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("capability_switch_chain: ok")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
