#!/bin/bash
# Comet Archive — automates the archive phase in one command
# Usage: comet-archive.sh <change-name> [--dry-run]
# Exit 0 = archive complete, exit 1 = fatal error

set -euo pipefail

red() { echo -e "\033[31m$1\033[0m" >&2; }
green() { echo -e "\033[32m$1\033[0m" >&2; }
yellow() { echo -e "\033[33m$1\033[0m" >&2; }

DRY_RUN=0
if [[ "${2:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

# Input validation
validate_change_name() {
  local name="$1"
  if [ -z "$name" ]; then
    red "FATAL: Change name cannot be empty"
    exit 1
  fi
  if [[ ! "$name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    red "FATAL: Invalid change name: '$name'"
    red "Valid characters: a-z, A-Z, 0-9, -, _"
    exit 1
  fi
  if [[ "$name" =~ \.\. ]]; then
    red "FATAL: Change name cannot contain '..'"
    exit 1
  fi
}

CHANGE="$1"
validate_change_name "$CHANGE"

CHANGE_DIR="openspec/changes/$CHANGE"
YAML="$CHANGE_DIR/.comet.yaml"
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")" 2>/dev/null || dirname "$0")" && pwd)"
STATE_SH="$SCRIPT_DIR/comet-state.sh"
TODAY=$(date +%Y-%m-%d)
ARCHIVE_NAME="${TODAY}-${CHANGE}"
ARCHIVE_DIR="openspec/changes/archive/${ARCHIVE_NAME}"

STEPS_OK=0
STEPS_TOTAL=0

step_ok() {
  green "  [OK] $1"
  STEPS_OK=$((STEPS_OK + 1))
  STEPS_TOTAL=$((STEPS_TOTAL + 1))
}

step_fail() {
  red "  [FAIL] $1"
  STEPS_TOTAL=$((STEPS_TOTAL + 1))
}

step_dry_run() {
  yellow "  [DRY-RUN] $1"
  STEPS_OK=$((STEPS_OK + 1))
  STEPS_TOTAL=$((STEPS_TOTAL + 1))
}

echo "=== Comet Archive: $CHANGE ===" >&2

# --- Step 1: Read .comet.yaml, extract paths ---

yaml_field() {
  local field="$1"
  if [ -f "$STATE_SH" ]; then
    bash "$STATE_SH" get "$CHANGE" "$field" 2>/dev/null
  else
    if [ -f "$YAML" ]; then
      grep "^${field}:" "$YAML" | sed "s/^${field}: *//" | tr -d '"' | tr -d "'"
    fi
  fi
}

if [ ! -f "$YAML" ]; then
  red "FATAL: .comet.yaml not found in $CHANGE_DIR/"
  exit 1
fi

DESIGN_DOC=$(yaml_field "design_doc")
PLAN_PATH=$(yaml_field "plan")

# --- Step 2: Validate entry state ---

PHASE_VAL=$(yaml_field "phase")
VERIFY_VAL=$(yaml_field "verify_result")
ARCHIVED_VAL=$(yaml_field "archived")

if [ "$PHASE_VAL" != "archive" ]; then
  red "FATAL: phase is '$PHASE_VAL', expected 'archive'"
  exit 1
fi

if [ "$VERIFY_VAL" != "pass" ]; then
  red "FATAL: verify_result is '$VERIFY_VAL', expected 'pass'. Run comet-verify first."
  exit 1
fi

if [ "$ARCHIVED_VAL" = "true" ]; then
  red "FATAL: change already archived"
  exit 1
fi

step_ok "Entry state verified"

# --- Step 2b: Validate management closing evidence ---

python_for_legacy_label_check() {
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  if command -v py >/dev/null 2>&1; then
    command -v py
    return 0
  fi
  return 1
}

checklist_done_legacy_mojibake() {
  local record="$1"
  shift
  local py_bin
  py_bin=$(python_for_legacy_label_check 2>/dev/null || true)
  if [ -z "$py_bin" ]; then
    return 1
  fi

  "$py_bin" - "$record" "$@" <<'PY'
from pathlib import Path
import sys

record = Path(sys.argv[1])
labels = sys.argv[2:]

try:
    text = record.read_text(encoding="utf-8", errors="replace")
except OSError:
    sys.exit(1)

checked = set()
for line in text.splitlines():
    if line.startswith("- [x] ") or line.startswith("- [X] "):
        checked.add(line[6:])

variants = set()
for label in labels:
    variants.add(label)
    data = label.encode("utf-8", errors="replace")
    for encoding in ("gbk", "cp936", "gb18030", "cp1252"):
        decoded = data.decode(encoding, errors="replace")
        variants.add(decoded)
        variants.add(decoded.replace("\ufffd", "?"))

sys.exit(0 if checked.intersection(variants) else 1)
PY
}

checklist_done_any() {
  local section="$1"
  local item="$2"
  shift 2
  local record="$1"
  shift
  local label
  for label in "$@"; do
    if grep -Fq -- "- [x] $label" "$record" || grep -Fq -- "- [X] $label" "$record"; then
      return 0
    fi
  done
  if checklist_done_legacy_mojibake "$record" "$@"; then
    return 0
  fi
  red "FATAL: management checklist item is not checked: $item"
  red "Missing management checklist section: $section"
  red "Accepted labels:"
  for label in "$@"; do
    red "  - $label"
  done
  red "Next: mark one accepted '- [x]' item in $record after recording the evidence."
  exit 1
}

checklist_done() {
  local label="$1"
  local record="$2"
  if grep -Fq -- "- [x] $label" "$record" || grep -Fq -- "- [X] $label" "$record"; then
    return 0
  fi
  red "FATAL: management checklist item is not checked: $label"
  red "Next: mark '- [x] $label' in $record after recording the evidence."
  exit 1
}

MANAGEMENT_RECORD=$(yaml_field "management_record")
if [ -z "$MANAGEMENT_RECORD" ] || [ "$MANAGEMENT_RECORD" = "null" ]; then
  MANAGEMENT_RECORD="$CHANGE_DIR/management.md"
fi
if [ ! -f "$MANAGEMENT_RECORD" ]; then
  red "FATAL: management record not found: $MANAGEMENT_RECORD"
  exit 1
fi

checklist_done_any "Archive / Closing" "Value outcome is summarized." "$MANAGEMENT_RECORD" \
  "价值结果已总结" "Value outcome is summarized."
checklist_done_any "Archive / Closing" "Lessons learned or reusable guidance are recorded." "$MANAGEMENT_RECORD" \
  "经验沉淀已记录" "Lessons learned or reusable guidance are recorded."
checklist_done_any "Archive / Closing" "Delta spec sync, verification evidence, and archive path are confirmed." "$MANAGEMENT_RECORD" \
  "delta spec sync / verification evidence / archive path 已确认" \
  "Delta spec sync, verification evidence, and archive path are confirmed."
checklist_done_any "Monitoring Loop" "Current facts are checked." "$MANAGEMENT_RECORD" \
  "当前阶段事实已检查" "Current facts are checked."
checklist_done_any "Monitoring Loop" "Continue, adjust, stop, or return decision is made." "$MANAGEMENT_RECORD" \
  "是否需要回退已判断" "Continue, adjust, stop, or return decision is made."

MONITORING_STATUS=$(yaml_field "monitoring_status")
CONTROL_DECISION=$(yaml_field "control_decision")
if [ -n "$MONITORING_STATUS" ] && [ "$MONITORING_STATUS" != "clear" ]; then
  red "FATAL: monitoring_status is '$MONITORING_STATUS', expected 'clear' before archive"
  exit 1
fi
if [ -n "$CONTROL_DECISION" ] && [ "$CONTROL_DECISION" != "continue" ]; then
  red "FATAL: control_decision is '$CONTROL_DECISION', expected 'continue' before archive"
  exit 1
fi

step_ok "Management closing evidence verified"

# --- Step 3: Check archive target ---

if [ -d "$ARCHIVE_DIR" ]; then
  red "FATAL: archive target already exists: $ARCHIVE_DIR"
  exit 1
fi

step_ok "Archive target available"

# --- Step 4: Sync delta specs → main specs ---

sync_delta_specs() {
  local delta_root="$CHANGE_DIR/specs"
  if [ ! -d "$delta_root" ]; then
    return 0
  fi

  for delta_spec_dir in "$delta_root"/*/; do
    [ -d "$delta_spec_dir" ] || continue
    local capability
    capability=$(basename "$delta_spec_dir")
    local delta_spec="$delta_spec_dir/spec.md"
    local main_spec="openspec/specs/$capability/spec.md"

    if [ ! -f "$delta_spec" ]; then
      continue
    fi

    if [ "$DRY_RUN" -eq 1 ]; then
      step_dry_run "Would sync: $capability → $main_spec"
      continue
    fi

    if [ ! -f "$main_spec" ]; then
      mkdir -p "openspec/specs/$capability"
    elif ! cmp -s "$main_spec" "$delta_spec"; then
      yellow "  [DIFF] Delta spec differs from main spec before sync: $capability"
      diff -u "$main_spec" "$delta_spec" >&2 || true
    fi
    cp "$delta_spec" "$main_spec"

    step_ok "Delta spec synced: $capability → openspec/specs/$capability/spec.md"
  done
}

sync_delta_specs

# --- Step 5: Annotate design doc frontmatter ---

annotate_frontmatter() {
  local file="$1"
  local extra_fields="$2"

  if [ ! -f "$file" ]; then
    return 0
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    step_dry_run "Would annotate: $file"
    return 0
  fi

  if head -1 "$file" | grep -q '^---'; then
    local tmp_file
    tmp_file=$(mktemp)
    awk -v archive="$ARCHIVE_NAME" -v extra="$extra_fields" '
      /^archived-with:/ { next }
      NR==1 && /^---/ { print; next }
      /^---/ && NR>1 {
        print "archived-with: " archive
        if (extra != "") print extra
        print; next
      }
      { print }
    ' "$file" > "$tmp_file"
    mv "$tmp_file" "$file"
  else
    local tmp_file
    tmp_file=$(mktemp)
    {
      echo "---"
      echo "archived-with: $ARCHIVE_NAME"
      if [ -n "$extra_fields" ]; then
        echo "$extra_fields"
      fi
      echo "status: final"
      echo "---"
      cat "$file"
    } > "$tmp_file"
    mv "$tmp_file" "$file"
  fi

  step_ok "Annotated: $file"
}

if [ -n "$DESIGN_DOC" ] && [ "$DESIGN_DOC" != "null" ]; then
  annotate_frontmatter "$DESIGN_DOC" "status: final"
fi

# --- Step 6: Annotate plan frontmatter ---

if [ -n "$PLAN_PATH" ] && [ "$PLAN_PATH" != "null" ]; then
  annotate_frontmatter "$PLAN_PATH" ""
fi

# --- Step 7: Move change to archive ---

if [ "$DRY_RUN" -eq 1 ]; then
  step_dry_run "Would move: $CHANGE_DIR → $ARCHIVE_DIR"
else
  mkdir -p "openspec/changes/archive"
  mv "$CHANGE_DIR" "$ARCHIVE_DIR"
  step_ok "Moved to: $ARCHIVE_DIR"
fi

# --- Step 8: Mark archived via comet-state transition ---

ARCHIVE_YAML="$ARCHIVE_DIR/.comet.yaml"

if [ "$DRY_RUN" -eq 1 ]; then
  step_dry_run "Would set archived: true in $ARCHIVE_YAML"
else
  if [ -f "$ARCHIVE_YAML" ]; then
    bash "$STATE_SH" transition "$ARCHIVE_NAME" archived >/dev/null
    step_ok "archived: true"
  else
    step_fail "archived: true (.comet.yaml not found after move)"
  fi
fi

# --- Step 9: Print summary ---

echo "" >&2
if [ "$DRY_RUN" -eq 1 ]; then
  yellow "Dry run complete. $STEPS_OK/$STEPS_TOTAL steps would succeed."
else
  green "Archive complete. $STEPS_OK/$STEPS_TOTAL steps succeeded."
fi

if [ "$STEPS_OK" -lt "$STEPS_TOTAL" ]; then
  exit 1
fi

exit 0
