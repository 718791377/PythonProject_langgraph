from __future__ import annotations

import contextlib
import importlib
import importlib.metadata
import io
from typing import Any, Callable


SCHEMA_VERSION = 1
PACKAGE_NAME = "PySide6-Fluent-Widgets"
IMPORT_NAME = "qfluentwidgets"
LICENSE_FAMILY = "GPLv3-or-commercial-dual-license"
NONCOMMERCIAL_LICENSE = "GPLv3"
EVIDENCE_URLS = [
    "https://pypi.org/project/PySide6-Fluent-Widgets/",
    "https://pyqt-fluent-widgets.readthedocs.io/en/latest/license.html",
]


def expected_qfluent_dependency() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "package_name": PACKAGE_NAME,
        "import_name": IMPORT_NAME,
        "purpose": "Project MOE GUI Fluent visual shell, cards, navigation sidebar, status and diagnostics widgets.",
        "runtime_surface": "shared-pyside6-runtime",
        "license_family": LICENSE_FAMILY,
        "noncommercial_license": NONCOMMERCIAL_LICENSE,
        "commercial_use_requires_review": True,
        "redistribution_requires_license_review": True,
        "fail_closed_if_missing": True,
        "evidence_urls": list(EVIDENCE_URLS),
    }


def qfluent_license_manifest() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "package_name": PACKAGE_NAME,
        "import_name": IMPORT_NAME,
        "license_family": LICENSE_FAMILY,
        "noncommercial_license": NONCOMMERCIAL_LICENSE,
        "commercial_use_requires_review": True,
        "redistribution_requires_license_review": True,
        "commercial_license_review_required_before": [
            "commercial redistribution",
            "public binary packaging",
            "customer-facing installer publication",
            "closed-source use that is not covered by a commercial license",
        ],
        "operator_decision": "approved-for-local-development-only-until-license-review",
        "evidence_urls": list(EVIDENCE_URLS),
    }


def _default_import_probe(import_name: str) -> object:
    # QFluentWidgets currently emits a promotional tip on stdout during import.
    # Machine-readable launcher modes must emit exactly one JSON document, so
    # treat third-party import chatter as internal probe noise.
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return importlib.import_module(import_name)


def _default_metadata_probe(package_name: str) -> dict[str, Any]:
    metadata = importlib.metadata.metadata(package_name)
    return {
        "version": importlib.metadata.version(package_name),
        "license": metadata.get("License") or metadata.get("Classifier", ""),
        "summary": metadata.get("Summary"),
    }


def check_qfluent_runtime(
    *,
    import_probe: Callable[[str], object] | None = None,
    metadata_probe: Callable[[str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    import_probe = import_probe or _default_import_probe
    metadata_probe = metadata_probe or _default_metadata_probe
    dependency = expected_qfluent_dependency()
    license_manifest = qfluent_license_manifest()
    try:
        module = import_probe(IMPORT_NAME)
    except Exception as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:qfluentwidgets_unavailable",
            "package_name": PACKAGE_NAME,
            "import_name": IMPORT_NAME,
            "import_status": "missing",
            "message": "QFluentWidgets is required for the Project MOE GUI Fluent visual shell and must fail closed when missing.",
            "error": str(exc),
            "dependency": dependency,
            "license_manifest": license_manifest,
            "blockers": [
                {
                    "code": "blocked:qfluentwidgets_unavailable",
                    "message": "Install PySide6-Fluent-Widgets in the shared PySide6 runtime before launching the Fluent GUI shell.",
                }
            ],
        }

    metadata: dict[str, Any] = {}
    metadata_status = "metadata_unavailable"
    try:
        metadata = dict(metadata_probe(PACKAGE_NAME) or {})
        metadata_status = "metadata_ok"
    except Exception as exc:
        metadata = {"error": str(exc)}
    installed_version = metadata.get("version") or getattr(module, "__version__", None)
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "token": "ok",
        "package_name": PACKAGE_NAME,
        "import_name": IMPORT_NAME,
        "import_status": "import_ok",
        "metadata_status": metadata_status,
        "installed_version": installed_version,
        "reported_license": metadata.get("license"),
        "dependency": dependency,
        "license_manifest": license_manifest,
        "blockers": [],
    }
