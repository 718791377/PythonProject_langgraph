from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
DEFAULT_RUNTIME_PYTHON = Path(r"D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe")
DEFAULT_SECTIONS = ["overview", "sessions", "workbench", "diagnostics", "settings"]
DEFAULT_VISUAL_SIZES = ((1180, 720), (1366, 768), (1440, 900))
FIXTURE_PROFILES = ("default", "long-content", "dense-sessions")
SECTION_REQUIRED_TEXT = {
    "overview": ["Project MOE", "Project default", "Enable project default", "Disable project default"],
    "sessions": [
        "Sessions",
        "Session list",
        "Session details",
        "Session:",
        "Created:",
        "Updated:",
        "Directory:",
        "Branch:",
        "Conversation:",
        "MOE status and actions",
        "Session MOE lenses",
        "MOE categories and lenses",
        "Strict Graduate Advisor Module",
        "Socratic Questioning Module",
        "Five Classic Thinking Models Module",
        "Enable session MOE",
        "Disable session MOE",
        "Apply session lenses",
        "Clear session lenses",
    ],
    "workbench": ["Expert Workbench", "Expert lenses", "Handoff target", "Copy handoff package"],
    "diagnostics": ["Diagnostics"],
    "settings": ["Settings", "Close behavior", "Loading state", "Empty state", "Error state", "Help"],
}
WINDOWS_FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\msyhbd.ttc"),
    Path(r"C:\Windows\Fonts\segoeui.ttf"),
    Path(r"C:\Windows\Fonts\arial.ttf"),
    Path(r"C:\Windows\Fonts\tahoma.ttf"),
]
PREFERRED_FONT_FAMILIES = ["Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", "Arial", "Tahoma"]


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def inside(self, other: "Rect", tolerance: float = 1.5) -> bool:
        return (
            self.x >= other.x - tolerance
            and self.y >= other.y - tolerance
            and self.right <= other.right + tolerance
            and self.bottom <= other.bottom + tolerance
        )

    def intersects(self, other: "Rect", tolerance: float = 0.0) -> bool:
        return not (
            self.right < other.x - tolerance
            or self.bottom < other.y - tolerance
            or self.x > other.right + tolerance
            or self.y > other.bottom + tolerance
        )

    def as_dict(self) -> dict[str, float]:
        return {"x": round(self.x, 2), "y": round(self.y, 2), "w": round(self.w, 2), "h": round(self.h, 2)}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def toolchain_root() -> Path:
    return Path(__file__).resolve().parent


def parse_size(value: str) -> tuple[int, int]:
    if "x" not in value.lower():
        raise argparse.ArgumentTypeError("size must be WIDTHxHEIGHT")
    left, right = value.lower().split("x", 1)
    try:
        width = int(left)
        height = int(right)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("size must use integer WIDTHxHEIGHT") from exc
    if width < 320 or height < 240:
        raise argparse.ArgumentTypeError("size is too small for Project MOE GUI validation")
    return width, height


def normalized_sizes(args: argparse.Namespace) -> tuple[tuple[int, int], ...]:
    values = getattr(args, "sizes", None)
    if not values:
        return DEFAULT_VISUAL_SIZES
    return tuple((int(width), int(height)) for width, height in values)


def _copy_jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _fixture_session_display_block(row: dict[str, Any]) -> dict[str, Any]:
    conversation = row.get("conversation") if isinstance(row.get("conversation"), dict) else {}
    title = str(conversation.get("title") or row.get("conversation_title") or "")
    preview = str(conversation.get("preview") or row.get("conversation_preview") or "")
    conversation_text = preview or title
    if title and preview and title != preview:
        conversation_text = f"{title}\n{preview}"
    fields = {
        "Session": str(row.get("visible_session_id") or row.get("full_session_id") or row.get("session_id") or row.get("display_id") or ""),
        "Created": str(row.get("created_display") or row.get("created_at") or ""),
        "Updated": str(row.get("updated_display") or row.get("updated_at") or row.get("last_seen_at") or ""),
        "Directory": str(row.get("directory") or ""),
        "Branch": str(row.get("branch") or "unknown"),
        "Conversation": conversation_text,
    }
    labels = ["Session", "Created", "Updated", "Directory", "Branch", "Conversation"]
    lines = [f"{label}: {fields[label]}" for label in labels]
    return {"schema_version": SCHEMA_VERSION, "labels": labels, "fields": fields, "lines": lines, "text": "\n".join(lines)}


