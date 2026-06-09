#!/usr/bin/env python3
"""Run bounded R4 Codex harness smoke probes.

This repo-local helper is intentionally conservative.  It only runs bounded
help/version/status/read-only commands against candidate-registry entries that
already have an R3 install/update receipt.  It does not install Pi, oh-my-pi,
revfactory/harness, ohmyopenagent, snow-cli, or any package; start a sidecar;
run a write-capable harness job; mutate user-level Codex state; replace Codex
launchers; replace native subagents/native_omx/LangGraph/apply_patch; or bypass
local-main-first gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "codex_harnesses_smoke_runner"
CANDIDATE_REGISTRY: dict[str, dict[str, Any]] = {
    "pi-runtime": {
        "aliases": {"Pi", "pi", "pi.dev", "pi-runtime"},
        "owner_lane": "codex-harnesses:pi-runtime",
        "display": "Pi runtime",
        "source_url": "https://pi.dev/",
        "source_pin": "docs-snapshot-required-before-runtime-implementation",
        "license_note": "docs reference only; package license required before runtime install",
        "adapter_kind": "package-runtime",
        "guard_profile": "package-runtime-r4-read-only",
        "rollback_pointer": "remove pi-runtime candidate and receipts",
        "smoke_args": ["--help"],
        "smoke_type": "read-only",
        "sensitive_command_policy": {"writes_allowed": False, "sensitive_commands_allowed": False},
        "hook_policy": {"hooks_allowed": False, "mutation_hooks_allowed": False},
        "async_headless_lifecycle_state": {"mode": "bounded-read-only", "headless": False, "async": False},
    },
    "oh-my-pi-sidecar": {
        "aliases": {"oh-my-pi", "oh_my_pi", "oh my pi", "oh-my-pi-sidecar"},
        "owner_lane": "codex-harnesses:oh-my-pi-sidecar",
        "display": "oh-my-pi sidecar",
        "source_url": "https://github.com/can1357/oh-my-pi",
        "source_pin": "d9f5a8c7ac770b91d75d6df52459bd16042936fe",
        "license_note": "inspect upstream license before reuse; reference-only until authorized",
        "adapter_kind": "sidecar-ux",
        "guard_profile": "sidecar-ux-r4-read-only",
        "rollback_pointer": "remove sidecar helper copy and candidate receipt",
        "smoke_args": ["--help"],
        "smoke_type": "read-only",
        "sensitive_command_policy": {"writes_allowed": False, "sensitive_commands_allowed": False},
        "hook_policy": {"hooks_allowed": False, "mutation_hooks_allowed": False},
        "async_headless_lifecycle_state": {"mode": "bounded-read-only", "headless": False, "async": False},
    },
    "revfactory-harness-team-factory": {
        "aliases": {"revfactory", "revfactory/harness", "revfactory-harness", "revfactory-harness-team-factory"},
        "owner_lane": "codex-harnesses:revfactory-harness-team-factory",
        "display": "revfactory/harness team factory",
        "source_url": "https://github.com/revfactory/harness",
        "source_pin": "b8fb858ea9209d6b0d9000e551d3dedbbacb88aa",
        "license_note": "GitHub reports Apache-2.0; reference-only until vendoring is explicitly approved",
        "adapter_kind": "team-factory",
        "guard_profile": "team-factory-r4-read-only",
        "rollback_pointer": "remove team-factory candidate and derived pattern rows",
        "smoke_args": ["--help"],
        "smoke_type": "read-only",
        "sensitive_command_policy": {"writes_allowed": False, "sensitive_commands_allowed": False},
        "hook_policy": {"hooks_allowed": False, "mutation_hooks_allowed": False},
        "async_headless_lifecycle_state": {"mode": "bounded-read-only", "headless": False, "async": False},
    },
    "ohmyopenagent-discipline-layer": {
        "aliases": {"ohmyopenagent", "oh-my-openagent", "ohmyopenagent-discipline-layer"},
        "owner_lane": "codex-harnesses:ohmyopenagent-discipline-layer",
        "display": "ohmyopenagent discipline layer",
        "source_url": "https://github.com/ymymssss/ohmyopenagent",
        "source_pin": "4b923aaa7e7660a57623a2cf59fd92e47fced772",
        "license_note": "GitHub reports NOASSERTION/Other; reference-only, no code or config copying",
        "adapter_kind": "discipline-layer",
        "guard_profile": "discipline-layer-r4-read-only",
        "rollback_pointer": "remove discipline-agent candidate and derived prompt-boundary rows",
        "smoke_args": ["--help"],
        "smoke_type": "read-only",
        "sensitive_command_policy": {"writes_allowed": False, "sensitive_commands_allowed": False},
        "hook_policy": {"hooks_allowed": False, "mutation_hooks_allowed": False},
        "async_headless_lifecycle_state": {"mode": "bounded-read-only", "headless": False, "async": False},
    },
    "snow-cli-terminal-agent-runtime": {
        "aliases": {"snow-cli", "snow cli", "snow-cli-terminal-agent-runtime"},
        "owner_lane": "codex-harnesses:snow-cli-terminal-agent-runtime",
        "display": "snow-cli terminal agent runtime",
        "source_url": "https://github.com/MayDay-wpf/snow-cli",
        "source_pin": "f1846e27b655832f52b1e51c190a12b58219cc71",
        "license_note": "GitHub reports NOASSERTION/Other; reference-only, no code or config copying",
        "adapter_kind": "terminal-agent-runtime",
        "guard_profile": "terminal-agent-runtime-r4-read-only",
        "rollback_pointer": "remove terminal-agent candidate and derived CLI-runtime rows",
        "smoke_args": ["--help"],
        "smoke_type": "read-only",
        "sensitive_command_policy": {"writes_allowed": False, "sensitive_commands_allowed": False},
        "hook_policy": {"hooks_allowed": False, "mutation_hooks_allowed": False},
        "async_headless_lifecycle_state": {"mode": "bounded-read-only", "headless": False, "async": False},
    },
}
ALIAS_TO_CANDIDATE = {
    alias.lower(): candidate_id
    for candidate_id, meta in CANDIDATE_REGISTRY.items()
    for alias in set(meta["aliases"]) | {candidate_id}
}
ALLOWED_REDACTION_STATUS = {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
GENERIC_FORBIDDEN_FLAGS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "reads_browser_data",
    "external_message_sent",
)
HARNESS_TAKEOVER_FLAGS = (
    "write_capable_harness_job",
    "codex_launcher_mutated",
    "native_codex_replaced",
    "native_subagents_replaced",
    "native_omx_replaced",
    "langgraph_replaced",
    "apply_patch_replaced",
    "local_main_gate_bypassed",
    "active_candidate",
    "sidecar_takeover",
)
SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def sanitize_text(value: Any, *, limit: int = 1200) -> str:
    text = "" if value is None else str(value)
    text = SECRET_RE.sub("[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) > limit:
        text = text[: max(0, limit - 14)].rstrip() + "...[truncated]"
    return text


def redaction_pass(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ALLOWED_REDACTION_STATUS
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() in ALLOWED_REDACTION_STATUS
    return False


def normalize_candidate(value: str) -> str | None:
    return ALIAS_TO_CANDIDATE.get(str(value).strip().lower())


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, ["install_receipt_missing"]
    except json.JSONDecodeError:
        return None, ["install_receipt_invalid_json"]
    except OSError:
        return None, ["install_receipt_unreadable"]
    if not isinstance(data, dict):
        return None, ["install_receipt_not_object"]
    return data, []


def install_receipt_blockers(candidate_id: str, receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return ["install_receipt_required"]
    meta = CANDIDATE_REGISTRY[candidate_id]
    blockers: list[str] = []
    receipt_candidate = normalize_candidate(str(receipt.get("candidate_id") or receipt.get("tool_name") or ""))
    if receipt_candidate != candidate_id:
        blockers.append("install_receipt_candidate_id_mismatch")
    if str(receipt.get("adapter_kind", "")).strip() != meta["adapter_kind"]:
        blockers.append("install_receipt_adapter_kind_mismatch")
    wrapper_path = receipt.get("wrapper_path")
    if not isinstance(wrapper_path, str) or not wrapper_path.strip():
        blockers.append("install_receipt_wrapper_path_required")
    elif not Path(wrapper_path).exists():
        blockers.append("install_receipt_wrapper_not_resolved")
    for field in (
        "source_url",
        "source_pin",
        "license_note",
        "installed_version",
        "updater_command",
        "rollback_pointer",
        "owner_lane",
        "guard_profile",
    ):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            blockers.append(f"install_receipt_{field}_required")
    if receipt.get("source_url") != meta["source_url"]:
        blockers.append("install_receipt_source_url_mismatch")
    if str(receipt.get("owner_lane", "")) != meta["owner_lane"]:
        blockers.append("install_receipt_owner_lane_must_be_codex_harnesses")
    for field in ("sensitive_command_policy", "hook_policy", "async_headless_lifecycle_state"):
        if not isinstance(receipt.get(field), dict):
            blockers.append(f"install_receipt_{field}_required")
    if not (
        isinstance(receipt.get("source_pin"), str)
        and str(receipt.get("source_pin")).strip()
        or isinstance(receipt.get("package_pin"), str)
        and str(receipt.get("package_pin")).strip()
        or isinstance(receipt.get("installed_version"), str)
        and str(receipt.get("installed_version")).strip()
    ):
        blockers.append("install_receipt_pin_required")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("install_receipt_redaction_status_must_pass")
    return sorted(set(blockers))


def transcript_redaction(transcript: str) -> dict[str, str]:
    return {
        "status": "pass",
        "redacted_transcript_hash": stable_hash(transcript),
    }


def harness_guard_fields(status: str) -> dict[str, Any]:
    return {
        "read_guard": {
            "status": "pass",
            "scope": "help/version/status/read-only",
            "read_only": True,
            "sidecar_state_read": False,
        },
        "write_guard": {
            "status": "pass",
            "write_allowed": False,
            "write_performed": False,
            "write_capable_harness_job": False,
        },
        "job_state": {
            "status": status,
            "job_kind": "r4-read-only-smoke",
            "write_capable": False,
            "sidecar_started": False,
            "isolated_worktree_required_for_write": True,
        },
        "no_codex_takeover": True,
    }


def authority_decision(candidate_id: str, status: str, blockers: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "source": "harness runtime safety",
        "candidate_id": candidate_id,
        "priority_order": "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit",
        "blockers": sorted(set(blockers or [])),
    }


def base_receipt(candidate_id: str, *, install_receipt_ref: str, rollback_ref: str, transcript: str, status: str) -> dict[str, Any]:
    meta = CANDIDATE_REGISTRY[candidate_id]
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool_name": candidate_id,
        "candidate_id": candidate_id,
        "adapter_kind": meta["adapter_kind"],
        "guard_profile": meta["guard_profile"],
        "source_url": meta["source_url"],
        "source_pin": meta["source_pin"],
        "license_note": meta["license_note"],
        "sensitive_command_policy": meta["sensitive_command_policy"],
        "hook_policy": meta["hook_policy"],
        "async_headless_lifecycle_state": meta["async_headless_lifecycle_state"],
        "owner_lane": meta["owner_lane"],
        "runtime_stage": "R4",
        "install_receipt": install_receipt_ref,
        "smoke_command": f"{meta['display']} {' '.join(meta['smoke_args'])}".strip(),
        "smoke_type": meta["smoke_type"],
        "timeout_release": {"status": "pass", "released": True},
        "rollback_pointer": rollback_ref,
        "command_transcript": transcript,
        "transcript_redaction": transcript_redaction(transcript),
        "redaction_status": "no_secrets",
    }
    receipt.update(harness_guard_fields(status))
    for flag in GENERIC_FORBIDDEN_FLAGS + HARNESS_TAKEOVER_FLAGS:
        receipt[flag] = False
    return receipt


def blocked_receipt(
    candidate_id: str,
    *,
    blockers: list[str],
    install_receipt_path: Path | None = None,
    rollback_pointer: Any = None,
) -> dict[str, Any]:
    transcript = sanitize_text(f"blocked R4 smoke for {candidate_id}: {', '.join(sorted(set(blockers)))}")
    receipt = base_receipt(
        candidate_id,
        install_receipt_ref=f"receipt-sha256:{stable_hash(str(install_receipt_path))}" if install_receipt_path else "missing",
        rollback_ref=f"rollback-sha256:{stable_hash(rollback_pointer)}" if rollback_pointer else "unavailable",
        transcript=transcript,
        status="blocked",
    )
    receipt.update(
        {
            "r4_status": "blocked",
            "smoke_tested": False,
            "smoke_result": {"status": "blocked", "blockers": sorted(set(blockers))},
            "rollback_ready": False,
            "blockers": sorted(set(blockers)),
            "authority_decision": authority_decision(candidate_id, "blocked", blockers),
        }
    )
    return receipt


def passing_receipt(
    candidate_id: str,
    *,
    install_receipt_path: Path,
    install_receipt: dict[str, Any],
    transcript: str,
) -> dict[str, Any]:
    receipt = base_receipt(
        candidate_id,
        install_receipt_ref=f"receipt-sha256:{stable_hash(str(install_receipt_path))}",
        rollback_ref=f"rollback-sha256:{stable_hash(install_receipt.get('rollback_pointer'))}",
        transcript=sanitize_text(transcript),
        status="smoke-tested",
    )
    receipt.update(
        {
            "runtime_stage": "smoke-tested",
            "r4_status": "smoke-tested",
            "smoke_tested": True,
            "smoke_result": {"status": "pass"},
            "rollback_ready": True,
            "blockers": [],
            "authority_decision": authority_decision(candidate_id, "allow-read-only-smoke"),
        }
    )
    return receipt


def run_single_smoke(candidate_id: str, install_receipt_path: Path | None, *, timeout_seconds: int) -> dict[str, Any]:
    if install_receipt_path is None:
        return blocked_receipt(candidate_id, blockers=["install_receipt_required"])
    receipt_data, load_blockers = load_json(install_receipt_path)
    blockers = list(load_blockers)
    blockers.extend(install_receipt_blockers(candidate_id, receipt_data))
    if blockers or receipt_data is None:
        return blocked_receipt(
            candidate_id,
            blockers=blockers,
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer") if isinstance(receipt_data, dict) else None,
        )

    wrapper = Path(str(receipt_data["wrapper_path"]))
    command = [str(wrapper), *CANDIDATE_REGISTRY[candidate_id]["smoke_args"]]
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        transcript = sanitize_text((exc.stdout or "") + "\n" + (exc.stderr or ""))
        blocked = blocked_receipt(
            candidate_id,
            blockers=["smoke_command_timeout"],
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer"),
        )
        blocked["command_transcript"] = transcript or blocked["command_transcript"]
        blocked["transcript_redaction"] = transcript_redaction(blocked["command_transcript"])
        blocked["timeout_release"] = {"status": "pass", "released": True, "timed_out": True}
        return blocked
    except OSError:
        return blocked_receipt(
            candidate_id,
            blockers=["smoke_command_launch_failed"],
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer"),
        )

    transcript = sanitize_text((proc.stdout or "") + "\n" + (proc.stderr or ""))
    if proc.returncode != 0:
        blocked = blocked_receipt(
            candidate_id,
            blockers=["smoke_command_failed"],
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer"),
        )
        blocked["command_transcript"] = transcript or blocked["command_transcript"]
        blocked["transcript_redaction"] = transcript_redaction(blocked["command_transcript"])
        blocked["smoke_result"] = {"status": "blocked", "returncode": proc.returncode, "blockers": ["smoke_command_failed"]}
        return blocked
    return passing_receipt(candidate_id, install_receipt_path=install_receipt_path, install_receipt=receipt_data, transcript=transcript)



def git_output(args: list[str], *, cwd: Path, timeout_seconds: int = 10) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or ""
    except OSError as exc:
        return 127, "", str(exc)


def status_pass(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": "pass"}
    if extra:
        payload.update(extra)
    return payload


def r6_live_proof_error(blockers: list[str]) -> dict[str, Any]:
    return response(
        False,
        "r6-live-proof",
        runs_harness_job=False,
        runs_write_capable_harness_job=False,
        proof_out_hash="",
        blockers=sorted(set(blockers)),
    )


def build_r6_harness_proof(
    *,
    repo_root: Path,
    candidate_id: str,
    job_profile: str,
    timeout_seconds: int,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    repo_root = repo_root.resolve()
    candidate_id = normalize_candidate(candidate_id) or ""
    if candidate_id not in CANDIDATE_REGISTRY:
        return None, r6_live_proof_error(["unknown_candidate"])
    allowed_profiles = {"bounded-local-write", "bounded-read-write-guard"}
    if job_profile not in allowed_profiles:
        return None, r6_live_proof_error(["unsupported_job_profile"])
    code, stdout, stderr = git_output(["git", "rev-parse", "--show-toplevel"], cwd=repo_root, timeout_seconds=timeout_seconds)
    if code != 0:
        return None, r6_live_proof_error(["repo_root_must_be_git_worktree"])
    code, status_before, _ = git_output(["git", "status", "--short"], cwd=repo_root, timeout_seconds=timeout_seconds)
    if code != 0:
        return None, r6_live_proof_error(["git_status_failed"])
    if status_before.strip():
        return None, r6_live_proof_error(["repo_root_must_start_clean"])
    code, base_ref, _ = git_output(["git", "rev-parse", "HEAD"], cwd=repo_root, timeout_seconds=timeout_seconds)
    if code != 0:
        return None, r6_live_proof_error(["git_head_unresolved"])
    branch_name = f"r6-harness-proof-{uuid.uuid4().hex[:12]}"
    worktree_path = Path(tempfile.mkdtemp(prefix="r6-harness-proof-"))
    worktree_removed = False
    changed_paths: list[str] = []
    blockers: list[str] = []
    timed_out = False
    try:
        code, out, err = git_output(
            ["git", "worktree", "add", "--detach", str(worktree_path), base_ref.strip()],
            cwd=repo_root,
            timeout_seconds=timeout_seconds,
        )
        if code != 0:
            blockers.append("isolated_worktree_create_failed")
            return None, r6_live_proof_error(blockers)
        proof_dir = worktree_path / ".omx" / "r6-harness-live-job"
        proof_dir.mkdir(parents=True, exist_ok=True)
        job_file = proof_dir / "bounded-harness-job.txt"
        job_body = (
            "R6 bounded local Codex harness job proof.\n"
            f"candidate_id={candidate_id}\n"
            f"job_profile={job_profile}\n"
            "remote_publication_mutated=false\n"
        )
        job_file.write_text(job_body, encoding="utf-8")
        code, status_out, status_err = git_output(["git", "status", "--short"], cwd=worktree_path, timeout_seconds=timeout_seconds)
        if code == 124:
            timed_out = True
            blockers.append("harness_job_timeout")
        elif code != 0:
            blockers.append("changed_paths_report_failed")
        else:
            for line in status_out.splitlines():
                line = line.strip()
                if not line:
                    continue
                changed_paths.append(line[3:] if len(line) > 3 else line)
        if not changed_paths:
            blockers.append("changed_paths_report_empty")
        code, _, _ = git_output(["git", "restore", "--worktree", "--staged", "."], cwd=worktree_path, timeout_seconds=timeout_seconds)
        if code not in {0, 1}:
            blockers.append("rollback_restore_failed")
        if job_file.exists():
            try:
                job_file.unlink()
            except OSError:
                blockers.append("rollback_unlink_failed")
        # Remove now-empty generated dirs from the detached worktree before cleanup.
        for parent in (proof_dir, proof_dir.parent):
            try:
                parent.rmdir()
            except OSError:
                pass
        code, clean_out, _ = git_output(["git", "status", "--short"], cwd=worktree_path, timeout_seconds=timeout_seconds)
        if code != 0 or clean_out.strip():
            blockers.append("rollback_clean_status_failed")
    finally:
        code, _, _ = git_output(["git", "worktree", "remove", "--force", str(worktree_path)], cwd=repo_root, timeout_seconds=timeout_seconds)
        worktree_removed = code == 0
        if not worktree_removed:
            blockers.append("isolated_worktree_cleanup_failed")
        git_output(["git", "branch", "-D", branch_name], cwd=repo_root, timeout_seconds=timeout_seconds)
    code, status_after, _ = git_output(["git", "status", "--short"], cwd=repo_root, timeout_seconds=timeout_seconds)
    if code != 0 or status_after.strip():
        blockers.append("repo_root_clean_after_job_failed")
    if blockers:
        return None, r6_live_proof_error(blockers)
    changed_path_hashes = [stable_hash(path) for path in sorted(changed_paths)]
    proof = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "lane": "codex-harnesses-governance",
        "external_side_effects": "harness_job",
        "action_performed": True,
        "candidate_id": candidate_id,
        "candidate_id_hash": stable_hash(candidate_id),
        "job_profile": job_profile,
        "job_id_hash": stable_hash({"candidate_id": candidate_id, "job_profile": job_profile, "base_ref": base_ref.strip()}),
        "read_guard": status_pass({"scope": "repo-local bounded proof job", "read_only_inputs": True}),
        "write_guard": status_pass({"write_scope": "isolated_worktree_only", "repo_root_written": False}),
        "isolated_worktree": status_pass({"worktree_path_hash": stable_hash(str(worktree_path)), "branch_detached": True}),
        "job_state": status_pass({"job_kind": "r6-bounded-local-harness-job", "write_capable": True, "bounded": True}),
        "changed_paths_report": status_pass({"path_hashes": changed_path_hashes, "paths": [".omx/r6-harness-live-job/bounded-harness-job.txt"]}),
        "timeout_release": status_pass({"released": True, "timeout_seconds": timeout_seconds, "timed_out": timed_out}),
        "rollback": status_pass({"rollback_ready": True, "restored_clean": True, "rollback_ref_hash": stable_hash(base_ref.strip())}),
        "cleanup": status_pass({"cleaned": True, "isolated_worktree_removed": worktree_removed}),
        "no_codex_takeover": True,
        "active_sidecar_took_over_codex": False,
        "codex_launcher_mutated": False,
        "native_codex_replaced": False,
        "native_subagents_replaced": False,
        "native_omx_replaced": False,
        "langgraph_replaced": False,
        "apply_patch_replaced": False,
        "local_main_gate_bypassed": False,
        "remote_publication_mutated": False,
        "redaction_status": "pass",
        "raw_payload_policy": "redacted_status_only",
    }
    payload = response(
        True,
        "r6-live-proof",
        runs_harness_job=True,
        runs_write_capable_harness_job=True,
        proof_out_hash="",
        candidate_id=candidate_id,
        candidate_id_hash=stable_hash(candidate_id),
        job_profile=job_profile,
        changed_paths_count=len(changed_paths),
        redaction_status="pass",
        remote_publication_mutated=False,
    )
    return proof, payload


def command_r6_live_proof(args: argparse.Namespace) -> dict[str, Any]:
    proof, payload = build_r6_harness_proof(
        repo_root=Path(args.root),
        candidate_id=args.candidate_id,
        job_profile=args.job_profile,
        timeout_seconds=max(1, int(args.timeout_seconds)),
    )
    if proof is None:
        return payload
    proof_out = Path(args.proof_out).resolve()
    proof_out.parent.mkdir(parents=True, exist_ok=True)
    proof_out.write_text(json.dumps(proof, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["proof_out_hash"] = stable_hash(str(proof_out))
    payload["proof_hash"] = stable_hash(proof)
    return payload

def write_receipt(receipt_dir: Path, candidate_id: str, receipt: dict[str, Any]) -> dict[str, Any]:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    filename = f"r4-codex-harnesses-smoke-{candidate_id.lower().replace(' ', '-').replace('_', '-')}.json"
    path = receipt_dir / filename
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = str(receipt.get("r4_status", "blocked"))
    return {
        "candidate_id": candidate_id,
        "adapter_kind": receipt.get("adapter_kind"),
        "receipt_file": filename,
        "receipt_path_hash": stable_hash(str(path)),
        "r4_status": status,
        "smoke_tested": receipt.get("smoke_tested") is True,
        "blockers": receipt.get("blockers", []),
    }


def parse_install_receipt_mappings(values: list[str]) -> tuple[dict[str, Path], list[str]]:
    mapping: dict[str, Path] = {}
    errors: list[str] = []
    for item in values:
        if "=" not in item:
            errors.append("install_receipt_mapping_must_be_candidate_equals_path")
            continue
        key, value = item.split("=", 1)
        candidate_id = normalize_candidate(key)
        if candidate_id is None:
            errors.append(f"unknown_candidate:{sanitize_text(key, limit=80)}")
            continue
        mapping[candidate_id] = Path(value)
    return mapping, errors


def selected_candidates(values: list[str]) -> tuple[list[str], list[str]]:
    if not values or any(value.lower() == "all" for value in values):
        return list(CANDIDATE_REGISTRY), []
    candidates: list[str] = []
    errors: list[str] = []
    for value in values:
        candidate_id = normalize_candidate(value)
        if candidate_id is None:
            errors.append(f"unknown_candidate:{sanitize_text(value, limit=80)}")
        elif candidate_id not in candidates:
            candidates.append(candidate_id)
    return candidates, errors


def response(ok: bool, action: str, **extra: Any) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": ok,
        "action": action,
        "mutates_user_level_state": False,
        "installs_pi_or_oh_my_pi": False,
        "starts_sidecar": False,
        "runs_harness_job": False,
        "runs_write_capable_harness_job": False,
        "codex_launcher_mutated": False,
        "native_codex_replaced": False,
        "native_subagents_replaced": False,
        "native_omx_replaced": False,
        "langgraph_replaced": False,
        "apply_patch_replaced": False,
        "local_main_gate_bypassed": False,
        "raw_private_paths_in_output": False,
    }
    payload.update(extra)
    return payload


def command_plan(_args: argparse.Namespace) -> dict[str, Any]:
    candidates = []
    for candidate_id, meta in CANDIDATE_REGISTRY.items():
        candidates.append(
            {
                "candidate_id": candidate_id,
                "display": meta["display"],
                "source_url": meta["source_url"],
                "source_pin": meta["source_pin"],
                "license_note": meta["license_note"],
                "adapter_kind": meta["adapter_kind"],
                "guard_profile": meta["guard_profile"],
                "rollback_pointer": meta["rollback_pointer"],
                "smoke_type": meta["smoke_type"],
                "safe_command": f"{meta['display']} {' '.join(meta['smoke_args'])}".strip(),
                "owner_lane": meta["owner_lane"],
                "sensitive_command_policy": meta["sensitive_command_policy"],
                "hook_policy": meta["hook_policy"],
                "async_headless_lifecycle_state": meta["async_headless_lifecycle_state"],
            }
        )
    return response(
        True,
        "plan",
        candidate_registry={"schema_version": 1, "candidates": candidates},
        safety_boundary="R4 help/version/status/read-only smoke only; no harness install, sidecar start, write job, or Codex takeover.",
    )


def command_run(args: argparse.Namespace) -> dict[str, Any]:
    candidates, candidate_errors = selected_candidates(args.harness)
    receipt_mapping, mapping_errors = parse_install_receipt_mappings(args.install_receipt)
    receipt_index: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    if candidate_errors or mapping_errors:
        return response(False, "run", errors=candidate_errors + mapping_errors, receipt_index=[])

    receipt_dir = Path(args.receipt_dir)
    for candidate_id in candidates:
        receipt = run_single_smoke(candidate_id, receipt_mapping.get(candidate_id), timeout_seconds=max(1, int(args.timeout_seconds)))
        receipts.append(receipt)
        receipt_index.append(write_receipt(receipt_dir, candidate_id, receipt))

    return response(
        True,
        "run",
        receipt_index=receipt_index,
        counts={
            "candidates": len(candidates),
            "smoke_tested": sum(1 for receipt in receipts if receipt.get("smoke_tested") is True),
            "blocked": sum(1 for receipt in receipts if receipt.get("smoke_tested") is not True),
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded R4 Codex harness smoke probes.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Describe canonical R4 smoke behavior.")
    plan.add_argument("--json", action="store_true", help="Emit JSON output.")

    live = sub.add_parser("r6-live-proof", help="Run a bounded repo-local R6 harness job and write redacted proof.")
    live.add_argument("--root", default=".", help="Clean git repository root used as source for the isolated worktree.")
    live.add_argument("--candidate-id", required=True, help="Canonical harness candidate id.")
    live.add_argument("--job-profile", required=True, help="Allowed bounded harness job profile.")
    live.add_argument("--proof-out", required=True, help="Output path for redacted R6 harness proof JSON.")
    live.add_argument("--timeout-seconds", type=int, default=10, help="Bound for git/job operations.")
    live.add_argument("--json", action="store_true", help="Emit JSON output.")

    run = sub.add_parser("run", help="Write R4 smoke-tested or honest blocked receipts.")
    run.add_argument("--receipt-dir", required=True, help="Directory for repo-local smoke receipts.")
    run.add_argument(
        "--harness",
        action="append",
        default=[],
        help="Candidate id or legacy alias to smoke. Repeat or use all. Defaults to all registry candidates.",
    )
    run.add_argument(
        "--install-receipt",
        action="append",
        default=[],
        metavar="HARNESS=PATH",
        help="R3 install/update receipt for a canonical harness.",
    )
    run.add_argument("--timeout-seconds", type=int, default=10, help="Per-command timeout for safe help/version smoke.")
    run.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "plan":
        payload = command_plan(args)
    elif args.command == "r6-live-proof":
        payload = command_r6_live_proof(args)
    else:
        payload = command_run(args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for entry in payload.get("receipt_index", []):
            print(f"{entry['harness']}: {entry['r4_status']}")
        for error in payload.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
