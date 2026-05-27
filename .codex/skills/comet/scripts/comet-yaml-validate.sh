#!/bin/bash
# Comet YAML Schema Validator — validates .comet.yaml structure
# Usage: comet-yaml-validate.sh <change-name>
# Exit 0 = valid, exit 1 = errors found (printed to stderr)

set -euo pipefail

red()   { echo -e "\033[31m$1\033[0m" >&2; }
green() { echo -e "\033[32m$1\033[0m" >&2; }
warn()  { echo -e "\033[33m$1\033[0m" >&2; }

# Input validation - prevent path traversal
validate_change_name() {
  local name="$1"
  # Reject empty names
  if [ -z "$name" ]; then
    red "ERROR: Change name cannot be empty" >&2
    exit 1
  fi
  # Only allow alphanumeric, hyphens, and underscores
  if [[ ! "$name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    red "ERROR: Invalid change name: '$name'" >&2
    red "Valid characters: a-z, A-Z, 0-9, -, _" >&2
    exit 1
  fi
  # Reject path traversal attempts
  if [[ "$name" =~ \.\. ]]; then
    red "ERROR: Change name cannot contain '..' (path traversal not allowed)" >&2
    exit 1
  fi
}

validate_change_name "$1"

CHANGE="$1"
CHANGE_DIR="openspec/changes/$CHANGE"
if [ ! -d "$CHANGE_DIR" ] && [ -d "openspec/changes/archive/$CHANGE" ]; then
  CHANGE_DIR="openspec/changes/archive/$CHANGE"
fi
YAML="$CHANGE_DIR/.comet.yaml"

ERRORS=0
WARNINGS=0

# Helper: get value of a top-level field (handles null, empty, quoted)
field_value() {
  local value
  value=$(grep "^${1}:" "$YAML" 2>/dev/null | sed "s/^${1}: *//" || true)
  strip_wrapping_quotes "$value"
}

strip_wrapping_quotes() {
  local value="$1"
  case "$value" in
    \"*\")
      printf '%s\n' "${value:1:${#value}-2}"
      ;;
    \'*\')
      printf '%s\n' "${value:1:${#value}-2}"
      ;;
    *)
      printf '%s\n' "$value"
      ;;
  esac
}

fail()  { red "  FAIL: $1"; ERRORS=$((ERRORS + 1)); }
warn_msg() { warn "  WARN: $1"; WARNINGS=$((WARNINGS + 1)); }

echo "[VALIDATE] $YAML" >&2

# --- Required fields ---
REQUIRED_FIELDS="workflow phase design_doc plan build_mode isolation verify_mode verify_result verification_report branch_status verified_at archived management_record monitoring_status control_decision target_phase rework_reason iteration_count"
for field in $REQUIRED_FIELDS; do
  if ! grep -q "^${field}:" "$YAML" 2>/dev/null; then
    fail "missing required field '$field'"
  fi
done

# --- Enum validation ---
validate_enum() {
  local field="$1" value="$2"
  shift 2
  local valid_values="$*"

  # null or empty is always acceptable
  if [ -z "$value" ] || [ "$value" = "null" ]; then
    return 0
  fi

  for v in $valid_values; do
    if [ "$value" = "$v" ]; then
      return 0
    fi
  done
  fail "$field='$value' is not valid. Expected: $valid_values"
}

workflow=$(field_value "workflow")
phase=$(field_value "phase")
build_mode=$(field_value "build_mode")
isolation=$(field_value "isolation")
verify_mode=$(field_value "verify_mode")
verify_result=$(field_value "verify_result")
branch_status=$(field_value "branch_status")
archived=$(field_value "archived")
direct_override=$(field_value "direct_override")
management_record=$(field_value "management_record")
monitoring_status=$(field_value "monitoring_status")
control_decision=$(field_value "control_decision")
target_phase=$(field_value "target_phase")
rework_reason=$(field_value "rework_reason")
iteration_count=$(field_value "iteration_count")
design_doc=$(field_value "design_doc")
plan=$(field_value "plan")

validate_enum "workflow"      "$workflow"      "full hotfix tweak"
validate_enum "phase"         "$phase"          "open design build verify archive"
validate_enum "build_mode"    "$build_mode"     "subagent-driven-development executing-plans direct"
validate_enum "isolation"     "$isolation"      "branch worktree"
validate_enum "verify_mode"   "$verify_mode"    "light full"
validate_enum "verify_result" "$verify_result"  "pending pass fail"
validate_enum "branch_status" "$branch_status"  "pending handled"
validate_enum "archived"      "$archived"       "true false"
validate_enum "direct_override" "$direct_override" "true false"
validate_enum "monitoring_status" "$monitoring_status" "clear needs_decision blocked"
validate_enum "control_decision" "$control_decision" "continue adjust-current return-open return-design return-build return-verify stop"
validate_enum "target_phase" "$target_phase" "null open design build verify"
validate_enum "rework_reason" "$rework_reason" "null scope-gap planning-gap execution-gap verification-gap value-gap risk-change stakeholder-change"

validate_return_invariants() {
  case "$control_decision" in
    return-open|return-design|return-build|return-verify)
      if [ -z "$target_phase" ] || [ "$target_phase" = "null" ] || [ -z "$rework_reason" ] || [ "$rework_reason" = "null" ]; then
        fail "return decision requires target_phase and rework_reason"
      fi
      ;;
    *)
      return 0
      ;;
  esac

  case "$control_decision" in
    return-open)
      if [ "$target_phase" != "open" ]; then
        fail "return-open target_phase must be open"
      fi
      ;;
    return-design)
      if [ "$target_phase" != "design" ]; then
        fail "return-design target_phase must be design"
      fi
      ;;
    return-build)
      if [ "$target_phase" != "build" ]; then
        fail "return-build target_phase must be build"
      fi
      ;;
    return-verify)
      if [ "$target_phase" != "verify" ]; then
        fail "return-verify target_phase must be verify"
      fi
      ;;
    *)
      return 0
      ;;
  esac
}
validate_return_invariants

