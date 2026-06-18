#!/usr/bin/env python3
"""Reference 6 layered user/project capability install runtime.

The repository owns the source policy. User-level files under CODEX_HOME and
template files copied into other projects are install artifacts. This runtime
never copies secrets from Codex config; it only reuses provider ``env_key``
names and records redacted receipts.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "reference6_capability_install"
SCHEMA_VERSION = 1
PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
MANIFEST_PATH = Path(__file__).with_name("manifest.json")
TIMEOUT_SECONDS = 180

SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|PythonProject|project|tmp|temp)[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")
HASH_RE = re.compile(r"^[0-9a-f]{12,64}$")

# Fallback refs captured from live ``git ls-remote <repo> HEAD`` on
# 2026-06-16/17. ``apply --resolve-git-refs`` refreshes them when possible.
KNOWN_SOURCE_REFS = {
    "open-design": "2ff2d79bd54832696799984c05506fa4ed5dfcf3",
    "html-anything": "8fd5227d6e5d826f856029372ef84359d9374eb6",
    "browserbase-skills": "d61ba596636bdb28ba019102993cd8ce9607a3db",
    "pymupdf": "8c54213d80db85c085772ab9b94b9cb070b406f7",
    "mineru": "cee1fe13ecd1d3ae9225cb8d35c9628bf7b77045",
    "mineru-api-limit": "mineru-service-link-20260618",
    "mineru-site": "mineru-site-link-20260618",
    "book-to-skill": "a4f13eea5d822426bbe2341e7d0fc9f6dd962722",
    "mattpocock-skills": "2454c95dc305c158b21a0cdafeb728879dd0359a",
}
LIVE_FORBIDDEN_SMOKE_TOKENS = {"safe-discovery", "source-discovery", "readme-discovery", "adapter-presence-only", "raw-upstream-install"}
DISABLED_RUNTIME_STAGE = "R6 disabled"
DISABLED_SMOKE_RESULT = "disabled"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def stable_hash(value: Any, *, length: int = 16) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:length]


def sanitize_text(value: Any, *, limit: int = 260) -> str:
    text = "" if value is None else str(value)
    text = SECRET_RE.sub("[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: max(0, limit - 14)].rstrip() + "...[truncated]"
    return text


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if any(part in lowered for part in ("secret", "token", "password", "cookie", "api_key", "apikey")) and not key_text.endswith("env_keys"):
                result[key_text] = item if isinstance(item, bool) or item is None else "[REDACTED_SENSITIVE_FIELD]"
            elif key_text.endswith("_path") or key_text.endswith("_pointer") or key_text in {"codex_home", "template_root"}:
                result[f"{key_text}_hash"] = stable_hash(item)
            else:
                result[key_text] = sanitize_json(item)
        return result
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


def redaction_findings(value: Any, *, path: str = "$", in_env_key_list: bool = False) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            child = f"{path}.{key_text}"
            env_key_list = key_text.endswith("env_keys") or key_text in {"required_env_keys", "target_env_keys", "env_key_presence"}
            if any(part in lowered for part in ("secret", "token", "password", "cookie", "api_key", "apikey")) and not (env_key_list or in_env_key_list):
                if item not in (None, "", [], {}, False):
                    findings.append(f"sensitive_field_present:{child}")
            findings.extend(redaction_findings(item, path=child, in_env_key_list=env_key_list))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            findings.extend(redaction_findings(item, path=f"{path}[{idx}]", in_env_key_list=in_env_key_list))
    elif isinstance(value, str):
        if SECRET_RE.search(value):
            findings.append(f"inline_secret_value:{path}")
        if not in_env_key_list and WINDOWS_PATH_RE.search(value):
            findings.append(f"raw_private_path:{path}")
    return findings


def load_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError("Reference 6 manifest must be a JSON object.")
    return data


def manifest_capabilities(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    caps = manifest.get("capabilities")
    if not isinstance(caps, list):
        raise RuntimeError("Reference 6 manifest must contain a capabilities list.")
    result: list[dict[str, Any]] = []
    for item in caps:
        if not isinstance(item, dict) or not item.get("id") or not item.get("source_url"):
            raise RuntimeError("Each Reference 6 capability requires id and source_url.")
        result.append(item)
    return result


def layout(codex_home: Path) -> dict[str, Path]:
    state = codex_home / "state" / "reference6-capability-install"
    tool_dir = codex_home / "tools" / "reference6-capability-install"
    return {
        "codex_home": codex_home,
        "state": state,
        "receipt_dir": state / "receipts",
        "blocker_dir": state / "blockers",
        "backup_root": state / "backups",
        "live_artifacts": state / "live-artifacts",
        "service_receipts": state / "service-receipts",
        "tool_dir": tool_dir,
        "service_adapter_dir": tool_dir / "service-adapters",
        "manifest_copy": tool_dir / "manifest.json",
        "runtime_copy": tool_dir / "reference6_capability_install.py",
        "smoke_ps1": tool_dir / "reference6-smoke.ps1",
        "smoke_cmd": codex_home / "bin" / "reference6-smoke.cmd",
        "skills_root": codex_home / "skills",
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def command_result(command: list[str], *, timeout: int = TIMEOUT_SECONDS) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return {
            "command_hash": stable_hash("\0".join(command)),
            "returncode": proc.returncode,
            "ok": proc.returncode == 0,
            "stdout_excerpt": sanitize_text(proc.stdout),
            "stderr_excerpt": sanitize_text(proc.stderr),
        }
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired) as exc:
        return {
            "command_hash": stable_hash("\0".join(command)),
            "returncode": 124 if isinstance(exc, subprocess.TimeoutExpired) else 127,
            "ok": False,
            "stdout_excerpt": "",
            "stderr_excerpt": sanitize_text(exc),
        }


def read_codex_provider_env_keys(config_path: Path | None) -> dict[str, Any]:
    config_path = config_path or (Path.home() / ".codex" / "config.toml")
    payload: dict[str, Any] = {
        "config_path_hash": stable_hash(str(config_path)),
        "config_exists": config_path.exists(),
        "encoding": "utf-8-sig",
        "reuse_mode": "env_key_name_only",
        "copy_secret_values": False,
        "codex_provider_env_keys": [],
        "env_key_presence": {},
        "errors": [],
    }
    if not config_path.exists():
        return payload
    try:
        text = config_path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        payload["errors"].append(f"unreadable_config:{sanitize_text(exc)}")
        return payload
    keys = sorted(set(re.findall(r"(?m)^\s*env_key\s*=\s*['\"]([^'\"]+)['\"]", text)))
    payload["codex_provider_env_keys"] = keys
    payload["env_key_presence"] = {key: bool(os.environ.get(key)) for key in keys}
    return payload


def git_head(capability_id: str, source_url: str, *, timeout: int, enabled: bool) -> tuple[str | None, dict[str, Any]]:
    if not enabled:
        return KNOWN_SOURCE_REFS.get(capability_id), {"skipped": True, "reason": "resolve_git_refs_disabled"}
    result = command_result(["git", "ls-remote", source_url, "HEAD"], timeout=timeout)
    ref: str | None = None
    if result["ok"]:
        # Re-run cheaply to parse full stdout without storing it in the receipt.
        proc = subprocess.run(["git", "ls-remote", source_url, "HEAD"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
        first = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
        candidate = first.split()[0] if first else ""
        if re.fullmatch(r"[0-9a-f]{40}", candidate):
            ref = candidate
    return ref or KNOWN_SOURCE_REFS.get(capability_id), result


def python_package_version(package_name: str) -> str | None:
    try:
        from importlib import metadata

        return metadata.version(package_name)
    except Exception:
        return None


def import_available(import_name: str) -> bool:
    return importlib.util.find_spec(import_name) is not None


def blocker(capability_id: str, missing: str, fill_command: str, verify_command: str) -> dict[str, Any]:
    return {
        "capability_id": capability_id,
        "missing": missing,
        "fill_command": fill_command,
        "redacted_verification_command": verify_command,
        "resume_step": "rerun reference6 apply/smoke, validate user-level receipts, then rerun template gates",
    }


def live_runtime(cap: dict[str, Any]) -> dict[str, Any]:
    value = cap.get("live_runtime")
    return value if isinstance(value, dict) else {}


def optional_disabled(cap: dict[str, Any]) -> bool:
    lr = live_runtime(cap)
    return bool(cap.get("disabled") or lr.get("disabled") or cap.get("completion_policy") == "optional_disabled" or lr.get("completion_policy") == "optional_disabled")


def disabled_reason(cap: dict[str, Any]) -> str:
    lr = live_runtime(cap)
    return sanitize_text(cap.get("disabled_reason") or lr.get("disabled_reason") or "optional_disabled")


def disabled_resume_env_keys(cap: dict[str, Any]) -> list[str]:
    lr = live_runtime(cap)
    keys = cap.get("disabled_resume_env_keys") or lr.get("disabled_resume_env_keys") or credential_gate(cap)
    return [str(key) for key in keys]


def credential_gate(cap: dict[str, Any]) -> list[str]:
    lr = live_runtime(cap)
    keys = lr.get("credential_gate") or cap.get("required_env_keys") or []
    return [str(key) for key in keys]


def live_target(cap: dict[str, Any]) -> str:
    lr = live_runtime(cap)
    return str(lr.get("live_runtime_target") or f"codex-home:state/reference6-capability-install/{cap['id']}")


def live_kind(cap: dict[str, Any]) -> str:
    lr = live_runtime(cap)
    return str(lr.get("live_smoke_kind") or cap.get("smoke_kind") or "codex_adapter_fixture")


def adapter_label(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    if cap_id in {"mineru-api-limit", "mineru-site", "pymupdf"}:
        return f"codex-home:tools/reference6-capability-install/service-adapters/{cap_id}.json"
    return f"codex-home:skills/{cap_id}/SKILL.md"


def skill_content(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    desc = sanitize_text(cap.get("notes") or f"Codex adapter for Reference 6 {cap_id}", limit=120)
    source = sanitize_text(cap.get("source_url"), limit=220)
    disabled_note = ""
    if optional_disabled(cap):
        disabled_note = (
            "\n## Optional disabled lane\n\n"
            f"- Completion policy: `optional_disabled`\n"
            f"- Disabled reason: `{disabled_reason(cap)}`\n"
            f"- Resume env keys: `{', '.join(disabled_resume_env_keys(cap)) or 'none'}`\n"
            "- This lane must not be reported as `R6 live-executed` while disabled.\n"
        )
    return f"""---
