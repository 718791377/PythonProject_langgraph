#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_operations_package as generator  # noqa: E402

CHECK_NAME = "embedded_codex_governance_alignment"
SCHEMA_VERSION = 1

REQUIRED_DOCS = (
    "docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md",
    "docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.zh-CN.md",
    "docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md",
    "docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.zh-CN.md",
    "docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md",
    "docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.zh-CN.md",
    "docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md",
    "docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.zh-CN.md",
    "docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md",
    "docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.zh-CN.md",
    "docs_bilingual/docs_registry.yaml",
)

POLICY_DOCS = (
    "docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md",
    "docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.zh-CN.md",
)

BOUNDARY_ANCHORS = (
    "embedded platform-governance capability",
    "not a peer authority",
    "business truth",
    "execution truth",
    "Mixed matters require two gates",
    "AI agents do not own final commitment rights",
    "scope: business | codex | mixed",
    "truth_owner: founder | codex-operator | human-review",
    "evidence_source: customer | revenue | repo | runtime | agent | legal",
    "decision_right: human | delegated-draft-only",
    "linked_docs: []",
)

REQUIRED_SHARED_LEDGER_FIELDS = (
    "scope",
    "truth_owner",
    "evidence_source",
    "decision_right",
    "linked_docs",
)

SHARED_LEDGERS = (
    "decision-log.md",
    "risk-register.md",
    "learning-log.md",
    "experiment-log.md",
    "data-dictionary.md",
    "tracking-plan.md",
    "backup-restore.md",
    "agent-role-map.md",
    "agent-permissions.md",
    "human-review-checklist.md",
    "monthly-review.md",
)

SAME_NAME_SEPARATE_TRUTH = (
    "vision.md",
    "strategy.md",
    "business-model.md",
    "pricing.md",
    "unit-economics.md",
    "user-segments.md",
    "market-map.md",
    "north-star.md",
    "metrics.md",
    "prd.md",
    "tech-stack.md",
    "privacy-policy.md",
)

CANONICAL_NAME_CONTRACT = {
    "agent-governance.md": ("docs_bilingual/operations_packages/codex_cli_durable_team/agent-governance.md",),
    "thesis.md": ("docs_bilingual/operations_packages/one_person_company/thesis.md",),
    "metrics.md": (
        "docs_bilingual/operations_packages/codex_cli_durable_team/metrics.md",
        "docs_bilingual/operations_packages/one_person_company/metrics.md",
    ),
    "support-playbook.md": ("docs_bilingual/operations_packages/one_person_company/support-playbook.md",),
}

LEGACY_NAME_FRAGMENTS = (
    "agent-tool-policy.md",
    "agent-tool-policy.zh-CN.md",
    "company-thesis.md",
    "company-thesis.zh-CN.md",
    "metrics.yaml",
    "support-policy.md",
    "support-policy.zh-CN.md",
)

BUSINESS_ONLY_FILES = (
    "offer.md",
    "finance-model.md",
    "cashflow.md",
    "contract-template.md",
    "terms-of-service.md",
    "sales-playbook.md",
    "customer-success-playbook.md",
    "refund-policy.md",
    "legal-checklist.md",
    "compliance-checklist.md",
)

CODEX_ONLY_FILES = (
    "architecture.md",
    "adr.md",
    "module-boundaries.md",
    "observability.md",
    "agent-evaluation.md",
    "agent-failure-modes.md",
    "access-control.md",
    "incident-response.md",
    "delivery-plan.md",
)

