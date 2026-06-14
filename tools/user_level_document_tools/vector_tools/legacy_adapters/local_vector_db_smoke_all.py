#!/usr/bin/env python3
"""Run the project-local local-vector-DB smoke workflow.

This orchestrator writes only to the development paths configured in
``config/local-vector-db.json``:

- ``<consumer-project-root>\\data\\local_vector_db``
- ``<consumer-project-root>\\.project-runtime\\local-vector-db``

It never writes to ``<configured-external-source-root>``. In ``offline`` mode it also
does not call the embedding sidecar; it only refreshes deterministic QMD
manifests, validates them, creates the non-mutating ingestion plan, and runs
the offline mirror verifier against already-created local mirror files.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path.cwd()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "local-vector-db.json"
PROTECTED_ROOTS = (
    PROJECT_ROOT / "current_progress",
    PROJECT_ROOT / "regulations",
    PROJECT_ROOT / "requirement",
)


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            data = json.loads(raw.decode(encoding))
            if not isinstance(data, dict):
                raise ValueError(f"config root must be an object: {path}")
            return data
        except UnicodeDecodeError:
            continue
    data = json.loads(raw.decode("utf-8", errors="replace"))
    if not isinstance(data, dict):
        raise ValueError(f"config root must be an object: {path}")
    return data


def as_text(value: Any) -> str:
    return str(value or "").strip()


def resolve_path(value: Any) -> Path:
    text = as_text(value)
    if not text:
        raise ValueError("empty path in config")
    return Path(text)


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def assert_safe_write_paths(paths: list[Path]) -> None:
    bad: list[str] = []
    for path in paths:
        for protected in PROTECTED_ROOTS:
            if is_relative_to(path, protected):
                bad.append(str(path))
                break
    if bad:
        joined = "\n".join(f"- {item}" for item in bad)
        raise ValueError(f"refusing to write under protected source directories:\n{joined}")


def run_step(
    name: str,
    command: list[str],
    *,
    keep_going: bool,
    max_output_chars: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    elapsed = round(time.perf_counter() - started, 3)
    step = {
        "name": name,
        "status": "passed" if proc.returncode == 0 else "failed",
        "returnCode": proc.returncode,
        "durationSeconds": elapsed,
        "command": command,
        "stdoutTail": proc.stdout[-max_output_chars:],
        "stderrTail": proc.stderr[-max_output_chars:],
    }
    if proc.returncode != 0 and not keep_going:
        step["stoppedWorkflow"] = True
    return step


def skip_step(name: str, reason: str) -> dict[str, Any]:
    return {"name": name, "status": "skipped", "reason": reason}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument(
        "--mode",
        choices=("offline", "online"),
        default="offline",
        help="offline avoids embedding calls; online rebuilds mirror and query smoke reports.",
    )
    parser.add_argument("--out", help="Optional orchestrator JSON report path.")
    parser.add_argument("--query", default="OpenSpec authority memory recall", help="Vector/hybrid smoke query.")
    parser.add_argument("--qmd-query", default="memory recall", help="QMD keyword smoke query.")
    parser.add_argument("--limit", type=int, default=5, help="Vector/hybrid result limit.")
    parser.add_argument("--qmd-limit", type=int, default=3, help="QMD result limit.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Embedding HTTP timeout for online mode.")
    parser.add_argument("--keep-going", action="store_true", help="Continue after a failed step.")
    parser.add_argument("--max-output-chars", type=int, default=4000, help="Captured stdout/stderr tail length.")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config = load_json(config_path)
    mirror = config.get("projectLocalMirror", {})
    if not isinstance(mirror, dict):
        raise ValueError("config.projectLocalMirror must be an object")
    metadata = mirror.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("config.projectLocalMirror.metadata must be an object")

    chunks_manifest = resolve_path(mirror.get("chunksManifestPath"))
    validation_report = resolve_path(mirror.get("validationReportPath"))
    ingestion_plan = resolve_path(mirror.get("ingestionPlanPath"))
    health_report = resolve_path(mirror.get("healthReportPath"))
    runtime_root = resolve_path(mirror.get("runtimeRoot"))
    reports_root = runtime_root / "reports"
    mirror_report = reports_root / "mirror_ingest.json"
    query_smoke_report = reports_root / "query_smoke.json"
    qmd_query_smoke_report = reports_root / "qmd_query_smoke.json"
    hybrid_query_smoke_report = reports_root / "hybrid_query_smoke.json"
    lancedb_sync_report = reports_root / "lancedb_sync.json"
    lancedb_query_smoke_report = reports_root / "lancedb_query_smoke.json"
    verify_report = reports_root / "mirror_verify.json"
    out_path = Path(args.out) if args.out else reports_root / "smoke_all.json"

    write_paths = [
        chunks_manifest,
        validation_report,
        ingestion_plan,
        health_report,
        mirror_report,
        query_smoke_report,
        qmd_query_smoke_report,
        hybrid_query_smoke_report,
        lancedb_sync_report,
        lancedb_query_smoke_report,
        verify_report,
        out_path,
    ]
    assert_safe_write_paths(write_paths)
    for path in write_paths:
        path.parent.mkdir(parents=True, exist_ok=True)

    py = sys.executable
    steps: list[dict[str, Any]] = []
    deferred_steps: list[dict[str, Any]] = []

    workflow: list[tuple[str, list[str]]] = [
        (
            "qmd_dry_run",
            [
                py,
                str(PROJECT_ROOT / "tools" / "qmd_vector_ingest_dry_run.py"),
                "--config",
                str(config_path),
                "--out",
                str(chunks_manifest),
            ],
        ),
        (
            "manifest_validate",
            [
                py,
                str(PROJECT_ROOT / "tools" / "local_vector_db_manifest_validate.py"),
                "--config",
                str(config_path),
                "--manifest",
                str(chunks_manifest),
                "--out",
                str(validation_report),
            ],
        ),
        (
            "ingestion_plan",
            [
                py,
                str(PROJECT_ROOT / "tools" / "local_vector_db_ingestion_plan.py"),
                "--config",
                str(config_path),
                "--manifest",
                str(chunks_manifest),
                "--manifest-validation",
                str(validation_report),
                "--out",
                str(ingestion_plan),
            ],
        ),
    ]

    if args.mode == "online":
        workflow.extend(
            [
                (
                    "health_check",
                    [
                        py,
                        str(PROJECT_ROOT / "tools" / "local_vector_db_health_check.py"),
                        "--config",
                        str(config_path),
                        "--out",
                        str(health_report),
                        "--timeout",
                        str(args.timeout),
                    ],
                ),
                (
                    "mirror_ingest",
                    [
                        py,
                        str(PROJECT_ROOT / "tools" / "local_vector_db_mirror_ingest.py"),
                        "--config",
                        str(config_path),
                        "--manifest",
                        str(chunks_manifest),
                        "--report",
                        str(mirror_report),
                        "--timeout",
                        str(args.timeout),
                    ],
                ),
                (
                    "query_vector",
                    [
                        py,
                        str(PROJECT_ROOT / "tools" / "local_vector_db_query.py"),
                        args.query,
                        "--config",
                        str(config_path),
                        "--mode",
                        "vector",
                        "--limit",
                        str(args.limit),
                        "--out",
                        str(query_smoke_report),
                        "--timeout",
                        str(args.timeout),
                    ],
                ),
                (
                    "lancedb_sync",
                    [
                        py,
                        str(PROJECT_ROOT / "tools" / "local_vector_db_lancedb_sync.py"),
                        "--config",
                        str(config_path),
                        "--report",
                        str(lancedb_sync_report),
                    ],
                ),
                (
                    "query_lancedb",
                    [
                        py,
                        str(PROJECT_ROOT / "tools" / "local_vector_db_lancedb_query.py"),
                        args.query,
                        "--config",
                        str(config_path),
                        "--limit",
                        str(args.limit),
                        "--out",
                        str(lancedb_query_smoke_report),
                        "--timeout",
                        str(args.timeout),
                    ],
                ),
                (
                    "query_qmd",
                    [
                        py,
                        str(PROJECT_ROOT / "tools" / "local_vector_db_query.py"),
                        args.qmd_query,
                        "--config",
                        str(config_path),
                        "--mode",
                        "qmd",
                        "--limit",
                        str(args.qmd_limit),
                        "--out",
                        str(qmd_query_smoke_report),
                        "--timeout",
                        str(args.timeout),
                    ],
                ),
                (
                    "query_hybrid",
                    [
                        py,
                        str(PROJECT_ROOT / "tools" / "local_vector_db_query.py"),
                        args.query,
                        "--config",
                        str(config_path),
                        "--mode",
                        "hybrid",
                        "--limit",
                        str(args.limit),
                        "--out",
                        str(hybrid_query_smoke_report),
                        "--timeout",
                        str(args.timeout),
                    ],
                ),
            ]
        )
    else:
        deferred_steps.extend(
            [
                skip_step("health_check", "offline mode avoids embedding sidecar calls"),
                skip_step("mirror_ingest", "offline mode does not rebuild vectors"),
                skip_step("query_vector", "offline mode avoids embedding sidecar calls"),
                skip_step("lancedb_sync", "offline mode keeps LanceDB table untouched"),
                skip_step("query_lancedb", "offline mode avoids embedding sidecar calls"),
                skip_step("query_qmd", "offline mode keeps existing query audit untouched"),
                skip_step("query_hybrid", "offline mode avoids embedding sidecar calls"),
            ]
        )

    workflow.append(
        (
            "offline_verify",
            [
                py,
                str(PROJECT_ROOT / "tools" / "local_vector_db_verify.py"),
                "--config",
                str(config_path),
                "--out",
                str(verify_report),
            ],
        )
    )

    for name, command in workflow:
        step = run_step(name, command, keep_going=args.keep_going, max_output_chars=args.max_output_chars)
        steps.append(step)
        if name == "ingestion_plan" and deferred_steps:
            steps.extend(deferred_steps)
            deferred_steps = []
        if step["status"] == "failed" and not args.keep_going:
            break

    failed = [step for step in steps if step.get("status") == "failed"]
    payload = {
        "ok": not failed,
        "mode": args.mode,
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "configPath": str(config_path),
        "dataRoot": as_text(mirror.get("dataRoot")),
        "runtimeRoot": str(runtime_root),
        "reportPath": str(out_path),
        "steps": steps,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    out_path.write_text(output, encoding="utf-8")
    # Windows shells may expose a legacy console encoding such as GBK. The
    # report can contain replacement characters from captured subprocess
    # output, so write UTF-8 bytes directly to avoid console encode failures
    # after an otherwise successful smoke run.
    sys.stdout.buffer.write(output.encode("utf-8", errors="replace"))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
