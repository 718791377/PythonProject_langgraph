#!/usr/bin/env python3
"""Validate repo-owned mcp2cli / skills2cli user-level install surfaces."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "user_level_mcp_skills_cli_install"
INSTALL_HELPER = Path("tools/install_user_level_mcp_skills_cli.py")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")
PLAN_EN = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md")
PARENT_EN = PLAN_EN
PARENT_ZH = PLAN_ZH
TEST_NAME = "user_level_mcp_skills_cli_install.test.py"
CHILD_PLAN_MARKERS = [
    "knowsuchagency/mcp2cli",
    "uvx mcp2cli --help",
    "uv tool install mcp2cli",
    "npx skills add knowsuchagency/mcp2cli --skill mcp2cli",
    "rollback pointer",
    "update receipt",
    "skills2cli",
    "native-subagent",
]
PARENT_PLAN_MARKERS = [
    "knowsuchagency/mcp2cli",
    "rollback pointer",
    "update receipt",
    "skills2cli",
    "mcp2cli",
]


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        errors.append(f"missing_or_unreadable:{path}:{exc}")
        return ""


def read_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        errors.append(f"missing_or_unreadable_json:{path}:{exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path}:{exc}")
    return None


def run_json(command: list[str], cwd: Path) -> tuple[int, dict[str, Any] | None, str]:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = None
    return proc.returncode, data, proc.stderr


def require_markers(label: str, text: str, markers: list[str], errors: list[str]) -> None:
    lowered = text.lower()
    for marker in markers:
        if marker.lower() not in lowered:
            errors.append(f"{label}:missing_marker:{marker}")


def evaluate(root: Path, *, require_user_level_installed: bool, smoke: bool, codex_home: Path | None) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    helper = root / INSTALL_HELPER
    if not helper.exists():
        errors.append(f"missing_helper:{INSTALL_HELPER}")

    for rel in (PLAN_EN, PLAN_ZH):
        require_markers(str(rel), read_text(root / rel, errors), CHILD_PLAN_MARKERS, errors)
    for rel in (PARENT_EN, PARENT_ZH):
        require_markers(str(rel), read_text(root / rel, errors), PARENT_PLAN_MARKERS, errors)

    manifest = read_json(root / CI_MANIFEST, errors)
    if isinstance(manifest, dict):
        tests = manifest.get("python_unittest")
        if not isinstance(tests, list) or TEST_NAME not in tests:
            errors.append(f"ci_manifest_missing:{TEST_NAME}")

    guard_text = read_text(root / GUARD_SCRIPT, errors)
    if "check_user_level_mcp_skills_cli_install" not in guard_text:
        errors.append("openspec_guard_missing:check_user_level_mcp_skills_cli_install")

    plan_code, plan_payload, plan_stderr = run_json(
        [sys.executable, str(helper), "plan", "--json"],
        root,
    )
    if plan_code != 0 or not isinstance(plan_payload, dict):
        errors.append(f"install_helper_plan_failed:{plan_stderr.strip()}")
    elif not plan_payload.get("ok"):
        errors.append("install_helper_plan_not_ok")
    else:
        upstream = plan_payload.get("upstream", {})
        if not isinstance(upstream, dict) or upstream.get("source_url") != "https://github.com/knowsuchagency/mcp2cli":
            errors.append("install_helper_plan_missing_upstream_source")
        safety = plan_payload.get("safety", {})
        if not isinstance(safety, dict) or safety.get("native_subagent_evidence") is not False:
            errors.append("install_helper_plan_mislabels_native_subagent_evidence")
        if safety.get("skills2cli_is_upstream_pattern_fork") is not True:
            errors.append("install_helper_plan_missing_skills2cli_fork_boundary")
        info.append("install_helper_plan_ok")

    user_level_check: dict[str, Any] | None = None
    if require_user_level_installed or smoke:
        cmd = [sys.executable, str(helper), "check", "--json"]
        if require_user_level_installed:
            cmd.append("--require-installed")
        if smoke:
            cmd.append("--smoke")
        if codex_home:
            cmd.extend(["--codex-home", str(codex_home)])
        check_code, user_level_check, check_stderr = run_json(cmd, root)
        if check_code != 0:
            if require_user_level_installed:
                errors.append(f"user_level_install_check_failed:{check_stderr.strip()}")
            else:
                warnings.append("user_level_install_smoke_not_ok")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "require_user_level_installed": require_user_level_installed,
        "smoke": smoke,
        "user_level_check": user_level_check,
        "policy": {
            "repo_local_source_canonical": True,
            "user_level_helpers_are_install_artifacts": True,
            "upstream_mcp2cli_required": True,
            "skills2cli_upstream_pattern_fork_required": True,
            "remote_publication_allowed": False,
        },
        "counts": {"errors": len(errors), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate user-level mcp2cli/skills2cli install surfaces.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--codex-home", default=None)
    parser.add_argument("--require-user-level-installed", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = evaluate(
        Path(args.root),
        require_user_level_installed=args.require_user_level_installed,
        smoke=args.smoke,
        codex_home=Path(args.codex_home).resolve() if args.codex_home else None,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