SEMANTIC_MAPPINGS = (
    ("thesis.md", ("thesis.md",)),
    ("agent-governance.md", ("agent-governance.md",)),
    ("agent-evaluation.md", ("agent-governance.md", "human-review-checklist.md")),
    ("agent-failure-modes.md", ("risk-register.md",)),
    ("architecture.md", ("automation-map.md",)),
    ("adr.md", ("decision-log.md",)),
    ("module-boundaries.md", ("tool-stack.md", "api-dependency-map.md")),
    ("delivery-plan.md", ("roadmap.md", "quarterly-plan.md")),
    ("observability.md", ("funnel-dashboard.md", "metrics.md")),
    ("security-policy.md", ("legal-checklist.md", "compliance-checklist.md")),
    ("access-control.md", ("agent-permissions.md",)),
    ("incident-response.md", ("support-playbook.md", "feedback-triage.md")),
    ("support-playbook.md", ("customer-success-playbook.md", "support-playbook.md")),
    ("cli-ux.md", ("onboarding.md", "service-blueprint.md")),
    ("changelog.md", ("roadmap.md", "monthly-review.md")),
    ("postmortem.md", ("learning-log.md",)),
    ("template-library.md", ("content-calendar.md", "landing-page.md")),
)

LINKED_BOUNDARY_SURFACES = (
    "docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md",
    "docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md",
    "docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md",
    "docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md",
    "docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md",
    "docs_bilingual/docs_registry.yaml",
)

REQUIRED_REGISTRY_DOC_IDS = (
    "one_person_company_embedded_codex_governance_policy",
    "embedded_codex_governance_in_one_person_company_plan",
    "embedded_codex_governance_alignment_runtime_plan",
)

CI_TEST_NAME = "check_embedded_codex_governance_alignment.test.py"
GUARD_STEP_NAME = "check_embedded_codex_governance_alignment"
CHECKER_PATH = "tools/check_embedded_codex_governance_alignment.py"
RUNTIME_PLAN_PATH = "docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md"

ZH_REQUIRED_READABILITY_SNIPPETS = (
    "Codex",
    "Agent",
    "scope: business | codex | mixed",
    "truth_owner",
    "decision_right",
)
ZH_MOJIBAKE_SENTINELS = ("\ufffd",)


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def read_text(path: Path, errors: list[str] | None = None) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="strict")
    except FileNotFoundError:
        if errors is not None:
            errors.append(f"Required file is missing: {norm(path)}")
        return ""
    except UnicodeDecodeError as exc:
        if errors is not None:
            errors.append(f"File is not valid UTF-8: {norm(path)}: {exc}")
        return ""


def parse_front_matter(text: str) -> dict[str, str]:
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
    return data


def parse_registry(path: Path) -> list[dict[str, str]]:
    text = read_text(path)
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
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


def add_missing_text_errors(*, rel: str, text: str, anchors: Iterable[str], errors: list[str], context: str) -> None:
    for anchor in anchors:
        if anchor not in text:
            errors.append(f"{rel} is missing {context} anchor `{anchor}`.")


def docs_with_same_name(package_docs: list[generator.GeneratedDoc], name: str) -> list[generator.GeneratedDoc]:
    return [doc for doc in package_docs if doc.source_name == name]


def validate_required_docs(root: Path, errors: list[str], checked: set[str]) -> dict[str, str]:
    docs: dict[str, str] = {}
    for rel in REQUIRED_DOCS:
        checked.add(rel)
        path = root / rel
        if not path.exists():
            errors.append(f"Required governance/alignment document is missing: {rel}")
            docs[rel] = ""
            continue
        text = read_text(path, errors)
        docs[rel] = text
        if "\ufffd" in text:
            errors.append(f"{rel} contains Unicode replacement character.")
    return docs


