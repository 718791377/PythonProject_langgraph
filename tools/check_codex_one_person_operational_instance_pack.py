#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

CHECK_NAME = "codex_one_person_operational_instance_pack"
SCHEMA_VERSION = 1
CHECKER_PATH = "tools/check_codex_one_person_operational_instance_pack.py"
TEST_NAME = "check_codex_one_person_operational_instance_pack.test.py"
TEST_PATH = f"test/{TEST_NAME}"
GUARD_STEP = "check_codex_one_person_operational_instance_pack"
PLAN_PATH = "docs_bilingual/implementation_plans/codex_one_person_operational_instance_pack_plan.md"
PLAN_ZH_PATH = "docs_bilingual/implementation_plans/codex_one_person_operational_instance_pack_plan.zh-CN.md"
REGISTRY_PATH = "docs_bilingual/docs_registry.yaml"
MANIFEST_PATH = "tools/ci/ci_test_manifest.json"
GUARD_PATH = "tools/run_openspec_guard.py"
GUARD_TEST_PATH = "test/run_openspec_guard_json.test.py"
SAFETY_PATH = "tools/safety_rule_script_backing_registry.json"
MOJIBAKE_SENTINELS = ["\ufffd", "????", "\u00c3", "\u00c2", "\u00e2\u20ac", "杈撳叆", "宸ュ叿", "杈撳嚭"]
PROCESS_GROUP_EN = ["Inputs", "Tools And Techniques", "Outputs"]
PROCESS_GROUP_ZH = ["输入", "工具与技术", "输出"]
SHARED_FIELDS = ["scope", "truth_owner", "evidence_source", "decision_right", "linked_docs"]

BASE = "docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances"

GROUPS: list[dict[str, Any]] = [
    {
        "id": "entrypoint",
        "prefix": "operational_instance_entrypoint",
        "folder": BASE,
        "category": "entrypoint",
        "files": ["README.md", "instance-profile.md", "operating-calendar.md", "artifact-index.md"],
        "required_tokens": ["operational instance", "business truth", "Codex execution truth", "evidence", "fillable record"],
    },
    {
        "id": "shared_ledgers",
        "prefix": "operational_instance_shared_ledgers",
        "folder": f"{BASE}/shared-ledgers",
        "category": "shared",
        "files": [
            "decision-log.instance.md",
            "risk-register.instance.md",
            "evidence-register.instance.md",
            "tailoring-decision-log.instance.md",
            "human-review-records.instance.md",
            "monthly-review.instance.md",
        ],
        "required_tokens": ["business truth", "Codex execution truth", "mixed", *SHARED_FIELDS],
    },
    {
        "id": "codex_platform",
        "prefix": "operational_instance_codex_platform",
        "folder": f"{BASE}/codex-platform",
        "category": "codex",
        "files": [
            "runtime-run-record.md",
            "local-main-integration-record.md",
            "validation-release-readiness-record.md",
            "agent-evaluation-run-record.md",
            "durable-state-recovery-drill.md",
            "incident-rollback-case-record.md",
        ],
        "required_tokens": [
            "execution truth",
            "Agent routing",
            "OpenSpec",
            "worktree",
            "durable state",
            "validation gates",
            "local-main evidence",
            "rollback",
            "release-boundary",
        ],
    },
    {
        "id": "business_operations",
        "prefix": "operational_instance_business_operations",
        "folder": f"{BASE}/business-operations",
        "category": "business",
        "files": [
            "offer-pricing-decision-record.md",
            "customer-intake-delivery-record.md",
            "sales-support-refund-case-record.md",
            "legal-contract-review-record.md",
            "cashflow-runway-review-record.md",
            "experiment-roadmap-readout.md",
        ],
        "required_tokens": [
            "business truth",
            "customers",
            "revenue",
            "pricing",
            "contracts",
            "legal posture",
            "cashflow",
            "support",
            "refunds",
            "delivery commitments",
            "business learning",
            "must not bypass Agent permissions",
            "runtime validation",
            "durable-state recovery",
            "local-main evidence",
            "rollback gates",
            "remote-publication gates",
        ],
    },
    {
        "id": "mixed_governance",
        "prefix": "operational_instance_mixed_governance",
        "folder": f"{BASE}/mixed-governance",
        "category": "mixed",
        "files": [
            "mixed-change-record.md",
            "business-to-codex-intake-instance.md",
            "codex-to-business-impact-instance.md",
            "module-tailoring-decision-record.md",
            "dual-gate-release-record.md",
            "quarterly-portfolio-review-record.md",
        ],
        "required_tokens": [
            "business gate",
            "Codex execution gate",
            "human final approval",
            "pricing",
            "contracts",
            "release",
            "customer promises",
            "financial commitments",
            "legal commitments",
            "remote publication",
        ],
    },
]

