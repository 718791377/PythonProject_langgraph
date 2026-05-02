#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "mcp_router_scope_policy"
CODEX_PRIVATE = ("omx_state", "omx_memory", "omx_code_intel", "omx_trace")
CODEX_DIRECT_UTILITY = ("chrome-devtools", "pencil")
CODEX_DIRECT_REQUIRED = CODEX_PRIVATE + CODEX_DIRECT_UTILITY
ROUTER_BRIDGE = "mcp_router"
ROUTER_SELF_REFERENCE = {"mcp-router", "mcp_router"}
ROUTER_FORBIDDEN = set(CODEX_PRIVATE) | ROUTER_SELF_REFERENCE
DEFAULT_EXCEPTIONS_PATH = Path("tools/mcp_router_scope_policy_exceptions.json")
MCP_ROUTER_DISABLED_EXCEPTION_SCOPE = "codex_mcp_router_bridge_disabled"


def default_codex_config() -> Path | None:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "config.toml"
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return Path(user_profile) / ".codex" / "config.toml"
    home = Path.home()
    if str(home):
        return home / ".codex" / "config.toml"
    return None


def default_router_db() -> Path | None:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "MCP Router" / "mcprouter.db"
    return None


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None


def load_exceptions(root: Path, exceptions_path: Path | None, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(exceptions_path) if exceptions_path else None,
        "present": False,
        "active": [],
        "invalid": [],
    }
    if exceptions_path is None:
        return result
    path = exceptions_path if exceptions_path.is_absolute() else root / exceptions_path
    result["path"] = str(path)
    if not path.exists():
        return result
    result["present"] = True
    data = read_json(path)
    if not isinstance(data, dict):
        errors.append(f"MCP scope policy exception file `{path}` must be a JSON object.")
        return result
    if data.get("schema_version") != 1:
        errors.append(f"MCP scope policy exception file `{path}` must declare `schema_version` 1.")
    exceptions = data.get("exceptions", [])
    if not isinstance(exceptions, list):
        errors.append(f"MCP scope policy exception file `{path}` must contain an `exceptions` list.")
        return result
    required = ("id", "status", "scope", "reason", "recovery_condition")
    for item in exceptions:
        if not isinstance(item, dict):
            result["invalid"].append(item)
            errors.append(f"MCP scope policy exception file `{path}` contains a non-object exception entry.")
            continue
        missing = [key for key in required if not isinstance(item.get(key), str) or not item.get(key, "").strip()]
        if missing:
            result["invalid"].append(item)
            errors.append(f"MCP scope policy exception `{item.get('id', '<missing id>')}` is missing required fields: {', '.join(missing)}.")
            continue
        if item.get("status") == "active":
            result["active"].append(item)
        elif item.get("status") not in {"inactive", "resolved"}:
            warnings.append(f"MCP scope policy exception `{item.get('id')}` has unknown status `{item.get('status')}`.")
    return result


def active_mcp_router_disabled_exception(exceptions: dict[str, Any]) -> dict[str, Any] | None:
    for item in exceptions.get("active", []):
        if isinstance(item, dict) and item.get("scope") == MCP_ROUTER_DISABLED_EXCEPTION_SCOPE:
            return item
    return None


def mcp_enabled(config: dict[str, Any]) -> bool:
    value = config.get("enabled", True)
    return value is not False


def load_codex_config(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        errors.append(f"Unable to read Codex config `{path}`: {exc}")
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"Unable to parse Codex config `{path}` as TOML: {exc}")
    return None


