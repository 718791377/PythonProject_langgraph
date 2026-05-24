#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "user_level_mcp_skills_browser_cli_baseline"
SPEC_DIR = "codex-user-level-mcp-skills-browser-cli-governance"
PLAN_ZH = Path("docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md")
PLAN_EN = Path("docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md")
STABLE_SPEC = Path("openspec/specs") / SPEC_DIR / "spec.md"
CHANGE_SPEC_GLOB = f"openspec/changes/*/specs/{SPEC_DIR}/spec.md"
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")

PLAN_REQUIRED: dict[str, list[str]] = {
    "zh": [
        "plan_readiness: execution-ready",
        "implementation_state:",
        "## 0.",
        "Token",
        "Readiness gate",
        "OpenSpec",
        "skills2cli",
        "mcp2cli",
        "CDP Bridge",
        "OpenCLI",
        "port registry",
        "codex-port",
        "pending_bind",
        "registry_revision",
        "39000-39299",
        "40000-40999",
        "authorization receipt schema",
        "operator confirmation",
        "update receipt",
        "rollback pointer",
    ],
    "en": [
        "plan_readiness: execution-ready",
        "implementation_state:",
        "## 0. Current review verdict",
        "Token and risk priority model",
        "Readiness gates and acceptance criteria",
        "Sensitive authorization matrix",
        "Installation and update evidence contract",
        "OpenSpec slice delivery matrix",
        "Fine-grained implementation checklist",
        "Slice completion rule",
        "port registry",
        "codex-port",
        "pending_bind",
        "registry_revision",
        "39000-39299",
        "40000-40999",
        "authorization receipt schema",
        "operator confirmation",
        "update receipt",
        "rollback pointer",
    ],
}
LANE_MARKERS = [
    "skills2cli",
    "mcp2cli",
    "chrome-devtools-mcp",
    "CDP Bridge",
    "OpenCLI",
    "oh-my-pi",
    "CLI-Anything",
    "wecom-cli",
    "active",
    "on-demand",
    "reference-only",
    "disabled",
]

AUTHORIZATION_FIELDS = ["action", "target", "scope", "expiry", "session", "operator confirmation"]
UPDATE_RECEIPT_FIELDS = [
    "tool name",
    "installed version",
    "source URL",
    "install path",
    "wrapper path",
    "state path",
    "smoke test command",
    "updater command",
    "rollback pointer",
    "owner lane",
]
REDACTION_MARKERS = [
    "secrets",
    "cookies",
    "tokens",
    "raw browser data",
    "plugin description dumps",
]
PORT_GOVERNANCE_MARKERS = [
    "port registry",
    "codex-port",
    "pending_bind",
    "registry_revision",
    "39000-39299",
    "40000-40999",
    "OpenCLI",
    "--port auto",
]
SPEC_MARKERS = [
    "Token/risk priority",
    "authorization receipt",
    "update receipt",
    "evidence redaction",
    "port registry/lease",
    "codex-port allocator",
    "pending_bind",
    "registry_revision",
    "39000-39299",
    "40000-40999",
    "OpenSpec slice",
    "fail closed",
]


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Missing or unreadable required file `{path}`: {exc}")
        return ""


def read_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"Missing or unreadable JSON file `{path}`: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON file `{path}`: {exc}")
    return None


def require_markers(label: str, text: str, markers: list[str], errors: list[str]) -> None:
    lowered = text.lower()
    for marker in markers:
        if marker.lower() not in lowered:
            errors.append(f"{label} is missing required marker `{marker}`.")


def check_plan(root: Path, rel_path: Path, lang: str, errors: list[str], info: list[str]) -> dict[str, Any]:
    path = root / rel_path
    text = read_text(path, errors)
    checklist_items = sum(1 for line in text.splitlines() if line.startswith("- [") and "]" in line[:6])
    table_rows = sum(1 for line in text.splitlines() if line.startswith("|"))
    headings = sum(1 for line in text.splitlines() if line.startswith("#"))
    require_markers(str(rel_path), text, PLAN_REQUIRED[lang], errors)
    require_markers(str(rel_path), text, LANE_MARKERS, errors)
    missing_authorization = [field for field in AUTHORIZATION_FIELDS if field not in text]
    if missing_authorization:
        errors.append(f"{rel_path} is missing authorization receipt fields: {', '.join(missing_authorization)}.")
    missing_update = [field for field in UPDATE_RECEIPT_FIELDS if field not in text]
    if missing_update:
        errors.append(f"{rel_path} is missing update receipt fields: {', '.join(missing_update)}.")
    missing_redaction = [field for field in REDACTION_MARKERS if field not in text]
    if missing_redaction:
        errors.append(f"{rel_path} is missing redaction markers: {', '.join(missing_redaction)}.")
    missing_port = [field for field in PORT_GOVERNANCE_MARKERS if field not in text]
    if missing_port:
        errors.append(f"{rel_path} is missing port-governance markers: {', '.join(missing_port)}.")
    if checklist_items < 30:
        errors.append(f"{rel_path} must keep at least 30 implementation checklist items; found {checklist_items}.")
    if table_rows < 40:
        errors.append(f"{rel_path} must keep the readiness and slice matrices; found only {table_rows} table rows.")
    info.append(f"{rel_path}: headings={headings}, checklist_items={checklist_items}, table_rows={table_rows}")
    return {
        "path": str(rel_path),
        "present": bool(text),
        "headings": headings,
        "checklist_items": checklist_items,
        "table_rows": table_rows,
    }