BAD_CODEX_CLAIMS = [
    r"codex\s+owns\s+business\s+truth",
    r"codex\s+owns\s+(?:customers|revenue|pricing|contracts|cashflow|refunds|customer\s+promises)",
    r"codex\s+(?:may|can|shall)\s+(?:approve|decide|commit)\s+(?:pricing|contracts|legal\s+commitments|customer\s+promises|refunds|financial\s+commitments)",
    r"agent\s+(?:may|can|shall)\s+(?:approve|decide|commit)\s+(?:pricing|contracts|legal\s+commitments|customer\s+promises|refunds|financial\s+commitments)",
]
BAD_BUSINESS_CLAIMS = [
    r"business\s+owns\s+execution\s+truth",
    r"business\s+(?:may|can|shall)\s+bypass\s+(?:agent\s+permissions|runtime\s+validation|durable-state\s+recovery|local-main\s+evidence|rollback\s+gates|remote-publication\s+gates)",
    r"business\s+(?:may|can|shall)\s+(?:approve|merge|publish|release)\s+(?:agent|runtime|local-main|remote-publication|runtime\s+release)\s+without\s+codex",
    r"business\s+(?:may|can|shall)\s+control\s+(?:agent\s+permissions|durable\s+state|worktree|runtime\s+validation)",
]


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def companion_for(en_rel: str) -> str:
    return en_rel[:-3] + ".zh-CN.md"


def doc_id_for(prefix: str, filename: str) -> str:
    stem = Path(filename).stem.replace("-", "_").replace(".", "_").lower()
    return f"{prefix}_{stem}"


def required_primary_files() -> list[str]:
    result: list[str] = []
    for group in GROUPS:
        for name in group["files"]:
            result.append(f"{group['folder']}/{name}")
    return result


def read_text(path: Path, errors: list[str], checked: set[str]) -> str:
    rel = norm(path)
    checked.add(rel)
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except FileNotFoundError:
        errors.append(f"Required file is missing: {rel}")
        return ""
    except UnicodeDecodeError as exc:
        errors.append(f"File is not valid UTF-8: {rel}: {exc}")
        return ""
    for sentinel in MOJIBAKE_SENTINELS:
        if sentinel in text:
            label = "replacement character" if sentinel == "\ufffd" else "mojibake sentinel"
            errors.append(f"{rel} contains {label}: {sentinel!r}.")
            break
    return text


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return {}


