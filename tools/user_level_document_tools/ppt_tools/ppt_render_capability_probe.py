#!/usr/bin/env python3
"""Probe local PPT render toolchain capabilities without mutating PATH."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_CONFIG_NAME = "ppt_render_toolchain_config.example.json"
KNOWN_TOOL_NAMES = {
    "soffice": ("soffice.exe", "soffice", "libreoffice"),
    "magick": ("magick.exe", "magick"),
    "ghostscript": ("gswin64c.exe", "gswin32c.exe", "gs.exe", "gswin64c"),
    "inkscape": ("inkscape.exe", "inkscape"),
    "pdftoppm": ("pdftoppm.exe", "pdftoppm"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(path: str | None) -> tuple[dict[str, Any], str | None, str | None]:
    if not path:
        default = Path(__file__).with_name(DEFAULT_CONFIG_NAME)
        if default.exists():
            path = str(default)
    if not path:
        return {}, None, None
    config_path = Path(path)
    if not config_path.exists():
        return {}, str(config_path), "config_not_found"
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8-sig"))
        if not isinstance(payload, dict):
            return {}, str(config_path), "config_not_object"
        return payload, str(config_path.resolve()), None
    except Exception as exc:  # noqa: BLE001 - JSON error payload, not traceback-only
        return {}, str(config_path), f"config_error:{exc.__class__.__name__}:{exc}"


def is_abs_file(value: Any) -> tuple[bool, bool, str]:
    if not isinstance(value, str) or not value.strip():
        return False, False, ""
    path = Path(value)
    if not path.is_absolute():
        return False, False, str(path)
    return True, path.is_file(), str(path)


def is_abs_dir(value: Any) -> tuple[bool, bool, str]:
    if not isinstance(value, str) or not value.strip():
        return False, False, ""
    path = Path(value)
    if not path.is_absolute():
        return False, False, str(path)
    return True, path.is_dir(), str(path)


def find_configured_or_path(config_value: Any, names: Iterable[str], *, allow_path: bool) -> tuple[bool, str, str]:
    """Return installed/path/probe_status. Configured non-absolute paths are not accepted."""
    if isinstance(config_value, str) and config_value.strip():
        absolute, exists, normalized = is_abs_file(config_value)
        if not absolute:
            return False, normalized, "configured_path_not_absolute"
        return exists, normalized, "configured_found" if exists else "configured_missing"
    if allow_path:
        for name in names:
            found = shutil.which(name)
            if found:
                return True, str(Path(found).resolve()), "found_on_process_path"
    return False, "", "not_found"


def find_poppler(config: dict[str, Any], *, allow_path: bool) -> tuple[bool, str, str]:
    poppler = config.get("poppler_bin_dir")
    if isinstance(poppler, str) and poppler.strip():
        absolute, exists, normalized = is_abs_dir(poppler)
        if not absolute:
            return False, normalized, "configured_dir_not_absolute"
        if not exists:
            return False, normalized, "configured_dir_missing"
        for name in KNOWN_TOOL_NAMES["pdftoppm"]:
            candidate = Path(normalized) / name
            if candidate.exists():
                return True, str(candidate.resolve()), "configured_found"
        return False, normalized, "pdftoppm_missing_in_configured_dir"
    if allow_path:
        found = shutil.which("pdftoppm")
        if found:
            return True, str(Path(found).resolve()), "found_on_process_path"
    return False, "", "not_found"


def run_version(path: str, args: list[str], timeout: int = 10) -> tuple[bool, str]:
    if not path:
        return False, ""
    try:
        proc = subprocess.run([path, *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        text = "\n".join((proc.stdout or "").splitlines()[:5])
        return proc.returncode == 0 or bool(text), text
    except Exception as exc:  # noqa: BLE001
        return False, f"version_probe_failed:{exc.__class__.__name__}:{exc}"


def module_record(name: str, *, enabled: bool = True, selected: bool = True, package: str | None = None) -> dict[str, Any]:
    try:
        spec = importlib.util.find_spec(name)
        installed = spec is not None
        origin = getattr(spec, "origin", "") if spec else ""
        status = "found" if installed else "not_found"
    except Exception as exc:  # noqa: BLE001
        installed = False
        origin = ""
        status = f"probe_error:{exc.__class__.__name__}:{exc}"
    return {
        "name": package or name,
        "kind": "python_module",
        "module": name,
        "installed": installed,
        "enabled": enabled,
        "selected": selected,
        "ready": bool(installed and enabled and selected),
        "path": origin or "",
        "probe_status": status,
        "notes": "",
    }


def executable_record(name: str, config: dict[str, Any], config_key: str, version_args: list[str], *, allow_path: bool, enabled: bool = True, selected: bool = True) -> dict[str, Any]:
    installed, path, probe_status = find_configured_or_path(config.get(config_key), KNOWN_TOOL_NAMES.get(name, (name,)), allow_path=allow_path)
    version_ok = False
    version = ""
    if installed:
        version_ok, version = run_version(path, version_args)
    ready = bool(installed and enabled and selected and version_ok)
    if installed and not version_ok and version:
        probe_status = f"{probe_status};version_probe_warning"
    return {
        "name": name,
        "kind": "executable",
        "installed": bool(installed),
        "enabled": bool(enabled),
        "selected": bool(selected),
        "ready": ready,
        "path": path,
        "probe_status": probe_status,
        "version": version,
        "notes": "configured paths must be absolute; PATH lookup is process-scoped only" if allow_path else "PATH lookup disabled by caller",
    }


def powerpoint_record(config: dict[str, Any], *, probe_com: bool) -> dict[str, Any]:
    enabled = bool(config.get("powerpoint_com_enabled", True))
    selected = True
    record: dict[str, Any] = {
        "name": "powerpoint",
        "kind": "com",
        "installed": False,
        "enabled": enabled,
        "selected": selected,
        "ready": False,
        "path": "",
        "probe_status": "not_probed",
        "version": "",
        "user_interactive": None,
        "notes": "Use powerpoint_com_probe.ps1 for export and leak-check evidence.",
    }
    if os.name != "nt":
        record["probe_status"] = "not_windows"
        return record
    powerpnt = shutil.which("POWERPNT.EXE") or shutil.which("powerpnt.exe")
    for candidate in (
        Path(os.environ.get("ProgramFiles", "")) / "Microsoft Office" / "root" / "Office16" / "POWERPNT.EXE",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Microsoft Office" / "root" / "Office16" / "POWERPNT.EXE",
    ):
        if not powerpnt and candidate.exists():
            powerpnt = str(candidate.resolve())
    record["installed"] = bool(powerpnt)
    record["path"] = powerpnt or ""
    if not enabled:
        record["probe_status"] = "disabled_by_config"
        return record
    if not probe_com:
        record["probe_status"] = "installed_check_only" if powerpnt else "not_found"
        record["ready"] = False
        return record
    ps = shutil.which("powershell") or shutil.which("pwsh")
    if not ps:
        record["probe_status"] = "powershell_not_found"
        return record
    script = """