def spec_candidates(root: Path) -> list[Path]:
    candidates: list[Path] = []
    stable = root / STABLE_SPEC
    if stable.exists():
        candidates.append(stable)
    candidates.extend(sorted(root.glob(CHANGE_SPEC_GLOB)))
    return candidates


def check_spec(root: Path, errors: list[str], info: list[str]) -> dict[str, Any]:
    candidates = spec_candidates(root)
    if not candidates:
        errors.append(f"No stable or active OpenSpec spec found for `{SPEC_DIR}`.")
        return {"present": False, "candidates": []}
    accepted: list[str] = []
    for path in candidates:
        text = read_text(path, errors)
        lowered = text.lower()
        missing = [marker for marker in SPEC_MARKERS if marker.lower() not in lowered]
        if not missing:
            accepted.append(str(path.relative_to(root)))
    if not accepted:
        errors.append(f"No `{SPEC_DIR}` spec candidate contains all baseline markers: {', '.join(SPEC_MARKERS)}.")
    else:
        info.append(f"Accepted baseline OpenSpec spec candidate(s): {', '.join(accepted)}")
    return {"present": True, "candidates": [str(path.relative_to(root)) for path in candidates], "accepted": accepted}


def check_safety_registry(root: Path, errors: list[str]) -> dict[str, Any]:
    data = read_json(root / SAFETY_REGISTRY, errors)
    found: dict[str, Any] | None = None
    if isinstance(data, dict):
        for item in data.get("rules", []):
            if isinstance(item, dict) and item.get("id") == "user-level-mcp-skills-browser-cli-baseline":
                found = item
                break
    if not found:
        errors.append("Safety rule registry is missing `user-level-mcp-skills-browser-cli-baseline`.")
        return {"present": False}
    required_scripts = {"tools/check_user_level_mcp_skills_browser_cli_baseline.py"}
    scripts = set(found.get("script_controls", [])) if isinstance(found.get("script_controls"), list) else set()
    if not required_scripts.issubset(scripts):
        errors.append("Safety rule registry entry lacks the baseline checker script control.")
    guard_steps = set(found.get("guard_steps", [])) if isinstance(found.get("guard_steps"), list) else set()
    if "check_user_level_mcp_skills_browser_cli_baseline" not in guard_steps:
        errors.append("Safety rule registry entry lacks guard step `check_user_level_mcp_skills_browser_cli_baseline`.")
    return {"present": True, "id": found.get("id"), "status": found.get("status")}


def check_ci_and_guard(root: Path, errors: list[str]) -> dict[str, Any]:
    manifest = read_json(root / CI_MANIFEST, errors)
    manifest_ok = False
    if isinstance(manifest, dict):
        tests = manifest.get("python_unittest", [])
        manifest_ok = "check_user_level_mcp_skills_browser_cli_baseline.test.py" in tests
    if not manifest_ok:
        errors.append("CI manifest must include `check_user_level_mcp_skills_browser_cli_baseline.test.py`.")
    guard_text = read_text(root / GUARD_SCRIPT, errors)
    guard_ok = "check_user_level_mcp_skills_browser_cli_baseline" in guard_text
    if not guard_ok:
        errors.append("OpenSpec guard must run `check_user_level_mcp_skills_browser_cli_baseline`.")
    return {"ci_manifest_registered": manifest_ok, "openspec_guard_registered": guard_ok}


def evaluate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    zh = check_plan(root, PLAN_ZH, "zh", errors, info)
    en = check_plan(root, PLAN_EN, "en", errors, info)
    spec = check_spec(root, errors, info)
    safety = check_safety_registry(root, errors)
    ci_guard = check_ci_and_guard(root, errors)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "plans": {"zh": zh, "en": en},
        "spec": spec,
        "safety_rule": safety,
        "ci_guard": ci_guard,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the user-level MCP/skills/browser/CLI governance baseline surfaces.")
    parser.add_argument("--root", default=".", help="Repository root to check.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    result = evaluate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for message in result["info"]:
            print(message)
        for message in result["warnings"]:
            print(f"WARNING: {message}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
        if result["ok"]:
            print("User-level MCP/skills/browser/CLI baseline check passed.")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