def validate_policy_contract(root: Path, docs: dict[str, str], errors: list[str]) -> None:
    en_policy = docs.get(POLICY_DOCS[0], "")
    add_missing_text_errors(rel=POLICY_DOCS[0], text=en_policy, anchors=BOUNDARY_ANCHORS, errors=errors, context="embedded-governance")
    for ledger in SHARED_LEDGERS:
        if f"`{ledger}`" not in en_policy and ledger not in en_policy:
            errors.append(f"{POLICY_DOCS[0]} is missing shared ledger `{ledger}`.")
    for field in REQUIRED_SHARED_LEDGER_FIELDS:
        if field not in en_policy:
            errors.append(f"{POLICY_DOCS[0]} is missing shared ledger field `{field}`.")
    for name in SAME_NAME_SEPARATE_TRUTH:
        if f"`{name}`" not in en_policy and name not in en_policy:
            errors.append(f"{POLICY_DOCS[0]} is missing same-name separate-truth entry `{name}`.")
    for left, rights in SEMANTIC_MAPPINGS:
        if f"`{left}`" not in en_policy and left not in en_policy:
            errors.append(f"{POLICY_DOCS[0]} is missing semantic mapping source `{left}`.")
        for right in rights:
            if f"`{right}`" not in en_policy and right not in en_policy:
                errors.append(f"{POLICY_DOCS[0]} is missing semantic mapping target `{right}` for `{left}`.")
    for name in BUSINESS_ONLY_FILES:
        if f"`{name}`" not in en_policy and name not in en_policy:
            errors.append(f"{POLICY_DOCS[0]} is missing business-only truth file `{name}`.")
    for name in CODEX_ONLY_FILES:
        if f"`{name}`" not in en_policy and name not in en_policy:
            errors.append(f"{POLICY_DOCS[0]} is missing Codex-only truth file `{name}`.")
    zh_policy = docs.get(POLICY_DOCS[1], "")
    for snippet in ZH_REQUIRED_READABILITY_SNIPPETS:
        if snippet not in zh_policy:
            errors.append(f"{POLICY_DOCS[1]} is missing zh-CN readability snippet `{snippet}`.")


def validate_links(docs: dict[str, str], errors: list[str]) -> None:
    policy_path = "docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md"
    runtime_plan = "docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md"
    forced_plan = "docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md"
    for rel in LINKED_BOUNDARY_SURFACES:
        text = docs.get(rel, "")
        if not text:
            continue
        if rel == runtime_plan and policy_path not in text:
            errors.append(f"{rel} no longer links the embedded governance policy boundary.")
            continue
        if rel != policy_path and policy_path not in text and "one_person_company_embedded_codex_governance_policy" not in text:
            errors.append(f"{rel} no longer links the embedded governance policy boundary.")
    if runtime_plan not in docs.get("docs_bilingual/docs_registry.yaml", ""):
        errors.append("docs_bilingual/docs_registry.yaml does not register the runtime alignment plan path.")
    if forced_plan not in docs.get(runtime_plan, ""):
        errors.append(f"{runtime_plan} no longer links the prior forced-rename plan.")


def validate_canonical_and_legacy(root: Path, registry_text: str, errors: list[str], checked: set[str]) -> None:
    for canonical, paths in CANONICAL_NAME_CONTRACT.items():
        for rel in paths:
            checked.add(rel)
            if not (root / rel).exists():
                errors.append(f"Canonical package file is missing for `{canonical}`: {rel}")
    for rel in generator.stale_legacy_files("all"):
        checked.add(rel)
        if (root / rel).exists():
            errors.append(f"Legacy generated physical file must not reappear: {rel}")
    for fragment in LEGACY_NAME_FRAGMENTS:
        if fragment in registry_text:
            errors.append(f"docs_bilingual/docs_registry.yaml contains legacy path/name fragment `{fragment}`.")


def validate_generated_counts(errors: list[str]) -> None:
    expected_counts = {
        "Codex primary documents": (len(generator.CODEX_DOCS), 48),
        "One-person-company primary documents": (len(generator.OPC_DOCS), 60),
        "Codex generated files": (len(generator.expected_files("codex")), 96),
        "One-person-company generated files": (len(generator.expected_files("one-person-company")), 120),
        "Total generated files": (len(generator.expected_files("all")), 216),
    }
    for label, (actual, expected) in expected_counts.items():
        if actual != expected:
            errors.append(f"{label} count drifted to {actual}; expected {expected}.")


