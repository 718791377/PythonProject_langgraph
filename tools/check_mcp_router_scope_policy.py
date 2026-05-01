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
CODEX_DEDICATED = ("omx_state", "omx_memory", "omx_code_intel", "omx_trace")
ROUTER_SHARED = ("chrome-devtools", "pencil")
ROUTER_BRIDGE = "mcp_router"
ROUTER_FORBIDDEN = {"omx_state", "omx_memory", "omx_code_intel", "omx_trace", "mcp-router", "mcp_router"}


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


def check_codex_config(path: Path | None, errors: list[str], warnings: list[str], info: list[str]) -> dict[str, Any]:
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

    for name in CODEX_DEDICATED:
        cfg = servers.get(name)
        if not isinstance(cfg, dict):
            errors.append(f"Codex-dedicated MCP server `{name}` is missing from Codex config `{path}`.")
        elif not mcp_enabled(cfg):
            errors.append(f"Codex-dedicated MCP server `{name}` must be enabled directly in Codex config `{path}`.")

    router_cfg = servers.get(ROUTER_BRIDGE)
    if not isinstance(router_cfg, dict):
        errors.append(f"Codex MCP Router bridge `{ROUTER_BRIDGE}` is missing from Codex config `{path}`.")
    elif not mcp_enabled(router_cfg):
        errors.append(f"Codex MCP Router bridge `{ROUTER_BRIDGE}` must remain enabled in Codex config `{path}`.")

    if isinstance(servers.get("mcp-router"), dict):
        errors.append("Codex config contains `mcp-router`; use `mcp_router` as the Codex-side bridge name instead.")

    for name in ROUTER_SHARED:
        cfg = servers.get(name)
        if isinstance(cfg, dict) and mcp_enabled(cfg):
            errors.append(
                f"Shared MCP server `{name}` should be disabled or absent as a direct Codex server when MCP Router is enabled."
            )

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
        message = f"MCP Router contains active forbidden server `{name}`; keep Codex-dedicated or Router self-reference servers out of MCP Router."
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


def run_check(root: Path, codex_config: Path | None, router_db: Path | None, strict_router_state: bool) -> dict[str, Any]:
    del root  # The checker is local-runtime oriented but keeps --root for guard consistency.
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    codex = check_codex_config(codex_config, errors, warnings, info)
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
        "policy": {
            "codex_dedicated": list(CODEX_DEDICATED),
            "router_shared": list(ROUTER_SHARED),
            "router_bridge": ROUTER_BRIDGE,
            "router_forbidden": sorted(ROUTER_FORBIDDEN),
        },
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "router_forbidden_records": len(router.get("forbidden_records", [])),
            "router_forbidden_access": len(router.get("forbidden_access", [])),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex and MCP Router server scope policy.")
    parser.add_argument("--root", default=".", help="Repository root; retained for guard consistency.")
    parser.add_argument("--codex-config", help="Explicit Codex config.toml path.")
    parser.add_argument("--mcp-router-db", help="Explicit MCP Router mcprouter.db path.")
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
    payload = run_check(root, codex_config, router_db, args.strict_router_state)

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
