"""Repo-local runtime helpers for LangGraph durable orchestration."""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any


def resolve_repo_root(repo_root: str | None) -> Path:
    if repo_root:
        return Path(repo_root).resolve()
    return Path.cwd().resolve()


def detect_worktree_id(repo_root: Path) -> str:
    cwd = Path.cwd().resolve()
    if cwd == repo_root:
        return repo_root.name
    if repo_root in cwd.parents:
        return cwd.name
    return repo_root.name


def langgraph_state_root(repo_root: Path) -> Path:
    return repo_root / ".omx" / "state" / "langgraph"


def selector_state_root(repo_root: Path) -> Path:
    return repo_root / ".omx" / "state" / "selectors"


def ensure_layout(repo_root: Path) -> dict[str, str]:
    root = langgraph_state_root(repo_root)
    selector_root = selector_state_root(repo_root)
    paths = {
        "root": root,
        "threads": root / "threads",
        "checkpoints": root / "checkpoints",
        "history": root / "history",
        "interrupts": root / "interrupts",
        "store": root / "store",
        "selectors": selector_root,
        "selector_leases": selector_root / "leases",
        "backend": root / "backend.json",
        "active_selector": selector_root / "active.json",
    }
    for key, value in paths.items():
        if key in {"backend", "active_selector"}:
            continue
        value.mkdir(parents=True, exist_ok=True)
    return {key: str(value) for key, value in paths.items()}


def stable_thread_id(repo_root: Path, worktree_id: str, task_id: str | None = None) -> str:
    repo_hash = hashlib.sha1(str(repo_root).encode("utf-8")).hexdigest()[:12]
    resolved_task_id = task_id or f"task-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    return f"{repo_hash}:{worktree_id}:{resolved_task_id}"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def backend_record_path(repo_root: Path) -> Path:
    return langgraph_state_root(repo_root) / "backend.json"


def active_selector_path(repo_root: Path) -> Path:
    return selector_state_root(repo_root) / "active.json"


def selector_lease_path(repo_root: Path, session_scope_id: str) -> Path:
    return selector_state_root(repo_root) / "leases" / f"{session_scope_id}.json"


def _thread_file_key(thread_id: str) -> str:
    return thread_id.replace(":", "__")


def load_backend_record(repo_root: Path) -> dict[str, Any]:
    return _read_json(backend_record_path(repo_root), {})


def save_backend_record(repo_root: Path, payload: dict[str, Any]) -> Path:
    path = backend_record_path(repo_root)
    _write_json(path, payload)
    return path


def load_active_selector(repo_root: Path) -> dict[str, Any]:
    return _read_json(active_selector_path(repo_root), {})


def save_active_selector(repo_root: Path, payload: dict[str, Any]) -> Path:
    path = active_selector_path(repo_root)
    _write_json(path, payload)
    return path


def read_selector_lease(repo_root: Path, session_scope_id: str) -> dict[str, Any]:
    return _read_json(selector_lease_path(repo_root, session_scope_id), {})


def write_selector_lease(repo_root: Path, session_scope_id: str, payload: dict[str, Any]) -> Path:
    path = selector_lease_path(repo_root, session_scope_id)
    _write_json(path, payload)
    return path


def thread_record_path(repo_root: Path, thread_id: str) -> Path:
    return langgraph_state_root(repo_root) / "threads" / f"{_thread_file_key(thread_id)}.json"


def checkpoint_record_path(repo_root: Path, thread_id: str) -> Path:
    return langgraph_state_root(repo_root) / "checkpoints" / f"{_thread_file_key(thread_id)}.json"


def history_record_path(repo_root: Path, thread_id: str) -> Path:
    return langgraph_state_root(repo_root) / "history" / f"{_thread_file_key(thread_id)}.json"


def interrupt_record_path(repo_root: Path, thread_id: str) -> Path:
    return langgraph_state_root(repo_root) / "interrupts" / f"{_thread_file_key(thread_id)}.json"


def implementation_brief_path(repo_root: Path, thread_id: str) -> Path:
    return langgraph_state_root(repo_root) / "store" / "briefs" / f"{_thread_file_key(thread_id)}.json"


def survivor_queue_path(repo_root: Path, thread_id: str) -> Path:
    return langgraph_state_root(repo_root) / "store" / "survivors" / f"{_thread_file_key(thread_id)}.json"


def release_receipt_path(repo_root: Path, thread_id: str) -> Path:
    return langgraph_state_root(repo_root) / "store" / "releases" / f"{_thread_file_key(thread_id)}.json"


def write_thread_record(repo_root: Path, payload: dict[str, Any]) -> Path:
    path = thread_record_path(repo_root, payload["thread_id"])
    _write_json(path, payload)
    return path


def read_thread_record(repo_root: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(thread_record_path(repo_root, thread_id), {})


def write_checkpoint(repo_root: Path, payload: dict[str, Any]) -> Path:
    path = checkpoint_record_path(repo_root, payload["thread_id"])
    _write_json(path, payload)
    return path


def read_checkpoint(repo_root: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(checkpoint_record_path(repo_root, thread_id), {})


def write_history(repo_root: Path, payload: dict[str, Any]) -> Path:
    path = history_record_path(repo_root, payload["thread_id"])
    _write_json(path, payload)
    return path


def read_history(repo_root: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(history_record_path(repo_root, thread_id), {})


def write_interrupt(repo_root: Path, payload: dict[str, Any]) -> Path:
    path = interrupt_record_path(repo_root, payload["thread_id"])
    _write_json(path, payload)
    return path


def read_interrupt(repo_root: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(interrupt_record_path(repo_root, thread_id), {})


def delete_interrupt(repo_root: Path, thread_id: str) -> None:
    path = interrupt_record_path(repo_root, thread_id)
    if path.exists():
        path.unlink()


def write_implementation_brief(repo_root: Path, thread_id: str, payload: dict[str, Any]) -> Path:
    path = implementation_brief_path(repo_root, thread_id)
    _write_json(path, payload)
    return path


def read_implementation_brief(repo_root: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(implementation_brief_path(repo_root, thread_id), {})


def write_survivor_queue(repo_root: Path, thread_id: str, payload: dict[str, Any]) -> Path:
    path = survivor_queue_path(repo_root, thread_id)
    _write_json(path, payload)
    return path


def read_survivor_queue(repo_root: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(survivor_queue_path(repo_root, thread_id), {})


def write_release_receipt(repo_root: Path, thread_id: str, payload: dict[str, Any]) -> Path:
    path = release_receipt_path(repo_root, thread_id)
    _write_json(path, payload)
    return path


def read_release_receipt(repo_root: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(release_receipt_path(repo_root, thread_id), {})
