from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ARTIFACT_KIND = "project_moe_gui_handoff"
CANONICAL_ARTIFACT_KIND = "project_expert_lens_gui_handoff"
RUNTIME_RELATIVE = Path(".project-runtime/project_moe_gui")
STATUS_DIRECTORIES = {
    "draft": "workbench_drafts",
    "queued": "handoff_queue",
    "copied": "expert_history",
    "completed": "expert_history",
    "superseded": "expert_history",
}
VALID_HANDOFF_TARGETS = {"main-session", "native-experts", "subagent", "durable-team", "persistent-team", "langgraph-workflow"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(value: Any) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def runtime_root(target_project: str | Path) -> Path:
    return Path(target_project).expanduser().resolve(strict=False) / RUNTIME_RELATIVE


def _safe_text(value: Any, *, limit: int = 4000) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, (str, int, float)):
            text = str(item).strip()
            if text:
                result.append(text)
    return result


def _execution_policy() -> dict[str, bool]:
    return {
        "starts_codex": False,
        "starts_native_experts": False,
        "starts_subagents": False,
        "starts_durable_team": False,
        "starts_persistent_team": False,
        "starts_langgraph_workflow": False,
        "calls_model_api": False,
        "writes_target_project_state": False,
        "gui_direct_state_write": False,
        "executes_target": False,
    }


def _target_project_display(target_project: str | Path) -> str:
    return str(Path(target_project).expanduser().resolve(strict=False))