def _fixture_session(index: int, *, long_content: bool = False) -> dict[str, Any]:
    suffix = f"{index:02d}"
    session_id = f"session-fixture-{suffix}-abcdef1234567890"
    label = "enabled" if index % 2 == 0 else "disabled"
    if long_content:
        display_id = "session-fixture-with-extra-long-display-name-for-visual-overflow-regression-" + suffix
        lens_summary = "lenses=" + ", ".join([f"very_long_lens_identifier_{item}_{suffix}" for item in range(4)])
        directory = "D:/target/projects/project-moe-gui-visual-regression-with-a-very-long-session-directory-name/" + suffix
        conversation_title = "Long session title used to verify wrapping and eliding in the Sessions card " + suffix
        conversation_preview = "Conversation preview stays inside the card while preserving the required Conversation label for visual checks. " + ("detail " * 18) + suffix
    else:
        display_id = f"session-fixture-{suffix}"
        lens_summary = "All lenses" if index % 3 else "lenses=blind_review,aigc_risk"
        directory = "D:/target/project-moe-gui-dense-fixture"
        conversation_title = f"Fixture task brief {suffix}"
        conversation_preview = f"Fixture conversation preview {suffix}"
    row = {
        "row_index": index,
        "valid": index % 7 != 0,
        "token": "ok" if index % 7 != 0 else "invalid_json",
        "message": "ok" if index % 7 != 0 else "Invalid fixture session record for visual gate.",
        "session_id": session_id,
        "display_id": display_id,
        "visible_session_id": session_id,
        "full_session_id": session_id,
        "created_at": f"2026-06-06T{index % 24:02d}:00:00+00:00",
        "created_display": f"2026-06-06 {index % 24:02d}:00:00",
        "created_relative": f"{index + 1}d ago",
        "updated_at": f"2026-06-07T{index % 24:02d}:00:00+00:00",
        "updated_display": f"2026-06-07 {index % 24:02d}:00:00",
        "updated_relative": f"{index + 2}h ago",
        "directory": directory,
        "branch": "main",
        "conversation": {"title": conversation_title, "preview": conversation_preview, "message_counts": {"user": 1, "assistant": 1}},
        "conversation_title": conversation_title,
        "conversation_preview": conversation_preview,
        "enabled": index % 2 == 0,
        "label": label,
        "source": "manual-session" if index % 2 == 0 else "project-propagated",
        "selected_lenses": [] if index % 3 else ["blind_review", "aigc_risk"],
        "selected_categories": [] if index % 4 else ["strict_graduate_advisor"],
        "effective_lens_mode": "all" if index % 3 else "selected",
        "lens_selection_scope": "session",
        "lens_selection_summary": lens_summary,
        "last_seen_at": f"2026-06-07T{index % 24:02d}:00:00+00:00",
        "actions": {},
        "status_badge": {
            "text": label,
            "token_text": "ok" if index % 7 != 0 else "invalid_json",
            "lens_text": lens_summary,
            "high_contrast_text": f"Session {display_id}: {label}; lenses: {lens_summary}",
        },
    }
    row["session_display_block"] = _fixture_session_display_block(row)
    row["session_display_lines"] = row["session_display_block"]["lines"]
    return row


def _fixture_lens(index: int, *, long_content: bool = False) -> dict[str, Any]:
    default_ids = [
        "blind_review",
        "advisor_interrogation",
        "aigc_risk",
        "novelty",
        "literature_evidence",
        "structure_expression",
        "socratic_cbt",
        "feynman_learning",
        "first_principles",
        "pyramid_principle",
        "swot_analysis",
        "decision_tree",
    ]
    lens_id = default_ids[index] if index < len(default_ids) else f"fixture_lens_{index:02d}"
    if long_content:
        label = "Extremely long Project MOE expert lens label for visual regression and wrapping behavior " + str(index).zfill(2)
        description = "Long fixture lens description used to stress card, checkbox, and handoff preview rendering without reading private prompts."
    else:
        label = f"Fixture lens {index:02d}"
        description = "Fixture lens for visual render gate."
    zh_label = {
        "blind_review": "盲审专家镜头",
        "advisor_interrogation": "严苛导师追问镜头",
        "aigc_risk": "AIGC / AI 味风险镜头",
        "novelty": "创新性与差异化镜头",
        "literature_evidence": "文献与证据链镜头",
        "structure_expression": "结构与表达镜头",
        "socratic_cbt": "认知行为式苏格拉底提问镜头",
        "feynman_learning": "费曼学习法专家",
        "first_principles": "第一性原理专家",
        "pyramid_principle": "金字塔原理专家",
        "swot_analysis": "SWOT 分析专家",
        "decision_tree": "决策树模型专家",
    }.get(lens_id, label)
    return {"id": lens_id, "label": label, "zh_label": zh_label, "en_label": label, "description": description, "category": f"category_{index % 8:02d}"}


def _fixture_category(index: int, lens_count: int, *, long_content: bool = False) -> dict[str, Any]:
    governed = [
        (
            "strict_graduate_advisor",
            "Strict Graduate Advisor Module",
            "严苛的研究生导师专家模块",
            ["blind_review", "advisor_interrogation", "aigc_risk", "novelty", "literature_evidence", "structure_expression"],
        ),
        (
            "socratic_questioning",
            "Socratic Questioning Module",
            "认知行为式提问专家模块",
            ["socratic_cbt"],
        ),
        (
            "five_classic_thinking_models",
            "Five Classic Thinking Models Module",
            "五大经典思维模型专家模块",
            ["feynman_learning", "first_principles", "pyramid_principle", "swot_analysis", "decision_tree"],
        ),
    ]
    if index < len(governed):
        category_id, label, zh_label, lens_ids = governed[index]
        return {"id": category_id, "label": label, "zh_label": zh_label, "en_label": label, "description": "Fixture governed category for visual render gate.", "lens_ids": [item for item in lens_ids if item]}
    category_id = f"category_{index:02d}"
    label = ("Very long Project MOE expert category label for dense visual regression " + str(index).zfill(2)) if long_content else f"Category {index:02d}"
    description = "Long category description used by the visual fixture profile." if long_content else "Fixture category for visual render gate."
    lens_ids = [f"fixture_lens_{item:02d}" for item in range(index, lens_count, max(1, min(8, lens_count)))]
    return {"id": category_id, "label": label, "zh_label": label, "en_label": label, "description": description, "lens_ids": lens_ids}