def check_codex_config(
    path: Path | None,
    errors: list[str],
    warnings: list[str],
    info: list[str],
    exceptions: dict[str, Any],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path) if path else None,
        "present": False,
        "servers": {},
    }
    if path is None:
        info.append("Codex config path could not be resolved; skipping local Codex MCP scope check.")
        return result
    if not path.exists():
        info.append(f"Codex config is absent; skipping local Codex MCP scope check: {path}")
        return result

    data = load_codex_config(path, errors)
    if data is None:
        return result
    result["present"] = True
    servers = data.get("mcp_servers", {})
    if not isinstance(servers, dict):
        errors.append(f"Codex config `{path}` has no valid `mcp_servers` table.")
        return result

    for name in sorted(servers):
        value = servers.get(name)
        if isinstance(value, dict):
            result["servers"][name] = {
                "enabled": mcp_enabled(value),
                "explicit_enabled": value.get("enabled", "<implicit>"),
                "command": value.get("command"),
            }

    for name in CODEX_DIRECT_REQUIRED:
        cfg = servers.get(name)
        if not isinstance(cfg, dict):
            errors.append(f"Codex direct MCP server `{name}` is missing from Codex config `{path}`.")
        elif not mcp_enabled(cfg):
            errors.append(f"Codex direct MCP server `{name}` must be enabled directly in Codex config `{path}`.")

    router_cfg = servers.get(ROUTER_BRIDGE)
    router_enabled = isinstance(router_cfg, dict) and mcp_enabled(router_cfg)
    if isinstance(router_cfg, dict) and router_enabled:
        errors.append(
            f"Codex MCP Router bridge `{ROUTER_BRIDGE}` must remain disabled; "
            "Codex uses direct MCP entries for browser, design, and orchestration tools."
        )
    elif isinstance(router_cfg, dict):
        result["mcp_router_disabled_by_policy"] = True
        exception = active_mcp_router_disabled_exception(exceptions)
        if exception:
            result["mcp_router_disabled_exception"] = {
                "id": exception.get("id"),
                "reason": exception.get("reason"),
                "recovery_condition": exception.get("recovery_condition"),
            }
            info.append(
                f"Codex MCP Router bridge `{ROUTER_BRIDGE}` is disabled by policy; "
                f"legacy exception `{exception.get('id')}` is present for audit history."
            )
    else:
        info.append(f"Codex MCP Router bridge `{ROUTER_BRIDGE}` is absent; this is acceptable because Codex does not use MCP Router by default.")

    if isinstance(servers.get("mcp-router"), dict):
        errors.append("Codex config contains `mcp-router`; use `mcp_router` as the Codex-side bridge name instead.")

    return result


def router_rows_from_db(path: Path, warnings: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        warnings.append(f"Unable to open MCP Router database `{path}`: {exc}")
        return rows
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.execute("SELECT name, command, args, auto_start, disabled, id FROM servers ORDER BY name")
        for row in cursor.fetchall():
            rows.append({key: row[key] for key in row.keys()})
    except sqlite3.Error as exc:
        warnings.append(f"Unable to read MCP Router servers table from `{path}`: {exc}")
    finally:
        connection.close()
    return rows


def load_router_access(shared_config_path: Path, id_to_name: dict[str, str]) -> list[dict[str, Any]]:
    data = read_json(shared_config_path)
    if not isinstance(data, dict):
        return []
    tokens = ((data.get("mcpApps") or {}).get("tokens") or []) if isinstance(data.get("mcpApps"), dict) else []
    access_rows: list[dict[str, Any]] = []
    for token in tokens:
        if not isinstance(token, dict):
            continue
        client_id = token.get("clientId")
        access = token.get("serverAccess") or {}
        if not isinstance(access, dict):
            continue
        for server_id, allowed in access.items():
            name = id_to_name.get(str(server_id))
            if name and allowed is True:
                access_rows.append({"clientId": client_id, "server_id": server_id, "name": name})
    return access_rows


def is_disabled(row: dict[str, Any]) -> bool:
    value = row.get("disabled")
    try:
        return int(value) == 1
    except (TypeError, ValueError):
        return False


def check_router_state(
    path: Path | None,
    strict_router_state: bool,
    errors: list[str],
    warnings: list[str],
    info: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path) if path else None,
        "present": False,
        "servers": [],
        "forbidden_records": [],
        "forbidden_access": [],
        "strict_router_state": strict_router_state,
    }
    if path is None:
        info.append("MCP Router database path could not be resolved; skipping local Router-state check.")
        return result
    if not path.exists():
        info.append(f"MCP Router database is absent; skipping local Router-state check: {path}")
        return result

    result["present"] = True
    rows = router_rows_from_db(path, warnings)
    result["servers"] = rows
    id_to_name = {str(row.get("id")): str(row.get("name")) for row in rows if row.get("id") and row.get("name")}
    for row in rows:
        name = str(row.get("name", ""))
        normalized = name.lower()
        if normalized not in ROUTER_FORBIDDEN:
            continue
        record = {
            "name": name,
            "id": row.get("id"),
            "disabled": row.get("disabled"),
            "auto_start": row.get("auto_start"),
            "command": row.get("command"),
        }
        result["forbidden_records"].append(record)
        if is_disabled(row):
            warnings.append(f"MCP Router contains disabled migration residue for forbidden server `{name}`.")
            continue
        message = f"MCP Router contains active forbidden server `{name}`; keep Codex-private or Router self-reference servers out of MCP Router."
        if strict_router_state:
            errors.append(message)
        else:
            warnings.append(message)

    shared_config = path.with_name("shared-config.json")
    if shared_config.exists():
        for access in load_router_access(shared_config, id_to_name):
            normalized = str(access.get("name", "")).lower()
            if normalized in ROUTER_FORBIDDEN:
                result["forbidden_access"].append(access)
                message = (
                    f"MCP Router token for client `{access.get('clientId')}` still grants access to forbidden server "
                    f"`{access.get('name')}`."
                )
                if strict_router_state:
                    errors.append(message)
                else:
                    warnings.append(message)
    return result


