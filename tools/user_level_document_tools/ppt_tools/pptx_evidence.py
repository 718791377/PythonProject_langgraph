#!/usr/bin/env python3
"""Shared PPTX/OOXML evidence helpers for document pipeline adapters.

This module is intentionally project-neutral. Consumer repositories pass their
own input/output paths and policy boundaries; this helper only inspects PPTX
packages and writes reusable evidence JSON/text artifacts.
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import zipfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"rel": REL_NS, "p": P_NS, "r": R_NS}

STRICT_PASS = "PASS: strict template use"
STRUCTURE_PARTIAL = "PARTIAL: template structure proven but visual review needed"
STRICT_FAIL = "FAIL: strict template use not proven / template not used"

MAX_PPTX_BYTES = 100 * 1024 * 1024
MAX_PART_BYTES = 10 * 1024 * 1024
MAX_ZIP_ENTRIES = 5000
MAX_COMPRESSION_RATIO = 100

CORE_PARTS = ("[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml")
HASH_PREFIXES = (
    "[Content_Types].xml",
    "ppt/presentation.xml",
    "ppt/_rels/presentation.xml.rels",
    "ppt/theme/",
    "ppt/slideMasters/",
    "ppt/slideMasters/_rels/",
    "ppt/slideLayouts/",
    "ppt/slideLayouts/_rels/",
    "ppt/slides/",
    "ppt/slides/_rels/",
)
UNSAFE_XML_DECLARATION_RE = re.compile(br"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)
UNSAFE_XML_DECLARATION_TEXT_RE = re.compile(r"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def file_metadata(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.exists():
        return {"path": str(resolved), "exists": False}
    stat = resolved.stat()
    metadata = {
        "path": str(resolved),
        "exists": True,
        "size": stat.st_size,
        "last_write_time": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
    }
    if stat.st_size <= MAX_PPTX_BYTES:
        metadata["sha256"] = sha256_bytes(resolved.read_bytes())
    else:
        metadata["sha256"] = ""
        metadata["sha256_status"] = "skipped:file_too_large"
    return metadata


def _validate_zip(zf: zipfile.ZipFile) -> None:
    infos = zf.infolist()
    if len(infos) > MAX_ZIP_ENTRIES:
        raise ValueError("too_many_zip_entries")
    total_uncompressed = 0
    total_compressed = 0
    seen_names: set[str] = set()
    for info in infos:
        if not info.filename.endswith("/"):
            if info.filename in seen_names:
                raise ValueError(f"duplicate_zip_entry:{info.filename}")
            seen_names.add(info.filename)
        total_uncompressed += info.file_size
        total_compressed += info.compress_size
        if info.file_size > MAX_PART_BYTES:
            raise ValueError(f"zip_part_too_large:{info.filename}")
        if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
            raise ValueError(f"zip_part_suspicious_ratio:{info.filename}")
    if total_uncompressed > MAX_PPTX_BYTES:
        raise ValueError("zip_total_uncompressed_too_large")
    if total_compressed > MAX_PPTX_BYTES:
        raise ValueError("zip_total_compressed_too_large")


def _safe_zip_read(zf: zipfile.ZipFile, name: str) -> bytes:
    info = zf.getinfo(name)
    if info.file_size > MAX_PART_BYTES:
        raise ValueError(f"zip_part_too_large:{name}")
    if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
        raise ValueError(f"zip_part_suspicious_ratio:{name}")
    return zf.read(name)


def _zip_names(zf: zipfile.ZipFile) -> list[str]:
    return sorted(name for name in zf.namelist() if not name.endswith("/"))


def _selected_for_hash(name: str) -> bool:
    return any(name == prefix or name.startswith(prefix) for prefix in HASH_PREFIXES)


def _normalize_xml_element(element: ET.Element) -> None:
    if element.attrib:
        ordered = dict(sorted(element.attrib.items()))
        element.attrib.clear()
        element.attrib.update(ordered)
    if element.text is not None and not element.text.strip():
        element.text = None
    if element.tail is not None and not element.tail.strip():
        element.tail = None
    for child in list(element):
        _normalize_xml_element(child)


def canonicalize_xml_bytes(data: bytes) -> bytes:
    try:
        root = parse_ooxml_part(data)
    except ET.ParseError:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    _normalize_xml_element(root)
    return ET.tostring(root, encoding="utf-8", short_empty_elements=True)


def parse_ooxml_part(data: bytes) -> ET.Element:
    if UNSAFE_XML_DECLARATION_RE.search(data):
        raise ValueError("unsafe_xml_doctype_or_entity")
    prefix = data[:4096]
    if b"\x00" in prefix:
        for encoding in ("utf-16", "utf-16-le", "utf-16-be", "utf-32", "utf-32-le", "utf-32-be"):
            try:
                decoded = prefix.decode(encoding, errors="ignore")
            except Exception:
                continue
            if UNSAFE_XML_DECLARATION_TEXT_RE.search(decoded):
                raise ValueError("unsafe_xml_doctype_or_entity")
        raise ValueError("unsupported_xml_encoding")
    return ET.fromstring(data)


def hash_ooxml_parts(path: Path) -> dict[str, dict[str, str]]:
    raw: dict[str, str] = {}
    canonicalized: dict[str, str] = {}
    with zipfile.ZipFile(path) as zf:
        _validate_zip(zf)
        for name in _zip_names(zf):
            if not _selected_for_hash(name):
                continue
            data = _safe_zip_read(zf, name)
            raw[name] = sha256_bytes(data)
            canonicalized[name] = sha256_bytes(canonicalize_xml_bytes(data) if name.endswith(".xml") or name.endswith(".rels") else data)
    return {"raw": raw, "canonicalized": canonicalized}


def _rels_path_for(part_name: str) -> str:
    directory, filename = posixpath.split(part_name)
    return posixpath.join(directory, "_rels", filename + ".rels")


def _read_relationships(zf: zipfile.ZipFile, rels_name: str) -> dict[str, dict[str, str]]:
    if rels_name not in zf.namelist():
        return {}
    try:
        root = parse_ooxml_part(_safe_zip_read(zf, rels_name))
    except ET.ParseError:
        return {}
    rels: dict[str, dict[str, str]] = {}
    for rel in root.findall("rel:Relationship", NS):
        rid = str(rel.attrib.get("Id", ""))
        if not rid:
            continue
        rels[rid] = {
            "id": rid,
            "type": str(rel.attrib.get("Type", "")),
            "target": str(rel.attrib.get("Target", "")),
            "target_mode": str(rel.attrib.get("TargetMode", "")),
        }
    return rels


def _resolve_relationship_target(source_part: str, target: str) -> str:
    if "://" in target or target.startswith(("\\", "//")) or re.match(r"^[A-Za-z]:", target) or "\\" in target:
        raise ValueError("external_or_absolute_relationship_target")
    if target.startswith("/"):
        candidate = posixpath.normpath(target.lstrip("/"))
    else:
        candidate = posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))
    if candidate in {".", ".."} or candidate.startswith("../") or candidate.startswith("/"):
        raise ValueError("relationship_target_traversal")
    return candidate


def _resolve_internal_relationship_target(source_part: str, rel: dict[str, str]) -> str:
    target_mode = str(rel.get("target_mode", "")).strip()
    if target_mode:
        raise ValueError("external_structural_relationship_target")
    return _resolve_relationship_target(source_part, str(rel.get("target", "")))


def _part_display_name(zf: zipfile.ZipFile, part: str) -> str:
    if part not in zf.namelist():
        return ""
    try:
        root = parse_ooxml_part(_safe_zip_read(zf, part))
    except ET.ParseError:
        return ""
    for key in ("name", f"{{{P_NS}}}name"):
        if key in root.attrib:
            return root.attrib[key]
    c_sld = root.find("p:cSld", NS)
    if c_sld is not None:
        return str(c_sld.attrib.get("name", ""))
    return ""


def _slide_number(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def inspect_pptx(path: str | Path) -> dict[str, Any]:
    pptx_path = Path(path).resolve()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "path": str(pptx_path),
        "status": "blocked",
        "reasons": [],
        "core_parts": {part: False for part in CORE_PARTS},
        "slide_count": 0,
        "slide_parts": [],
        "theme_parts": [],
        "slide_master_parts": [],
        "slide_layout_parts": [],
        "media_parts": [],
        "embedded_object_parts": [],
        "hyperlink_count": 0,
        "ooxml_hashes": {"raw": {}, "canonicalized": {}},
        "metadata": file_metadata(pptx_path),
    }
    if not pptx_path.exists():
        payload["status"] = "missing"
        payload["reasons"].append("input_missing")
        return payload
    try:
        with zipfile.ZipFile(pptx_path) as zf:
            _validate_zip(zf)
            names = _zip_names(zf)
            name_set = set(names)
            payload["core_parts"] = {part: part in name_set for part in CORE_PARTS}
            payload["slide_parts"] = sorted([name for name in names if re.match(r"ppt/slides/slide\d+\.xml$", name)], key=_slide_number)
            payload["slide_count"] = len(payload["slide_parts"])
            payload["theme_parts"] = sorted(name for name in names if name.startswith("ppt/theme/") and name.endswith(".xml"))
            payload["slide_master_parts"] = sorted(name for name in names if name.startswith("ppt/slideMasters/") and name.endswith(".xml"))
            payload["slide_layout_parts"] = sorted(name for name in names if name.startswith("ppt/slideLayouts/") and name.endswith(".xml"))
            payload["media_parts"] = sorted(name for name in names if name.startswith("ppt/media/"))
            payload["embedded_object_parts"] = sorted(name for name in names if name.startswith("ppt/embeddings/"))
            hyperlink_count = 0
            for name in names:
                if name.endswith(".rels"):
                    for rel in _read_relationships(zf, name).values():
                        if "hyperlink" in rel.get("type", ""):
                            hyperlink_count += 1
            payload["hyperlink_count"] = hyperlink_count
            payload["ooxml_hashes"] = hash_ooxml_parts(pptx_path)
    except zipfile.BadZipFile:
        payload["status"] = "invalid"
        payload["reasons"].append("not_zip_file")
        return payload
    except ValueError as exc:
        payload["status"] = "blocked"
        payload["reasons"].append(f"zip_safety_error:{exc}")
        return payload
    except Exception as exc:  # noqa: BLE001 - keep CLI evidence structured
        payload["status"] = "blocked"
        payload["reasons"].append(f"inspect_error:{exc.__class__.__name__}")
        payload["error_message"] = str(exc)
        return payload
    missing_core = [part for part, present in payload["core_parts"].items() if not present]
    if "ppt/presentation.xml" in missing_core:
        payload["status"] = "invalid"
        payload["reasons"].append("missing_presentation_xml")
    elif missing_core:
        payload["status"] = "degraded"
        payload["reasons"].extend(f"missing_core_part:{part}" for part in missing_core)
    else:
        payload["status"] = "ok"
    return payload


def _part_hashes(inspected: dict[str, Any], flavor: str = "canonicalized") -> dict[str, str]:
    hashes = inspected.get("ooxml_hashes", {})
    selected = hashes.get(flavor, {}) if isinstance(hashes, dict) else {}
    return selected if isinstance(selected, dict) else {}


def _part_kind(part: str) -> str:
    if re.match(r"ppt/slides/slide\d+\.xml$", part):
        return "slide"
    if part.startswith("ppt/slideLayouts/") and part.endswith(".xml"):
        return "slide_layout"
    if part.startswith("ppt/slideMasters/") and part.endswith(".xml"):
        return "slide_master"
    if part.startswith("ppt/theme/") and part.endswith(".xml"):
        return "theme"
    return "other"


def _matching_parts_by_hash(info: dict[str, Any] | None, kind: str, digest: str) -> list[str]:
    if not info or not digest:
        return []
    return sorted(part for part, candidate in _part_hashes(info).items() if candidate == digest and _part_kind(part) == kind)


def _classify_part_match(part: str, result_info: dict[str, Any], template_info: dict[str, Any] | None, source_info: dict[str, Any] | None) -> tuple[str, str]:
    result_hash = _part_hashes(result_info).get(part)
    if not result_hash:
        return "unknown", ""
    kind = _part_kind(part)
    source_matches = _matching_parts_by_hash(source_info, kind, result_hash)
    template_matches = _matching_parts_by_hash(template_info, kind, result_hash)
    renumbered_source_matches = [match for match in source_matches if match != part]
    if kind == "slide" and renumbered_source_matches:
        return "source_legacy_residue", renumbered_source_matches[0]
    if template_matches:
        return "template_exact", template_matches[0]
    if source_matches:
        return "source_legacy_residue", source_matches[0]
    return "unknown", ""


def _classify_part(part: str, result_info: dict[str, Any], template_info: dict[str, Any] | None, source_info: dict[str, Any] | None) -> str:
    return _classify_part_match(part, result_info, template_info, source_info)[0]


def _build_part_records(result_info: dict[str, Any], template_info: dict[str, Any] | None, source_info: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for field in ("theme_parts", "slide_master_parts", "slide_layout_parts"):
        for part in result_info.get(field, []):
            classification, match_part = _classify_part_match(part, result_info, template_info, source_info)
            row = {
                "part": part,
                "kind": field.removesuffix("_parts"),
                "raw_sha256": _part_hashes(result_info, "raw").get(part, ""),
                "canonical_sha256": _part_hashes(result_info).get(part, ""),
                "source_classification": classification,
            }
            if match_part:
                row["template_match_part" if classification == "template_exact" else "source_match_part"] = match_part
            records[part] = row
    return records


def _parse_slide_chains(path: Path, result_info: dict[str, Any], template_info: dict[str, Any] | None, source_info: dict[str, Any] | None) -> list[dict[str, Any]]:
    chains: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as zf:
            _validate_zip(zf)
            names = set(zf.namelist())
            for slide in result_info.get("slide_parts", []):
                slide_rels = _read_relationships(zf, _rels_path_for(slide))
                layout = ""
                master = ""
                theme = ""
                for rel in slide_rels.values():
                    if rel["type"].endswith("/slideLayout"):
                        layout = _resolve_internal_relationship_target(slide, rel)
                        break
                if layout:
                    layout_rels = _read_relationships(zf, _rels_path_for(layout))
                    for rel in layout_rels.values():
                        if rel["type"].endswith("/slideMaster"):
                            master = _resolve_internal_relationship_target(layout, rel)
                            break
                if master:
                    master_rels = _read_relationships(zf, _rels_path_for(master))
                    for rel in master_rels.values():
                        if rel["type"].endswith("/theme"):
                            theme = _resolve_internal_relationship_target(master, rel)
                            break
                class_parts = [part for part in (theme, master, layout) if part]
                slide_classification, slide_match_part = _classify_part_match(slide, result_info, template_info, source_info)
                if class_parts:
                    layout_classifications = [_classify_part(part, result_info, template_info, source_info) for part in class_parts]
                    combined = [slide_classification, *layout_classifications]
                    if "source_legacy_residue" in combined:
                        classification = "source_legacy_residue"
                    elif layout and master and theme and all(item == "template_exact" for item in layout_classifications):
                        classification = "template_exact" if slide_classification == "template_exact" else "template_derived_delta"
                    elif all(item == "template_exact" for item in combined):
                        classification = "template_exact"
                    elif "unknown" in combined:
                        classification = "unknown"
                    else:
                        classification = "template_derived_delta"
                else:
                    # Minimal OOXML test decks may omit layout/master/theme relations. In that
                    # case the slide XML itself still participates in provenance. A result slide
                    # copied from source is legacy residue; a result slide matching the template
                    # is exact; otherwise it is unknown until the adapter records a derived delta.
                    classification = slide_classification
                row = {
                    "slide": slide,
                    "slide_number": _slide_number(slide),
                    "slide_layout": layout,
                    "slide_master": master,
                    "theme": theme,
                    "layout_name": _part_display_name(zf, layout) if layout in names else "",
                    "master_name": _part_display_name(zf, master) if master in names else "",
                    "theme_name": _part_display_name(zf, theme) if theme in names else "",
                    "slide_source_classification": slide_classification,
                    "source_classification": classification,
                }
                if slide_match_part:
                    row["slide_template_match_part" if slide_classification == "template_exact" else "slide_source_match_part"] = slide_match_part
                chains.append(row)
    except Exception as exc:  # noqa: BLE001
        chains.append({"slide": "", "source_classification": "unknown", "error": f"chain_parse_error:{exc.__class__.__name__}:{exc}"})
    return chains


def aggregate_template_status(per_slide_chain: list[dict[str, Any]], legacy_source_residue: list[str]) -> str:
    classifications = [str(row.get("source_classification", "unknown")) for row in per_slide_chain]
    if legacy_source_residue or "source_legacy_residue" in classifications or "unknown" in classifications:
        return STRICT_FAIL
    if classifications and all(item == "template_exact" for item in classifications):
        return STRICT_PASS
    return STRUCTURE_PARTIAL


def build_provenance_manifest(
    result_pptx: str | Path,
    template_pptx: str | Path | None = None,
    source_pptx: str | Path | None = None,
) -> dict[str, Any]:
    result_path = Path(result_pptx).resolve()
    template_path = Path(template_pptx).resolve() if template_pptx else None
    source_path = Path(source_pptx).resolve() if source_pptx else None
    result_info = inspect_pptx(result_path)
    template_info = inspect_pptx(template_path) if template_path else None
    source_info = inspect_pptx(source_path) if source_path else None
    result_parts = _build_part_records(result_info, template_info, source_info)
    legacy = sorted(part for part, row in result_parts.items() if row.get("source_classification") == "source_legacy_residue")
    chains = _parse_slide_chains(result_path, result_info, template_info, source_info) if result_info.get("status") in {"ok", "degraded"} else []
    for row in chains:
        if row.get("slide_source_classification") == "source_legacy_residue":
            slide_part = row.get("slide")
            if slide_part and slide_part not in legacy:
                legacy.append(str(slide_part))
        if row.get("source_classification") == "source_legacy_residue":
            for part in (row.get("theme"), row.get("slide_master"), row.get("slide_layout")):
                if part and part not in legacy:
                    legacy.append(str(part))
    overall = aggregate_template_status(chains, legacy) if result_info.get("status") in {"ok", "degraded"} else STRICT_FAIL
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "result_pptx": result_info.get("metadata", file_metadata(result_path)),
        "template_pptx": template_info.get("metadata") if template_info else None,
        "source_pptx": source_info.get("metadata") if source_info else None,
        "ooxml_hashes": {
            "raw": {
                "result": _part_hashes(result_info, "raw"),
                "template": _part_hashes(template_info, "raw") if template_info else {},
                "source": _part_hashes(source_info, "raw") if source_info else {},
            },
            "canonicalized": {
                "result": _part_hashes(result_info),
                "template": _part_hashes(template_info) if template_info else {},
                "source": _part_hashes(source_info) if source_info else {},
            },
        },
        "template_parts": _build_part_records(template_info, template_info, None) if template_info else {},
        "result_parts": result_parts,
        "per_slide_chain": chains,
        "legacy_source_residue": sorted(legacy),
        "overall_status": overall,
        "inspect_status": result_info.get("status"),
        "reasons": result_info.get("reasons", []),
        "result_pptx_inspection": {"status": result_info.get("status"), "reasons": result_info.get("reasons", [])},
        "template_pptx_inspection": {"status": template_info.get("status"), "reasons": template_info.get("reasons", [])} if template_info else None,
        "source_pptx_inspection": {"status": source_info.get("status"), "reasons": source_info.get("reasons", [])} if source_info else None,
    }


def write_render_export_log(path: str | Path, *, result_pptx: str | Path | None = None, artifacts: list[str] | None = None, status: str = "ok", errors: list[str] | None = None) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"generated_at={utc_now()}",
        f"status={status}",
    ]
    if result_pptx:
        lines.append(f"result_pptx={Path(result_pptx).resolve()}")
    for artifact in artifacts or []:
        lines.append(f"artifact={Path(artifact).resolve()}")
    for error in errors or []:
        lines.append(f"error={error}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_com_generation_transcript(path: str | Path, events: list[dict[str, Any]] | None = None, **metadata: Any) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": utc_now(), "metadata": metadata, "events": events or []}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_visual_signature_report(
    *,
    template_screenshots: list[str] | None = None,
    result_screenshots: list[str] | None = None,
    roi_results: list[dict[str, Any]] | None = None,
    manual_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    roi_rows = roi_results or []
    statuses = {str(row.get("status", "review")) for row in roi_rows}
    manual_status = str((manual_review or {}).get("status", ""))
    manual_mode = str((manual_review or {}).get("mode", ""))
    if "fail" in statuses:
        overall = STRICT_FAIL
    elif not roi_rows and manual_mode != "manual_only":
        overall = STRUCTURE_PARTIAL
    elif "review" in statuses or manual_status not in {"accepted", "pass"}:
        overall = STRUCTURE_PARTIAL
    else:
        overall = STRICT_PASS
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "template_screenshots": template_screenshots or [],
        "result_screenshots": result_screenshots or [],
        "roi_results": roi_rows,
        "manual_review": manual_review or {},
        "overall_status": overall,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect PPTX OOXML and write reusable provenance/render evidence.")
    parser.add_argument("--input", help="PPTX/PPTM path to inspect without requiring renderers.")
    parser.add_argument("--result-pptx", help="Result PPTX path for provenance manifest mode.")
    parser.add_argument("--template-pptx", help="Template PPTX path for provenance comparison.")
    parser.add_argument("--source-pptx", help="Optional source PPTX path for legacy residue comparison.")
    parser.add_argument("--manifest-out", help="Optional template_provenance_manifest.json output path.")
    parser.add_argument("--render-log-out", help="Optional render_export_log.txt output path.")
    parser.add_argument("--artifact", action="append", default=[], help="Evidence artifact path to include in render export log.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON to stdout.")
    return parser


def _emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload.get("overall_status") or payload.get("status") or "ok")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    target = args.result_pptx or args.input
    if not target:
        payload = {"schema_version": 1, "generated_at": utc_now(), "status": "blocked", "reasons": ["input_required"]}
        _emit(payload, args.json)
        return 2
    if args.result_pptx:
        result_path = Path(args.result_pptx)
        if not result_path.exists():
            payload = {"schema_version": 1, "generated_at": utc_now(), "status": "missing", "overall_status": STRICT_FAIL, "reasons": ["input_missing"], "path": str(result_path.resolve())}
            _emit(payload, args.json)
            return 1
        manifest = build_provenance_manifest(result_path, args.template_pptx, args.source_pptx)
        if args.manifest_out:
            write_json(Path(args.manifest_out), manifest)
        if args.render_log_out:
            write_render_export_log(args.render_log_out, result_pptx=result_path, artifacts=[str(Path(item)) for item in args.artifact], status=manifest["overall_status"])
        _emit(manifest, args.json)
        return 0 if manifest.get("overall_status") != STRICT_FAIL else 1
    input_path = Path(args.input)
    payload = inspect_pptx(input_path)
    _emit(payload, args.json)
    return 0 if payload.get("status") in {"ok", "degraded"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
