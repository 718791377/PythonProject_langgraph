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
READINESS_RECEIPT_KIND = "durable_capability_readiness_projection"
READINESS_PROMOTION_MARKER = "smoke-tested"
READINESS_R5_PROMOTION_MARKER = "active-candidate"


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

    receipt_summary = validate_capability_readiness_receipt_metadata(data, errors, warnings, label=label)
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
        "receipt": receipt_summary,
    }


def validate_capability_readiness_receipt_metadata(
    data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    *,
    label: str,
) -> dict[str, Any] | None:
    receipt_kind = as_string(data, "receipt_kind")
    if not receipt_kind:
        return None
    if receipt_kind != READINESS_RECEIPT_KIND:
        errors.append(f"{label}.receipt_kind must be `{READINESS_RECEIPT_KIND}` when present; got `{receipt_kind}`.")
    promotion_marker = as_string(data, "promotion_marker")
    if promotion_marker not in {READINESS_PROMOTION_MARKER, READINESS_R5_PROMOTION_MARKER}:
        errors.append(
            f"{label}.promotion_marker must be `{READINESS_PROMOTION_MARKER}` or `{READINESS_R5_PROMOTION_MARKER}`."
        )
    generated_at = as_string(data, "generated_at")
    if not generated_at:
        errors.append(f"{label}.generated_at is required for readiness receipts.")
    if not isinstance(data.get("source_receipts"), dict):
        errors.append(f"{label}.source_receipts must be an object.")
    selector_evidence = data.get("selector_evidence")
    if not isinstance(selector_evidence, dict):
        errors.append(f"{label}.selector_evidence must be an object.")
    else:
        if as_string(selector_evidence, "selector_authority") != ".omx/state/selectors/active.json":
            errors.append(f"{label}.selector_evidence.selector_authority must be `.omx/state/selectors/active.json`.")
        if not as_string(selector_evidence, "active_selector_status"):
            errors.append(f"{label}.selector_evidence.active_selector_status is required.")
    version_evidence = data.get("version_evidence")
    if not isinstance(version_evidence, dict):
        errors.append(f"{label}.version_evidence must be an object.")
    else:
        for backend_name in READINESS_BACKENDS:
            backend_evidence = version_evidence.get(backend_name)
            if not isinstance(backend_evidence, dict):
                errors.append(f"{label}.version_evidence.{backend_name} must be an object.")
            elif not as_string(backend_evidence, "install_state"):
                errors.append(f"{label}.version_evidence.{backend_name}.install_state is required.")
    if not isinstance(data.get("blockers"), list):
        errors.append(f"{label}.blockers must be an array.")
    if promotion_marker == READINESS_PROMOTION_MARKER and data.get("durable_workflow_adopted") is not False:
        errors.append(f"{label}.durable_workflow_adopted must be false for readiness refresh receipts.")
    if data.get("persistent_team_launched") is not False:
        errors.append(f"{label}.persistent_team_launched must be false for readiness refresh receipts.")
    smoke = data.get("smoke")
    if not isinstance(smoke, dict):
        errors.append(f"{label}.smoke must be an object.")
    else:
        if as_string(smoke, "marker") != READINESS_PROMOTION_MARKER:
            errors.append(f"{label}.smoke.marker must be `{READINESS_PROMOTION_MARKER}`.")
        if smoke.get("launched_backend") is not False:
            errors.append(f"{label}.smoke.launched_backend must be false.")
        if smoke.get("launched_persistent_team") is not False:
            errors.append(f"{label}.smoke.launched_persistent_team must be false.")
    if promotion_marker == READINESS_R5_PROMOTION_MARKER:
        active = data.get("active_candidate_receipt")
        if not isinstance(active, dict):
            errors.append(f"{label}.active_candidate_receipt must be an object for R5 readiness receipts.")
        else:
            if as_string(active, "runtime_stage").lower().replace("_", "-") not in {"r5", "active-candidate"}:
                errors.append(f"{label}.active_candidate_receipt.runtime_stage must be R5 or active-candidate.")
            if not as_string(active, "receipt_path_hash"):
                errors.append(f"{label}.active_candidate_receipt.receipt_path_hash is required.")
            if not as_string(active, "authorization_receipt_hash"):
                errors.append(f"{label}.active_candidate_receipt.authorization_receipt_hash is required.")
            if not as_string(active, "owner_lease_hash"):
                errors.append(f"{label}.active_candidate_receipt.owner_lease_hash is required.")
            if not as_string(active, "rollback_pointer_hash"):
                errors.append(f"{label}.active_candidate_receipt.rollback_pointer_hash is required.")
            if active.get("remote_publication_mutated") is not False:
                errors.append(f"{label}.active_candidate_receipt.remote_publication_mutated must be false.")
    return {"receipt_kind": receipt_kind, "promotion_marker": promotion_marker, "generated_at": generated_at}


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