def run_check(
    root: Path,
    codex_config: Path | None,
    router_db: Path | None,
    strict_router_state: bool,
    exceptions_path: Path | None,
) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    exceptions = load_exceptions(root, exceptions_path, errors, warnings)
    codex = check_codex_config(codex_config, errors, warnings, info, exceptions)
    router = check_router_state(router_db, strict_router_state, errors, warnings, info)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "codex_config": codex,
        "mcp_router": router,
        "exceptions": exceptions,
        "policy": {
            "codex_private": list(CODEX_PRIVATE),
            "codex_direct_utility": list(CODEX_DIRECT_UTILITY),
            "codex_direct_required": list(CODEX_DIRECT_REQUIRED),
            "router_bridge": ROUTER_BRIDGE,
            "router_forbidden": sorted(ROUTER_FORBIDDEN),
        },
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "router_forbidden_records": len(router.get("forbidden_records", [])),
            "router_forbidden_access": len(router.get("forbidden_access", [])),
            "active_exceptions": len(exceptions.get("active", [])),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex and MCP Router server scope policy.")
    parser.add_argument("--root", default=".", help="Repository root; retained for guard consistency.")
    parser.add_argument("--codex-config", help="Explicit Codex config.toml path.")
    parser.add_argument("--mcp-router-db", help="Explicit MCP Router mcprouter.db path.")
    parser.add_argument(
        "--exceptions-path",
        default=DEFAULT_EXCEPTIONS_PATH.as_posix(),
        help="Repository-relative or absolute JSON file declaring temporary MCP scope exceptions.",
    )
    parser.add_argument(
        "--strict-router-state",
        action="store_true",
        help="Treat forbidden MCP Router records or access grants as blocking errors.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    codex_config = Path(args.codex_config).resolve() if args.codex_config else default_codex_config()
    router_db = Path(args.mcp_router_db).resolve() if args.mcp_router_db else default_router_db()
    exceptions_path = Path(args.exceptions_path).resolve() if Path(args.exceptions_path).is_absolute() else Path(args.exceptions_path)
    payload = run_check(root, codex_config, router_db, args.strict_router_state, exceptions_path)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(f"INFO: {message}")
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
        if payload["ok"]:
            print("MCP Router scope policy check passed.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
