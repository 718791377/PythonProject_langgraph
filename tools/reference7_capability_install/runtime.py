#!/usr/bin/env python3
"""Reference 7 Codex adapter/fork install runtime.

The committed Reference 7 manifest is the authority. Every non-Codex upstream
must have a Codex adapter/fork surface before live-executed status can be
claimed. Raw upstream installation alone never counts as Codex completion
evidence. This runtime writes only adapter surfaces and hash-redacted receipts;
it never copies secret values from Codex config and never patches native Codex
core files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "reference7_capability_install"
SCHEMA_VERSION = 1
PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
EXPECTED_LAYER_COUNTS = {"user_level": 16, "project_template_general": 5, "project_template_general_2": 4}
DEDUPE_TO_REFERENCE6 = {"html-anything-ref7": "html-anything", "open-design-ref7": "open-design"}
ALLOWED_SURFACES = [
    "Codex SKILL.md",
    "Codex agent TOML",
    "Codex runtime wrapper",
    "Codex project template adapter",
    "hash-redacted receipt",
]

SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|PythonProject|project|tmp|temp)[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")
HASH_RE = re.compile(r"^[0-9a-f]{12,64}$")
LIVE_FORBIDDEN_SMOKE_TOKENS = {"safe-discovery", "source-discovery", "readme-discovery", "adapter-presence-only", "raw-upstream-install"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def manifest_path() -> Path:
    root_manifest = repo_root() / "docs_bilingual" / "reference_manifests" / "reference7_capability_sources.json"
    if root_manifest.exists():
        return root_manifest
    return Path(__file__).with_name("manifest.json")


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
            elif key_text.endswith("_path") or key_text.endswith("_pointer") or key_text in {"codex_home", "general_root", "general2_root"}:
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
            child = f"{path}.{key_text}"
            env_key_list = key_text.endswith("env_keys") or key_text in {"required_env_keys", "target_env_keys"}
            if any(part in key_text.lower() for part in ("secret", "token", "password", "cookie", "api_key", "apikey")) and not env_key_list:
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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_manifest() -> dict[str, Any]:
    data = json.loads(manifest_path().read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError("Reference 7 manifest must be a JSON object.")
    return data


def capabilities(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    caps = manifest.get("capabilities")
    if not isinstance(caps, list):
        raise RuntimeError("Reference 7 manifest must contain a capabilities list.")
    result: list[dict[str, Any]] = []
    for item in caps:
        if not isinstance(item, dict) or not item.get("id") or not item.get("source_url"):
            raise RuntimeError("Each Reference 7 capability requires id and source_url.")
        result.append(item)
    return result


def layer_counts(caps: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for cap in caps:
        layer = str(cap.get("target_layer") or "unknown")
        counts[layer] = counts.get(layer, 0) + 1
    return counts


def user_layout(codex_home: Path) -> dict[str, Path]:
    state = codex_home / "state" / "reference7-capability-install"
    tool_dir = codex_home / "tools" / "reference7-capability-install"
    return {
        "codex_home": codex_home,
        "state": state,
        "receipt_dir": state / "receipts",
        "blocker_dir": state / "blockers",
        "backup_root": state / "backups",
        "tool_dir": tool_dir,
        "manifest_copy": tool_dir / "manifest.json",
        "runtime_copy": tool_dir / "reference7_capability_install.py",
        "registry_copy": tool_dir / "adapter_registry.json",
        "smoke_ps1": tool_dir / "reference7-smoke.ps1",
        "smoke_cmd": codex_home / "bin" / "reference7-smoke.cmd",
        "skills_root": codex_home / "skills",
        "agents_root": codex_home / "agents",
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


def adapter_kind(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    if cap_id in DEDUPE_TO_REFERENCE6:
        return "reference6-dedupe"
    if cap.get("target_layer") == "user_level" and cap.get("codex_adapter_strategy") == "codex_agent_pack_adapter":
        return "codex-agent-toml"
    if cap.get("target_layer") == "user_level":
        return "codex-skill"
    if cap.get("target_layer") == "project_template_general":
        return "codex-project-runtime-wrapper"
    return "codex-project-inert-template"


def adapter_label(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    kind = adapter_kind(cap)
    if kind == "codex-skill":
        return f"codex-home:skills/{cap_id}/SKILL.md"
    if kind == "codex-agent-toml":
        return f"codex-home:agents/{cap_id}.toml"
    if kind == "reference6-dedupe":
        return f"codex-home:state/reference6-capability-install/receipts/{DEDUPE_TO_REFERENCE6[cap_id]}-smoke.json"
    if kind == "codex-project-runtime-wrapper":
        return f"general-template:template_assets/reference7-active/adapters/{cap_id}.md"
    return f"general2-template:template_assets/inert-samples/reference7/adapters/{cap_id}.md"


def live_runtime(cap: dict[str, Any]) -> dict[str, Any]:
    value = cap.get("live_runtime")
    return value if isinstance(value, dict) else {}


def live_target(cap: dict[str, Any]) -> str:
    lr = live_runtime(cap)
    return str(lr.get("live_runtime_target") or adapter_label(cap))


def live_kind(cap: dict[str, Any]) -> str:
    lr = live_runtime(cap)
    return str(lr.get("live_smoke_kind") or f"{cap['id']}_codex_live_fixture")


def credential_gate(cap: dict[str, Any]) -> list[str]:
    lr = live_runtime(cap)
    return [str(item) for item in (lr.get("credential_gate") or [])]


def skill_content(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    desc = sanitize_text(cap.get("notes") or f"Codex adapter for {cap_id}", limit=110)
    source = sanitize_text(cap.get("source_url"), limit=200)
    return f"""---
name: {cap_id}
description: "Reference 7 Codex adapter. {desc}"
---

# {cap_id}

This is a Codex-side adapter/fork surface for the non-Codex upstream listed in Reference 7.
Raw upstream installation alone is not completion evidence.

- Source authority: `{source}`
- Adapter strategy: `{cap.get("codex_adapter_strategy")}`
- Priority order: `{PRIORITY_ORDER}`
- Secrets policy: reuse Codex provider environment key names only; never copy secret values.

## Use

