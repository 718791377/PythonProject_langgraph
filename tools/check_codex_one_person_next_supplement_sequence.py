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

CHECK_NAME = "codex_one_person_next_supplement_sequence"
SCHEMA_VERSION = 1
CHECKER_PATH = "tools/check_codex_one_person_next_supplement_sequence.py"
TEST_NAME = "check_codex_one_person_next_supplement_sequence.test.py"
TEST_PATH = f"test/{TEST_NAME}"
GUARD_STEP = "check_codex_one_person_next_supplement_sequence"
PLAN_PATH = "docs_bilingual/implementation_plans/codex_one_person_next_supplement_file_sequence_plan.md"
PLAN_ZH_PATH = "docs_bilingual/implementation_plans/codex_one_person_next_supplement_file_sequence_plan.zh-CN.md"
REGISTRY_PATH = "docs_bilingual/docs_registry.yaml"
MANIFEST_PATH = "tools/ci/ci_test_manifest.json"
GUARD_PATH = "tools/run_openspec_guard.py"
GUARD_TEST_PATH = "test/run_openspec_guard_json.test.py"
SAFETY_PATH = "tools/safety_rule_script_backing_registry.json"
GENERATOR_PATH = "tools/generate_operations_package.py"
NO_PEER_WHITEPAPER_PATTERNS = [
    "docs_bilingual/whitepapers/embedded_codex_one_person_company_whitepaper.md",
    "docs_bilingual/whitepapers/one_person_company_embedded_codex_whitepaper.md",
    "docs_bilingual/whitepapers/codex_one_person_company_peer_whitepaper.md",
]
MOJIBAKE_SENTINELS = ["\ufffd", "\u00c3", "\u00c2", "\u00e2\u20ac", "\u951b", "\u6d93", "\u4e71\u7801"]
PROCESS_GROUP_EN = ["Inputs", "Tools And Techniques", "Outputs"]
PROCESS_GROUP_ZH = ["\u8f93\u5165", "\u5de5\u5177\u4e0e\u6280\u672f", "\u8f93\u51fa"]
STAGE_B_MARKER = "## Stage B Embedded Governance Closeout"