def create_handoff_package(
    *,
    target_project: str | Path,
    session_id: str | None,
    session_display_id: str,
    selected_lenses: list[str] | None = None,
    selected_categories: list[str] | None = None,
    handoff_target: str = "main-session",
    task_template_id: str = "default",
    brief_text: str = "",
    status: str = "draft",
    created_at: str | None = None,
) -> dict[str, Any]:
    created = created_at or utc_now_iso()
    normalized_target = _target_project_display(target_project)
    session_key_hash = stable_hash(session_id or session_display_id)
    handoff_target = handoff_target if handoff_target in VALID_HANDOFF_TARGETS else "main-session"
    normalized_status = status if status in STATUS_DIRECTORIES else "draft"
    lenses = _string_list(selected_lenses or [])
    categories = _string_list(selected_categories or [])
    brief = _safe_text(brief_text)
    artifact_seed = json.dumps(
        {
            "target_project": normalized_target,
            "session_key_hash": session_key_hash,
            "selected_lenses": lenses,
            "selected_categories": categories,
            "handoff_target": handoff_target,
            "task_template_id": task_template_id,
            "brief_text": brief,
            "created_at": created,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    artifact_id = stable_hash(artifact_seed)[:24]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": ARTIFACT_KIND,
        "canonical_artifact_kind": CANONICAL_ARTIFACT_KIND,
        "artifact_id": artifact_id,
        "created_at": created,
        "updated_at": created,
        "target_project": normalized_target,
        "session_display_id": _safe_text(session_display_id, limit=120),
        "session_key_hash": session_key_hash,
        "selected_lenses": lenses,
        "selected_categories": categories,
        "selected_expert_lenses": lenses,
        "selected_expert_categories": categories,
        "effective_expert_lens_mode": "selected" if (lenses or categories) else "all",
        "handoff_target": handoff_target,
        "task_template_id": _safe_text(task_template_id, limit=120),
        "brief_text": brief,
        "status": normalized_status,
        "execution_policy": _execution_policy(),
        "privacy_policy": {
            "raw_session_id_serialized": False,
            "private_prompt_body_serialized": False,
            "developer_instructions_serialized": False,
        },
    }


def _artifact_dir(target_project: str | Path, status: str) -> Path:
    directory = STATUS_DIRECTORIES.get(status, "expert_history")
    return runtime_root(target_project) / directory


def save_handoff_artifact(target_project: str | Path, package: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(package, dict) or package.get("artifact_kind") != ARTIFACT_KIND:
        return {
            "ok": False,
            "token": "blocked:invalid_handoff_artifact",
            "message": "Project Expert Lens handoff artifact must be a JSON object with a compatible artifact_kind.",
        }
    status = str(package.get("status") or "draft")
    artifact_id = str(package.get("artifact_id") or stable_hash(json.dumps(package, sort_keys=True, default=str))[:24])
    target_dir = _artifact_dir(target_project, status)
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(package)
    payload["artifact_id"] = artifact_id
    payload["updated_at"] = utc_now_iso()
    path = target_dir / f"{artifact_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "token": "ok",
        "path": str(path),
        "artifact_id": artifact_id,
        "status": status,
        "writes_target_project_state": False,
    }


def _load_artifact(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    if not isinstance(payload, dict) or payload.get("artifact_kind") != ARTIFACT_KIND:
        return None
    payload.setdefault("path", str(path))
    return payload


def list_handoff_artifacts(
    target_project: str | Path,
    *,
    handoff_target: str | None = None,
    status: str | None = None,
    lens: str | None = None,
    category: str | None = None,
    session_key_hash: str | None = None,
) -> dict[str, Any]:
    root = runtime_root(target_project)
    items: list[dict[str, Any]] = []
    for directory in STATUS_DIRECTORIES.values():
        candidate = root / directory
        if not candidate.exists():
            continue
        for path in sorted(candidate.glob("*.json")):
            payload = _load_artifact(path)
            if payload is None:
                continue
            if handoff_target and payload.get("handoff_target") != handoff_target:
                continue
            if status and payload.get("status") != status:
                continue
            if lens and lens not in _string_list(payload.get("selected_lenses")):
                continue
            if category and category not in _string_list(payload.get("selected_categories")):
                continue
            if session_key_hash and payload.get("session_key_hash") != session_key_hash:
                continue
            items.append(payload)
    items.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return {
        "ok": True,
        "token": "ok",
        "runtime_root": str(root),
        "items": items,
        "count": len(items),
        "read_only": True,
    }


def carrier_instructions_for(handoff_target: str) -> str:
    if handoff_target in {"native-experts", "subagent"}:
        return "Paste this package into one or more native expert/subagent tasks. The GUI does not spawn experts or subagents."
    if handoff_target == "durable-team":
        return "Use this package as a durable team brief after the leader confirms the durable-team threshold."
    if handoff_target == "persistent-team":
        return "Use this package as a persistent team brief after the leader confirms the persistent-team threshold."
    if handoff_target == "langgraph-workflow":
        return "Use this package as a LangGraph workflow brief or checkpoint artifact. The GUI does not invoke LangGraph."
    return "Use this package directly in the main session with the selected expert lenses."


def export_handoff_package(package: dict[str, Any], handoff_target: str) -> dict[str, Any]:
    payload = deepcopy(package)
    normalized_target = handoff_target if handoff_target in VALID_HANDOFF_TARGETS else "main-session"
    payload["handoff_target"] = normalized_target
    payload["status"] = "copied"
    payload["exported_at"] = utc_now_iso()
    payload["execution_policy"] = {**_execution_policy(), **dict(payload.get("execution_policy") or {})}
    payload["execution_policy"]["executes_target"] = False
    payload["carrier_instructions"] = carrier_instructions_for(normalized_target)
    lenses = ", ".join(_string_list(payload.get("selected_lenses"))) or "all lenses"
    categories = ", ".join(_string_list(payload.get("selected_categories"))) or "all categories"
    payload["export_text"] = "\n".join(
        [
            "Project Expert Lens handoff package",
            f"Handoff target: {normalized_target}",
            f"Session: {payload.get('session_display_id') or '<none>'}",
            f"Lenses: {lenses}",
            f"Categories: {categories}",
            f"Task template: {payload.get('task_template_id') or '<none>'}",
            "",
            "Brief:",
            str(payload.get("brief_text") or ""),
            "",
            "Carrier instructions:",
            payload["carrier_instructions"],
            "",
            "Execution boundary: artifact export only; no carrier is executed by the GUI.",
        ]
    )
    return payload