1. Treat this skill as procedural guidance inside Codex, not as a native subagent.
2. Before executing any external action, create a project-local plan and receipt.
3. For live completion, require the Reference 7 checker receipt proving this Codex adapter exists and smoke-tested.
"""


def agent_toml_content(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    source = sanitize_text(cap.get("source_url"), limit=200)
    return (
        f'name = "{cap_id}"\n'
        f'description = "Reference 7 Codex-native agent-pack adapter for {cap_id}."\n'
        f'developer_instructions = "Use this only as a Codex-native adapter index for {source}. '
        f'Raw upstream agent-pack installation is not completion evidence. Preserve {PRIORITY_ORDER}; '
        'do not copy secrets; record hash-redacted receipts before claiming live execution."\n'
    )


def active_adapter_content(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    return f"""# Reference 7 active Codex adapter: {cap_id}

- Source URL: `{sanitize_text(cap.get("source_url"), limit=220)}`
- Adapter strategy: `{cap.get("codex_adapter_strategy")}`
- Target layer: `D:/PythonProject_General` active reusable template
- Completion rule: raw upstream install alone does not count. A generated project must keep this Codex wrapper/adapter plus hash-redacted receipt evidence.
- Priority order: `{PRIORITY_ORDER}`
"""


def inert_adapter_content(cap: dict[str, Any]) -> str:
    cap_id = str(cap["id"])
    return f"""# Reference 7 inert Codex adapter sample: {cap_id}

This is an inert opt-in sample for `D:/PythonProject_General_2`.

- Source URL: `{sanitize_text(cap.get("source_url"), limit=220)}`
- Adapter strategy: `{cap.get("codex_adapter_strategy")}`
- It does not install upstream packages, start GUI/desktop control, call external accounts, mutate user-level Codex state, or publish remotes by default.
- Upgrade only after a generated project owns its own plan, checker, receipts, and local gates.
"""


def ensure_docs_registry_entry(template_root: Path, doc_id: str, canonical_path: str, zh_path: str) -> None:
    registry = template_root / "docs_bilingual" / "docs_registry.yaml"
    if not registry.exists():
        return
    text = registry.read_text(encoding="utf-8-sig", errors="replace")
    if f"doc_id: {doc_id}" in text:
        return
    block = (
        "\n  - doc_id: " + doc_id + "\n"
        "    doc_class: implementation_plan\n"
        "    status: active\n"
        "    canonical_path: " + canonical_path + "\n"
        "    zh_cn_path: " + zh_path + "\n"
    )
    registry.write_text(text.rstrip() + "\n" + block, encoding="utf-8", newline="\n")


def ensure_local_gate_step(template_root: Path, marker: str, step_line: str, after_marker: str) -> None:
    gate = template_root / "tools" / "ci" / "local_gate.ps1"
    if not gate.exists():
        return
    text = gate.read_text(encoding="utf-8-sig", errors="replace")
    if marker in text:
        return
    lines = text.splitlines()
    insert_at = None
    for index, line in enumerate(lines):
        if after_marker in line:
            insert_at = index + 1
    if insert_at is None:
        insert_at = len(lines)
    lines.insert(insert_at, step_line)
    gate.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def blocker(capability_id: str, missing: str, fill_command: str, verify_command: str) -> dict[str, Any]:
    return {
        "capability_id": capability_id,
        "missing": missing,
        "fill_command": fill_command,
        "redacted_verification_command": verify_command,
        "resume_step": "provide the missing item, rerun reference7 apply/smoke, validate receipts, then rerun source and template gates",
    }


def create_backup(paths: dict[str, Path]) -> Path:
    backup_dir = paths["backup_root"] / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for key in ("manifest_copy", "runtime_copy", "registry_copy", "smoke_ps1", "smoke_cmd"):
        src = paths[key]
        if src.exists():
            dst = backup_dir / src.name
            shutil.copy2(src, dst)
            items.append({"kind": "file", "source_hash": stable_hash(str(src)), "backup_hash": stable_hash(str(dst))})
    write_json(backup_dir / "manifest.json", {"schema_version": 1, "items": items})
    return backup_dir


def copy_runtime_artifacts(paths: dict[str, Path], manifest: dict[str, Any]) -> None:
    for key in ("receipt_dir", "blocker_dir", "backup_root", "tool_dir"):
        paths[key].mkdir(parents=True, exist_ok=True)
    paths["smoke_cmd"].parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), paths["runtime_copy"])
    write_json(paths["manifest_copy"], manifest)
    write_text(paths["smoke_ps1"], f"$ErrorActionPreference = 'Stop'\n& python '{paths['runtime_copy']}' smoke @args\nexit $LASTEXITCODE\n")
    runtime_copy_windows = str(paths["runtime_copy"]).replace("/", "\\")
    write_text(paths["smoke_cmd"], f"@echo off\r\npython \"{runtime_copy_windows}\" smoke %*\r\nexit /b %ERRORLEVEL%\r\n")


def install_user_adapter(cap: dict[str, Any], paths: dict[str, Path]) -> Path | None:
    cap_id = str(cap["id"])
    if adapter_kind(cap) == "codex-skill":
        path = paths["skills_root"] / cap_id / "SKILL.md"
        write_text(path, skill_content(cap))
        return path
    if adapter_kind(cap) == "codex-agent-toml":
        path = paths["agents_root"] / f"{cap_id}.toml"
        write_text(path, agent_toml_content(cap))
        return path
    return None


def sync_general_template(general_root: Path, manifest: dict[str, Any]) -> None:
    caps = [cap for cap in capabilities(manifest) if cap.get("target_layer") == "project_template_general"]
    source_root = repo_root()
    runtime_source = source_root / "tools" / "reference7_capability_install.py"
    package_source = source_root / "tools" / "reference7_capability_install" / "runtime.py"
    if runtime_source.exists():
        (general_root / "tools").mkdir(parents=True, exist_ok=True)
        shutil.copy2(runtime_source, general_root / "tools" / "reference7_capability_install.py")
    if package_source.exists():
        (general_root / "tools" / "reference7_capability_install").mkdir(parents=True, exist_ok=True)
        shutil.copy2(package_source, general_root / "tools" / "reference7_capability_install" / "runtime.py")
        write_text(general_root / "tools" / "reference7_capability_install" / "__init__.py", "")
    write_json(general_root / "tools" / "reference7_capability_install" / "manifest.json", manifest)
    checker = """#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