GROUPS: list[dict[str, Any]] = [
    {
        "id": "shared_boundary_and_tailoring_rules",
        "heading": "Group 1: Shared Boundary And Tailoring Rules",
        "zh_heading": "Required Group 1: Shared Boundary And Tailoring Rules",
        "doc_class": "product_lifecycle",
        "files": [
            "docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md",
            "docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.md",
            "docs_bilingual/product_lifecycle/durable_team_process_group_contract.md",
            "docs_bilingual/product_lifecycle/durable_team_source_traceability.md",
            "docs_bilingual/product_lifecycle/fresh_source_reading_evidence.md",
        ],
        "required_tokens": [
            "full architecture",
            "whole-project lightweight",
            "phase-local lightweight",
            "module-level lightweight",
            "hybrid",
            "Tailoring does not delete the twelve-layer mental model",
            "scoped",
            "business truth",
            "execution truth",
        ],
    },
    {
        "id": "codex_side_governance_skeleton",
        "heading": "Group 2: Codex-Side Governance Skeleton",
        "zh_heading": "Required Group 2: Codex-Side Governance Skeleton",
        "doc_class": "product_lifecycle",
        "files": [
            "docs_bilingual/product_lifecycle/codex_platform_inventory_map.md",
            "docs_bilingual/product_lifecycle/codex_platform_virtual_departments_operating_map.md",
            "docs_bilingual/product_lifecycle/codex_platform_responsibility_raci.md",
            "docs_bilingual/product_lifecycle/codex_platform_core_documents_register.md",
            "docs_bilingual/product_lifecycle/codex_platform_cross_cutting_module_map.md",
            "docs_bilingual/product_lifecycle/codex_platform_governed_agent_catalog.md",
            "docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_document_generation_order.md",
            "docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_operating_slice_template.md",
            "docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.md",
        ],
        "required_tokens": [
            "execution truth",
            "agents",
            "OpenSpec",
            "worktrees",
            "durable state",
            "validation gates",
            "local-main",
            "rollback",
            "release boundaries",
            "not a peer business authority",
        ],
    },
    {
        "id": "one_person_company_governance_skeleton",
        "heading": "Group 3: One-Person-Company Governance Skeleton",
        "zh_heading": "Required Group 3: One-Person-Company Governance Skeleton",
        "doc_class": "product_lifecycle",
        "files": [
            "docs_bilingual/product_lifecycle/one_person_company_inventory_map.md",
            "docs_bilingual/product_lifecycle/one_person_company_minimum_startup_documents.md",
            "docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md",
            "docs_bilingual/product_lifecycle/one_person_company_tailoring_decision_tree.md",
            "docs_bilingual/product_lifecycle/one_person_company_architecture_mode_selection_guide.md",
            "docs_bilingual/product_lifecycle/one_person_company_pmi_process_group_playbook.md",
            "docs_bilingual/product_lifecycle/one_person_company_operations_document_system.md",
            "docs_bilingual/product_lifecycle/one_person_company_operations_metrics_and_monthly_review.md",
            "docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.md",
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
            "business learning",
            "embedded Codex",
            "not a peer business authority",
        ],
    },
    {
        "id": "whitepapers_and_north_stars",
        "heading": "Group 4: White Papers And North Stars",
        "zh_heading": "Required Group 4: White Papers And North Stars",
        "doc_class": "summary",
        "files": [
            "docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md",
            "docs_bilingual/north_star/codex_cli_personal_production_durable_team_north_star.md",
            "docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md",
            "docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md",
        ],
        "required_tokens": [
            "10-layer",
            "12-layer",
            "business truth",
            "execution truth",
            "must not redefine business truth",
            "not a peer business authority",
        ],
    },
    {
        "id": "project_kit_and_body_package_closeout",
        "heading": "Group 5: Project Kit And Body Package Closeout",
        "zh_heading": "Required Group 5: Project Kit And Body Package Closeout",
        "doc_class": "mixed",
        "files": [
            "docs_bilingual/project_kits/one_person_company_with_embedded_codex/README.md",
            "docs_bilingual/project_kits/one_person_company_with_embedded_codex/startup-checklist.md",
            "docs_bilingual/project_kits/one_person_company_with_embedded_codex/folder-structure.md",
            "docs_bilingual/project_kits/one_person_company_with_embedded_codex/governance-gates.md",
            "docs_bilingual/project_kits/one_person_company_with_embedded_codex/local-main-workflow.md",
            "docs_bilingual/project_kits/one_person_company_with_embedded_codex/remote-publication-gate.md",
            "docs_bilingual/project_kits/one_person_company_with_embedded_codex/monthly-review-sample.md",
            "docs_bilingual/operations_packages/codex_cli_durable_team/architecture.md",
            "docs_bilingual/operations_packages/one_person_company/agent-governance.md",
        ],
        "required_tokens": [
            "business truth",
            "execution truth",
            "not a peer business authority",
            "full architecture",
            "whole-project lightweight",
            "phase-local lightweight",
            "module-level lightweight",
            "hybrid",
        ],
    },
]


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def companion_for(en_rel: str) -> str:
    if en_rel.endswith(".zh-CN.md"):
        return en_rel
    return en_rel[:-3] + ".zh-CN.md"


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
        if not stripped:
            continue
        if stripped.startswith("- doc_id:"):
            if current:
                entries.append(current)
            current = {"doc_id": stripped.split(":", 1)[1].strip()}
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def headings_in_order(text: str, headings: list[str]) -> bool:
    position = -1
    for heading in headings:
        index = text.find(heading)
        if index <= position:
            return False
        position = index
    return True


def section_body(text: str, heading: str, following: list[str]) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    candidates = [text.find(next_heading, start) for next_heading in following if text.find(next_heading, start) >= 0]
    end = min(candidates) if candidates else len(text)
    return text[start:end].strip()


def validate_plan_order(root: Path, errors: list[str], checked: set[str]) -> None:
    plan = read_text(root / PLAN_PATH, errors, checked)
    plan_zh = read_text(root / PLAN_ZH_PATH, errors, checked)
    positions: list[int] = []
    zh_positions: list[int] = []
    for group in GROUPS:
        heading = str(group["heading"])
        zh_heading = str(group["zh_heading"])
        position = plan.find(heading)
        if position < 0:
            errors.append(f"{PLAN_PATH} is missing ordered group heading `{heading}`.")
        positions.append(position)
        zh_position = plan_zh.find(zh_heading)
        if zh_position < 0:
            errors.append(f"{PLAN_ZH_PATH} is missing ordered group heading `{zh_heading}`.")
        zh_positions.append(zh_position)
    if any(pos < 0 for pos in positions) or positions != sorted(positions):
        errors.append(f"{PLAN_PATH} Stage B ordered groups are missing or out of order.")
    if any(pos < 0 for pos in zh_positions) or zh_positions != sorted(zh_positions):
        errors.append(f"{PLAN_ZH_PATH} Stage B ordered groups are missing or out of order.")
    fixed = "shared -> Codex -> one-person company -> white papers and North Stars -> project kit and body packages"
    if fixed not in plan or fixed not in plan_zh:
        errors.append("Frozen plan is missing the fixed Stage B implementation order sentence.")
    for token in (CHECKER_PATH, TEST_PATH, MANIFEST_PATH, GUARD_PATH, SAFETY_PATH):
        if token not in plan:
            errors.append(f"{PLAN_PATH} is missing runtime contract token `{token}`.")