def build_fixture_view_model(profile: str, view_model: dict[str, Any]) -> dict[str, Any]:
    if profile not in FIXTURE_PROFILES:
        raise ValueError(f"unsupported fixture profile: {profile}")
    model = _copy_jsonable(view_model if isinstance(view_model, dict) else {})
    model["fixture_profile"] = profile
    if profile == "default":
        return model

    long_content = profile == "long-content"
    session_count = 8 if long_content else 24
    lens_count = 10 if long_content else 18
    category_count = 5 if long_content else 8
    sessions = [_fixture_session(index, long_content=long_content) for index in range(session_count)]
    lenses = [_fixture_lens(index, long_content=long_content) for index in range(lens_count)]
    categories = [_fixture_category(index, lens_count, long_content=long_content) for index in range(category_count)]

    banner = dict(model.get("top_banner") or {})
    if long_content:
        banner["project_root"] = "D:/target/projects/project-moe-gui-visual-regression-with-a-very-long-project-root-name/" + (banner.get("project_root") or "fixture")
        banner["agent_name"] = "project-moe-agent-with-a-very-long-human-readable-agent-name-for-layout-checks"
        banner["state_namespace"] = "project_moe_visual_regression_namespace_with_long_name"
    else:
        banner.setdefault("project_root", "D:/target/project-moe-gui-dense-fixture")
        banner.setdefault("agent_name", "project-moe-agent")
        banner.setdefault("state_namespace", "project_moe")
    model["top_banner"] = banner

    session_table = dict(model.get("session_table") or {})
    session_table.update({
        "token": "ok",
        "rows": sessions,
        "empty_state": {"is_empty": False, "message": ""},
        "invalid_count": sum(1 for row in sessions if row.get("token") != "ok"),
        "fixture_profile": profile,
    })
    model["session_table"] = session_table

    lens_catalog = dict(model.get("lens_catalog") or {})
    lens_catalog.update({
        "schema_version": SCHEMA_VERSION,
        "token": "ok",
        "source": f"visual-fixture:{profile}",
        "lenses": lenses,
        "categories": categories,
        "selection_semantics": {"empty_selection": "all", "scope": "session", "mode_field": "effective_lens_mode"},
        "private_prompt_source_read": False,
    })
    model["lens_catalog"] = lens_catalog

    panel = dict(model.get("session_lens_panel") or {})
    panel.update({"lenses": lenses, "categories": categories, "selected_row_index": 0, "empty_selection_means": "all"})
    model["session_lens_panel"] = panel

    workbench = dict(model.get("expert_workbench") or {})
    workbench.setdefault("title", "Expert Workbench v2")
    workbench.setdefault("subtitle", "Fixture profile for visual render validation.")
    workbench["lenses"] = lenses
    workbench["categories"] = categories
    workbench.setdefault("handoff_targets", [
        {"id": "main-session", "label": "Main session", "description": "Fixture target."},
        {"id": "subagent", "label": "Subagent", "description": "Fixture target."},
        {"id": "durable-team", "label": "Durable team", "description": "Fixture target."},
        {"id": "langgraph-workflow", "label": "LangGraph workflow", "description": "Fixture target."},
    ])
    workbench.setdefault("task_templates", [
        {"id": "fixture_review", "label": "Fixture review brief", "objective": "Exercise long visual content.", "prompt": "Return fixture findings."}
    ])
    model["expert_workbench"] = workbench

    cards = list(model.get("status_cards") or [])
    if not cards:
        cards = [
            {"id": "project-default", "title": "Project default", "value": "disabled", "token": "ok"},
            {"id": "effective-status", "title": "Effective status", "value": "disabled", "token": "ok"},
            {"id": "session-count", "title": "Sessions", "value": str(session_count), "token": "ok"},
            {"id": "runtime", "title": "GUI runtime", "value": "import_ok", "token": "ok"},
        ]
    model["status_cards"] = cards
    model.setdefault("project_default_card", {"label": "disabled", "effective_label": "disabled"})
    model.setdefault("banners", [])
    return model