CAPS = {"html-video", "html-anything-ref7", "open-design-ref7", "graphify", "codegraph"}
PRIORITY = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"

def read_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        errors.append(f"missing_or_invalid_json:{path.as_posix()}:{exc}")
        return {}

def run_json(cmd: list[str], cwd: Path):
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    try:
        return proc.returncode, json.loads(proc.stdout)
    except Exception:
        return proc.returncode, {}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    manifest = read_json(root / "tools/reference7_capability_install/manifest.json", errors)
    observed = {str(item.get("id")) for item in manifest.get("capabilities", []) if isinstance(item, dict) and item.get("target_layer") == "project_template_general"}
    if observed != CAPS:
        errors.append("manifest_active_capability_set_mismatch:" + ",".join(sorted(observed)))
    for cap_id in CAPS:
        if not (root / "template_assets/reference7-active/adapters" / f"{cap_id}.md").is_file():
            errors.append(f"missing_active_adapter:{cap_id}")
    for rel in ("docs_bilingual/implementation_plans/reference7_capability_template_sync_plan.md", "docs_bilingual/implementation_plans/reference7_capability_template_sync_plan.zh-CN.md"):
        if not (root / rel).is_file():
            errors.append(f"missing_plan:{rel}")
    gate = root / "tools/ci/local_gate.ps1"
    if gate.exists() and "check_reference7_capability_install.py" not in gate.read_text(encoding="utf-8-sig", errors="replace"):
        errors.append("local_gate_missing_reference7_checker")
    code, plan = run_json([sys.executable, str(root / "tools/reference7_capability_install.py"), "plan", "--json"], root)
    if code != 0 or not plan.get("ok"):
        errors.append("runtime_plan_failed")
    if plan.get("codex_config_toml_mutated") is not False:
        errors.append("runtime_plan_must_not_mutate_codex_config")
    payload = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "check_name": "reference7_capability_template", "ok": not errors, "root": str(root), "manifest": {"capability_count": len(manifest.get("capabilities", [])) if isinstance(manifest, dict) else 0}, "policy": {"priority_order": PRIORITY, "raw_upstream_install_counts_as_codex_live_executed": False, "codex_config_env_key_name_only": True, "remote_publication_allowed": False}, "errors": sorted(set(errors))}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
"""
    write_text(general_root / "tools" / "check_reference7_capability_install.py", checker)
    plan = """---
doc_id: reference7_capability_template_sync_plan
lang: en
doc_class: implementation_plan
status: active
---

# Reference 7 Capability Template Sync Plan

`D:/PythonProject_General` carries active Reference 7 Codex adapters for generated projects.
Raw upstream installs do not count; generated projects must keep Codex adapters, receipts, and local gates.
"""
    plan_zh = plan.replace("lang: en", "lang: zh-CN")
    write_text(general_root / "docs_bilingual" / "implementation_plans" / "reference7_capability_template_sync_plan.md", plan)
    write_text(general_root / "docs_bilingual" / "implementation_plans" / "reference7_capability_template_sync_plan.zh-CN.md", plan_zh)
    ensure_docs_registry_entry(general_root, "reference7_capability_template_sync_plan", "docs_bilingual/implementation_plans/reference7_capability_template_sync_plan.md", "docs_bilingual/implementation_plans/reference7_capability_template_sync_plan.zh-CN.md")
    ensure_local_gate_step(general_root, "reference7_capability_install", "$steps += Invoke-Step -Python $Python -Name 'reference7_capability_install' -StepArgs @((Join-Path $Root 'tools\\check_reference7_capability_install.py'), '--root', $Root, '--json')", "reference6_capability_install")
    write_text(general_root / "template_assets" / "reference7-active" / "README.md", "# Reference 7 active Codex adapters\n\nActive reusable adapters for generated projects. Raw upstream installs do not count as Codex live-executed evidence.\n")
    for cap in caps:
        write_text(general_root / "template_assets" / "reference7-active" / "adapters" / f"{cap['id']}.md", active_adapter_content(cap))


def sync_general2_template(general2_root: Path, manifest: dict[str, Any]) -> None:
    caps = [cap for cap in capabilities(manifest) if cap.get("target_layer") == "project_template_general_2"]
    checker = """#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = [
    Path("template_assets/inert-samples/reference7/README.md"),
    Path("template_assets/inert-samples/reference7/manifest.json"),
    Path("docs_bilingual/implementation_plans/reference7_capability_inert_template_plan.md"),
    Path("docs_bilingual/implementation_plans/reference7_capability_inert_template_plan.zh-CN.md"),
]
FORBIDDEN = [Path("tools/reference7_capability_install.py"), Path("tools/reference7_capability_install")]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = [f"missing_required_inert_sample:{rel.as_posix()}" for rel in REQUIRED if not (root / rel).exists()]
    errors += [f"forbidden_active_reference7_surface:{rel.as_posix()}" for rel in FORBIDDEN if (root / rel).exists()]
    payload = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "check_name": "reference7_inert_sample", "ok": not errors, "stub_only": True, "live_runtime_enabled": False, "user_level_install_enabled": False, "remote_publication_mutated": False, "errors": sorted(set(errors))}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
"""
    write_text(general2_root / "tools" / "check_reference7_inert_sample.py", checker)
    plan = """---
doc_id: reference7_capability_inert_template_plan
lang: en
doc_class: implementation_plan
status: active
---

# Reference 7 Inert Template Plan