def validate_package_placement(root: Path, errors: list[str], checked: set[str]) -> None:
    codex_dir = root / "docs_bilingual" / "operations_packages" / "codex_cli_durable_team"
    opc_dir = root / "docs_bilingual" / "operations_packages" / "one_person_company"
    for name in BUSINESS_ONLY_FILES:
        for suffix in ("", ".zh-CN"):
            rel = f"docs_bilingual/operations_packages/codex_cli_durable_team/{name[:-3]}{suffix}.md"
            checked.add(rel)
            if (root / rel).exists():
                errors.append(f"Business-only truth file appears under Codex package: {rel}")
    for name in CODEX_ONLY_FILES:
        for suffix in ("", ".zh-CN"):
            rel = f"docs_bilingual/operations_packages/one_person_company/{name[:-3]}{suffix}.md"
            checked.add(rel)
            if (root / rel).exists():
                errors.append(f"Codex-only truth file appears under one-person-company package: {rel}")
    if not codex_dir.exists():
        errors.append("Codex operations-package directory is missing.")
    if not opc_dir.exists():
        errors.append("One-person-company operations-package directory is missing.")
    for name in SAME_NAME_SEPARATE_TRUTH:
        codex_matches = docs_with_same_name(generator.CODEX_DOCS, name)
        opc_matches = docs_with_same_name(generator.OPC_DOCS, name)
        if codex_matches and opc_matches:
            codex_rel = codex_matches[0].rel_path
            opc_rel = opc_matches[0].rel_path
            checked.update({codex_rel, opc_rel})
            if not (root / codex_rel).exists() or not (root / opc_rel).exists():
                errors.append(f"Same-name separate-truth pair `{name}` must exist in both package directories.")
            for doc in (codex_matches[0], opc_matches[0]):
                text = read_text(root / doc.rel_path, errors)
                fm = parse_front_matter(text)
                if fm.get("package") != doc.package:
                    errors.append(f"{doc.rel_path} front matter package={fm.get('package')!r}; expected {doc.package!r}.")


def validate_registry(root: Path, errors: list[str]) -> tuple[list[dict[str, str]], str]:
    registry_path = root / "docs_bilingual" / "docs_registry.yaml"
    registry_text = read_text(registry_path, errors)
    entries = parse_registry(registry_path)
    doc_ids = [entry.get("doc_id", "") for entry in entries]
    canonical_paths = [entry.get("canonical_path", "") for entry in entries]
    zh_paths = [entry.get("zh_cn_path", "") for entry in entries]
    for doc_id, count in Counter(doc_ids).items():
        if doc_id and count > 1:
            errors.append(f"docs_bilingual/docs_registry.yaml has duplicate doc_id `{doc_id}`.")
    for path, count in Counter(canonical_paths + zh_paths).items():
        if path and count > 1:
            errors.append(f"docs_bilingual/docs_registry.yaml has duplicate path `{path}`.")
    by_doc_id = {entry.get("doc_id", ""): entry for entry in entries}
    for doc_id in REQUIRED_REGISTRY_DOC_IDS:
        if doc_id not in by_doc_id:
            errors.append(f"docs_bilingual/docs_registry.yaml is missing required doc_id `{doc_id}`.")
    for doc_id in generator.stale_legacy_doc_ids("all"):
        if doc_id in by_doc_id:
            errors.append(f"docs_bilingual/docs_registry.yaml contains stale legacy doc_id `{doc_id}`.")
    for entry in entries:
        canonical = entry.get("canonical_path", "")
        zh = entry.get("zh_cn_path", "")
        if canonical and not (root / canonical).exists():
            errors.append(f"docs_bilingual/docs_registry.yaml canonical_path does not exist: {canonical}")
        if zh and not (root / zh).exists():
            errors.append(f"docs_bilingual/docs_registry.yaml zh_cn_path does not exist: {zh}")
    return entries, registry_text