$ErrorActionPreference='Stop'
$result=[ordered]@{ user_interactive=[Environment]::UserInteractive; ok=$false; version=''; error='' }
$app=$null
try {
  $app=New-Object -ComObject PowerPoint.Application
  $result.version=[string]$app.Version
  $result.ok=$true
} catch { $result.error=$_.Exception.Message } finally {
  if ($null -ne $app) { try { $app.Quit() | Out-Null } catch {}; try { [Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null } catch {} }
}
$result | ConvertTo-Json -Compress
if (-not $result.ok) { exit 1 }
"""
    try:
        proc = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        text = proc.stdout.strip()
        payload = json.loads(text.splitlines()[-1]) if text else {}
        record["user_interactive"] = payload.get("user_interactive")
        record["version"] = payload.get("version") or ""
        record["ready"] = bool(proc.returncode == 0 and payload.get("ok") and enabled)
        if payload.get("ok"):
            record["installed"] = True
        record["probe_status"] = "com_ready" if record["ready"] else f"com_failed:{payload.get('error') or text}"
    except Exception as exc:  # noqa: BLE001
        record["probe_status"] = f"com_probe_error:{exc.__class__.__name__}:{exc}"
    return record


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    config, config_path, config_error = load_config(args.config)
    allow_path = not args.no_path_lookup
    records: list[dict[str, Any]] = []
    records.append(powerpoint_record(config, probe_com=args.probe_com))
    records.append(executable_record("soffice", config, "soffice_exe", ["--version"], allow_path=allow_path))
    aspose = module_record("aspose.slides", enabled=bool(config.get("aspose_enabled", True)), selected=True, package="aspose")
    license_value = config.get("aspose_license_path", "")
    license_abs, license_exists, license_path = is_abs_file(license_value)
    aspose["license_path"] = license_path
    aspose["license_present"] = bool(license_abs and license_exists)
    aspose["evaluation_watermark_risk"] = not aspose["license_present"]
    aspose["notes"] = "Aspose.Slides is degraded unless a valid license is configured."
    records.append(aspose)
    poppler_installed, poppler_path, poppler_status = find_poppler(config, allow_path=allow_path)
    poppler_version_ok, poppler_version = run_version(poppler_path, ["-v"]) if poppler_installed else (False, "")
    if poppler_installed and not poppler_version_ok and poppler_version:
        poppler_status = f"{poppler_status};version_probe_warning"
    records.append({
        "name": "pdftoppm",
        "kind": "executable",
        "installed": bool(poppler_installed),
        "enabled": True,
        "selected": True,
        "ready": bool(poppler_installed and poppler_version_ok),
        "path": poppler_path,
        "probe_status": poppler_status,
        "version": poppler_version,
        "notes": "Poppler rasterizer used by both pdftoppm and pdf2image.",
    })
    pdf2 = module_record("pdf2image", package="pdf2image")
    pdf2["poppler_ready"] = bool(poppler_installed)
    pdf2["ready"] = bool(pdf2["installed"] and poppler_installed)
    pdf2["notes"] = "pdf2image requires Poppler/pdftoppm on Windows."
    records.append(pdf2)
    records.append(executable_record("magick", config, "magick_exe", ["-version"], allow_path=allow_path))
    records.append(executable_record("ghostscript", config, "ghostscript_exe", ["--version"], allow_path=allow_path))
    records.append(executable_record("inkscape", config, "inkscape_exe", ["--version"], allow_path=allow_path))
    requested = {p.strip().lower() for raw in args.require_ready for p in raw.split(",") if p.strip()}
    missing = sorted(name for name in requested if not any(r["name"].lower() == name and r.get("ready") for r in records))
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "config_path": config_path,
        "config_error": config_error,
        "process_scoped_path_lookup": allow_path,
        "permanent_path_mutation": False,
        "states_contract": ["installed", "enabled", "selected", "ready"],
        "tools": records,
        "missing_required_ready": missing,
        "status": "blocked" if missing else ("degraded" if any(not r.get("ready") for r in records) else "ok"),
    }
    return payload, 1 if (config_error and args.strict_config) or missing else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe PPT render toolchain capabilities.")
    parser.add_argument("--config", help="Local JSON config copied from ppt_render_toolchain_config.example.json.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--output", help="Optional JSON report path.")
    parser.add_argument("--probe-com", action="store_true", help="Actually create PowerPoint.Application COM object.")
    parser.add_argument("--no-path-lookup", action="store_true", help="Only use explicitly configured absolute paths.")
    parser.add_argument("--strict-config", action="store_true", help="Return non-zero for config parse/load errors.")
    parser.add_argument("--require-ready", action="append", default=[], help="Require named tools to be ready, comma-separated allowed.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload, code = build_payload(args)
    except Exception as exc:  # noqa: BLE001
        payload = {
            "schema_version": 1,
            "generated_at": utc_now(),
            "status": "error",
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
            "permanent_path_mutation": False,
        }
        code = 1
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
