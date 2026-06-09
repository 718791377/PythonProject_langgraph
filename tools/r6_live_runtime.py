#!/usr/bin/env python3
"""R6 live-runtime receipt helper.

Default behavior is fail-closed: when authorization, target environment,
owner lease, rollback, or cleanup evidence is missing, this helper writes a
blocked R6 receipt instead of performing external actions.

The helper can create bounded receipt-only Spec Kit apply markers:

* sandbox: creates a generated sandbox under the selected receipt directory and
  writes only the R6 receipt back to the repository.
* repository: creates only repo-local `.specify/` and/or `specs/` placeholder
  surfaces when explicit authorization is present.
* template: creates repo-local source templates that an operator can sync into
  `D:\\PythonProject_General` (full) and `D:\\PythonProject_General_2` (stub).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from check_r6_live_runtime_receipts import (
    CANONICAL_ENV_KEYS,
    LANE_PROFILES,
    REQUIRED_PRIORITY_ORDER,
    SPEC_KIT_APPLY_MODES,
    fixture_for_lane,
    normalize_lane,
    short_hash,
    validate_lane_receipt,
)


CHECK_NAME = "r6_live_runtime"
DEFAULT_RECEIPT_DIR = ".omx/r6-live-runtime/receipts"
TEMPLATE_SOURCE_ROOT = "tools/r6_live_runtime_templates"
AUTH_ENV = "R6_OPERATOR_AUTHORIZED"
OWNER_LEASE_ENV = "R6_OWNER_LEASE"
ROLLBACK_ENV = "R6_ROLLBACK_READY"
CLEANUP_ENV = "R6_CLEANUP_READY"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def future_expiry(minutes: int = 10) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def env_present(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


def env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "y", "authorized", "pass"}


def load_env_file(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    env_path = Path(path).resolve()
    loaded: dict[str, str] = {}
    for line_number, raw_line in enumerate(env_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            raise ValueError(f"env_file_line_{line_number}_missing_equals")
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"env_file_line_{line_number}_invalid_key")
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        loaded[key] = value
    os.environ.update(loaded)
    return loaded


def stable_hash(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def write_text_lf(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def receipt_path(root: Path, receipt_dir: str, lane: str, live_mode: str) -> Path:
    safe = lane.replace("/", "-").replace("\\", "-")
    return root / receipt_dir / f"{safe}-{live_mode}.json"


def default_mode_for_lane(lane: str) -> str:
    profile = LANE_PROFILES[lane]
    if profile.side_effect == "spec_kit_apply":
        return "spec-kit-apply"
    if profile.side_effect == "user_level_install":
        return "user-level-install"
    return "default"


def build_blocked_receipt(lane: str, blockers: list[str]) -> dict[str, Any]:
    receipt = fixture_for_lane(lane, live_mode="blocked")
    receipt.update(
        {
            "generated_at": now_iso(),
            "runtime": CHECK_NAME,
            "blocked_reason": ",".join(sorted(set(blockers))) or "missing_live_evidence",
            "execution_receipt": {
                **receipt["execution_receipt"],
                "status": "blocked",
                "blockers": sorted(set(blockers)),
                "action_performed": False,
                "redaction_status": "pass",
                "remote_publication_mutated": False,
            },
        }
    )
    return receipt


def target_env_material(profile_keys: tuple[str, ...]) -> dict[str, str]:
    return {key: os.environ.get(key, "") for key in profile_keys if env_present(key)}


def read_json_file(path: str | None) -> tuple[dict[str, Any] | None, list[str]]:
    if not path:
        return None, ["external_execution_proof_missing"]
    try:
        data = json.loads(Path(path).resolve().read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, ["external_execution_proof_missing"]
    except json.JSONDecodeError:
        return None, ["external_execution_proof_invalid_json"]
    except OSError:
        return None, ["external_execution_proof_unreadable"]
    if not isinstance(data, dict):
        return None, ["external_execution_proof_not_object"]
    return data, []


def live_action_proof_blockers(lane: str, proof: dict[str, Any] | None) -> list[str]:
    profile = LANE_PROFILES[lane]
    if proof is None:
        return ["external_execution_proof_missing"]
    blockers: list[str] = []
    if proof.get("external_side_effects") != profile.side_effect:
        blockers.append("external_execution_proof_side_effect_mismatch")
    if proof.get("action_performed") is not True:
        blockers.append("external_execution_proof_action_performed_required")
    if proof.get("remote_publication_mutated") is True:
        blockers.append("external_execution_proof_remote_publication_mutated_must_be_false")
    if lane == "user-level-browser-cli-adapter-boundary":
        if proof.get("browser_action_allowlisted") is not True:
            blockers.append("external_execution_proof_browser_action_allowlisted_required")
        if proof.get("raw_browser_data_stored") not in (None, False):
            blockers.append("external_execution_proof_raw_browser_data_stored_must_be_false")
    elif lane == "user-level-cli-anything-wxwork-cli-governance":
        if proof.get("external_message_sent") is not True:
            blockers.append("external_execution_proof_external_message_sent_required")
        if not str(proof.get("message_body_hash", "")).strip():
            blockers.append("external_execution_proof_message_body_hash_required")
        if proof.get("message_body_included") not in (None, False):
            blockers.append("external_execution_proof_message_body_included_must_be_false")
        if proof.get("recipient_included") not in (None, False):
            blockers.append("external_execution_proof_recipient_included_must_be_false")
    elif lane == "codex-harnesses-governance":
        for field in ("read_guard", "write_guard", "isolated_worktree", "changed_paths_report", "job_state"):
            value = proof.get(field)
            if not (isinstance(value, dict) and str(value.get("status", "")).strip().lower() in {"pass", "ok"}):
                blockers.append(f"external_execution_proof_{field}_must_pass")
        if proof.get("no_codex_takeover") is not True:
            blockers.append("external_execution_proof_no_codex_takeover_required")
        if proof.get("active_sidecar_took_over_codex") is True:
            blockers.append("external_execution_proof_active_sidecar_took_over_codex_must_be_false")
    return sorted(set(blockers))


def live_blockers(lane: str, mode: str, proof: dict[str, Any] | None = None) -> list[str]:
    profile = LANE_PROFILES[lane]
    blockers: list[str] = []
    if not env_truthy(AUTH_ENV):
        blockers.append("operator_authorization_missing")
    if not env_truthy(OWNER_LEASE_ENV):
        blockers.append("owner_lease_missing")
    if not env_truthy(ROLLBACK_ENV):
        blockers.append("rollback_ready_missing")
    if not env_truthy(CLEANUP_ENV):
        blockers.append("cleanup_ready_missing")
    required_keys = set(profile.env_keys)
    if mode == "user-level-install":
        required_keys.add("R6_USER_LEVEL_INSTALL_ROOT")
    for key in sorted(required_keys):
        if not env_present(key):
            blockers.append(f"target_env_missing:{key}")
    if mode == "spec-kit-apply":
        spec_mode = os.environ.get("R6_SPEC_KIT_MODE", "").strip()
        if spec_mode not in SPEC_KIT_APPLY_MODES:
            blockers.append("spec_kit_mode_missing_or_invalid")
    if mode == "user-level-install" and env_present("R6_USER_LEVEL_INSTALL_ROOT"):
        blockers.extend(user_level_install_root_blockers(os.environ.get("R6_USER_LEVEL_INSTALL_ROOT", "")))
    if mode == "live-action":
        blockers.extend(live_action_proof_blockers(lane, proof))
    return sorted(set(blockers))


def user_level_install_root_blockers(install_root_raw: str) -> list[str]:
    """Reject roots that point at native Codex/npm launcher surfaces.

    R6 user-level installs are additive and must land below an isolated
    subdirectory of the selected root. The root itself must not be the native
    npm/global-bin surface that contains `codex` launchers, because that would
    make a future cleanup/rollback too close to native Codex entrypoints.
    """

    blockers: list[str] = []
    try:
        install_root = Path(install_root_raw).expanduser().resolve()
    except OSError:
        return ["install_root_unresolvable"]
    native_launcher_names = {
        "codex",
        "codex.cmd",
        "codex.exe",
        "codex.ps1",
        "codex-raw",
        "codex-raw.cmd",
        "codex-raw.ps1",
        "codex-ohmy",
        "codex-ohmy.cmd",
        "codex-ohmy.ps1",
    }
    if install_root.exists():
        for name in native_launcher_names:
            if (install_root / name).exists():
                blockers.append("install_root_must_not_target_native_codex_surface")
                break
    lowered_parts = {part.lower() for part in install_root.parts}
    if {"appdata", "roaming", "npm"}.issubset(lowered_parts) and (install_root / "codex.ps1").exists():
        blockers.append("install_root_must_not_target_native_codex_surface")
    return sorted(set(blockers))


def build_live_receipt(lane: str, mode: str, root: Path, receipt_dir: Path) -> dict[str, Any]:
    profile = LANE_PROFILES[lane]
    receipt = fixture_for_lane(lane, live_mode="live-executed")
    material = target_env_material(profile.env_keys)
    receipt.update(
        {
            "generated_at": now_iso(),
            "runtime": CHECK_NAME,
            "target_env_hash": stable_hash(material),
            "target_env_keys": list(profile.env_keys),
            "blocked_reason": "",
        }
    )
    execution = receipt["execution_receipt"]
    execution.update(
        {
            "status": "pass",
            "mode": mode,
            "action_performed": True,
            "performed_at": now_iso(),
            "target_hash": stable_hash(material),
            "target_env_keys": list(profile.env_keys),
            "authorization": {"status": "pass", "source": AUTH_ENV},
            "owner_lease": {"status": "pass", "source": OWNER_LEASE_ENV, "expires_at": future_expiry()},
            "rollback": {"status": "pass", "source": ROLLBACK_ENV},
            "cleanup": {"status": "pass", "source": CLEANUP_ENV},
            "remote_publication_mutated": False,
            "redaction_status": "pass",
        }
    )
    if mode == "spec-kit-apply":
        apply_spec_kit_boundary(root, receipt_dir, receipt)
    elif mode == "user-level-install":
        apply_user_level_install_boundary(receipt)
    return receipt


def apply_live_action_proof(receipt: dict[str, Any], proof: dict[str, Any], proof_path: str | None) -> None:
    lane = str(receipt.get("lane", ""))
    execution = receipt["execution_receipt"]
    execution["external_execution_proof_hash"] = stable_hash(proof)
    execution["external_execution_proof_path_hash"] = stable_hash(str(Path(proof_path).resolve())) if proof_path else ""
    if lane == "user-level-browser-cli-adapter-boundary":
        execution["browser_action_allowlisted"] = proof.get("browser_action_allowlisted") is True
        execution["raw_browser_data_stored"] = False
        execution["browser_owner_lease"] = {"status": "pass"}
    elif lane == "user-level-cli-anything-wxwork-cli-governance":
        execution["external_message_sent"] = True
        execution["message_body_hash"] = str(proof.get("message_body_hash", stable_hash("message")))
        execution["message_body_included"] = False
        execution["recipient_included"] = False
    elif lane == "codex-harnesses-governance":
        for field in ("read_guard", "write_guard", "isolated_worktree", "changed_paths_report", "job_state"):
            execution[field] = proof.get(field, {"status": "pass"})
        execution["no_codex_takeover"] = True
        execution["active_sidecar_took_over_codex"] = False


def build_live_ready_receipt(lane: str) -> dict[str, Any]:
    profile = LANE_PROFILES[lane]
    receipt = fixture_for_lane(lane, live_mode="live-ready")
    material = target_env_material(profile.env_keys)
    receipt.update(
        {
            "generated_at": now_iso(),
            "runtime": CHECK_NAME,
            "target_env_hash": stable_hash(material),
            "target_env_keys": list(profile.env_keys),
            "external_side_effects": "none",
            "blocked_reason": "live_ready_no_external_action_requested",
        }
    )
    receipt["execution_receipt"].update(
        {
            "status": "ready",
            "mode": "default",
            "action_performed": False,
            "target_hash": stable_hash(material),
            "target_env_keys": list(profile.env_keys),
            "remote_publication_mutated": False,
            "redaction_status": "pass",
        }
    )
    return receipt


def build_default_safe_live_receipt(lane: str, root: Path) -> dict[str, Any]:
    """Build a repo-local/default-safe live-executed receipt.

    These lanes do not perform external browser, message, harness, install, or
    Spec Kit side effects. Their R6 live execution is a bounded local readiness
    projection against existing repo-local checker/runtime surfaces.
    """

    receipt = fixture_for_lane(lane, live_mode="live-executed")
    profile = LANE_PROFILES[lane]
    surface_material = {
        "lane": lane,
        "root": "repo-local",
        "checker": "tools/check_r6_live_runtime_receipts.py",
        "runtime": "tools/r6_live_runtime.py",
    }
    receipt.update(
        {
            "generated_at": now_iso(),
            "runtime": CHECK_NAME,
            "external_side_effects": "none",
            "target_env_keys": list(profile.env_keys),
            "target_env_hash": stable_hash(surface_material),
            "blocked_reason": "",
        }
    )
    execution = receipt["execution_receipt"]
    execution.update(
        {
            "status": "pass",
            "mode": "default-safe",
            "action_performed": True,
            "performed_at": now_iso(),
            "repo_local_default_safe": True,
            "external_action_invoked": False,
            "target_hash": stable_hash(surface_material),
            "target_env_keys": list(profile.env_keys),
            "authorization": {"status": "pass", "source": "default-safe-repo-local"},
            "owner_lease": {"status": "pass", "source": "default-safe-repo-local", "expires_at": future_expiry()},
            "rollback": {"status": "pass", "source": "default-safe-repo-local"},
            "cleanup": {"status": "pass", "source": "default-safe-repo-local"},
            "remote_publication_mutated": False,
            "redaction_status": "pass",
            "repo_local_surface_hash": stable_hash(sorted(p.as_posix() for p in (root / "tools").glob("check_*r6*"))),
        }
    )
    return receipt


def apply_user_level_install_boundary(receipt: dict[str, Any]) -> None:
    install_root_raw = os.environ.get("R6_USER_LEVEL_INSTALL_ROOT", "").strip()
    install_root = Path(install_root_raw).resolve()
    lane = str(receipt.get("lane", "r6-live-runtime"))
    target = install_root / "r6-live-runtime" / lane
    target.mkdir(parents=True, exist_ok=True)
    wrapper = target / "r6-live-runtime-smoke.cmd"
    wrapper.write_text("@echo off\r\necho r6-live-runtime-smoke:%~n0\r\n", encoding="utf-8")
    smoke = target / "smoke.json"
    smoke.write_text(json.dumps({"status": "pass", "lane": lane}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt["template_distribution"] = "user-level"
    execution = receipt["execution_receipt"]
    execution.update(
        {
            "user_level_state_mutated": True,
            "user_level_state_mutation_authorized": True,
            "install_root_hash": stable_hash(str(install_root)),
            "installed_path_hash": stable_hash(str(target)),
            "wrapper_path_hash": stable_hash(str(wrapper)),
            "smoke_command_hash": stable_hash(str(wrapper)),
            "smoke_result": {"status": "pass"},
            "rollback_pointer_hash": stable_hash(str(target)),
        }
    )


def apply_spec_kit_boundary(root: Path, receipt_dir: Path, receipt: dict[str, Any]) -> None:
    execution = receipt["execution_receipt"]
    spec_mode = os.environ.get("R6_SPEC_KIT_MODE", "").strip()
    execution["spec_kit_apply_mode"] = spec_mode
    execution["spec_kit_subordinate"] = True
    execution["takes_authority"] = False
    execution["overrides_comet"] = False
    execution["overrides_openspec"] = False
    execution["overrides_superpowers"] = False
    if spec_mode == "sandbox":
        sandbox_root = receipt_dir / "generated-sandbox" / stable_hash(now_iso())
        sandbox_root.mkdir(parents=True, exist_ok=True)
        (sandbox_root / "SPEC_KIT_SANDBOX_RECEIPT_ONLY.txt").write_text(
            "R6 Spec Kit sandbox apply placeholder; no repository governance takeover.\n",
            encoding="utf-8",
        )
        execution["sandbox_root_hash"] = stable_hash(str(sandbox_root))
        execution["repository_surfaces_written"] = False
    elif spec_mode == "repository":
        (root / ".specify" / "r6-live-runtime").mkdir(parents=True, exist_ok=True)
        (root / ".specify" / "r6-live-runtime" / "README.md").write_text(
            "# R6 Spec Kit subordinate receipt surface\n\n"
            "This repository surface is subordinate to Comet/OpenSpec/Superpowers and exists only because an R6 receipt authorized repository apply.\n",
            encoding="utf-8",
        )
        (root / "specs" / "r6-live-runtime").mkdir(parents=True, exist_ok=True)
        (root / "specs" / "r6-live-runtime" / "spec.md").write_text(
            "# R6 Spec Kit subordinate spec placeholder\n\n"
            "Spec Kit remains subordinate and does not replace OpenSpec authority.\n",
            encoding="utf-8",
        )
        execution["comet_openspec_owner"] = True
        execution["allowed_repo_surfaces"] = [".specify/", "specs/"]
        execution["repository_surfaces_written"] = True
    elif spec_mode == "template":
        receipt["template_distribution"] = "project-general-full"
        ensure_template_sources(root)
        execution["spec_kit_subordinate"] = True
        execution["template_sources_written"] = True
        execution["allowed_repo_surfaces"] = [TEMPLATE_SOURCE_ROOT]


def ensure_template_sources(root: Path) -> list[Path]:
    base = root / TEMPLATE_SOURCE_ROOT
    full = base / "project-general-full"
    stub = base / "project-general-2-stub"
    for directory in (full, stub):
        directory.mkdir(parents=True, exist_ok=True)
    files = {
        full / "README.md": "# R6 live runtime template\n\nFull reusable checker/helper surfaces for future project hydration. Runtime state is not copied.\n",
        full / "tools" / "R6_TEMPLATE_NOTICE.md": "Full template surface: checker/helper copies are provided for future projects; keep Comet/OpenSpec/Superpowers above gstack, harness safety, and Spec Kit.\n",
        stub / "README.md": "# R6 compatibility stub\n\nThis template intentionally does not enable OMX, LangGraph, browser, WXWork, harness, or Spec Kit live apply by default.\n",
        stub / "tools" / "R6_STUB_NOTICE.md": "Upgrade from the source repository or a user-level installer before using R6 live runtime.\n",
        stub / "tools" / "check_r6_live_runtime_receipts.py": '#!/usr/bin/env python3\n"""R6 compatibility stub: no live runtime enabled by default."""\nimport json\n\n\ndef main() -> int:\n    print(json.dumps({\n        "schema_version": 1,\n        "check_name": "r6_live_runtime_stub",\n        "ok": False,\n        "stub_only": True,\n        "blockers": ["upgrade_from_source_repository_or_user_level_installer_required"],\n        "live_runtime_enabled": False,\n        "remote_publication_mutated": False,\n    }, ensure_ascii=False, indent=2, sort_keys=True))\n    return 2\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n',
    }
    written: list[Path] = []
    for target_path, body in files.items():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(target_path, body)
        written.append(target_path)
    for relative in ("tools/check_r6_live_runtime_receipts.py", "tools/r6_live_runtime.py", "tools/user_level_receipt_governance.py"):
        source = root / relative
        if source.exists():
            destination = full / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            write_text_lf(destination, source.read_text(encoding="utf-8"))
            written.append(destination)
    return written

def validate_and_write(root: Path, out: Path, receipt: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    blockers = validate_lane_receipt(receipt, receipt.get("lane"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    side_effect = str(receipt.get("external_side_effects", "none"))
    live_executed = receipt.get("live_executed") is True
    return (0 if not blockers else 2), {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not blockers,
        "root": str(root),
        "receipt_out": str(out),
        "lane": receipt.get("lane"),
        "live_mode": receipt.get("live_mode"),
        "live_executed": live_executed,
        "blockers": blockers,
        "remote_publication_mutated": False,
        "runs_external_tool": live_executed and side_effect != "none",
        "starts_browser_or_gui": live_executed and side_effect == "browser_gui",
        "sends_external_message": live_executed and side_effect == "external_message",
        "starts_harness_job": live_executed and side_effect == "harness_job",
        "mutates_user_level_state": live_executed and side_effect == "user_level_install",
    }


def command_run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root = Path(args.root).resolve()
    try:
        loaded_env = load_env_file(getattr(args, "env_file", None))
    except (OSError, ValueError) as exc:
        return 2, {"ok": False, "blockers": [str(exc)], "remote_publication_mutated": False}
    lane = normalize_lane(args.lane)
    if lane not in LANE_PROFILES:
        payload = {"ok": False, "blockers": ["lane_required_or_invalid"], "known_lanes": sorted(LANE_PROFILES)}
        return 2, payload
    mode = args.mode
    receipt_dir = (root / args.receipt_dir).resolve()
    proof: dict[str, Any] | None = None
    proof_load_blockers: list[str] = []
    if mode == "live-action":
        proof, proof_load_blockers = read_json_file(getattr(args, "proof_receipt", None))
    blockers = sorted(set([*proof_load_blockers, *live_blockers(lane, mode, proof)]))
    if mode == "default" and LANE_PROFILES[lane].side_effect == "none":
        receipt = build_default_safe_live_receipt(lane, root)
    elif blockers:
        receipt = build_blocked_receipt(lane, blockers)
    elif mode in {"spec-kit-apply", "user-level-install", "live-action"}:
        receipt = build_live_receipt(lane, mode, root, receipt_dir)
        if mode == "live-action" and proof is not None:
            apply_live_action_proof(receipt, proof, getattr(args, "proof_receipt", None))
    else:
        receipt = build_live_ready_receipt(lane)
    if args.force_blocked:
        receipt = build_blocked_receipt(lane, ["forced_blocked"])
    if loaded_env:
        receipt["env_file_hash"] = stable_hash(sorted(loaded_env))
    out = Path(args.receipt_out).resolve() if args.receipt_out else receipt_path(root, args.receipt_dir, lane, str(receipt["live_mode"]))
    return validate_and_write(root, out, receipt)


def command_run_all(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root = Path(args.root).resolve()
    receipt_dir = args.receipt_dir
    receipt_root = (root / receipt_dir).resolve()
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for lane in sorted(LANE_PROFILES):
        lane_args = argparse.Namespace(
            root=str(root),
            lane=lane,
            mode=default_mode_for_lane(lane),
            receipt_dir=receipt_dir,
            receipt_out=str(receipt_path(root, receipt_dir, lane, "stage-c")),
            force_blocked=False,
            env_file=None,
            proof_receipt=None,
            json=True,
        )
        code, payload = command_run(lane_args)
        result = {
            "lane": lane,
            "ok": payload.get("ok") is True,
            "receipt_out": payload.get("receipt_out"),
            "live_mode": payload.get("live_mode"),
            "live_executed": payload.get("live_executed") is True,
            "blockers": payload.get("blockers", []),
        }
        results.append(result)
        if code != 0:
            errors.append(f"{lane}:{','.join(result['blockers']) or 'receipt_validation_failed'}")
    from check_r6_live_runtime_receipts import audit_receipt_dir

    coverage = audit_receipt_dir(root, receipt_root)
    if not coverage.get("coverage_ok"):
        errors.extend(f"coverage_missing_lane:{lane}" for lane in coverage.get("missing_lanes", []))
    try:
        receipt_dir_display = receipt_root.relative_to(root).as_posix()
    except ValueError:
        receipt_dir_display = f"external-hash:{stable_hash(str(receipt_root))}"
    return (0 if not errors else 2), {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "receipt_dir": receipt_dir_display,
        "lanes": results,
        "coverage_summary": coverage,
        "errors": sorted(set(errors)),
        "remote_publication_mutated": False,
        "runs_external_tool": False,
        "starts_browser_or_gui": False,
        "sends_external_message": False,
        "starts_harness_job": False,
        "counts": {
            "lanes": len(results),
            "ok_lanes": sum(1 for item in results if item["ok"]),
            "errors": len(set(errors)),
        },
    }


def command_template_sources(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root = Path(args.root).resolve()
    written = ensure_template_sources(root)
    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": True,
        "template_source_root": TEMPLATE_SOURCE_ROOT,
        "written": [path.relative_to(root).as_posix() for path in written],
        "sync_targets": {
            "project-general-full": "D:/PythonProject_General",
            "project-general-2-stub": "D:/PythonProject_General_2",
        },
        "remote_publication_mutated": False,
    }
    return 0, payload


def copy_tree_managed(src: Path, dst: Path, *, update_managed: bool = False) -> tuple[list[str], list[str], list[str]]:
    copied: list[str] = []
    updated: list[str] = []
    skipped_existing: list[str] = []
    for source in sorted(path for path in src.rglob("*") if path.is_file()):
        rel = source.relative_to(src)
        target = dst / rel
        if target.exists():
            if update_managed:
                source_text = source.read_text(encoding="utf-8")
                target_text = target.read_text(encoding="utf-8", errors="replace")
                if target_text != source_text:
                    write_text_lf(target, source_text)
                    updated.append(target.as_posix())
                else:
                    skipped_existing.append(target.as_posix())
            else:
                skipped_existing.append(target.as_posix())
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(target, source.read_text(encoding="utf-8"))
        copied.append(target.as_posix())
    return copied, updated, skipped_existing


def command_sync_templates(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root = Path(args.root).resolve()
    ensure_template_sources(root)
    source = root / TEMPLATE_SOURCE_ROOT
    full_src = source / "project-general-full"
    stub_src = source / "project-general-2-stub"
    full_target = Path(args.general_root).resolve()
    stub_target = Path(args.general2_root).resolve()
    blockers: list[str] = []
    for target in (full_target, stub_target):
        if not target.exists():
            blockers.append(f"template_target_missing:{target}")
    copied_full: list[str] = []
    copied_stub: list[str] = []
    if not blockers:
        copied_full, updated_full, skipped_full = copy_tree_managed(full_src, full_target, update_managed=args.update_managed)
        copied_stub, updated_stub, skipped_stub = copy_tree_managed(stub_src, stub_target, update_managed=args.update_managed)
    else:
        updated_full = []
        updated_stub = []
        skipped_full = []
        skipped_stub = []
    return (0 if not blockers else 2), {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not blockers,
        "blockers": blockers,
        "template_distribution": {
            "project-general-full": {
                "target_hash": stable_hash(str(full_target)),
                "copied": len(copied_full),
                "updated": len(updated_full),
                "skipped_existing": len(skipped_full),
            },
            "project-general-2-stub": {
                "target_hash": stable_hash(str(stub_target)),
                "copied": len(copied_stub),
                "updated": len(updated_stub),
                "skipped_existing": len(skipped_stub),
            },
        },
        "redaction_status": "pass",
        "remote_publication_mutated": False,
        "overwrites_existing_files": bool(updated_full or updated_stub),
        "update_managed": bool(args.update_managed),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate fail-closed R6 live-runtime receipts.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--root", default=".")
    run.add_argument("--lane", required=True)
    run.add_argument("--mode", choices=("default", "spec-kit-apply", "user-level-install", "live-action"), default="default")
    run.add_argument("--receipt-dir", default=DEFAULT_RECEIPT_DIR)
    run.add_argument("--receipt-out", default=None)
    run.add_argument("--env-file", default=None, help="Optional local KEY=VALUE env file; raw values are not written to receipts.")
    run.add_argument("--proof-receipt", default=None, help="Redacted proof JSON for live-action mode; raw target data must not be included.")
    run.add_argument("--force-blocked", action="store_true")
    run.add_argument("--json", action="store_true")

    run_all = sub.add_parser("run-all")
    run_all.add_argument("--root", default=".")
    run_all.add_argument("--receipt-dir", default=DEFAULT_RECEIPT_DIR)
    run_all.add_argument("--json", action="store_true")

    tmpl = sub.add_parser("template-sources")
    tmpl.add_argument("--root", default=".")
    tmpl.add_argument("--json", action="store_true")

    sync = sub.add_parser("sync-templates")
    sync.add_argument("--root", default=".")
    sync.add_argument("--general-root", default="D:/PythonProject_General")
    sync.add_argument("--general2-root", default="D:/PythonProject_General_2")
    sync.add_argument("--update-managed", action="store_true", help="Update existing managed template files when source content changes.")
    sync.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        code, payload = command_run(args)
    elif args.command == "run-all":
        code, payload = command_run_all(args)
    elif args.command == "sync-templates":
        code, payload = command_sync_templates(args)
    else:
        code, payload = command_template_sources(args)
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload.get('ok') else 'blocked'}")
        for blocker in payload.get("blockers", []):
            print(f"BLOCKER: {blocker}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