def parse_json_from_output(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty preflight output")
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("preflight output must be a JSON object")
    return payload


def run_target_preflight(target_project: Path, timeout_seconds: int) -> dict[str, Any]:
    launcher = target_project / "project-moe-gui.cmd"
    if not launcher.exists():
        raise FileNotFoundError(f"target launcher is missing: {launcher}")
    comspec = os.environ.get("ComSpec") or str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe")
    result = subprocess.run(
        [comspec, "/d", "/c", str(launcher), "--preflight", "--json"],
        cwd=str(target_project),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        check=False,
    )
    payload = parse_json_from_output(result.stdout)
    payload.setdefault("preflight_process", {})
    payload["preflight_process"].update(
        {
            "returncode": result.returncode,
            "stderr_tail": result.stderr[-1200:],
            "command": [str(launcher), "--preflight", "--json"],
        }
    )
    return payload


def load_view_model(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    if args.view_model_json:
        payload = json.loads(Path(args.view_model_json).read_text(encoding="utf-8-sig"))
        if "view_model" in payload and isinstance(payload["view_model"], dict):
            return payload["view_model"], payload
        if isinstance(payload, dict):
            return payload, {"schema_version": SCHEMA_VERSION, "ok": True, "token": "ok", "view_model": payload}
        raise ValueError("view-model JSON must be an object")
    if not args.target_project:
        raise ValueError("--target-project or --view-model-json is required")
    preflight = run_target_preflight(Path(args.target_project), args.preflight_timeout_seconds)
    view_model = preflight.get("view_model")
    if not isinstance(view_model, dict):
        raise ValueError("target preflight did not return view_model")
    return view_model, preflight


def resolve_qml_path(args: argparse.Namespace, view_model: dict[str, Any]) -> tuple[Path, str]:
    if args.qml_path:
        return Path(args.qml_path).resolve(strict=False), "explicit"
    source = args.qml_source
    if source == "source":
        source = "current-worktree"
    if source == "current-worktree":
        return (toolchain_root() / "src" / "project_moe_gui" / "qml" / "ProjectMoeGui.qml").resolve(strict=False), source
    if source == "target-project":
        if not args.target_project:
            raise ValueError("--qml-source target-project requires --target-project")
        return (Path(args.target_project) / "tools" / "project_moe_gui" / "qml" / "ProjectMoeGui.qml").resolve(strict=False), source
    if source == "central-toolchain":
        return (Path(r"D:\PythonProject_langgraph\tools\project_moe_gui_toolchain\src\project_moe_gui\qml\ProjectMoeGui.qml")).resolve(strict=False), source
    visual = view_model.get("visual") if isinstance(view_model, dict) else None
    status = visual.get("qml_source_status") if isinstance(visual, dict) else None
    configured = status.get("path") if isinstance(status, dict) else None
    if configured and Path(str(configured)).exists():
        return Path(str(configured)).resolve(strict=False), "view-model"
    if args.target_project:
        target_qml = Path(args.target_project) / "tools" / "project_moe_gui" / "qml" / "ProjectMoeGui.qml"
        if target_qml.exists():
            return target_qml.resolve(strict=False), "target-project"
    return (toolchain_root() / "src" / "project_moe_gui" / "qml" / "ProjectMoeGui.qml").resolve(strict=False), "current-worktree"


def maybe_reexec_under_runtime(args: argparse.Namespace) -> None:
    if args.no_runtime_reexec:
        return
    runtime = Path(args.runtime_python).resolve(strict=False) if args.runtime_python else DEFAULT_RUNTIME_PYTHON
    if not runtime.exists():
        return
    current = Path(sys.executable).resolve(strict=False)
    if current == runtime.resolve(strict=False):
        return
    env = dict(os.environ)
    env["PROJECT_MOE_GUI_VISUAL_CHECK_REEXEC"] = "1"
    result = subprocess.run([str(runtime), *sys.argv], env=env, text=True, encoding="utf-8", errors="replace")
    raise SystemExit(result.returncode)


def _bool_prop(obj: Any, name: str, default: bool = False) -> bool:
    try:
        value = obj.property(name)
    except Exception:
        return default
    if value is None:
        return default
    return bool(value)


def _float_prop(obj: Any, name: str, default: float = 0.0) -> float:
    try:
        value = obj.property(name)
    except Exception:
        return default
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int_prop(obj: Any, name: str, default: int = 0) -> int:
    try:
        value = obj.property(name)
    except Exception:
        return default
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(value.value)  # enum-like value
        except Exception:
            return default


def _text_prop(obj: Any) -> str:
    try:
        value = obj.property("text")
    except Exception:
        return ""
    if value is None:
        return ""
    return str(value)


def _class_name(obj: Any) -> str:
    try:
        return str(obj.metaObject().className())
    except Exception:
        return type(obj).__name__


def _is_scroll_class(class_name: str) -> bool:
    lowered = class_name.lower()
    return "flickable" in lowered or "scrollview" in lowered or "scrollbar" in lowered


def _is_text_area_class(class_name: str) -> bool:
    return "textarea" in class_name.lower()


def _is_user_visible_class(class_name: str) -> bool:
    lowered = class_name.lower()
    return any(token in lowered for token in ["text", "label", "button", "checkbox", "combobox", "textarea", "textfield"])


def _item_rect(obj: Any, origin_x: float, origin_y: float) -> Rect | None:
    width = _float_prop(obj, "width", -1.0)
    height = _float_prop(obj, "height", -1.0)
    if width < 0 or height < 0:
        return None
    x = origin_x + _float_prop(obj, "x", 0.0)
    y = origin_y + _float_prop(obj, "y", 0.0)
    return Rect(x, y, width, height)


def collect_visible_items(root: Any, window_rect: Rect) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    def walk(obj: Any, origin_x: float, origin_y: float, effective_visible: bool, clip_rect: Rect, scroll_depth: int, path: str) -> None:
        class_name = _class_name(obj)
        own_visible = _bool_prop(obj, "visible", True)
        visible = effective_visible and own_visible
        rect = _item_rect(obj, origin_x, origin_y)
        if rect is None:
            rect = Rect(origin_x, origin_y, 0.0, 0.0)
        is_scroll = _is_scroll_class(class_name)
        next_scroll_depth = scroll_depth + (1 if is_scroll else 0)
        object_name = ""
        try:
            object_name = str(obj.objectName() or "")
        except Exception:
            object_name = ""
        text = _text_prop(obj)
        item_path = f"{path}/{class_name}{('#' + object_name) if object_name else ''}"
        if visible and rect.w > 0 and rect.h > 0:
            user_visible = bool(text) or _is_user_visible_class(class_name)
            text_item: dict[str, Any] | None = None
            if text:
                content_width = _float_prop(obj, "contentWidth", _float_prop(obj, "paintedWidth", 0.0))
                content_height = _float_prop(obj, "contentHeight", _float_prop(obj, "paintedHeight", 0.0))
                wrap_mode = _int_prop(obj, "wrapMode", 0)
                elide = _int_prop(obj, "elide", 0)
                clipped_by_clip = not rect.inside(clip_rect, tolerance=1.5)
                clipped_by_window = not rect.intersects(window_rect, tolerance=0.0)
                text_item = {
                    "class": class_name,
                    "path": item_path,
                    "text": text,
                    "rect": rect.as_dict(),
                    "clip_rect": clip_rect.as_dict(),
                    "content_width": round(content_width, 2),
                    "content_height": round(content_height, 2),
                    "wrap_mode": wrap_mode,
                    "elide": elide,
                    "scroll_depth": next_scroll_depth,
                    "clipped_by_clip": clipped_by_clip,
                    "clipped_by_window": clipped_by_window,
                }
                items.append(text_item)
                if content_width > rect.w + 2 and wrap_mode == 0 and elide == 0 and next_scroll_depth == 0:
                    violations.append({"kind": "text_width_overflow", **text_item})
                if content_height > rect.h + 2 and next_scroll_depth == 0 and not _is_text_area_class(class_name):
                    violations.append({"kind": "text_height_overflow", **text_item})
            if user_visible and next_scroll_depth == 0 and not rect.inside(clip_rect, tolerance=2.0):
                violations.append(
                    {
                        "kind": "visible_item_outside_clip",
                        "class": class_name,
                        "path": item_path,
                        "text": text[:160],
                        "rect": rect.as_dict(),
                        "clip_rect": clip_rect.as_dict(),
                    }
                )
        next_clip = clip_rect
        if visible and rect.w > 0 and rect.h > 0 and _bool_prop(obj, "clip", False) and not is_scroll:
            next_clip = rect
        child_origin_x = rect.x
        child_origin_y = rect.y
        try:
            children = list(obj.children())
        except Exception:
            children = []
        for index, child in enumerate(children):
            walk(child, child_origin_x, child_origin_y, visible, next_clip, next_scroll_depth, f"{item_path}[{index}]")

    walk(root, 0.0, 0.0, True, window_rect, 0, "root")
    return items, violations


def image_stats(image: Any) -> dict[str, Any]:
    width = int(image.width())
    height = int(image.height())
    colors: set[tuple[int, int, int, int]] = set()
    min_luma = 255.0
    max_luma = 0.0
    sample_count = 0
    step_x = max(1, width // 96)
    step_y = max(1, height // 72)
    for y in range(0, height, step_y):
        for x in range(0, width, step_x):
            color = image.pixelColor(x, y)
            rgba = (int(color.red()), int(color.green()), int(color.blue()), int(color.alpha()))
            colors.add(rgba)
            luma = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
            min_luma = min(min_luma, luma)
            max_luma = max(max_luma, luma)
            sample_count += 1
    return {
        "width": width,
        "height": height,
        "sample_count": sample_count,
        "unique_sample_colors": len(colors),
        "min_luma": round(min_luma, 2),
        "max_luma": round(max_luma, 2),
        "luma_range": round(max_luma - min_luma, 2),
        "non_blank": len(colors) >= 8 and (max_luma - min_luma) >= 8,
    }


def visible_required_texts(items: list[dict[str, Any]], required: Iterable[str]) -> tuple[list[str], dict[str, dict[str, Any]]]:
    found: dict[str, dict[str, Any]] = {}
    for needle in required:
        for item in items:
            text = item.get("text", "")
            if needle in text and not item.get("clipped_by_clip") and not item.get("clipped_by_window"):
                found[needle] = item
                break
    missing = [needle for needle in required if needle not in found]
    return missing, found


def collect_widget_visible_items(root: Any, window_rect: Rect) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    def walk(widget: Any, clip_rect: Rect, path: str, scroll_depth: int = 0) -> None:
        try:
            visible = bool(widget.isVisible())
        except Exception:
            visible = True
        try:
            geom = widget.geometry()
            top_left = widget.mapTo(root, widget.rect().topLeft())
            rect = Rect(float(top_left.x()), float(top_left.y()), float(geom.width()), float(geom.height()))
        except Exception:
            rect = Rect(0.0, 0.0, 0.0, 0.0)
        class_name = type(widget).__name__
        next_scroll_depth = scroll_depth + (1 if "ScrollArea" in class_name or "ScrollBar" in class_name else 0)
        object_name = ""
        try:
            object_name = str(widget.objectName() or "")
        except Exception:
            object_name = ""
        widget_path = f"{path}/{class_name}{('#' + object_name) if object_name else ''}"
        text = ""
        try:
            if hasattr(widget, "text"):
                text = str(widget.text() or "")
            elif hasattr(widget, "placeholderText"):
                text = str(widget.placeholderText() or "")
        except Exception:
            text = ""
        if visible and rect.w > 0 and rect.h > 0:
            user_visible = bool(text) or class_name in {"QPushButton", "QCheckBox", "QComboBox", "QLineEdit", "QTextEdit", "QListWidget", "QLabel"}
            if text:
                text_width: float | None = None
                try:
                    text_width = float(widget.fontMetrics().horizontalAdvance(text))
                except Exception:
                    text_width = None
                available_text_width = rect.w
                if class_name == "QCheckBox":
                    available_text_width = max(0.0, rect.w - 30.0)
                elif class_name == "QPushButton":
                    available_text_width = max(0.0, rect.w - 24.0)
                item = {
                    "class": class_name,
                    "path": widget_path,
                    "text": text,
                    "rect": rect.as_dict(),
                    "clip_rect": clip_rect.as_dict(),
                    "content_width": round(text_width, 2) if text_width is not None else None,
                    "content_height": None,
                    "wrap_mode": None,
                    "elide": None,
                    "scroll_depth": next_scroll_depth,
                    "clipped_by_clip": not rect.inside(clip_rect, tolerance=2.0),
                    "clipped_by_window": not rect.intersects(window_rect, tolerance=0.0),
                }
                items.append(item)
                if (
                    text_width is not None
                    and class_name in {"QLabel", "QCheckBox", "QPushButton"}
                    and text_width > available_text_width + 4.0
                ):
                    violations.append(
                        {
                            "kind": "widget_text_width_overflow",
                            **item,
                            "available_text_width": round(available_text_width, 2),
                        }
                    )
            if user_visible and next_scroll_depth == 0 and not rect.inside(clip_rect, tolerance=2.0):
                violations.append(
                    {
                        "kind": "widget_outside_clip",
                        "class": class_name,
                        "path": widget_path,
                        "text": text[:160],
                        "rect": rect.as_dict(),
                        "clip_rect": clip_rect.as_dict(),
                    }
                )
        try:
            children = widget.children()
        except Exception:
            children = []
        direct_children = []
        for child in children:
            try:
                if hasattr(child, "geometry"):
                    direct_children.append(child)
            except Exception:
                continue
        for index, child in enumerate(direct_children):
            child_clip = clip_rect
            if "ScrollArea" in class_name and rect.w > 0 and rect.h > 0:
                child_clip = rect
            walk(child, child_clip, f"{widget_path}[{index}]", next_scroll_depth)

    walk(root, window_rect, "root")
    return items, violations


def install_fonts(app: Any) -> dict[str, Any]:
    from PySide6.QtGui import QFont, QFontDatabase

    loaded_files: list[str] = []
    failed_files: list[str] = []
    for candidate in WINDOWS_FONT_CANDIDATES:
        if not candidate.exists():
            continue
        font_id = QFontDatabase.addApplicationFont(str(candidate))
        if font_id >= 0:
            loaded_files.append(str(candidate))
        else:
            failed_files.append(str(candidate))
    families = set(QFontDatabase.families())
    selected = None
    for family in PREFERRED_FONT_FAMILIES:
        if family in families:
            app.setFont(QFont(family, 10))
            selected = family
            break
    return {
        "loaded_files": loaded_files,
        "failed_files": failed_files,
        "selected_family": selected,
        "family_count": len(families),
        "ok": bool(loaded_files) or bool(selected),
    }


def run_visual_check(args: argparse.Namespace) -> dict[str, Any]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_QUICK_BACKEND", "software")
    os.environ.setdefault("QSG_RHI_BACKEND", "software")
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.path.insert(0, str(toolchain_root() / "src"))

    from PySide6.QtCore import QObject, QUrl, Slot, qInstallMessageHandler
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuickControls2 import QQuickStyle

    view_model, preflight = load_view_model(args)
    view_model = build_fixture_view_model(args.fixture_profile, view_model)
    qml_path, qml_source = resolve_qml_path(args, view_model)
    if not qml_path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:qml_shell_source_missing",
            "message": "QML source file is missing.",
            "qml_path": str(qml_path),
            "qml_source": qml_source,
        }

    class Bridge(QObject):
        @Slot(result=str)
        def refreshViewModel(self) -> str:
            return json.dumps({"schema_version": SCHEMA_VERSION, "ok": True, "token": "ok", "message": "visual render check refresh", "view_model": view_model}, ensure_ascii=False)

        @Slot(str, str, str, str, result=str)
        def executeWriteAction(self, action: str, session_id: str, lenses_json: str, categories_json: str) -> str:
            return json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "ok": True,
                    "token": "ok",
                    "message": f"visual render check skipped write action {action}",
                    "view_model": view_model,
                    "session_id": session_id,
                    "selected_lenses": lenses_json,
                    "selected_categories": categories_json,
                },
                ensure_ascii=False,
            )

        @Slot(str, str, str, str, str, str, str, result=str)
        def saveHandoffDraft(
            self,
            session_id: str,
            session_display_id: str,
            selected_lenses_json: str,
            selected_categories_json: str,
            handoff_target: str,
            task_template_id: str,
            brief_text: str,
        ) -> str:
            return json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "ok": True,
                    "token": "ok",
                    "message": "visual render check skipped Workbench draft save",
                    "session_id": session_id,
                    "session_display_id": session_display_id,
                    "selected_lenses": selected_lenses_json,
                    "selected_categories": selected_categories_json,
                    "handoff_target": handoff_target,
                    "task_template_id": task_template_id,
                    "brief_text": brief_text,
                    "executes_carrier": False,
                },
                ensure_ascii=False,
            )

        @Slot(str, str, str, str, str, str, str, result=str)
        def exportHandoffPackage(
            self,
            session_id: str,
            session_display_id: str,
            selected_lenses_json: str,
            selected_categories_json: str,
            handoff_target: str,
            task_template_id: str,
            brief_text: str,
        ) -> str:
            return json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "ok": True,
                    "token": "ok",
                    "message": "visual render check skipped Workbench handoff export",
                    "export_text": "Project MOE visual render handoff export placeholder",
                    "session_id": session_id,
                    "session_display_id": session_display_id,
                    "selected_lenses": selected_lenses_json,
                    "selected_categories": selected_categories_json,
                    "handoff_target": handoff_target,
                    "task_template_id": task_template_id,
                    "brief_text": brief_text,
                    "executes_carrier": False,
                },
                ensure_ascii=False,
            )

    qt_messages: list[dict[str, Any]] = []

    def message_handler(mode: Any, context: Any, message: str) -> None:  # pragma: no cover - Qt callback
        qt_messages.append({"mode": str(mode), "file": str(getattr(context, "file", "") or ""), "line": int(getattr(context, "line", 0) or 0), "message": str(message)})

    qInstallMessageHandler(message_handler)
    app = QGuiApplication.instance() or QGuiApplication(["project-moe-gui-visual-render-check"])
    font_report = install_fonts(app)
    QQuickStyle.setStyle("Material")
    engine = QQmlApplicationEngine()
    qml_warnings: list[str] = []
    engine.warnings.connect(lambda warnings: qml_warnings.extend([warning.toString() for warning in warnings]))
    engine.rootContext().setContextProperty("viewModelJson", json.dumps(view_model, ensure_ascii=False))
    engine.rootContext().setContextProperty("projectMoeBridge", Bridge())
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    roots = engine.rootObjects()
    if not roots:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:qml_shell_load_failed",
            "qml_path": str(qml_path),
            "qml_warnings": qml_warnings,
            "qt_messages": qt_messages,
        }
    root = roots[0]
    output_dir = Path(args.output_dir).resolve(strict=False)
    output_dir.mkdir(parents=True, exist_ok=True)

    page_reports: list[dict[str, Any]] = []
    for width, height in args.sizes:
        try:
            root.setWidth(width)
            root.setHeight(height)
        except Exception:
            pass
        root.show()
        for section in args.sections:
            root.setProperty("selectedSection", section)
            for _ in range(args.settle_iterations):
                app.processEvents()
                time.sleep(args.settle_sleep_seconds)
            image = root.grabWindow()
            screenshot = output_dir / f"{section}_{width}x{height}.png"
            image.save(str(screenshot))
            window_rect = Rect(0.0, 0.0, float(width), float(height))
            items, violations = collect_visible_items(root, window_rect)
            required = SECTION_REQUIRED_TEXT.get(section, [])
            missing, found = visible_required_texts(items, required)
            stats = image_stats(image)
            page_ok = bool(stats["non_blank"]) and not missing and not violations
            page_reports.append(
                {
                    "section": section,
                    "width": width,
                    "height": height,
                    "ok": page_ok,
                    "screenshot": str(screenshot),
                    "image_stats": stats,
                    "required_text": {"required": required, "missing": missing, "found": {key: value["rect"] for key, value in found.items()}},
                    "visible_text_count": len(items),
                    "violations": violations[:120],
                }
            )
    suspicious_messages = [
        item for item in qt_messages if any(token in item.get("message", "") for token in ["ReferenceError", "TypeError", "Cannot assign", "Unable to", "failed", "Failed"])
    ]
    ok = all(page["ok"] for page in page_reports) and not qml_warnings and not suspicious_messages and font_report["ok"]
    token = "ok" if ok else "blocked:visual_render_check_failed"
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": ok,
        "token": token,
        "message": "Project MOE GUI visual render check passed." if ok else "Project MOE GUI visual render check found render, visibility, or overflow issues.",
        "toolchain": "project_moe_gui_visual_render_check",
        "qml_path": str(qml_path),
        "qml_source": qml_source,
        "target_project": str(args.target_project) if args.target_project else None,
        "sections": args.sections,
        "sizes": [f"{width}x{height}" for width, height in args.sizes],
        "output_dir": str(output_dir),
        "font_report": font_report,
        "qml_warnings": qml_warnings,
        "qt_suspicious_messages": suspicious_messages,
        "preflight_token": preflight.get("token"),
        "preflight_ok": preflight.get("ok"),
        "pages": page_reports,
    }