def parse_registry(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("- doc_id:"):
            if current:
                entries.append(current)
            current = {"doc_id": stripped.split(":", 1)[1].strip()}
            continue
        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def validate_frontmatter(en_rel: str, zh_rel: str, en_text: str, zh_text: str, prefix: str, filename: str, errors: list[str]) -> None:
    en_fm = parse_frontmatter(en_text)
    zh_fm = parse_frontmatter(zh_text)
    expected_doc_id = doc_id_for(prefix, filename)
    if not en_fm:
        errors.append(f"{en_rel} is missing YAML front matter.")
    else:
        if en_fm.get("lang") != "en":
            errors.append(f"{en_rel} front matter lang={en_fm.get('lang')!r}; expected 'en'.")
        if en_fm.get("translation_of"):
            errors.append(f"{en_rel} English primary must not contain translation_of.")
        if en_fm.get("doc_class") != "operations_instance_pack":
            errors.append(f"{en_rel} doc_class={en_fm.get('doc_class')!r}; expected operations_instance_pack.")
        if en_fm.get("doc_id") != expected_doc_id:
            errors.append(f"{en_rel} doc_id={en_fm.get('doc_id')!r}; expected {expected_doc_id!r}.")
    if not zh_fm:
        errors.append(f"{zh_rel} is missing YAML front matter.")
    else:
        if zh_fm.get("lang") != "zh-CN":
            errors.append(f"{zh_rel} front matter lang={zh_fm.get('lang')!r}; expected 'zh-CN'.")
        if zh_fm.get("translation_of") != en_rel:
            errors.append(f"{zh_rel} front matter translation_of={zh_fm.get('translation_of')!r}; expected {en_rel!r}.")
        if zh_fm.get("doc_class") != "operations_instance_pack":
            errors.append(f"{zh_rel} doc_class={zh_fm.get('doc_class')!r}; expected operations_instance_pack.")
        if zh_fm.get("doc_id") != expected_doc_id:
            errors.append(f"{zh_rel} doc_id={zh_fm.get('doc_id')!r}; expected {expected_doc_id!r}.")


def validate_ascii_primary(rel: str, text: str, errors: list[str]) -> None:
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        errors.append(f"{rel} English primary contains non-ASCII text at character index {exc.start}.")


def has_process_group(text: str, labels: list[str]) -> bool:
    pos = -1
    for label in labels:
        match = re.search(rf"(?m)^#{{2,4}}\s+{re.escape(label)}\s*$", text)
        if not match or match.start() <= pos:
            return False
        section_start = match.end()
        next_match = re.search(r"(?m)^#{2,4}\s+", text[section_start:])
        section = text[section_start : section_start + next_match.start()] if next_match else text[section_start:]
        if not section.strip():
            return False
        pos = match.start()
    return True


def validate_process_group(rel: str, text: str, zh: bool, errors: list[str]) -> None:
    if has_process_group(text, PROCESS_GROUP_ZH if zh else PROCESS_GROUP_EN):
        return
    expected = " / ".join(PROCESS_GROUP_ZH if zh else PROCESS_GROUP_EN)
    errors.append(f"{rel} is missing non-empty process-group headings in order: {expected}.")


def validate_tokens(rel: str, text: str, tokens: list[str], errors: list[str]) -> None:
    lowered = text.lower()
    for token in tokens:
        if token.lower() not in lowered:
            errors.append(f"{rel} is missing required token `{token}`.")


def validate_negative_patterns(rel: str, text: str, patterns: list[str], errors: list[str]) -> None:
    lowered = text.lower()
    for pattern in patterns:
        if re.search(pattern, lowered):
            errors.append(f"{rel} contains prohibited authority claim matching /{pattern}/.")


def validate_files(root: Path, errors: list[str], checked: set[str]) -> None:
    for group in GROUPS:
        category = str(group["category"])
        for filename in group["files"]:
            en_rel = f"{group['folder']}/{filename}"
            zh_rel = companion_for(en_rel)
            en_text = read_text(root / en_rel, errors, checked)
            zh_text = read_text(root / zh_rel, errors, checked)
            if en_text:
                validate_ascii_primary(en_rel, en_text, errors)
                validate_tokens(en_rel, en_text, list(group["required_tokens"]), errors)
                validate_process_group(en_rel, en_text, False, errors)
                if category == "codex":
                    validate_negative_patterns(en_rel, en_text, BAD_CODEX_CLAIMS, errors)
                if category == "business":
                    validate_negative_patterns(en_rel, en_text, BAD_BUSINESS_CLAIMS, errors)
            if zh_text:
                validate_process_group(zh_rel, zh_text, True, errors)
                validate_tokens(zh_rel, zh_text, list(group["required_tokens"]), errors)
                if category == "codex":
                    validate_negative_patterns(zh_rel, zh_text, BAD_CODEX_CLAIMS, errors)
                if category == "business":
                    validate_negative_patterns(zh_rel, zh_text, BAD_BUSINESS_CLAIMS, errors)
            if en_text and zh_text:
                validate_frontmatter(en_rel, zh_rel, en_text, zh_text, str(group["prefix"]), filename, errors)


def validate_registry(root: Path, errors: list[str], checked: set[str]) -> None:
    text = read_text(root / REGISTRY_PATH, errors, checked)
    entries = parse_registry(text)
    doc_ids = [entry.get("doc_id", "") for entry in entries if entry.get("doc_id")]
    for doc_id, count in Counter(doc_ids).items():
        if count > 1:
            errors.append(f"{REGISTRY_PATH} has duplicate doc_id `{doc_id}`.")
    paths = [entry.get("canonical_path", "") for entry in entries] + [entry.get("zh_cn_path", "") for entry in entries]
    for path, count in Counter([p for p in paths if p]).items():
        if count > 1:
            errors.append(f"{REGISTRY_PATH} has duplicate path `{path}`.")
    by_pair = {(entry.get("canonical_path", ""), entry.get("zh_cn_path", "")): entry for entry in entries}
    for group in GROUPS:
        for filename in group["files"]:
            en_rel = f"{group['folder']}/{filename}"
            zh_rel = companion_for(en_rel)
            entry = by_pair.get((en_rel, zh_rel))
            if not entry:
                errors.append(f"{REGISTRY_PATH} is missing instance-pack pair `{en_rel}` / `{zh_rel}`.")
                continue
            expected_doc_id = doc_id_for(str(group["prefix"]), filename)
            if entry.get("doc_id") != expected_doc_id:
                errors.append(f"{REGISTRY_PATH} pair `{en_rel}` has doc_id={entry.get('doc_id')!r}; expected {expected_doc_id!r}.")
            if entry.get("doc_class") != "operations_instance_pack":
                errors.append(f"{REGISTRY_PATH} pair `{en_rel}` doc_class={entry.get('doc_class')!r}; expected operations_instance_pack.")
    for entry in entries:
        for key in ("canonical_path", "zh_cn_path"):
            value = entry.get(key, "")
            if value and not (root / value).exists():
                errors.append(f"{REGISTRY_PATH} {key} does not exist: {value}")


def validate_registrations(root: Path, errors: list[str], checked: set[str]) -> None:
    manifest_text = read_text(root / MANIFEST_PATH, errors, checked)
    try:
        manifest = json.loads(manifest_text) if manifest_text else {}
    except json.JSONDecodeError as exc:
        errors.append(f"{MANIFEST_PATH} is not valid JSON: {exc}")
        manifest = {}
    if TEST_NAME not in manifest.get("python_unittest", []):
        errors.append(f"{MANIFEST_PATH} does not register `{TEST_NAME}`.")

    guard_text = read_text(root / GUARD_PATH, errors, checked)
    for token in (CHECKER_PATH.split("/", 1)[1], GUARD_STEP, "codex_one_person_operational_instance_pack_script"):
        if token not in guard_text:
            errors.append(f"{GUARD_PATH} does not register `{token}`.")
    if "OpenSpec guard failed during Codex one-person operational instance pack verification." not in guard_text:
        errors.append(f"{GUARD_PATH} is missing the operational instance pack guard failure message.")

    guard_test_text = read_text(root / GUARD_TEST_PATH, errors, checked)
    for token in (GUARD_STEP, "check_codex_one_person_operational_instance_pack.py", CHECK_NAME):
        if token not in guard_test_text:
            errors.append(f"{GUARD_TEST_PATH} does not register `{token}`.")

    safety_text = read_text(root / SAFETY_PATH, errors, checked)
    for token in ("codex-one-person-operational-instance-pack", CHECKER_PATH, TEST_PATH, GUARD_STEP, PLAN_PATH, PLAN_ZH_PATH):
        if token not in safety_text:
            errors.append(f"{SAFETY_PATH} does not register `{token}`.")


def validate_plan(root: Path, errors: list[str], checked: set[str]) -> None:
    plan = read_text(root / PLAN_PATH, errors, checked)
    plan_zh = read_text(root / PLAN_ZH_PATH, errors, checked)
    for token in (
        "Instance entrypoint",
        "Shared Ledger Instances",
        "Codex Execution Instances",
        "One-Person-Company Business Instances",
        "Mixed Dual-Gate Instances",
        CHECKER_PATH,
        TEST_PATH,
    ):
        if token not in plan:
            errors.append(f"{PLAN_PATH} is missing frozen instance-pack token `{token}`.")
    if "Remote publication is not authorized" not in plan:
        errors.append(f"{PLAN_PATH} must preserve remote-publication boundary language.")
    if plan_zh and PLAN_PATH not in plan_zh:
        errors.append(f"{PLAN_ZH_PATH} must reference the canonical English plan path.")


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: set[str] = set()
    validate_plan(root, errors, checked)
    validate_files(root, errors, checked)
    validate_registry(root, errors, checked)
    validate_registrations(root, errors, checked)
    primary_count = len(required_primary_files())
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check": CHECK_NAME,
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": ["Validated Codex and one-person-company operational instance pack contract."],
        "groups": [
            {"id": group["id"], "primary_files": len(group["files"]), "bilingual_pairs": len(group["files"])}
            for group in GROUPS
        ],
        "checked_paths": sorted(checked),
        "counts": {
            "groups": len(GROUPS),
            "required_primary_files": primary_count,
            "required_bilingual_files": primary_count * 2,
            "shared_ledger_fields": len(SHARED_FIELDS),
            "checked_paths": len(checked),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex and one-person-company operational instance pack contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'fail'}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