if [ -n "$iteration_count" ] && [ "$iteration_count" != "null" ] && [[ ! "$iteration_count" =~ ^[0-9]+$ ]]; then
  fail "iteration_count='$iteration_count' is not a non-negative integer"
fi

# --- Path validation ---

if [ -n "$design_doc" ] && [ "$design_doc" != "null" ]; then
  if [ ! -f "$design_doc" ]; then
    fail "design_doc='$design_doc' does not exist on disk"
  fi
fi

if [ -n "$plan" ] && [ "$plan" != "null" ]; then
  if [ ! -f "$plan" ]; then
    fail "plan='$plan' does not exist on disk"
  fi
fi

if [ -n "$management_record" ] && [ "$management_record" != "null" ]; then
  if [ ! -f "$management_record" ]; then
    fail "management_record='$management_record' does not exist on disk"
  fi
fi

# --- Unknown keys check ---
KNOWN_KEYS="workflow phase design_doc plan build_mode isolation verify_mode verify_result verification_report branch_status verified_at archived direct_override build_command verify_command management_record monitoring_status control_decision target_phase rework_reason iteration_count"
while IFS=: read -r key _; do
  key="${key// /}"
  [ -z "$key" ] && continue
  found=0
  for known in $KNOWN_KEYS; do
    [ "$key" = "$known" ] && found=1 && break
  done
  if [ "$found" -eq 0 ]; then
    warn_msg "unknown field '$key' found"
  fi
done < "$YAML"

# --- Summary ---
echo "" >&2
if [ "$ERRORS" -gt 0 ]; then
  red "$ERRORS error(s), $WARNINGS warning(s) — validation FAILED"
  exit 1
else
  green "0 errors, $WARNINGS warning(s) — validation PASSED"
  exit 0
fi