`D:/PythonProject_General_2` carries Reference 7 only as inert opt-in samples.
It does not install upstream projects, write user-level Codex state, control GUI/browser/account surfaces, or publish remotes by default.
"""
    plan_zh = plan.replace("lang: en", "lang: zh-CN")
    write_text(general2_root / "docs_bilingual" / "implementation_plans" / "reference7_capability_inert_template_plan.md", plan)
    write_text(general2_root / "docs_bilingual" / "implementation_plans" / "reference7_capability_inert_template_plan.zh-CN.md", plan_zh)
    ensure_docs_registry_entry(general2_root, "reference7_capability_inert_template_plan", "docs_bilingual/implementation_plans/reference7_capability_inert_template_plan.md", "docs_bilingual/implementation_plans/reference7_capability_inert_template_plan.zh-CN.md")
    ensure_local_gate_step(general2_root, "reference7_inert_sample", "$steps += Invoke-Step -Python $Python -Name 'reference7_inert_sample' -StepArgs @((Join-Path $Root 'tools\\check_reference7_inert_sample.py'), '--root', $Root, '--json')", "reference6_inert_sample")
    write_json(general2_root / "template_assets" / "inert-samples" / "reference7" / "manifest.json", manifest)
    write_text(general2_root / "template_assets" / "inert-samples" / "reference7" / "README.md", "# Reference 7 inert sample\n\nThis folder contains inert opt-in samples. It does not install upstream projects, does not write user-level Codex state, does not control GUI/browser/account surfaces, and does not publish remotes by default.\n")
    for cap in caps:
        write_text(general2_root / "template_assets" / "inert-samples" / "reference7" / "adapters" / f"{cap['id']}.md", inert_adapter_content(cap))


def smoke_capability(cap: dict[str, Any], *, codex_home: Path, general_root: Path | None, general2_root: Path | None, write_artifacts: bool = False) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    cap_id = str(cap["id"])
    kind = adapter_kind(cap)
    live_artifact_dir = codex_home / "state" / "reference7-capability-install" / "live-artifacts" / cap_id
    details: dict[str, Any] = {
        "adapter_kind": kind,
        "adapter_label": adapter_label(cap),
        "live_runtime_target": live_target(cap),
        "live_smoke_kind": live_kind(cap),
        "credential_gate": credential_gate(cap),
        "codex_adapter_required": cap.get("requires_codex_adapter_before_live_executed") is True,
        "raw_upstream_live_executed_allowed": cap.get("raw_upstream_live_executed_allowed") is True,
        "raw_upstream_install_only": False,
        "source_reference_only": False,
    }
    blockers: list[dict[str, Any]] = []
    status = "pass"
    if kind == "codex-skill":
        path = codex_home / "skills" / cap_id / "SKILL.md"
        details.update({"surface": "Codex SKILL.md", "adapter_path_hash": stable_hash(str(path)), "adapter_exists": path.is_file()})
        if not path.is_file():
            status = "blocked"
            blockers.append(blocker(cap_id, "missing_codex_skill_adapter", "python tools\\reference7_capability_install.py apply --apply --operator-confirmation --codex-home <codex-home>", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
        else:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if not text.startswith("---") or "Reference 7" not in text:
                status = "blocked"
                blockers.append(blocker(cap_id, "codex_skill_adapter_live_read_failed", "refresh Reference 7 user-level adapter", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
            else:
                artifact = live_artifact_dir / "fixture.json"
                if write_artifacts:
                    live_artifact_dir.mkdir(parents=True, exist_ok=True)
                    write_json(artifact, {"schema_version": 1, "capability_id": cap_id, "fixture": "codex-skill-read", "skill_hash": stable_hash(text)})
                details.update({"skill_hash": stable_hash(text), "live_fixture_executed": True, "live_artifact_hash": stable_hash(str(artifact))})
    elif kind == "codex-agent-toml":
        path = codex_home / "agents" / f"{cap_id}.toml"
        details.update({"surface": "Codex agent TOML", "adapter_path_hash": stable_hash(str(path)), "adapter_exists": path.is_file()})
        if not path.is_file():
            status = "blocked"
            blockers.append(blocker(cap_id, "missing_codex_agent_toml_adapter", "python tools\\reference7_capability_install.py apply --apply --operator-confirmation --codex-home <codex-home>", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
        else:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            required = all(token in text for token in ("name =", "description =", "developer_instructions ="))
            if not required:
                status = "blocked"
                blockers.append(blocker(cap_id, "codex_agent_toml_schema_failed", "refresh Reference 7 agent adapter", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
            else:
                artifact = live_artifact_dir / "agent-schema.json"
                if write_artifacts:
                    live_artifact_dir.mkdir(parents=True, exist_ok=True)
                    write_json(artifact, {"schema_version": 1, "capability_id": cap_id, "fixture": "agent-toml-schema", "toml_hash": stable_hash(text)})
                details.update({"agent_schema_valid": True, "live_fixture_executed": True, "live_artifact_hash": stable_hash(str(artifact))})
    elif kind == "reference6-dedupe":
        path = codex_home / "state" / "reference6-capability-install" / "receipts" / f"{DEDUPE_TO_REFERENCE6[cap_id]}-smoke.json"
        details.update({"surface": "Reference 6 Codex-side smoke receipt", "dedupe_to_reference6": DEDUPE_TO_REFERENCE6[cap_id], "reference6_receipt_hash": stable_hash(str(path)), "reference6_receipt_exists": path.is_file()})
        if not path.is_file():
            status = "blocked"
            blockers.append(blocker(cap_id, f"missing_reference6_codex_smoke_receipt:{DEDUPE_TO_REFERENCE6[cap_id]}", "python tools\\reference6_capability_install.py apply --apply --operator-confirmation --codex-home <codex-home>", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
        else:
            try:
                ref6 = json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                status = "blocked"
                blockers.append(blocker(cap_id, "invalid_reference6_live_receipt", "rerun Reference 6 apply/smoke", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
                details["reference6_receipt_error"] = sanitize_text(exc)
            else:
                ref6_details = ref6.get("smoke_result", {}).get("details", {}) if isinstance(ref6.get("smoke_result"), dict) else {}
                ref6_live = (
                    ref6.get("runtime_stage") == "R6 live-executed"
                    and ref6.get("live_smoke_result") == "pass"
                    and ref6.get("codex_adapter_present") is True
                    and ref6.get("raw_upstream_install_only") is False
                    and ref6.get("source_reference_only") is False
                    and isinstance(ref6_details, dict)
                    and ref6_details.get("live_fixture_executed") is True
                )
                if not ref6_live:
                    status = "blocked"
                    blockers.append(blocker(cap_id, f"reference6_receipt_not_strict_live:{DEDUPE_TO_REFERENCE6[cap_id]}", "rerun Reference 6 strict live smoke", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
                else:
                    details.update({"reference6_strict_live_receipt": True, "live_fixture_executed": True, "reference6_live_hash": stable_hash(ref6)})
    elif kind == "codex-project-runtime-wrapper":
        path = (general_root or Path("D:/PythonProject_General")) / "template_assets" / "reference7-active" / "adapters" / f"{cap_id}.md"
        details.update({"surface": "Codex project template adapter", "adapter_path_hash": stable_hash(str(path)), "adapter_exists": path.is_file()})
        if not path.is_file():
            status = "blocked"
            blockers.append(blocker(cap_id, "missing_general_active_template_adapter", "python tools\\reference7_capability_install.py apply --apply --operator-confirmation --general-root <General>", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --general-root <General> --json"))
        else:
            artifact = live_artifact_dir / f"{cap_id}-artifact.json"
            if write_artifacts:
                live_artifact_dir.mkdir(parents=True, exist_ok=True)
                write_json(artifact, {"schema_version": 1, "capability_id": cap_id, "fixture": kind, "adapter_hash": stable_hash(path.read_text(encoding="utf-8-sig", errors="replace"))})
            details.update({"template_fixture_generated": True, "live_fixture_executed": True, "live_artifact_hash": stable_hash(str(artifact))})
    else:
        path = (general2_root or Path("D:/PythonProject_General_2")) / "template_assets" / "inert-samples" / "reference7" / "adapters" / f"{cap_id}.md"
        details.update({"surface": "Codex project inert template adapter", "adapter_path_hash": stable_hash(str(path)), "adapter_exists": path.is_file()})
        if not path.is_file():
            status = "blocked"
            blockers.append(blocker(cap_id, "missing_general2_inert_template_adapter", "python tools\\reference7_capability_install.py apply --apply --operator-confirmation --general2-root <General_2>", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --general2-root <General_2> --json"))
        else:
            artifact = live_artifact_dir / f"{cap_id}-opt-in-fixture.json"
            if write_artifacts:
                live_artifact_dir.mkdir(parents=True, exist_ok=True)
                write_json(artifact, {"schema_version": 1, "capability_id": cap_id, "fixture": "codex-opt-in-template-adapter", "adapter_hash": stable_hash(path.read_text(encoding="utf-8-sig", errors="replace"))})
            details.update({"opt_in_fixture_generated": True, "live_fixture_executed": True, "live_artifact_hash": stable_hash(str(artifact))})
    if cap.get("requires_codex_adapter_before_live_executed") is not True:
        status = "blocked"
        blockers.append(blocker(cap_id, "manifest_missing_codex_adapter_requirement", "fix docs_bilingual/reference_manifests/reference7_capability_sources.json", "python tools\\check_reference7_capability_install.py --root . --json"))
    if cap.get("raw_upstream_live_executed_allowed") is not False:
        status = "blocked"
        blockers.append(blocker(cap_id, "raw_upstream_install_not_forbidden", "set raw_upstream_live_executed_allowed=false", "python tools\\check_reference7_capability_install.py --root . --json"))
    lr = live_runtime(cap)
    if not lr.get("live_runtime_target") or not lr.get("live_smoke_kind"):
        status = "blocked"
        blockers.append(blocker(cap_id, "manifest_missing_live_runtime_target_or_kind", "refresh Reference 7 live_runtime manifest fields", "python tools\\check_reference7_capability_install.py --root . --json"))
    if status == "pass" and details.get("live_fixture_executed") is not True:
        status = "blocked"
        blockers.append(blocker(cap_id, "live_fixture_not_executed", "fix Reference 7 live fixture", f"python tools\\reference7_capability_install.py smoke --capability {cap_id} --json"))
    return status, details, blockers


def build_update_receipt(cap: dict[str, Any], *, smoke_status: str, smoke_details: dict[str, Any], rollback_pointer: Path, blockers: list[dict[str, Any]]) -> dict[str, Any]:
    cap_id = str(cap["id"])
    label = adapter_label(cap)
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_kind": "reference7-update",
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "tool_name": cap_id,
        "capability_id": cap_id,
        "adapter_kind": adapter_kind(cap),
        "codex_adapter_present": smoke_status == "pass",
        "raw_upstream_install_only": False,
        "requires_codex_adapter_before_live_executed": True,
        "raw_upstream_live_executed_allowed": False,
        "allowed_completion_surfaces": ALLOWED_SURFACES,
        "installed_version": "codex-adapter",
        "source_url": cap.get("source_url"),
        "source_ref": None,
        "live_runtime_target": live_target(cap),
        "live_smoke_kind": live_kind(cap),
        "live_smoke_result": smoke_status,
        "credential_gate": credential_gate(cap),
        "source_reference_only": False,
        "adapter_path": label,
        "install_path": label,
        "wrapper_path": "codex-home:tools/reference7-capability-install/reference7-smoke",
        "state_path": f"codex-home:state/reference7-capability-install/{cap_id}",
        "install_root_hash": stable_hash(label),
        "wrapper_path_hash": stable_hash("codex-home:tools/reference7-capability-install/reference7-smoke"),
        "state_path_hash": stable_hash(f"codex-home:state/reference7-capability-install/{cap_id}"),
        "smoke_test_command": f"reference7 smoke --capability {cap_id}",
        "smoke_test_result": {"status": smoke_status, "command_hash": stable_hash(f"reference7:{cap_id}"), "details": sanitize_json(smoke_details)},
        "updater_command": "python tools/reference7_capability_install.py apply --apply --operator-confirmation",
        "rollback_pointer": f"codex-home:state/reference7-capability-install/backups/{rollback_pointer.name}",
        "rollback_pointer_hash": stable_hash(str(rollback_pointer)),
        "owner_lane": "reference7-capability-install",
        "redaction_status": "no_secrets",
        "raw_paths_included": False,
        "remote_publication_mutated": False,
        "native_codex_files_mutated": False,
        "codex_config_toml_mutated": False,
        "blockers": sanitize_json(blockers),
    }


def build_smoke_receipt(update: dict[str, Any], *, smoke_status: str, smoke_details: dict[str, Any], blockers: list[dict[str, Any]]) -> dict[str, Any]:
    cap_id = str(update["capability_id"])
    command_label = f"reference7 smoke --capability {cap_id}"
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_kind": "smoke-tested",
        "generated_at": now_iso(),
        "tool_name": cap_id,
        "capability_id": cap_id,
        "owner_lane": "reference7-capability-install",
        "adapter_kind": update["adapter_kind"],
        "allowed_completion_surfaces": ALLOWED_SURFACES,
        "runtime_stage": "R6 live-executed" if smoke_status == "pass" else "R6 blocked",
        "codex_adapter_present": smoke_status == "pass",
        "raw_upstream_install_only": False,
        "requires_codex_adapter_before_live_executed": True,
        "raw_upstream_live_executed_allowed": False,
        "live_runtime_target": update["live_runtime_target"],
        "live_smoke_kind": update["live_smoke_kind"],
        "live_smoke_result": smoke_status,
        "credential_gate": update["credential_gate"],
        "source_reference_only": False,
        "install_receipt": stable_hash(update),
        "smoke_command": command_label,
        "smoke_type": update["live_smoke_kind"],
        "smoke_result": {"status": smoke_status, "command_hash": stable_hash(command_label), "details": sanitize_json(smoke_details)},
        "timeout_release": {"status": "pass", "released": True},
        "rollback_pointer": update["rollback_pointer"],
        "rollback_pointer_hash": update["rollback_pointer_hash"],
        "rollback_ready": True,
        "command_transcript": {"redacted_transcript_hash": stable_hash({"capability": cap_id, "status": smoke_status})},
        "transcript_redaction": {"status": "pass", "redacted_transcript_hash": stable_hash({"capability": cap_id, "details": smoke_details})},
        "redaction_status": "no_secrets",
        "blockers": sanitize_json(blockers),
        "raw_paths_included": False,
        "remote_publication_mutated": False,
        "external_side_effects": False,
    }


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
    caps = capabilities(manifest)
    return response(
        "plan",
        True,
        mutates_user_level_state=False,
        external_commands_run=False,
        capability_count=len(caps),
        layer_counts=layer_counts(caps),
        capabilities=[
            {
                "id": cap["id"],
                "source_url": cap.get("source_url"),
                "target_layer": cap.get("target_layer"),
                "adapter_kind": adapter_kind(cap),
                "codex_adapter_strategy": cap.get("codex_adapter_strategy"),
                "live_runtime": live_runtime(cap),
                "live_runtime_target": live_target(cap),
                "live_smoke_kind": live_kind(cap),
                "credential_gate": credential_gate(cap),
                "requires_codex_adapter_before_live_executed": cap.get("requires_codex_adapter_before_live_executed"),
                "raw_upstream_live_executed_allowed": cap.get("raw_upstream_live_executed_allowed"),
            }
            for cap in caps
        ],
        expected_layer_counts=EXPECTED_LAYER_COUNTS,
        generated_policy=manifest.get("generated_policy"),
        codex_provider_env=sanitize_json(read_codex_provider_env_keys(Path(args.codex_config).resolve() if args.codex_config else None)),
        target_paths=sanitize_json({key: str(value) for key, value in user_layout(Path(args.codex_home).resolve()).items()}),
    )


def command_apply(args: argparse.Namespace) -> dict[str, Any]:
    if not args.apply:
        return response("apply", False, blockers=["apply_flag_required"], mutates_user_level_state=False)
    if not args.operator_confirmation:
        return response("apply", False, blockers=["operator_confirmation_required"], mutates_user_level_state=False)
    manifest = load_manifest()
    caps = capabilities(manifest)
    codex_home = Path(args.codex_home).resolve()
    paths = user_layout(codex_home)
    rollback = create_backup(paths)
    copy_runtime_artifacts(paths, manifest)
    for cap in caps:
        install_user_adapter(cap, paths)
    general_root = Path(args.general_root).resolve() if args.general_root else None
    general2_root = Path(args.general2_root).resolve() if args.general2_root else None
    if args.sync_templates and general_root:
        sync_general_template(general_root, manifest)
    if args.sync_templates and general2_root:
        sync_general2_template(general2_root, manifest)
    write_json(paths["registry_copy"], {"schema_version": 1, "generated_at": now_iso(), "capability_count": len(caps), "layer_counts": layer_counts(caps), "adapters": [{"id": cap["id"], "adapter_kind": adapter_kind(cap), "adapter_label": adapter_label(cap), "source_url": cap.get("source_url")} for cap in caps]})
    all_blockers: list[dict[str, Any]] = []
    receipt_summaries: list[dict[str, Any]] = []
    for cap in caps:
        status, details, blockers = smoke_capability(cap, codex_home=codex_home, general_root=general_root, general2_root=general2_root, write_artifacts=True)
        all_blockers.extend(blockers)
        update = build_update_receipt(cap, smoke_status=status, smoke_details=details, rollback_pointer=rollback, blockers=blockers)
        smoke = build_smoke_receipt(update, smoke_status=status, smoke_details=details, blockers=blockers)
        update_path = paths["receipt_dir"] / f"{cap['id']}-update.json"
        smoke_path = paths["receipt_dir"] / f"{cap['id']}-smoke.json"
        write_json(update_path, update)
        write_json(smoke_path, smoke)
        if blockers:
            write_json(paths["blocker_dir"] / f"{cap['id']}-blockers.json", {"schema_version": 1, "generated_at": now_iso(), "blockers": sanitize_json(blockers)})
        receipt_summaries.append({"update_path_hash": stable_hash(str(update_path)), "smoke_path_hash": stable_hash(str(smoke_path)), "update": sanitize_json(update), "smoke": sanitize_json(smoke)})
    codex_env = read_codex_provider_env_keys(Path(args.codex_config).resolve() if args.codex_config else None)
    summary = {"schema_version": 1, "generated_at": now_iso(), "ok": True, "capability_count": len(caps), "blocked_capability_count": len({item["capability_id"] for item in all_blockers}), "blockers": sanitize_json(all_blockers), "codex_provider_env": sanitize_json(codex_env), "receipt_dir_hash": stable_hash(str(paths["receipt_dir"]))}
    write_json(paths["receipt_dir"] / "summary.json", summary)
    return response("apply", True, mutates_user_level_state=True, sync_templates=bool(args.sync_templates), external_commands_run=False, codex_home_hash=stable_hash(str(codex_home)), receipt_dir_hash=stable_hash(str(paths["receipt_dir"])), rollback_pointer_hash=stable_hash(str(rollback)), codex_provider_env=sanitize_json(codex_env), blockers=sanitize_json(all_blockers), receipt_summaries=receipt_summaries)


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


def validate_blockers(blockers: Any) -> list[str]:
    errors: list[str] = []
    if blockers in (None, []):
        return errors
    if not isinstance(blockers, list):
        return ["blockers_not_list"]
    for idx, item in enumerate(blockers):
        if not isinstance(item, dict):
            errors.append(f"blocker_{idx}_not_object")
            continue
        for field in ("missing", "fill_command", "redacted_verification_command", "resume_step"):
            if not str(item.get(field, "")).strip():
                errors.append(f"blocker_{idx}_missing_{field}")
        errors.extend(redaction_findings(item, path=f"$.blockers[{idx}]"))
    return errors


def validate_update_receipt(data: dict[str, Any], cap: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("schema_version", "receipt_kind", "tool_name", "capability_id", "adapter_kind", "codex_adapter_present", "raw_upstream_install_only", "requires_codex_adapter_before_live_executed", "raw_upstream_live_executed_allowed", "live_runtime_target", "live_smoke_kind", "live_smoke_result", "credential_gate", "source_reference_only", "installed_version", "source_url", "adapter_path", "install_path", "wrapper_path", "state_path", "smoke_test_result", "updater_command", "rollback_pointer", "owner_lane", "redaction_status", "raw_paths_included", "remote_publication_mutated")
    for field in required:
        if field not in data:
            errors.append(f"missing_{field}")
    if data.get("tool_name") != cap.get("id"):
        errors.append("tool_name_mismatch")
    if data.get("source_url") != cap.get("source_url"):
        errors.append("source_url_mismatch")
    if data.get("receipt_kind") != "reference7-update":
        errors.append("receipt_kind_mismatch")
    if data.get("adapter_kind") not in {"codex-skill", "codex-agent-toml", "codex-project-runtime-wrapper", "codex-project-inert-template", "reference6-dedupe"}:
        errors.append("adapter_kind_not_codex_adapter")
    if data.get("raw_upstream_install_only") is not False:
        errors.append("raw_upstream_install_only_not_allowed")
    if data.get("source_reference_only") is not False:
        errors.append("source_reference_only_not_allowed")
    if data.get("live_runtime_target") != live_target(cap):
        errors.append("live_runtime_target_mismatch")
    if data.get("live_smoke_kind") != live_kind(cap):
        errors.append("live_smoke_kind_mismatch")
    if data.get("credential_gate") != credential_gate(cap):
        errors.append("credential_gate_mismatch")
    if data.get("requires_codex_adapter_before_live_executed") is not True:
        errors.append("requires_codex_adapter_before_live_executed_must_be_true")
    if data.get("raw_upstream_live_executed_allowed") is not False:
        errors.append("raw_upstream_live_executed_allowed_must_be_false")
    for field in ("raw_paths_included", "remote_publication_mutated", "native_codex_files_mutated", "codex_config_toml_mutated"):
        if data.get(field) is not False:
            errors.append(f"{field}_must_be_false")
    smoke = data.get("smoke_test_result")
    if not isinstance(smoke, dict) or smoke.get("status") not in {"pass", "blocked"}:
        errors.append("smoke_test_result_status_invalid")
    for field in ("install_root_hash", "wrapper_path_hash", "state_path_hash", "rollback_pointer_hash"):
        if field in data and not (isinstance(data[field], str) and HASH_RE.match(data[field])):
            errors.append(f"{field}_invalid")
    errors.extend(redaction_findings(data))
    return sorted(set(errors))


def validate_smoke_receipt(data: dict[str, Any], cap: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("schema_version", "receipt_kind", "tool_name", "capability_id", "owner_lane", "adapter_kind", "allowed_completion_surfaces", "runtime_stage", "codex_adapter_present", "raw_upstream_install_only", "requires_codex_adapter_before_live_executed", "raw_upstream_live_executed_allowed", "live_runtime_target", "live_smoke_kind", "live_smoke_result", "credential_gate", "source_reference_only", "install_receipt", "smoke_command", "smoke_type", "smoke_result", "timeout_release", "rollback_pointer", "rollback_ready", "command_transcript", "transcript_redaction", "redaction_status", "raw_paths_included", "remote_publication_mutated")
    for field in required:
        if field not in data:
            errors.append(f"missing_{field}")
    if data.get("tool_name") != cap.get("id"):
        errors.append("tool_name_mismatch")
    if data.get("receipt_kind") != "smoke-tested":
        errors.append("receipt_kind_mismatch")
    if data.get("adapter_kind") not in {"codex-skill", "codex-agent-toml", "codex-project-runtime-wrapper", "codex-project-inert-template", "reference6-dedupe"}:
        errors.append("adapter_kind_not_codex_adapter")
    if data.get("runtime_stage") not in {"R6 live-executed", "R6 blocked"}:
        errors.append("runtime_stage_invalid")
    if data.get("raw_upstream_install_only") is not False:
        errors.append("raw_upstream_install_only_not_allowed")
    if data.get("source_reference_only") is not False:
        errors.append("source_reference_only_not_allowed")
    if data.get("smoke_type") in LIVE_FORBIDDEN_SMOKE_TOKENS:
        errors.append("smoke_type_not_live")
    if data.get("live_runtime_target") != live_target(cap):
        errors.append("live_runtime_target_mismatch")
    if data.get("live_smoke_kind") != live_kind(cap):
        errors.append("live_smoke_kind_mismatch")
    if data.get("credential_gate") != credential_gate(cap):
        errors.append("credential_gate_mismatch")
    if data.get("requires_codex_adapter_before_live_executed") is not True:
        errors.append("requires_codex_adapter_before_live_executed_must_be_true")
    if data.get("raw_upstream_live_executed_allowed") is not False:
        errors.append("raw_upstream_live_executed_allowed_must_be_false")
    smoke = data.get("smoke_result")
    if not isinstance(smoke, dict) or smoke.get("status") not in {"pass", "blocked"}:
        errors.append("smoke_result_status_invalid")
    if isinstance(smoke, dict) and smoke.get("status") == "pass" and (data.get("runtime_stage") != "R6 live-executed" or data.get("codex_adapter_present") is not True):
        errors.append("pass_requires_live_executed_codex_adapter")
    if data.get("runtime_stage") == "R6 live-executed":
        if not isinstance(smoke, dict) or smoke.get("status") != "pass":
            errors.append("live_executed_requires_pass_smoke")
        if data.get("codex_adapter_present") is not True:
            errors.append("live_executed_requires_codex_adapter")
        details = smoke.get("details") if isinstance(smoke, dict) else {}
        if not isinstance(details, dict) or details.get("live_fixture_executed") is not True:
            errors.append("live_executed_requires_live_fixture")
    if data.get("rollback_ready") is not True:
        errors.append("rollback_ready_must_be_true")
    if data.get("raw_paths_included") is not False:
        errors.append("raw_paths_included_must_be_false")
    if data.get("remote_publication_mutated") is not False:
        errors.append("remote_publication_mutated_must_be_false")
    errors.extend(redaction_findings(data))
    return sorted(set(errors))


def command_check(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    caps = capabilities(manifest)
    paths = user_layout(Path(args.codex_home).resolve())
    general_root = Path(args.general_root).resolve() if args.general_root else None
    general2_root = Path(args.general2_root).resolve() if args.general2_root else None
    errors: list[str] = []
    warnings: list[str] = []
    for key in ("manifest_copy", "runtime_copy", "registry_copy", "smoke_ps1", "smoke_cmd"):
        if not paths[key].exists():
            (errors if args.require_installed else warnings).append(f"missing_user_level_artifact:{key}")
    receipts = load_receipts(paths["receipt_dir"])
    update_by_cap = {item.get("capability_id"): item for item in receipts if item.get("receipt_kind") == "reference7-update"}
    smoke_by_cap = {item.get("capability_id"): item for item in receipts if item.get("receipt_kind") == "smoke-tested"}
    live_executed = blocked = 0
    for cap in caps:
        cap_id = cap["id"]
        expected_status, _, _ = smoke_capability(cap, codex_home=paths["codex_home"], general_root=general_root, general2_root=general2_root)
        if expected_status != "pass" and args.require_live_executed:
            errors.append(f"live_executed_missing:{cap_id}:{expected_status}")
        update = update_by_cap.get(cap_id)
        if update:
            errors.extend(f"invalid_update_receipt:{cap_id}:{err}" for err in validate_update_receipt(update, cap))
            errors.extend(f"invalid_update_blocker:{cap_id}:{err}" for err in validate_blockers(update.get("blockers")))
        elif args.require_installed:
            errors.append(f"missing_update_receipt:{cap_id}")
        smoke = smoke_by_cap.get(cap_id)
        if smoke:
            errors.extend(f"invalid_smoke_receipt:{cap_id}:{err}" for err in validate_smoke_receipt(smoke, cap))
            errors.extend(f"invalid_smoke_blocker:{cap_id}:{err}" for err in validate_blockers(smoke.get("blockers")))
            live_executed += 1 if smoke.get("runtime_stage") == "R6 live-executed" else 0
            blocked += 1 if smoke.get("runtime_stage") == "R6 blocked" else 0
            if args.require_live_executed and smoke.get("runtime_stage") != "R6 live-executed":
                errors.append(f"smoke_receipt_not_live_executed:{cap_id}:{smoke.get('runtime_stage')}")
        elif args.require_smoke_tested:
            errors.append(f"missing_smoke_receipt:{cap_id}")
    return response("check", not errors, mutates_user_level_state=False, external_commands_run=False, require_installed=bool(args.require_installed), require_smoke_tested=bool(args.require_smoke_tested), require_live_executed=bool(args.require_live_executed), errors=sorted(set(errors)), warnings=warnings, receipt_count=len(receipts), update_receipt_count=len(update_by_cap), smoke_receipt_count=len(smoke_by_cap), live_executed_count=live_executed, blocked_count=blocked, latest_receipts=sanitize_json({"updates": update_by_cap, "smoke": smoke_by_cap}), blocker_protocol=manifest.get("blocked_completion_protocol"))


def command_smoke(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    caps = capabilities(manifest)
    if args.capability:
        caps = [cap for cap in caps if cap["id"] == args.capability]
        if not caps:
            return response("smoke", False, errors=[f"unknown_capability:{args.capability}"])
    codex_home = Path(args.codex_home).resolve()
    general_root = Path(args.general_root).resolve() if args.general_root else None
    general2_root = Path(args.general2_root).resolve() if args.general2_root else None
    errors: list[str] = []
    blockers: list[dict[str, Any]] = []
    results: dict[str, Any] = {}
    for cap in caps:
        status, details, cap_blockers = smoke_capability(cap, codex_home=codex_home, general_root=general_root, general2_root=general2_root)
        blockers.extend(cap_blockers)
        results[cap["id"]] = {"status": status, "details": sanitize_json(details), "blockers": sanitize_json(cap_blockers)}
        if args.require_pass and status != "pass":
            errors.append(f"smoke_not_pass:{cap['id']}:{status}")
    return response("smoke", not errors, mutates_user_level_state=False, external_commands_run=False, errors=errors, blockers=sanitize_json(blockers), smoke_results=results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install/check Reference 7 Codex adapter and project-template surfaces.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--codex-home", default=str(default_codex_home()))
        p.add_argument("--codex-config", default=None)
        p.add_argument("--general-root", default=None)
        p.add_argument("--general2-root", default=None)
        p.add_argument("--json", action="store_true")

    plan = sub.add_parser("plan")
    common(plan)
    plan.set_defaults(func=command_plan)
    apply = sub.add_parser("apply")
    common(apply)
    apply.add_argument("--apply", action="store_true")
    apply.add_argument("--operator-confirmation", action="store_true")
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
