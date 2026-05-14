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


def run_check(
    root: Path,
    state_file: Path | None = None,
    backend_file: Path | None = None,
    *,
    require_state: bool = False,
    require_backend: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    state_path = (state_file or default_state_file()).expanduser()
    backend_path = backend_file or default_backend_file(root)
    errors: list[str] = []
    warnings: list[str] = []

    state_data = load_json(state_path, errors, warnings, "user-level capability state", required=require_state)
    state_summary = validate_state(state_data, errors, warnings) if state_data is not None else None
    backend_data = load_json(backend_path, errors, warnings, "repo-local LangGraph backend context", required=require_backend)
    backend_summary = validate_backend_context(backend_data, state_summary, errors, warnings)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "state_file": str(state_path),
        "backend_file": str(backend_path),
        "state": state_summary,
        "backend_context": backend_summary,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "state_loaded": 1 if state_data is not None else 0,
            "backend_context_loaded": 1 if backend_data is not None else 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Codex user-level orchestration capability-switch dependency chain.")
    parser.add_argument("--root", default=".", help="Repository root; repo-local LangGraph backend context defaults under <root>/.omx/state/langgraph/backend.json.")
    parser.add_argument("--state-file", default=None, help="Override the user-level team-mode capability state JSON file.")
    parser.add_argument("--backend-file", default=None, help="Override the repo-local LangGraph backend context JSON file.")
    parser.add_argument("--require-state", action="store_true", help="Fail when the capability state JSON file is missing.")
    parser.add_argument("--require-backend", action="store_true", help="Fail when the repo-local LangGraph backend context JSON file is missing.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(
        Path(args.root),
        Path(args.state_file) if args.state_file else None,
        Path(args.backend_file) if args.backend_file else None,
        require_state=args.require_state,
        require_backend=args.require_backend,
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