def run_widget_visual_check(args: argparse.Namespace) -> dict[str, Any]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.path.insert(0, str(toolchain_root() / "src"))

    from PySide6.QtCore import qInstallMessageHandler
    from project_moe_gui.gui_shell import create_product_widget_window

    view_model, preflight = load_view_model(args)
    view_model = build_fixture_view_model(args.fixture_profile, view_model)
    qt_messages: list[dict[str, Any]] = []

    def message_handler(mode: Any, context: Any, message: str) -> None:  # pragma: no cover - Qt callback
        qt_messages.append({"mode": str(mode), "file": str(getattr(context, "file", "") or ""), "line": int(getattr(context, "line", 0) or 0), "message": str(message)})

    qInstallMessageHandler(message_handler)
    app, window = create_product_widget_window(view_model, config={}, project_root=args.target_project)
    font_report = install_fonts(app)
    output_dir = Path(args.output_dir).resolve(strict=False)
    output_dir.mkdir(parents=True, exist_ok=True)
    page_reports: list[dict[str, Any]] = []
    for width, height in args.sizes:
        window.resize(width, height)
        window.show()
        for section in args.sections:
            if hasattr(window, "set_selected_section"):
                window.set_selected_section(section)
            for _ in range(args.settle_iterations):
                app.processEvents()
                time.sleep(args.settle_sleep_seconds)
            image = window.grab().toImage()
            screenshot = output_dir / f"{section}_{width}x{height}.png"
            image.save(str(screenshot))
            window_rect = Rect(0.0, 0.0, float(width), float(height))
            items, violations = collect_widget_visible_items(window, window_rect)
            required = SECTION_REQUIRED_TEXT.get(section, [])
            missing, found = visible_required_texts(items, required)
            stats = image_stats(image)
            page_ok = bool(stats["non_blank"]) and not missing and not violations
            page_reports.append(
                {
                    "section": section,
                    "width": width,
                    "height": height,
                    "ok": page_ok,
                    "screenshot": str(screenshot),
                    "image_stats": stats,
                    "required_text": {"required": required, "missing": missing, "found": {key: value["rect"] for key, value in found.items()}},
                    "visible_text_count": len(items),
                    "violations": violations[:120],
                }
            )
    suspicious_messages = [
        item for item in qt_messages if any(token in item.get("message", "") for token in ["ReferenceError", "TypeError", "Cannot assign", "Unable to", "failed", "Failed"])
    ]
    window.hide()
    ok = all(page["ok"] for page in page_reports) and not suspicious_messages and font_report["ok"]
    token = "ok" if ok else "blocked:visual_render_check_failed"
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": ok,
        "token": token,
        "message": "Project MOE GUI widget visual render check passed." if ok else "Project MOE GUI widget visual render check found render, visibility, or overflow issues.",
        "toolchain": "project_moe_gui_visual_render_check",
        "shell": "widgets",
        "target_project": str(args.target_project) if args.target_project else None,
        "sections": args.sections,
        "sizes": [f"{width}x{height}" for width, height in args.sizes],
        "output_dir": str(output_dir),
        "font_report": font_report,
        "qt_suspicious_messages": suspicious_messages,
        "preflight_token": preflight.get("token"),
        "preflight_ok": preflight.get("ok"),
        "pages": page_reports,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render Project MOE GUI QML pages offscreen or product Widgets pages offscreen and fail on missing text or visual overflow.")
    parser.add_argument("--target-project", type=Path, help="Target project that has project-moe-gui.cmd installed.")
    parser.add_argument("--view-model-json", type=Path, help="JSON file containing either a view_model object or a raw view model.")
    parser.add_argument("--shell", choices=["auto", "widgets", "qml"], default="auto", help="Visual shell to render. auto uses the product Widgets shell when the view model declares it, otherwise QML fallback.")
    parser.add_argument("--qml-source", choices=["auto", "target-project", "current-worktree", "source", "central-toolchain"], default="auto")
    parser.add_argument("--qml-path", type=Path, help="Explicit QML path to render.")
    parser.add_argument("--sections", nargs="+", choices=DEFAULT_SECTIONS, default=list(DEFAULT_SECTIONS))
    parser.add_argument("--size", dest="sizes", action="append", type=parse_size, help="Render size WIDTHxHEIGHT. Can be repeated. Default: 1180x720, 1366x768, 1440x900.")
    parser.add_argument("--fixture-profile", choices=FIXTURE_PROFILES, default="default", help="View-model fixture profile for visual regression: default, long-content, or dense-sessions.")
    parser.add_argument("--output-dir", type=Path, default=Path(".tmp") / "project_moe_gui_visual_render")
    parser.add_argument("--runtime-python", type=Path, default=DEFAULT_RUNTIME_PYTHON)
    parser.add_argument("--no-runtime-reexec", action="store_true", help="Do not re-execute through the shared PySide6 runtime.")
    parser.add_argument("--preflight-timeout-seconds", type=int, default=60)
    parser.add_argument("--settle-iterations", type=int, default=16)
    parser.add_argument("--settle-sleep-seconds", type=float, default=0.03)
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.sizes = normalized_sizes(args)
    maybe_reexec_under_runtime(args)
    try:
        shell = args.shell
        if shell == "auto":
            view_model, _preflight = load_view_model(args)
            visual = view_model.get("visual") if isinstance(view_model, dict) else {}
            product_ui = view_model.get("product_ui") if isinstance(view_model, dict) else {}
            shell = "widgets" if (
                (isinstance(visual, dict) and visual.get("primary_shell") == "qfluentwidgets-qtwidgets")
                or (isinstance(product_ui, dict) and product_ui.get("primary_shell") == "qfluentwidgets-qtwidgets")
            ) else "qml"
        payload = run_widget_visual_check(args) if shell == "widgets" else run_visual_check(args)
    except Exception as exc:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:visual_render_check_exception",
            "message": str(exc),
            "exception_type": type(exc).__name__,
        }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