def validate_frontmatter(en_rel: str, zh_rel: str, en_text: str, zh_text: str, errors: list[str]) -> None:
    en_fm = parse_frontmatter(en_text)
    zh_fm = parse_frontmatter(zh_text)
    if not en_fm:
        errors.append(f"{en_rel} is missing YAML front matter.")
    elif en_fm.get("lang") != "en":
        errors.append(f"{en_rel} front matter lang={en_fm.get('lang')!r}; expected 'en'.")
    if en_fm.get("translation_of"):
        errors.append(f"{en_rel} English primary must not contain translation_of.")
    if not zh_fm:
        errors.append(f"{zh_rel} is missing YAML front matter.")
    elif zh_fm.get("lang") != "zh-CN":
        errors.append(f"{zh_rel} front matter lang={zh_fm.get('lang')!r}; expected 'zh-CN'.")
    if zh_fm and zh_fm.get("translation_of") != en_rel:
        errors.append(f"{zh_rel} front matter translation_of={zh_fm.get('translation_of')!r}; expected {en_rel!r}.")


def validate_registry(root: Path, errors: list[str], checked: set[str]) -> None:
    registry_text = read_text(root / REGISTRY_PATH, errors, checked)
    entries = parse_registry(registry_text)
    doc_ids = [entry.get("doc_id", "") for entry in entries]
    for doc_id, count in Counter([item for item in doc_ids if item]).items():
        if count > 1:
            errors.append(f"{REGISTRY_PATH} has duplicate doc_id `{doc_id}`.")
    paths = [entry.get("canonical_path", "") for entry in entries] + [entry.get("zh_cn_path", "") for entry in entries]
    for path, count in Counter([item for item in paths if item]).items():
        if count > 1:
            errors.append(f"{REGISTRY_PATH} has duplicate path `{path}`.")
    by_pair = {(entry.get("canonical_path", ""), entry.get("zh_cn_path", "")): entry for entry in entries}
    for en_rel in required_primary_files():
        zh_rel = companion_for(en_rel)
        entry = by_pair.get((en_rel, zh_rel))
        if not entry:
            errors.append(f"{REGISTRY_PATH} is missing Stage B pair `{en_rel}` / `{zh_rel}`.")
            continue
        if entry.get("canonical_path") == entry.get("zh_cn_path"):
            errors.append(f"{REGISTRY_PATH} has identical canonical_path and zh_cn_path for `{entry.get('doc_id')}`.")
    for entry in entries:
        canonical = entry.get("canonical_path", "")
        zh = entry.get("zh_cn_path", "")
        if canonical and not (root / canonical).exists():
            errors.append(f"{REGISTRY_PATH} canonical_path does not exist: {canonical}")
        if zh and not (root / zh).exists():
            errors.append(f"{REGISTRY_PATH} zh_cn_path does not exist: {zh}")


def validate_token_set(rel: str, text: str, tokens: list[str], errors: list[str]) -> None:
    lowered = text.lower()
    for token in tokens:
        if token.lower() not in lowered:
            errors.append(f"{rel} is missing required Stage B token `{token}`.")