def validate_stage_b_registration(root: Path, errors: list[str], checked: set[str]) -> None:
    manifest_rel = "tools/ci/ci_test_manifest.json"
    guard_rel = "tools/run_openspec_guard.py"
    safety_rel = "tools/safety_rule_script_backing_registry.json"
    mirror_test_rel = "test/run_openspec_guard_json.test.py"
    for rel in (manifest_rel, guard_rel, safety_rel, mirror_test_rel):
        checked.add(rel)
    manifest_text = read_text(root / manifest_rel, errors)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"{manifest_rel} is not valid JSON: {exc}")
        manifest = {}
    if CI_TEST_NAME not in manifest.get("python_unittest", []):
        errors.append(f"{manifest_rel} does not register `{CI_TEST_NAME}`.")
    guard_text = read_text(root / guard_rel, errors)
    guard_declares_checker = (
        CHECKER_PATH in guard_text
        or (
            "embedded_codex_governance_alignment_script" in guard_text
            and "check_embedded_codex_governance_alignment.py" in guard_text
        )
    )
    if not guard_declares_checker:
        errors.append(f"{guard_rel} does not declare `{CHECKER_PATH}`.")
    if GUARD_STEP_NAME not in guard_text:
        errors.append(f"{guard_rel} does not include guard step `{GUARD_STEP_NAME}`.")
    safety_text = read_text(root / safety_rel, errors)
    if CHECKER_PATH not in safety_text:
        errors.append(f"{safety_rel} does not register checker `{CHECKER_PATH}` as script backing.")
    if GUARD_STEP_NAME not in safety_text:
        errors.append(f"{safety_rel} does not register guard step `{GUARD_STEP_NAME}`.")
    if RUNTIME_PLAN_PATH not in safety_text:
        errors.append(f"{safety_rel} does not reference runtime plan `{RUNTIME_PLAN_PATH}`.")
    mirror_text = read_text(root / mirror_test_rel, errors)
    if GUARD_STEP_NAME not in mirror_text:
        errors.append(f"{mirror_test_rel} does not mirror guard step `{GUARD_STEP_NAME}`.")


def validate_text_encoding(root: Path, errors: list[str], checked: set[str]) -> None:
    paths = list(REQUIRED_DOCS)
    paths.extend(doc.zh_path for doc in generator.ALL_DOCS)
    paths.extend(doc.rel_path for doc in generator.ALL_DOCS)
    for rel in paths:
        checked.add(rel)
        path = root / rel
        if not path.exists():
            continue
        text = read_text(path, errors)
        for sentinel in ZH_MOJIBAKE_SENTINELS:
            if sentinel in text:
                errors.append(f"{rel} contains corrupted text sentinel U+{ord(sentinel):04X}.")
                break


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    checked: set[str] = set()

    docs = validate_required_docs(root, errors, checked)
    registry_entries, registry_text = validate_registry(root, errors)
    docs["docs_bilingual/docs_registry.yaml"] = registry_text
    validate_policy_contract(root, docs, errors)
    validate_links(docs, errors)
    validate_canonical_and_legacy(root, registry_text, errors, checked)
    validate_generated_counts(errors)
    validate_package_placement(root, errors, checked)
    validate_stage_b_registration(root, errors, checked)
    validate_text_encoding(root, errors, checked)

    out_of_date, _matched = generator.check_expected(root, "all")
    if out_of_date:
        errors.append("Operations-package generator check is out of date: " + ", ".join(out_of_date))

    info.append("Validated embedded Codex governance boundary, package isolation, registry, and live checker registration.")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "required_docs": len(REQUIRED_DOCS),
            "registry_entries": len(registry_entries),
            "shared_ledgers": len(SHARED_LEDGERS),
            "same_name_separate_truth_slots": len(SAME_NAME_SEPARATE_TRUTH),
            "semantic_mappings": len(SEMANTIC_MAPPINGS),
            "business_only_files": len(BUSINESS_ONLY_FILES),
            "codex_only_files": len(CODEX_ONLY_FILES),
            "codex_body_primaries": len(generator.CODEX_DOCS),
            "one_person_company_body_primaries": len(generator.OPC_DOCS),
            "codex_body_files": len(generator.expected_files("codex")),
            "one_person_company_body_files": len(generator.expected_files("one-person-company")),
            "total_generated_files": len(generator.expected_files("all")),
            "checked_surfaces": len(checked),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate embedded Codex governance alignment inside one-person-company operations.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    payload = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'fail'}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