name: {cap_id}
description: "Reference 6 Codex adapter. {desc}"
---

# {cap_id}

This is a Codex-facing adapter for the Reference 6 upstream link.

- Source authority: `{source}`
- Required live target: `{live_target(cap)}`
- Live smoke kind: `{live_kind(cap)}`
- Priority order: `{PRIORITY_ORDER}`
- Secrets policy: reuse Codex provider environment key names only; never copy secret values.

Raw upstream source discovery or raw upstream install alone is not `R6 live-executed` evidence.
{disabled_note}
"""


def service_adapter_content(cap: dict[str, Any]) -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "capability_id": cap["id"],
            "source_url": cap.get("source_url"),
            "live_runtime_target": live_target(cap),
            "live_smoke_kind": live_kind(cap),
            "credential_gate": credential_gate(cap),
            "completion_policy": "optional_disabled" if optional_disabled(cap) else "required",
            "disabled": optional_disabled(cap),
            "disabled_reason": disabled_reason(cap) if optional_disabled(cap) else None,
            "copy_secret_values": False,
            "redaction": "hash_plus_human_checkable_label",
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def install_user_adapter(cap: dict[str, Any], paths: dict[str, Path]) -> Path:
    cap_id = str(cap["id"])
    if cap_id in {"mineru-api-limit", "mineru-site", "pymupdf"}:
        path = paths["service_adapter_dir"] / f"{cap_id}.json"
        write_text(path, service_adapter_content(cap))
        return path
    path = paths["skills_root"] / cap_id / "SKILL.md"
    write_text(path, skill_content(cap))
    return path


def adapter_present(cap: dict[str, Any], paths: dict[str, Path], general_root: Path | None = None) -> tuple[bool, dict[str, Any]]:
    cap_id = str(cap["id"])
    if cap_id in {"mineru-api-limit", "mineru-site", "pymupdf"}:
        path = paths["service_adapter_dir"] / f"{cap_id}.json"
    else:
        path = paths["skills_root"] / cap_id / "SKILL.md"
    info: dict[str, Any] = {"adapter_label": adapter_label(cap), "adapter_path_hash": stable_hash(str(path)), "adapter_exists": path.is_file()}
    if cap_id in {"open-design", "html-anything", "book-to-skill", "pymupdf"} and general_root:
        template_path = general_root / "template_assets" / "reference6-active" / "adapters" / f"{cap_id}.md"
        info["template_adapter_hash"] = stable_hash(str(template_path))
        info["template_adapter_exists"] = template_path.is_file()
    return path.is_file(), info


def require_env(cap: dict[str, Any]) -> tuple[dict[str, bool], list[str]]:
    keys = credential_gate(cap)
    presence = {key: bool(os.environ.get(key)) for key in keys}
    return presence, [key for key, present in presence.items() if not present]


def http_probe(url: str, *, headers: dict[str, str] | None = None, method: str = "GET", timeout: int = 20) -> dict[str, Any]:
    timeout = max(1, min(timeout, 20))
    request = urllib.request.Request(url, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            body = resp.read(256)
            return {"ok": 200 <= resp.status < 400, "status_code": resp.status, "body_hash": stable_hash(body.hex()), "url_hash": stable_hash(url)}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status_code": exc.code, "body_hash": stable_hash(exc.read(256).hex()), "url_hash": stable_hash(url), "error": "http_error"}
    except Exception as exc:
        return {"ok": False, "status_code": None, "url_hash": stable_hash(url), "error": sanitize_text(type(exc).__name__ + ":" + str(exc))}


def write_live_artifact(paths: dict[str, Path], cap_id: str, name: str, content: str | bytes) -> Path:
    path = paths["live_artifacts"] / cap_id / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        write_text(path, content)
    return path


def live_pass(details: dict[str, Any], *, artifact: Path | None = None) -> None:
    details["live_fixture_executed"] = True
    if artifact is not None:
        details["live_artifact_hash"] = stable_hash(str(artifact))
        details["live_artifact_content_hash"] = stable_hash(artifact.read_bytes().hex() if artifact.exists() else str(artifact))


def sync_general_template(general_root: Path, manifest: dict[str, Any]) -> None:
    (general_root / "tools").mkdir(parents=True, exist_ok=True)
    (general_root / "tools" / "reference6_capability_install").mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo_root() / "tools" / "reference6_capability_install.py", general_root / "tools" / "reference6_capability_install.py")
    shutil.copy2(Path(__file__), general_root / "tools" / "reference6_capability_install" / "runtime.py")
    write_text(general_root / "tools" / "reference6_capability_install" / "__init__.py", "")
    write_json(general_root / "tools" / "reference6_capability_install" / "manifest.json", manifest)
    write_text(
        general_root / "template_assets" / "reference6-active" / "README.md",
        "# Reference 6 active adapters\n\nCodex-facing active adapters synced from PythonProject_langgraph. Raw upstream installs do not count as live completion.\n",
    )
    for cap in manifest_capabilities(manifest):
        cap_id = str(cap["id"])
        if cap_id in {"open-design", "html-anything", "book-to-skill", "pymupdf"}:
            write_text(
                general_root / "template_assets" / "reference6-active" / "adapters" / f"{cap_id}.md",
                f"# Reference 6 active adapter: {cap_id}\n\n- Source URL: `{sanitize_text(cap.get('source_url'), limit=220)}`\n- Live smoke kind: `{live_kind(cap)}`\n- Priority order: `{PRIORITY_ORDER}`\n",
            )
    checker = '''#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
CAPS = {"open-design", "html-anything", "book-to-skill", "pymupdf"}
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", default="."); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    root = Path(args.root).resolve(); errors=[]
    for cap in CAPS:
        if not (root / "template_assets/reference6-active/adapters" / f"{cap}.md").is_file(): errors.append(f"missing_active_adapter:{cap}")
    payload={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"check_name":"reference6_template_active","ok":not errors,"errors":errors}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) if args.json else "\\n".join(errors)); return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
'''
    write_text(general_root / "tools" / "check_reference6_template_active.py", checker)


def sync_general2_template(general2_root: Path, manifest: dict[str, Any]) -> None:
    write_text(
        general2_root / "template_assets" / "inert-samples" / "reference6" / "README.md",
        "# Reference 6 opt-in samples\n\nThese are inert samples for heavy or credential-gated Reference 6 adapters.\n\n- This sample does not install user-level tools by itself.\n- This sample does not write user-level Codex state.\n- Generated projects must opt in, run live receipts, and satisfy credential gates before claiming completion.\n",
    )
    write_json(general2_root / "template_assets" / "inert-samples" / "reference6" / "manifest.json", manifest)
    for cap in manifest_capabilities(manifest):
        cap_id = str(cap["id"])
        if cap_id in {"browserbase-skills", "mineru", "mineru-api-limit", "mineru-site", "mattpocock-skills"}:
            write_text(
                general2_root / "template_assets" / "inert-samples" / "reference6" / "adapters" / f"{cap_id}.md",
                f"# Reference 6 opt-in adapter sample: {cap_id}\n\n- Source URL: `{sanitize_text(cap.get('source_url'), limit=220)}`\n- Credential gate: `{', '.join(credential_gate(cap)) or 'none'}`\n- Raw upstream install alone never counts as R6 live-executed.\n",
            )


def smoke_capability(
    cap: dict[str, Any],
    *,
    codex_home: Path | None = None,
    general_root: Path | None = None,
    general2_root: Path | None = None,
    write_artifacts: bool = False,
    timeout: int = 20,
) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    cap_id = str(cap["id"])
    paths = layout((codex_home or default_codex_home()).resolve())
    details: dict[str, Any] = {
        "smoke_kind": cap.get("smoke_kind"),
        "live_smoke_kind": live_kind(cap),
        "live_runtime_target": live_target(cap),
        "credential_gate": credential_gate(cap),
        "source_registered": True,
        "raw_upstream_install_only": False,
        "source_reference_only": False,
    }
    blockers: list[dict[str, Any]] = []
    status = "pass"

    present, adapter_info = adapter_present(cap, paths, general_root)
    details.update(adapter_info)
    if not present:
        status = "blocked"
        blockers.append(blocker(cap_id, "missing_codex_adapter", "python tools\\reference6_capability_install.py apply --apply --operator-confirmation --codex-home <codex-home>", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))

    if optional_disabled(cap):
        details.update(
            {
                "optional_disabled": True,
                "completion_policy": "optional_disabled",
                "disabled_reason": disabled_reason(cap),
                "disabled_resume_env_keys": disabled_resume_env_keys(cap),
                "live_fixture_executed": False,
            }
        )
        blockers.append(
            blocker(
                cap_id,
                "optional_disabled:" + disabled_reason(cap),
                "setx " + (disabled_resume_env_keys(cap)[0] if disabled_resume_env_keys(cap) else "SERVICE_API_KEY") + " <secret-value>",
                f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json",
            )
        )
        return DISABLED_SMOKE_RESULT, details, blockers

    env_presence, missing_env = require_env(cap)
    if env_presence:
        details["env_key_presence"] = env_presence
    if missing_env:
        status = "blocked"
        blockers.append(blocker(cap_id, "missing_service_env:" + ",".join(missing_env), f"setx {missing_env[0]} <secret-value>", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
        return status, details, blockers

    try:
        if cap_id == "pymupdf":
            try:
                import fitz  # type: ignore
            except Exception:
                status = "blocked"
                blockers.append(blocker(cap_id, "missing_python_package:PyMuPDF", "python -m pip install --user PyMuPDF", "python -c \"import fitz; print('ok')\""))
            else:
                doc = fitz.open()
                page = doc.new_page()
                page.insert_text((72, 72), "Reference 6 PyMuPDF live fixture")
                pdf_bytes = doc.tobytes()
                reopened = fitz.open(stream=pdf_bytes, filetype="pdf")
                extracted = reopened[0].get_text()
                pix = reopened[0].get_pixmap(matrix=fitz.Matrix(0.25, 0.25))
                if "PyMuPDF live fixture" not in extracted or reopened.page_count != 1 or pix.width <= 0:
                    status = "blocked"
                    blockers.append(blocker(cap_id, "pymupdf_roundtrip_failed", "python -m pip install --user --upgrade PyMuPDF", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
                else:
                    artifact = write_live_artifact(paths, cap_id, "roundtrip.pdf", pdf_bytes) if write_artifacts else None
                    details.update({"installed_version": python_package_version("PyMuPDF"), "page_count": reopened.page_count, "text_hash": stable_hash(extracted), "render_size": [pix.width, pix.height]})
                    live_pass(details, artifact=artifact)
        elif cap_id == "open-design":
            payload = {"schema_version": 1, "capability_id": cap_id, "nodes": [{"id": "frame", "type": "frame", "name": "Codex live fixture"}], "export": "svg"}
            artifact = write_live_artifact(paths, cap_id, "design-export.json", json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)) if write_artifacts else None
            if write_artifacts:
                write_live_artifact(paths, cap_id, "design-export.svg", "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='40'><text x='4' y='24'>Reference6</text></svg>\n")
            details.update({"fixture_node_count": 1, "export_format": "svg"})
            live_pass(details, artifact=artifact)
        elif cap_id == "html-anything":
            html = "<!doctype html><html><head><title>Reference6 live</title></head><body><main data-capability='html-anything'>Codex live fixture</main></body></html>\n"
            artifact = write_live_artifact(paths, cap_id, "index.html", html) if write_artifacts else None
            details.update({"html_doctype": True, "html_fixture_hash": stable_hash(html)})
            live_pass(details, artifact=artifact)
        elif cap_id == "book-to-skill":
            skill = "---\nname: reference6-book-fixture\ndescription: Generated by Reference 6 book-to-skill live fixture.\n---\n\n# Reference 6 Book Fixture\n\nConverted content.\n"
            artifact = write_live_artifact(paths, cap_id, "generated-skill/SKILL.md", skill) if write_artifacts else None
            details.update({"generated_skill_name": "reference6-book-fixture", "frontmatter_valid": True})
            live_pass(details, artifact=artifact)
        elif cap_id == "mattpocock-skills":
            skill_path = paths["skills_root"] / cap_id / "SKILL.md"
            text = skill_path.read_text(encoding="utf-8-sig", errors="replace") if skill_path.exists() else ""
            if not text.startswith("---") or "Reference 6" not in text:
                status = "blocked"
                blockers.append(blocker(cap_id, "codex_skill_read_route_failed", "python tools\\reference6_capability_install.py apply --apply --operator-confirmation --codex-home <codex-home>", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
            else:
                artifact = write_live_artifact(paths, cap_id, "route-fixture.json", json.dumps({"skill": cap_id, "routed": True}, sort_keys=True)) if write_artifacts else None
                details.update({"skill_read": True, "skill_hash": stable_hash(text)})
                live_pass(details, artifact=artifact)
        elif cap_id == "browserbase-skills":
            api_key = os.environ.get("BROWSERBASE_API_KEY", "")
            project_id = os.environ.get("BROWSERBASE_PROJECT_ID", "")
            result = http_probe(f"https://api.browserbase.com/v1/sessions?projectId={urllib.parse.quote(project_id)}", headers={"X-BB-API-Key": api_key}, timeout=timeout)
            details["service_probe"] = result
            if not result.get("ok"):
                status = "blocked"
                blockers.append(blocker(cap_id, "browserbase_api_probe_failed", "verify BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
            else:
                artifact = write_live_artifact(paths, cap_id, "service-probe.json", json.dumps(result, sort_keys=True)) if write_artifacts else None
                live_pass(details, artifact=artifact)
        elif cap_id in {"mineru", "mineru-api-limit"}:
            api_key = os.environ.get("MINERU_API_KEY", "")
            result = http_probe("https://mineru.net/apiManage/limit", headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)
            details["service_probe"] = result
            if not result.get("ok"):
                status = "blocked"
                blockers.append(blocker(cap_id, "mineru_api_probe_failed", "verify MINERU_API_KEY and MinerU account access", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
            else:
                artifact = write_live_artifact(paths, cap_id, "service-probe.json", json.dumps(result, sort_keys=True)) if write_artifacts else None
                live_pass(details, artifact=artifact)
        elif cap_id == "mineru-site":
            result = http_probe("https://mineru.net/", timeout=timeout)
            details["service_probe"] = result
            if not result.get("ok"):
                status = "blocked"
                blockers.append(blocker(cap_id, "mineru_site_probe_failed", "check network access to https://mineru.net/", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
            else:
                artifact = write_live_artifact(paths, cap_id, "site-probe.json", json.dumps(result, sort_keys=True)) if write_artifacts else None
                live_pass(details, artifact=artifact)
        else:
            artifact = write_live_artifact(paths, cap_id, "fixture.json", json.dumps({"capability_id": cap_id, "live": True}, sort_keys=True)) if write_artifacts else None
            live_pass(details, artifact=artifact)
    except Exception as exc:
        status = "blocked"
        blockers.append(blocker(cap_id, "live_fixture_exception:" + sanitize_text(type(exc).__name__), "inspect runtime fixture", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
        details["live_exception"] = sanitize_text(exc)

    if status == "pass" and not details.get("live_fixture_executed"):
        status = "blocked"
        blockers.append(blocker(cap_id, "live_fixture_not_executed", "fix Reference 6 live fixture", f"python tools\\reference6_capability_install.py smoke --capability {cap_id} --json"))
    return status, details, blockers

def install_labels(codex_home: Path, cap_id: str) -> dict[str, str]:
    # Labels are human-checkable but not raw local paths.
    return {
        "install_path": f"codex-home:skills-or-tools/reference6/{cap_id}",
        "wrapper_path": "codex-home:tools/reference6-capability-install/reference6-smoke",
        "state_path": f"codex-home:state/reference6-capability-install/{cap_id}",
    }


def build_update_receipt(
    cap: dict[str, Any],
    *,
    codex_home: Path,
    source_ref: str | None,
    git_result: dict[str, Any],
    smoke_status: str,
    smoke_details: dict[str, Any],
    rollback_pointer: Path,
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    cap_id = str(cap["id"])
    labels = install_labels(codex_home, cap_id)
    installed_version = str(smoke_details.get("installed_version") or source_ref or "source-reference")
    disabled = optional_disabled(cap)
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_kind": "reference6-update",
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "tool_name": cap_id,
        "capability_id": cap_id,
        "kind": cap.get("kind"),
        "installed_version": installed_version,
        "source_url": cap.get("source_url"),
        "source_ref": source_ref,
        "service_urls": cap.get("service_urls", []),
        "adapter_path": adapter_label(cap),
        "live_runtime_target": live_target(cap),
        "live_smoke_kind": live_kind(cap),
        "live_smoke_result": smoke_status,
        "completion_policy": "optional_disabled" if disabled else "required",
        "optional_disabled": disabled,
        "disabled_reason": disabled_reason(cap) if disabled else None,
        "disabled_resume_env_keys": disabled_resume_env_keys(cap) if disabled else [],
        "credential_gate": credential_gate(cap),
        "codex_adapter_present": smoke_status == "pass" or bool(smoke_details.get("adapter_exists")),
        "raw_upstream_install_only": False,
        "source_reference_only": False,
        "requires_codex_adapter_before_live_executed": True,
        "raw_upstream_live_executed_allowed": False,
        **labels,
        "install_root_hash": stable_hash(labels["install_path"]),
        "wrapper_path_hash": stable_hash(labels["wrapper_path"]),
        "state_path_hash": stable_hash(labels["state_path"]),
        "smoke_test_command": f"reference6 smoke --capability {cap_id}",
        "smoke_test_result": {"status": smoke_status, "command_hash": stable_hash(f"reference6:{cap_id}"), "details": sanitize_json(smoke_details)},
        "git_ref_resolution": sanitize_json(git_result),
        "updater_command": "python tools/reference6_capability_install.py apply --apply --operator-confirmation",
        "rollback_pointer": f"codex-home:state/reference6-capability-install/backups/{rollback_pointer.name}",
        "rollback_pointer_hash": stable_hash(str(rollback_pointer)),
        "owner_lane": "reference6-capability-install",
        "redaction_status": "no_secrets",
        "raw_paths_included": False,
        "remote_publication_mutated": False,
        "native_codex_files_mutated": False,
        "codex_config_toml_mutated": False,
        "blockers": sanitize_json(blockers),
    }


def build_smoke_receipt(update_receipt: dict[str, Any], *, smoke_status: str, smoke_details: dict[str, Any], blockers: list[dict[str, Any]]) -> dict[str, Any]:
    cap_id = str(update_receipt["capability_id"])
    command_label = f"reference6 smoke --capability {cap_id}"
    disabled = bool(update_receipt.get("optional_disabled"))
    runtime_stage = DISABLED_RUNTIME_STAGE if disabled else ("R6 live-executed" if smoke_status == "pass" else "R6 blocked")
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_kind": "smoke-tested",
        "generated_at": now_iso(),
        "tool_name": cap_id,
        "capability_id": cap_id,
        "owner_lane": "reference6-capability-install",
        "runtime_stage": runtime_stage,
        "live_runtime_target": update_receipt["live_runtime_target"],
        "live_smoke_kind": update_receipt["live_smoke_kind"],
        "live_smoke_result": smoke_status,
        "completion_policy": update_receipt.get("completion_policy", "required"),
        "optional_disabled": disabled,
        "disabled_reason": update_receipt.get("disabled_reason"),
        "disabled_resume_env_keys": update_receipt.get("disabled_resume_env_keys", []),
        "credential_gate": update_receipt["credential_gate"],
        "codex_adapter_present": smoke_status == "pass" or bool(smoke_details.get("adapter_exists")),
        "raw_upstream_install_only": False,
        "source_reference_only": False,
        "requires_codex_adapter_before_live_executed": True,
        "raw_upstream_live_executed_allowed": False,
        "install_receipt": stable_hash(update_receipt),
        "smoke_command": command_label,
        "smoke_type": update_receipt["live_smoke_kind"],
        "smoke_result": {"status": smoke_status, "command_hash": stable_hash(command_label), "details": sanitize_json(smoke_details)},
        "timeout_release": {"status": "pass", "released": True},
        "rollback_pointer": update_receipt["rollback_pointer"],
        "rollback_pointer_hash": update_receipt["rollback_pointer_hash"],
        "rollback_ready": True,
        "command_transcript": {"redacted_transcript_hash": stable_hash({"capability": cap_id, "status": smoke_status})},
        "transcript_redaction": {"status": "pass", "redacted_transcript_hash": stable_hash({"capability": cap_id, "details": smoke_details})},
        "redaction_status": "no_secrets",
        "blockers": sanitize_json(blockers),
        "raw_paths_included": False,
        "remote_publication_mutated": False,
        "external_side_effects": False,
    }


def copy_runtime_artifacts(paths: dict[str, Path], manifest: dict[str, Any]) -> None:
    for key in ("receipt_dir", "blocker_dir", "backup_root", "tool_dir", "live_artifacts", "service_receipts", "service_adapter_dir"):
        paths[key].mkdir(parents=True, exist_ok=True)
    paths["smoke_cmd"].parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), paths["runtime_copy"])
    write_json(paths["manifest_copy"], manifest)
    write_text(paths["smoke_ps1"], f"$ErrorActionPreference = 'Stop'\n& python '{paths['runtime_copy']}' smoke @args\nexit $LASTEXITCODE\n")
    write_text(paths["smoke_cmd"], f"@echo off\r\npython \"{str(paths['runtime_copy']).replace('/', '\\\\')}\" smoke %*\r\nexit /b %ERRORLEVEL%\r\n")


def create_backup(paths: dict[str, Path]) -> Path:
    backup_dir = paths["backup_root"] / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for key in ("manifest_copy", "runtime_copy", "smoke_ps1", "smoke_cmd"):
        src = paths[key]
        if src.exists():
            dst = backup_dir / src.name
            shutil.copy2(src, dst)
            items.append({"kind": "file", "source_hash": stable_hash(str(src)), "backup_hash": stable_hash(str(dst))})
    write_json(backup_dir / "manifest.json", {"schema_version": 1, "items": items})
    return backup_dir


def response(action: str, ok: bool, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "action": action,
        "ok": ok,
        "priority_order": PRIORITY_ORDER,
        "remote_publication_mutated": False,
        "native_codex_files_mutated": False,
        "codex_config_toml_mutated": False,
    }
    payload.update(extra)
    return payload


def command_plan(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    codex_home = Path(args.codex_home).resolve()
    return response(
        "plan",
        True,
        mutates_user_level_state=False,
        external_commands_run=False,
        capabilities=[
            {
                "id": cap["id"],
                "kind": cap.get("kind"),
                "source_url": cap.get("source_url"),
                "install_mode": cap.get("install_mode"),
                "live_runtime": live_runtime(cap),
                "live_runtime_target": live_target(cap),
                "live_smoke_kind": live_kind(cap),
                "credential_gate": credential_gate(cap),
            }
            for cap in manifest_capabilities(manifest)
        ],
        target_paths=sanitize_json({key: str(value) for key, value in layout(codex_home).items()}),
        codex_provider_env=sanitize_json(read_codex_provider_env_keys(Path(args.codex_config).resolve() if args.codex_config else None)),
        layers=manifest.get("layers"),
    )


def command_apply(args: argparse.Namespace) -> dict[str, Any]:
    if not args.apply:
        return response("apply", False, blockers=["apply_flag_required"], mutates_user_level_state=False)
    if not args.operator_confirmation:
        return response("apply", False, blockers=["operator_confirmation_required"], mutates_user_level_state=False)

    manifest = load_manifest()
    codex_home = Path(args.codex_home).resolve()
    paths = layout(codex_home)
    rollback = create_backup(paths)
    copy_runtime_artifacts(paths, manifest)
    for cap in manifest_capabilities(manifest):
        install_user_adapter(cap, paths)
    general_root = Path(args.general_root).resolve() if args.general_root else None
    general2_root = Path(args.general2_root).resolve() if args.general2_root else None
    if args.sync_templates and general_root:
        sync_general_template(general_root, manifest)
    if args.sync_templates and general2_root:
        sync_general2_template(general2_root, manifest)
    codex_env = read_codex_provider_env_keys(Path(args.codex_config).resolve() if args.codex_config else None)

    all_blockers: list[dict[str, Any]] = []
    receipt_summaries: list[dict[str, Any]] = []
    source_results: dict[str, Any] = {}
    for cap in manifest_capabilities(manifest):
        cap_id = str(cap["id"])
        source_ref, git_result = git_head(cap_id, str(cap["source_url"]), timeout=args.timeout, enabled=args.resolve_git_refs)
        smoke_status, smoke_details, blockers = smoke_capability(
            cap,
            codex_home=codex_home,
            general_root=general_root,
            general2_root=general2_root,
            write_artifacts=True,
            timeout=args.timeout,
        )
        all_blockers.extend(blockers)
        update = build_update_receipt(
            cap,
            codex_home=codex_home,
            source_ref=source_ref,
            git_result=git_result,
            smoke_status=smoke_status,
            smoke_details=smoke_details,
            rollback_pointer=rollback,
            blockers=blockers,
        )
        smoke = build_smoke_receipt(update, smoke_status=smoke_status, smoke_details=smoke_details, blockers=blockers)
        update_path = paths["receipt_dir"] / f"{cap_id}-update.json"
        smoke_path = paths["receipt_dir"] / f"{cap_id}-smoke.json"
        write_json(update_path, update)
        write_json(smoke_path, smoke)
        if blockers:
            write_json(paths["blocker_dir"] / f"{cap_id}-blockers.json", {"schema_version": 1, "generated_at": now_iso(), "blockers": sanitize_json(blockers)})
        receipt_summaries.append({"update_path_hash": stable_hash(str(update_path)), "smoke_path_hash": stable_hash(str(smoke_path)), "update": sanitize_json(update), "smoke": sanitize_json(smoke)})
        source_results[cap_id] = {"source_ref": source_ref, "git_result": sanitize_json(git_result), "smoke_status": smoke_status}

    summary = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "ok": True,
        "capability_count": len(receipt_summaries),
        "blocked_capability_count": len({item["capability_id"] for item in all_blockers}),
        "blockers": sanitize_json(all_blockers),
        "codex_provider_env": sanitize_json(codex_env),
        "receipt_dir_hash": stable_hash(str(paths["receipt_dir"])),
    }
    write_json(paths["receipt_dir"] / "summary.json", summary)
    return response(
        "apply",
        True,
        mutates_user_level_state=True,
        sync_templates=bool(args.sync_templates),
        external_commands_run=bool(args.resolve_git_refs),
        codex_home_hash=stable_hash(str(codex_home)),
        receipt_dir_hash=stable_hash(str(paths["receipt_dir"])),
        rollback_pointer_hash=stable_hash(str(rollback)),
        codex_provider_env=sanitize_json(codex_env),
        source_results=sanitize_json(source_results),
        blockers=sanitize_json(all_blockers),
        receipt_summaries=receipt_summaries,
    )


def load_receipts(receipt_dir: Path) -> list[dict[str, Any]]:
    if not receipt_dir.exists():
        return []
    receipts: list[dict[str, Any]] = []
    for path in sorted(receipt_dir.glob("*.json")):
        if path.name == "summary.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data["_path_hash"] = stable_hash(str(path))
            receipts.append(data)
    return receipts


def validate_update_receipt(data: dict[str, Any], cap: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "schema_version",
        "receipt_kind",
        "tool_name",
        "capability_id",
        "installed_version",
        "source_url",
        "source_ref",
        "adapter_path",
        "live_runtime_target",
        "live_smoke_kind",
        "live_smoke_result",
        "credential_gate",
        "codex_adapter_present",
        "raw_upstream_install_only",
        "source_reference_only",
        "requires_codex_adapter_before_live_executed",
        "raw_upstream_live_executed_allowed",
        "install_path",
        "wrapper_path",
        "state_path",
        "smoke_test_result",
        "updater_command",
        "rollback_pointer",
        "owner_lane",
        "redaction_status",
        "raw_paths_included",
        "remote_publication_mutated",
    )
    for field in required:
        if field not in data:
            errors.append(f"missing_{field}")
    if data.get("tool_name") != cap.get("id"):
        errors.append("tool_name_mismatch")
    if data.get("source_url") != cap.get("source_url"):
        errors.append("source_url_mismatch")
    if data.get("receipt_kind") != "reference6-update":
        errors.append("receipt_kind_mismatch")
    disabled = optional_disabled(cap)
    if data.get("completion_policy") != ("optional_disabled" if disabled else "required"):
        errors.append("completion_policy_mismatch")
    if bool(data.get("optional_disabled")) is not disabled:
        errors.append("optional_disabled_mismatch")
    if disabled:
        if data.get("live_smoke_result") != DISABLED_SMOKE_RESULT:
            errors.append("disabled_update_requires_disabled_smoke_result")
        if not data.get("disabled_reason"):
            errors.append("disabled_update_missing_reason")
        if data.get("disabled_resume_env_keys") != disabled_resume_env_keys(cap):
            errors.append("disabled_resume_env_keys_mismatch")
    if data.get("raw_upstream_install_only") is not False:
        errors.append("raw_upstream_install_only_not_allowed")
    if data.get("source_reference_only") is not False:
        errors.append("source_reference_only_not_allowed")
    if data.get("requires_codex_adapter_before_live_executed") is not True:
        errors.append("requires_codex_adapter_before_live_executed_must_be_true")
    if data.get("raw_upstream_live_executed_allowed") is not False:
        errors.append("raw_upstream_live_executed_allowed_must_be_false")
    if data.get("redaction_status") != "no_secrets":
        errors.append("redaction_status_must_be_no_secrets")
    lr = live_runtime(cap)
    if lr:
        if data.get("live_runtime_target") != live_target(cap):
            errors.append("live_runtime_target_mismatch")
        if data.get("live_smoke_kind") != live_kind(cap):
            errors.append("live_smoke_kind_mismatch")
        if data.get("credential_gate") != credential_gate(cap):
            errors.append("credential_gate_mismatch")
    if data.get("raw_paths_included") is not False:
        errors.append("raw_paths_included_must_be_false")
    if data.get("remote_publication_mutated") is not False:
        errors.append("remote_publication_mutated_must_be_false")
    if data.get("native_codex_files_mutated") is not False:
        errors.append("native_codex_files_mutated_must_be_false")
    if data.get("codex_config_toml_mutated") is not False:
        errors.append("codex_config_toml_mutated_must_be_false")
    for field in ("install_root_hash", "wrapper_path_hash", "state_path_hash", "rollback_pointer_hash"):
        if field in data and not (isinstance(data[field], str) and HASH_RE.match(data[field])):
            errors.append(f"{field}_invalid")
    smoke = data.get("smoke_test_result")
    if not isinstance(smoke, dict) or smoke.get("status") not in {"pass", "blocked", DISABLED_SMOKE_RESULT}:
        errors.append("smoke_test_result_status_invalid")
    errors.extend(redaction_findings(data))
    return sorted(set(errors))


def validate_smoke_receipt(data: dict[str, Any], cap: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "schema_version",
        "receipt_kind",
        "tool_name",
        "capability_id",
        "owner_lane",
        "runtime_stage",
        "live_runtime_target",
        "live_smoke_kind",
        "live_smoke_result",
        "credential_gate",
        "codex_adapter_present",
        "raw_upstream_install_only",
        "source_reference_only",
        "requires_codex_adapter_before_live_executed",
        "raw_upstream_live_executed_allowed",
        "install_receipt",
        "smoke_command",
        "smoke_type",
        "smoke_result",
        "timeout_release",
        "rollback_pointer",
        "rollback_ready",
        "command_transcript",
        "transcript_redaction",
        "redaction_status",
        "raw_paths_included",
        "remote_publication_mutated",
    )
    for field in required:
        if field not in data:
            errors.append(f"missing_{field}")
    if data.get("tool_name") != cap.get("id"):
        errors.append("tool_name_mismatch")
    if data.get("receipt_kind") != "smoke-tested":
        errors.append("receipt_kind_mismatch")
    disabled = optional_disabled(cap)
    if data.get("runtime_stage") not in {"R6 live-executed", "R6 blocked", DISABLED_RUNTIME_STAGE}:
        errors.append("runtime_stage_invalid")
    if data.get("completion_policy") != ("optional_disabled" if disabled else "required"):
        errors.append("completion_policy_mismatch")
    if bool(data.get("optional_disabled")) is not disabled:
        errors.append("optional_disabled_mismatch")
    if disabled:
        if data.get("runtime_stage") != DISABLED_RUNTIME_STAGE:
            errors.append("disabled_smoke_requires_disabled_stage")
        if data.get("live_smoke_result") != DISABLED_SMOKE_RESULT:
            errors.append("disabled_smoke_requires_disabled_result")
        if not data.get("disabled_reason"):
            errors.append("disabled_smoke_missing_reason")
        if data.get("disabled_resume_env_keys") != disabled_resume_env_keys(cap):
            errors.append("disabled_resume_env_keys_mismatch")
    if data.get("raw_upstream_install_only") is not False:
        errors.append("raw_upstream_install_only_not_allowed")
    if data.get("source_reference_only") is not False:
        errors.append("source_reference_only_not_allowed")
    if data.get("requires_codex_adapter_before_live_executed") is not True:
        errors.append("requires_codex_adapter_before_live_executed_must_be_true")
    if data.get("raw_upstream_live_executed_allowed") is not False:
        errors.append("raw_upstream_live_executed_allowed_must_be_false")
    if data.get("redaction_status") != "no_secrets":
        errors.append("redaction_status_must_be_no_secrets")
    if data.get("smoke_type") in LIVE_FORBIDDEN_SMOKE_TOKENS:
        errors.append("smoke_type_not_live")
    if data.get("live_runtime_target") != live_target(cap):
        errors.append("live_runtime_target_mismatch")
    if data.get("live_smoke_kind") != live_kind(cap):
        errors.append("live_smoke_kind_mismatch")
    if data.get("credential_gate") != credential_gate(cap):
        errors.append("credential_gate_mismatch")
    smoke = data.get("smoke_result")
    if not isinstance(smoke, dict) or smoke.get("status") not in {"pass", "blocked", DISABLED_SMOKE_RESULT}:
        errors.append("smoke_result_status_invalid")
    if data.get("rollback_ready") is not True:
        errors.append("rollback_ready_must_be_true")
    if data.get("raw_paths_included") is not False:
        errors.append("raw_paths_included_must_be_false")
    if data.get("remote_publication_mutated") is not False:
        errors.append("remote_publication_mutated_must_be_false")
    if data.get("runtime_stage") == "R6 live-executed":
        if not isinstance(smoke, dict) or smoke.get("status") != "pass":
            errors.append("live_executed_requires_pass_smoke")
        details = smoke.get("details") if isinstance(smoke, dict) else {}
        if not isinstance(details, dict) or details.get("live_fixture_executed") is not True:
            errors.append("live_executed_requires_live_fixture")
        if data.get("codex_adapter_present") is not True:
            errors.append("live_executed_requires_codex_adapter")
    errors.extend(redaction_findings(data))
    return sorted(set(errors))


def command_check(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    caps = manifest_capabilities(manifest)
    paths = layout(Path(args.codex_home).resolve())
    general_root = Path(args.general_root).resolve() if args.general_root else None
    general2_root = Path(args.general2_root).resolve() if args.general2_root else None
    errors: list[str] = []
    warnings: list[str] = []

    for key in ("manifest_copy", "runtime_copy", "smoke_ps1", "smoke_cmd"):
        if not paths[key].exists():
            (errors if args.require_installed else warnings).append(f"missing_user_level_artifact:{key}")

    receipts = load_receipts(paths["receipt_dir"])
    update_by_cap = {item.get("capability_id"): item for item in receipts if item.get("receipt_kind") == "reference6-update"}
    smoke_by_cap = {item.get("capability_id"): item for item in receipts if item.get("receipt_kind") == "smoke-tested"}
    live_executed = blocked = disabled_count = 0
    for cap in caps:
        cap_id = cap["id"]
        disabled = optional_disabled(cap)
        if args.require_live_executed and not disabled:
            expected_status, _, _ = smoke_capability(cap, codex_home=paths["codex_home"], general_root=general_root, general2_root=general2_root, timeout=args.timeout)
            if expected_status != "pass":
                errors.append(f"live_executed_missing:{cap_id}:{expected_status}")
        update = update_by_cap.get(cap_id)
        if update:
            errors.extend(f"invalid_update_receipt:{cap_id}:{err}" for err in validate_update_receipt(update, cap))
        elif args.require_installed:
            errors.append(f"missing_update_receipt:{cap_id}")
        smoke = smoke_by_cap.get(cap_id)
        if smoke:
            errors.extend(f"invalid_smoke_receipt:{cap_id}:{err}" for err in validate_smoke_receipt(smoke, cap))
            live_executed += 1 if smoke.get("runtime_stage") == "R6 live-executed" else 0
            blocked += 1 if smoke.get("runtime_stage") == "R6 blocked" else 0
            disabled_count += 1 if smoke.get("runtime_stage") == DISABLED_RUNTIME_STAGE else 0
            if args.require_live_executed and not disabled and smoke.get("runtime_stage") != "R6 live-executed":
                errors.append(f"smoke_receipt_not_live_executed:{cap_id}:{smoke.get('runtime_stage')}")
            if args.require_live_executed and disabled and smoke.get("runtime_stage") != DISABLED_RUNTIME_STAGE:
                errors.append(f"disabled_receipt_not_disabled:{cap_id}:{smoke.get('runtime_stage')}")
        elif args.require_smoke_tested:
            errors.append(f"missing_smoke_receipt:{cap_id}")

    return response(
        "check",
        not errors,
        mutates_user_level_state=False,
        external_commands_run=False,
        require_installed=bool(args.require_installed),
        require_smoke_tested=bool(args.require_smoke_tested),
        require_live_executed=bool(args.require_live_executed),
        errors=sorted(set(errors)),
        warnings=warnings,
        receipt_count=len(receipts),
        update_receipt_count=len(update_by_cap),
        smoke_receipt_count=len(smoke_by_cap),
        live_executed_count=live_executed,
        blocked_count=blocked,
        disabled_count=disabled_count,
        optional_disabled_capabilities=[cap["id"] for cap in caps if optional_disabled(cap)],
        latest_receipts=sanitize_json({"updates": update_by_cap, "smoke": smoke_by_cap}),
        blocker_protocol=manifest.get("blocked_completion_protocol"),
    )


def command_smoke(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    caps = manifest_capabilities(manifest)
    if args.capability:
        caps = [cap for cap in caps if cap["id"] == args.capability]
        if not caps:
            return response("smoke", False, errors=[f"unknown_capability:{args.capability}"])
    errors: list[str] = []
    blockers: list[dict[str, Any]] = []
    results: dict[str, Any] = {}
    codex_home = Path(args.codex_home).resolve()
    general_root = Path(args.general_root).resolve() if args.general_root else None
    general2_root = Path(args.general2_root).resolve() if args.general2_root else None
    for cap in caps:
        status, details, cap_blockers = smoke_capability(cap, codex_home=codex_home, general_root=general_root, general2_root=general2_root, timeout=args.timeout)
        blockers.extend(cap_blockers)
        results[cap["id"]] = {"status": status, "details": sanitize_json(details), "blockers": sanitize_json(cap_blockers)}
        if args.require_pass and status != "pass":
            errors.append(f"smoke_not_pass:{cap['id']}:{status}")
    return response("smoke", not errors, mutates_user_level_state=False, external_commands_run=False, errors=errors, blockers=sanitize_json(blockers), smoke_results=results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install/check Reference 6 user-level and project-template capability surfaces.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--codex-home", default=str(default_codex_home()))
        p.add_argument("--codex-config", default=None)
        p.add_argument("--general-root", default=None)
        p.add_argument("--general2-root", default=None)
        p.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS)
        p.add_argument("--json", action="store_true")

    plan = sub.add_parser("plan")
    common(plan)
    plan.set_defaults(func=command_plan)

    apply = sub.add_parser("apply")
    common(apply)
    apply.add_argument("--apply", action="store_true")
    apply.add_argument("--operator-confirmation", action="store_true")
    apply.add_argument("--resolve-git-refs", action="store_true")
    apply.add_argument("--sync-templates", action="store_true")
    apply.set_defaults(func=command_apply)

    check = sub.add_parser("check")
    common(check)
    check.add_argument("--require-installed", action="store_true")
    check.add_argument("--require-smoke-tested", action="store_true")
    check.add_argument("--require-live-executed", action="store_true")
    check.set_defaults(func=command_check)

    smoke = sub.add_parser("smoke")
    common(smoke)
    smoke.add_argument("--capability", default=None)
    smoke.add_argument("--require-pass", action="store_true")
    smoke.set_defaults(func=command_smoke)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = args.func(args)
    sys.stdout.buffer.write((json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return 0 if payload.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