def validate_process_group(rel: str, text: str, zh: bool, errors: list[str]) -> None:
    labels = PROCESS_GROUP_ZH if zh else PROCESS_GROUP_EN
    search_text = text
    marker_position = text.rfind(STAGE_B_MARKER)
    if marker_position >= 0:
        search_text = text[marker_position:]
    if zh and all(re.search(rf"(?m)^#{{2,4}}\s+{re.escape(label)}\s*$", search_text) for label in PROCESS_GROUP_EN):
        labels = PROCESS_GROUP_EN
    positions: list[int] = []
    for label in labels:
        match = re.search(rf"(?m)^#{{2,4}}\s+{re.escape(label)}\s*$", search_text)
        if match is None and zh:
            match = re.search(rf"(?m)^#{{2,4}}\s+{re.escape(label)}\s*$", text)
        if match is None:
            errors.append(f"{rel} is missing process-group heading `{label}`.")
            return
        positions.append(match.start())
    if positions != sorted(positions):
        errors.append(f"{rel} process-group headings are out of order: {', '.join(labels)}.")
        return
    for idx, label in enumerate(labels):
        start = positions[idx]
        heading_end = search_text.find("\n", start)
        if heading_end < 0:
            heading_end = start + len(label)
        end = positions[idx + 1] if idx + 1 < len(positions) else len(search_text)
        body = search_text[heading_end:end].strip()
        if not body:
            errors.append(f"{rel} process-group section `{label}` is empty.")


def required_primary_files() -> list[str]:
    result: list[str] = []
    for group in GROUPS:
        for rel in group["files"]:
            if rel not in result:
                result.append(str(rel))
    return result


def validate_files(root: Path, errors: list[str], checked: set[str]) -> None:
    for group in GROUPS:
        tokens = list(group.get("required_tokens", []))
        for en_rel in group["files"]:
            en_rel = str(en_rel)
            zh_rel = companion_for(en_rel)
            en_text = read_text(root / en_rel, errors, checked)
            zh_text = read_text(root / zh_rel, errors, checked)
            if en_text and zh_text:
                validate_frontmatter(en_rel, zh_rel, en_text, zh_text, errors)
            if en_text:
                try:
                    en_text.encode("ascii")
                except UnicodeEncodeError as exc:
                    errors.append(f"{en_rel} English primary contains non-ASCII text at character index {exc.start}.")
                validate_token_set(en_rel, en_text, tokens, errors)
                validate_process_group(en_rel, en_text, False, errors)
            if zh_text:
                zh_tokens = [token for token in tokens if token in {"business truth", "execution truth", "not a peer business authority", "must not redefine business truth"}]
                validate_token_set(zh_rel, zh_text, zh_tokens, errors)
                validate_process_group(zh_rel, zh_text, True, errors)


def validate_generation_and_no_peer(root: Path, errors: list[str], checked: set[str]) -> None:
    generator_text = read_text(root / GENERATOR_PATH, errors, checked)
    for token in ("Codex owns execution truth", "The one-person company owns business truth", "must not redefine business truth"):
        if token not in generator_text:
            errors.append(f"{GENERATOR_PATH} is missing generated closeout token `{token}`.")
    for rel in NO_PEER_WHITEPAPER_PATTERNS:
        if (root / rel).exists():
            errors.append(f"Unauthorized third peer whitepaper exists: {rel}")


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
    for token, label in (("check_codex_one_person_next_supplement_sequence.py", "checker path"), (GUARD_STEP, "guard step"), ("codex_one_person_next_supplement_sequence_script", "script variable")):
        if token not in guard_text:
            errors.append(f"{GUARD_PATH} does not register {label} `{token}`.")

    guard_test_text = read_text(root / GUARD_TEST_PATH, errors, checked)
    for token in (GUARD_STEP, "check_codex_one_person_next_supplement_sequence.py", CHECK_NAME):
        if token not in guard_test_text:
            errors.append(f"{GUARD_TEST_PATH} does not register `{token}`.")

    safety_text = read_text(root / SAFETY_PATH, errors, checked)
    for token, label in ((CHECKER_PATH, "checker"), (TEST_PATH, "test"), (GUARD_STEP, "guard step"), (PLAN_PATH, "plan"), (PLAN_ZH_PATH, "zh plan")):
        if token not in safety_text:
            errors.append(f"{SAFETY_PATH} does not register {label} `{token}`.")


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: set[str] = set()
    validate_plan_order(root, errors, checked)
    validate_files(root, errors, checked)
    validate_registry(root, errors, checked)
    validate_generation_and_no_peer(root, errors, checked)
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
        "info": ["Validated Codex and one-person-company Stage B supplement sequence contract."],
        "groups": [
            {
                "id": group["id"],
                "order": index + 1,
                "primary_files": len(group["files"]),
                "bilingual_pairs": len(group["files"]),
            }
            for index, group in enumerate(GROUPS)
        ],
        "checked_paths": sorted(checked),
        "counts": {
            "groups": len(GROUPS),
            "required_primary_files": primary_count,
            "required_bilingual_files": primary_count * 2,
            "checked_paths": len(checked),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex and one-person-company next supplement sequence Stage B contract.")
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
