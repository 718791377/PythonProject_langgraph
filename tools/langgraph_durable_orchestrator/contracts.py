"""Static contracts for the LangGraph durable orchestration MVP."""

from __future__ import annotations

ROOT_PHASES = [
    "define-target",
    "read-context",
    "freeze-plan",
    "execute-parallel",
    "integrate-converge",
    "stabilize",
    "verify-accept",
]

CURRENT_GRAPH_CONTRACT = {
    "graph_contract_id": "codex_user_level_langgraph",
    "topology_version": "1.0",
    "state_schema_version": "1.0",
}

GRAPH_CONTRACT_FIELDS = [
    "graph_contract_id",
    "topology_version",
    "state_schema_version",
]

TOPOLOGY_COMPATIBILITY_POSTURES = [
    "migration_safe",
    "degraded_compatible",
    "incompatible",
]

STATE_SCHEMA_COMPATIBILITY_POSTURES = [
    "migration_safe",
    "degraded_compatible",
    "incompatible",
]

THREAD_COMPATIBILITY_VERDICTS = [
    "migration_safe",
    "degraded_compatible",
    "incompatible",
]

MIGRATION_REASON_CODES = [
    "graph_contract_id_mismatch",
    "topology_version_missing",
    "topology_minor_drift",
    "topology_major_drift",
    "state_schema_version_missing",
    "state_schema_minor_drift",
    "state_schema_major_drift",
]

MIGRATION_PROJECTION_FIELDS = [
    "current_graph_contract",
    "thread_graph_contract",
    "topology_compatibility",
    "state_schema_compatibility",
    "compatibility",
    "reason_codes",
    "helper_pointer",
]

GRAPH_KERNEL_IDENTITY = {
    "kernel_kind": "stategraph",
    "kernel_id": "codex_user_level_stategraph",
    "graph_api_surface": "StateGraph",
    "operator_shell_model": "seven_phase_durable_shell",
}

GRAPH_KERNEL_IDENTITY_FIELDS = [
    "kernel_kind",
    "kernel_id",
    "graph_api_surface",
    "operator_shell_model",
]

GRAPH_KERNEL_NODE_POSTURES = [
    "phase_active",
    "approval_wait",
    "recovery_pending_resume",
    "terminal",
]

GRAPH_KERNEL_TRANSITION_KINDS = [
    "sequential",
    "loop",
    "command",
    "interrupt",
    "recovery",
    "terminal",
]

GRAPH_KERNEL_NODE_FIELDS = [
    "node_id",
    "phase",
    "node_kind",
    "subgraph_id",
    "loop_capable",
    "terminal",
]

GRAPH_KERNEL_EDGE_FIELDS = [
    "edge_id",
    "source_node",
    "target_node",
    "transition_kind",
    "condition",
]

GRAPH_KERNEL_PROJECTION_FIELDS = [
    "kernel_identity",
    "current_node_id",
    "mapped_phase",
    "node_posture",
    "current_node",
    "available_next_nodes",
    "last_transition",
    "helper_pointer",
]

PRIMARY_RUNTIME_ENGINE_IDENTITY = {
    "engine_kind": "compiled_stategraph_engine",
    "engine_id": "codex_user_level_primary_stategraph",
    "graph_api_surface": "StateGraph",
    "operator_shell_model": "seven_phase_durable_shell",
}

PRIMARY_RUNTIME_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "operator_shell_model",
]

PRIMARY_RUNTIME_ENGINE_POSTURES = [
    "compiled_unavailable",
    "compiled_ready",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
]

PRIMARY_RUNTIME_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "checkpointer_expected",
    "entry_node",
    "finish_nodes",
    "current_execution_node",
    "mapped_phase",
    "execution_posture",
    "last_execution_reason",
    "helper_pointer",
]

COMPILED_INVOCATION_IDENTITY = {
    "invocation_kind": "compiled_stategraph_path",
    "invocation_id": "codex_user_level_compiled_stategraph",
    "compiler_surface": "StateGraph.compile",
    "invoke_surface": "CompiledGraph.invoke",
    "stream_surface": "CompiledGraph.stream",
}

COMPILED_INVOCATION_IDENTITY_FIELDS = [
    "invocation_kind",
    "invocation_id",
    "compiler_surface",
    "invoke_surface",
    "stream_surface",
]

COMPILED_INVOCATION_POSTURES = [
    "unavailable",
    "compiled_ready",
    "interrupt_wait",
    "recovery_wait",
    "completed",
]

COMPILED_INVOCATION_RUN_KINDS = [
    "invoke",
    "stream",
]

COMPILED_INVOCATION_PROJECTION_FIELDS = [
    "invocation_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "compiled_node_count",
    "compiled_edge_count",
    "current_execution_node",
    "mapped_phase",
    "invocation_posture",
    "last_invoke_kind",
    "last_invoke_reason",
    "helper_pointer",
]

LIVE_EXECUTION_IDENTITY = {
    "execution_kind": "live_compiled_stategraph_path",
    "execution_id": "codex_user_level_live_compiled_stategraph",
    "compiler_surface": "StateGraph.compile",
    "execute_surface": "CompiledGraph.invoke/stream",
}

LIVE_EXECUTION_IDENTITY_FIELDS = [
    "execution_kind",
    "execution_id",
    "compiler_surface",
    "execute_surface",
]

LIVE_EXECUTION_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "execution_failed",
]

LIVE_EXECUTION_RUN_KINDS = [
    "invoke",
    "stream",
]

LIVE_EXECUTION_PROJECTION_FIELDS = [
    "execution_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "last_output_keys",
    "last_stream_event_count",
    "helper_pointer",
]

FULLER_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "fuller_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
}

FULLER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
]

FULLER_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "execution_failed",
]

FULLER_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

FULLER_LIVE_PRIMARY_ENGINE_TRANSITION_KINDS = [
    "sequential",
    "loop",
    "command",
    "interrupt",
    "recovery",
    "terminal",
    "stayed_put",
]

FULLER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "execution_node_path",
    "resulting_phase",
    "resulting_status",
    "phase_transition_kind",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "deeper_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_deeper_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "recursion_limit_surface": "config.recursion_limit",
    "remaining_steps_surface": "RemainingSteps",
}

DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "recursion_limit_surface",
    "remaining_steps_surface",
]

DEEPER_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "projected",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "projection_failed",
]

DEEPER_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

DEEPER_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

DEEPER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "projected_node_path",
    "projected_phase_path",
    "planned_supersteps",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "superstep_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_superstep_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "superstep_surface": "Pregel supersteps",
    "trace_surface": "node_visit_path/phase_visit_path",
}

SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "superstep_surface",
    "trace_surface",
]

SUPERSTEP_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

SUPERSTEP_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

SUPERSTEP_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

SUPERSTEP_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "node_visit_path",
    "phase_visit_path",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "stateful_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_stateful_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "remaining_steps_surface": "RemainingSteps",
    "decision_surface": "next_execution_node_from_graph_state",
}

STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "remaining_steps_surface",
    "decision_surface",
]

STATEFUL_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

STATEFUL_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

STATEFUL_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

STATEFUL_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "stateful_node_path",
    "stateful_phase_path",
    "stateful_transition_log",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "graph_resident_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_graph_resident_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "boundary_surface": "graph_resident_boundary_state",
    "decision_surface": "compiled_boundary_nodes_and_phase_end",
}

BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "boundary_surface",
    "decision_surface",
]

BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "boundary_node_path",
    "boundary_phase_path",
    "boundary_transition_log",
    "boundary_state_kind",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "subgraph_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_subgraph_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "handoff_surface": "subgraph_and_parent_handoff_state",
    "subgraph_surface": "active_subgraph/source_subgraph/target_subgraph",
}

HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "handoff_surface",
    "subgraph_surface",
]

HANDOFF_STATE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

HANDOFF_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

HANDOFF_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

HANDOFF_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "handoff_node_path",
    "handoff_phase_path",
    "handoff_subgraph_path",
    "handoff_transition_log",
    "handoff_state_kind",
    "active_subgraph",
    "source_subgraph",
    "target_subgraph",
    "parent_handoff_target",
    "graph_scope",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "approval_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_approval_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "approval_surface": "approval_queue_and_resume_map_state",
    "resume_surface": "queue_posture/resume_map_keys/current_interrupt_id",
}

APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "approval_surface",
    "resume_surface",
]

APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "approval_node_path",
    "approval_phase_path",
    "approval_transition_log",
    "resume_state_kind",
    "queue_posture",
    "pending_count",
    "resolved_count",
    "current_interrupt_id",
    "resume_map_keys",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "recovery_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_recovery_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "recovery_surface": "recovery_target_and_action_state",
    "provenance_surface": "source_records_and_history_targets",
}

PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "recovery_surface",
    "provenance_surface",
]

PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "provenance_node_path",
    "provenance_phase_path",
    "provenance_transition_log",
    "provenance_state_kind",
    "recovery_posture",
    "recovery_action",
    "recovery_target_id",
    "recovery_target_kind",
    "source_records",
    "recoverable_fields_touched",
    "history_compatibility",
    "history_target_count",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "durable_artifact_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_durable_artifact_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "artifact_surface": "implementation_brief_and_survivor_queue_state",
    "artifact_summary_surface": "artifact_state_kind/brief_id/source_evidence_ref_count/survivor_count",
}

DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "artifact_surface",
    "artifact_summary_surface",
]

DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "artifact_node_path",
    "artifact_phase_path",
    "artifact_transition_log",
    "artifact_state_kind",
    "implementation_brief_present",
    "implementation_brief_id",
    "implementation_brief_source_evidence_ref_count",
    "survivor_queue_present",
    "survivor_queue_kind",
    "survivor_count",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "reducer_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_reducer_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "reducer_surface": "reducer_merge_channels_and_single_writer_state",
    "merge_surface": "fanout_state/merge_channels_updated/source_records",
}

REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "reducer_surface",
    "merge_surface",
]

REDUCER_AWARE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

REDUCER_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

REDUCER_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

REDUCER_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "merge_node_path",
    "merge_phase_path",
    "merge_transition_log",
    "merge_state_kind",
    "reducer_compatibility",
    "fanout_state",
    "invalid_multi_writer_detected",
    "invalid_multi_writer_updates",
    "merge_channels_updated",
    "channel_item_counts",
    "source_records",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "command_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_command_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "command_surface": "update_goto_resume_and_parent_handoff_state",
    "control_surface": "transition_kind/graph_scope/target_subgraph/resume_posture",
}

COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "command_surface",
    "control_surface",
]

COMMAND_AWARE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

COMMAND_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

COMMAND_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

COMMAND_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "command_node_path",
    "command_phase_path",
    "command_transition_log",
    "control_state_kind",
    "transition_kind",
    "update_keys",
    "goto_target",
    "graph_scope",
    "source_subgraph",
    "target_subgraph",
    "parent_handoff_target",
    "resume_posture",
    "resume_payload_present",
    "resume_payload_keys",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "runtime_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_runtime_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "runtime_surface": "runtime_context_and_context_schema_state",
    "store_surface": "injected_store_configuration_state",
}

RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "runtime_surface",
    "store_surface",
]

RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "runtime_node_path",
    "runtime_phase_path",
    "runtime_transition_log",
    "runtime_state_kind",
    "context_schema",
    "runtime_context_present",
    "runtime_context_keys",
    "runtime_context_kind_hints",
    "store_configured",
    "store_access_expected",
    "store_kind",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "memory_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_memory_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "memory_surface": "memory_store_and_namespace_state",
    "semantic_surface": "semantic_memory_enablement_and_store_state",
}

MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "memory_surface",
    "semantic_surface",
]

MEMORY_AWARE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

MEMORY_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

MEMORY_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

MEMORY_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "memory_node_path",
    "memory_phase_path",
    "memory_transition_log",
    "memory_state_kind",
    "memory_store_configured",
    "memory_store_kind",
    "memory_namespaces",
    "semantic_memory_enabled",
    "semantic_store_kind",
    "semantic_namespaces",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY = {
    "engine_kind": "migration_aware_live_stategraph_primary_execution_engine",
    "engine_id": "codex_user_level_migration_aware_live_primary_execution_engine",
    "graph_api_surface": "StateGraph",
    "execute_surface": "CompiledGraph.invoke/stream",
    "migration_surface": "graph_contract_and_thread_compatibility_state",
    "compatibility_surface": "topology_state_schema_and_reason_codes",
}

MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS = [
    "engine_kind",
    "engine_id",
    "graph_api_surface",
    "execute_surface",
    "migration_surface",
    "compatibility_surface",
]

MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_POSTURES = [
    "unavailable",
    "ready",
    "executed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "recursion_limited",
    "execution_failed",
]

MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS = [
    "invoke",
    "stream",
]

MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES = [
    "phase_boundary",
    "command_boundary",
    "loop_boundary",
    "interrupt_boundary",
    "recovery_boundary",
    "terminal_boundary",
    "recursion_limit_boundary",
]

MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS = [
    "engine_identity",
    "compile_supported",
    "compiled_graph_present",
    "invoke_supported",
    "stream_supported",
    "current_execution_node",
    "mapped_phase",
    "compatibility_node_path",
    "compatibility_phase_path",
    "compatibility_transition_log",
    "compatibility_state_kind",
    "current_graph_contract",
    "thread_graph_contract",
    "topology_compatibility",
    "state_schema_compatibility",
    "compatibility",
    "reason_codes",
    "superstep_count",
    "stop_boundary",
    "terminal_reached",
    "recursion_limit_supported",
    "remaining_steps_supported",
    "recursion_limit",
    "execution_posture",
    "last_run_kind",
    "last_run_status",
    "last_run_reason",
    "helper_pointer",
]

GENERALIZED_LIVE_ROUTING_IDENTITY = {
    "routing_kind": "generalized_live_stategraph_path",
    "routing_id": "codex_user_level_generalized_live_stategraph",
    "graph_api_surface": "StateGraph",
    "route_decision_surface": "StateGraph.add_conditional_edges",
}

GENERALIZED_LIVE_ROUTING_IDENTITY_FIELDS = [
    "routing_kind",
    "routing_id",
    "graph_api_surface",
    "route_decision_surface",
]

GENERALIZED_LIVE_ROUTING_POSTURES = [
    "unavailable",
    "ready",
    "routed",
    "interrupt_wait",
    "recovery_wait",
    "terminal",
    "routing_failed",
]

GENERALIZED_LIVE_ROUTING_ROUTE_KINDS = [
    "phase_linear",
    "loop_review",
    "loop_execution",
    "loop_stabilization",
    "approval_wait",
    "recovery_wait",
    "terminal_accept",
    "terminal_halt",
    "terminal_escalate",
    "command_controlled",
]

GENERALIZED_LIVE_ROUTING_PROJECTION_FIELDS = [
    "routing_identity",
    "compile_supported",
    "compiled_graph_present",
    "route_posture",
    "current_route",
    "candidate_routes",
    "selected_route",
    "loop_route_kind",
    "current_execution_node",
    "mapped_phase",
    "next_execution_nodes",
    "approval_route_pending",
    "helper_pointer",
]

GRAPH_KERNEL_PHASE_TO_NODE = {
    "define-target": "define_target",
    "read-context": "read_context",
    "freeze-plan": "freeze_plan",
    "execute-parallel": "execute_parallel",
    "integrate-converge": "integrate_converge",
    "stabilize": "stabilize",
    "verify-accept": "verify_accept",
}

GRAPH_KERNEL_NODES = {
    "define_target": {
        "node_id": "define_target",
        "phase": "define-target",
        "node_kind": "phase",
        "subgraph_id": "research",
        "loop_capable": False,
        "terminal": False,
    },
    "read_context": {
        "node_id": "read_context",
        "phase": "read-context",
        "node_kind": "phase",
        "subgraph_id": "research",
        "loop_capable": False,
        "terminal": False,
    },
    "freeze_plan": {
        "node_id": "freeze_plan",
        "phase": "freeze-plan",
        "node_kind": "phase",
        "subgraph_id": "planning",
        "loop_capable": False,
        "terminal": False,
    },
    "execute_parallel": {
        "node_id": "execute_parallel",
        "phase": "execute-parallel",
        "node_kind": "phase",
        "subgraph_id": "execution",
        "loop_capable": True,
        "terminal": False,
    },
    "integrate_converge": {
        "node_id": "integrate_converge",
        "phase": "integrate-converge",
        "node_kind": "phase",
        "subgraph_id": "execution",
        "loop_capable": False,
        "terminal": False,
    },
    "stabilize": {
        "node_id": "stabilize",
        "phase": "stabilize",
        "node_kind": "phase",
        "subgraph_id": "execution",
        "loop_capable": True,
        "terminal": False,
    },
    "verify_accept": {
        "node_id": "verify_accept",
        "phase": "verify-accept",
        "node_kind": "phase",
        "subgraph_id": "verification",
        "loop_capable": False,
        "terminal": False,
    },
    "approval_wait": {
        "node_id": "approval_wait",
        "phase": "",
        "node_kind": "interrupt_wait",
        "subgraph_id": "",
        "loop_capable": False,
        "terminal": False,
    },
    "recovery_pending_resume": {
        "node_id": "recovery_pending_resume",
        "phase": "",
        "node_kind": "recovery_wait",
        "subgraph_id": "",
        "loop_capable": False,
        "terminal": False,
    },
    "accepted_terminal": {
        "node_id": "accepted_terminal",
        "phase": "",
        "node_kind": "terminal",
        "subgraph_id": "",
        "loop_capable": False,
        "terminal": True,
    },
    "halted_terminal": {
        "node_id": "halted_terminal",
        "phase": "",
        "node_kind": "terminal",
        "subgraph_id": "",
        "loop_capable": False,
        "terminal": True,
    },
    "escalated_terminal": {
        "node_id": "escalated_terminal",
        "phase": "",
        "node_kind": "terminal",
        "subgraph_id": "",
        "loop_capable": False,
        "terminal": True,
    },
}

GRAPH_KERNEL_EDGES = [
    {
        "edge_id": "define_target_to_read_context",
        "source_node": "define_target",
        "target_node": "read_context",
        "transition_kind": "sequential",
        "condition": "target_defined",
    },
    {
        "edge_id": "read_context_to_freeze_plan",
        "source_node": "read_context",
        "target_node": "freeze_plan",
        "transition_kind": "sequential",
        "condition": "context_read",
    },
    {
        "edge_id": "freeze_plan_to_execute_parallel",
        "source_node": "freeze_plan",
        "target_node": "execute_parallel",
        "transition_kind": "sequential",
        "condition": "plan_frozen",
    },
    {
        "edge_id": "execute_parallel_to_integrate_converge",
        "source_node": "execute_parallel",
        "target_node": "integrate_converge",
        "transition_kind": "sequential",
        "condition": "execution_complete",
    },
    {
        "edge_id": "integrate_converge_to_stabilize",
        "source_node": "integrate_converge",
        "target_node": "stabilize",
        "transition_kind": "sequential",
        "condition": "integration_complete",
    },
    {
        "edge_id": "stabilize_to_verify_accept",
        "source_node": "stabilize",
        "target_node": "verify_accept",
        "transition_kind": "sequential",
        "condition": "stabilization_complete",
    },
    {
        "edge_id": "verify_accept_to_accepted_terminal",
        "source_node": "verify_accept",
        "target_node": "accepted_terminal",
        "transition_kind": "terminal",
        "condition": "accepted",
    },
    {
        "edge_id": "execute_parallel_loop",
        "source_node": "execute_parallel",
        "target_node": "execute_parallel",
        "transition_kind": "loop",
        "condition": "revise",
    },
    {
        "edge_id": "stabilize_loop",
        "source_node": "stabilize",
        "target_node": "stabilize",
        "transition_kind": "loop",
        "condition": "revise",
    },
    {
        "edge_id": "approval_wait_resume",
        "source_node": "approval_wait",
        "target_node": "*phase_resume*",
        "transition_kind": "interrupt",
        "condition": "approved_resume",
    },
    {
        "edge_id": "recovery_pending_resume",
        "source_node": "recovery_pending_resume",
        "target_node": "*phase_resume*",
        "transition_kind": "recovery",
        "condition": "explicit_resume",
    },
]

SUBGRAPH_LIBRARY_FIELDS = [
    "subgraph_id",
    "role_family",
    "roles",
    "default_phase",
    "phase_families",
    "input_artifacts",
    "output_artifacts",
    "handoff_artifacts",
    "fresh_context_boundary",
    "durable_worker_default",
    "read_only_default",
    "persistence_mode_default",
    "checkpointer_mode_default",
    "state_inspection_default",
    "state_inspection_scope_default",
    "static_discoverable",
    "same_subgraph_parallel_calls_supported",
    "allowed_parent_graph_scopes",
]

SUBGRAPH_PROJECTION_FIELDS = [
    "active_subgraph",
    "active_subgraph_posture",
    "available_subgraphs",
    "helper_pointer",
]

SUBGRAPH_PERSISTENCE_MODES = [
    "per_invocation",
    "per_thread",
    "stateless",
]

SUBGRAPH_CHECKPOINTER_MODES = [
    "inherit_parent",
    "separate_subgraph",
    "disabled",
]

SUBGRAPH_STATE_INSPECTION_SCOPES = [
    "current_invocation",
    "thread_accumulated",
    "unavailable",
]

SUBGRAPH_STATE_INSPECTION_FIELDS = [
    "active_subgraph",
    "persistence_mode",
    "checkpointer_mode",
    "inherits_parent_checkpointer",
    "separate_subgraph_memory",
    "durable_execution_supported",
    "interrupts_supported",
    "state_inspection_available",
    "state_inspection_scope",
    "static_discoverable",
    "same_subgraph_parallel_calls_supported",
    "inspection_blockers",
]

SUBGRAPH_STATE_INSPECTION_PROJECTION_FIELDS = [
    "active_subgraph",
    "persistence_mode",
    "checkpointer_mode",
    "inherits_parent_checkpointer",
    "separate_subgraph_memory",
    "durable_execution_supported",
    "interrupts_supported",
    "state_inspection_available",
    "state_inspection_scope",
    "static_discoverable",
    "same_subgraph_parallel_calls_supported",
    "inspection_blockers",
    "helper_pointer",
]

STREAM_OBSERVABILITY_MODES = [
    "updates",
    "checkpoints",
    "tasks",
    "debug",
]

STREAM_EVENT_FIELDS = [
    "selected_modes",
    "subgraphs",
    "latest_event_kind",
    "latest_namespace",
    "latest_checkpoint_kind",
    "latest_task_path",
    "latest_task_status",
    "latest_debug_summary",
    "event_count",
]

STREAM_PROJECTION_FIELDS = [
    "selected_modes",
    "subgraphs",
    "latest_event_kind",
    "latest_namespace",
    "latest_checkpoint_kind",
    "latest_task_path",
    "latest_task_status",
    "latest_debug_summary",
    "event_count",
    "helper_pointer",
]

RUNTIME_CONTEXT_FIELDS = [
    "context_schema",
    "runtime_context_present",
    "runtime_context_keys",
    "runtime_context_kind_hints",
]

STORE_INJECTION_FIELDS = [
    "store_configured",
    "store_access_expected",
    "store_kind",
]

RUNTIME_INJECTION_PROJECTION_FIELDS = [
    "context_schema",
    "runtime_context_present",
    "runtime_context_keys",
    "runtime_context_kind_hints",
    "store_configured",
    "store_access_expected",
    "store_kind",
    "helper_pointer",
]

MEMORY_STORE_FIELDS = [
    "memory_store_configured",
    "memory_store_kind",
    "memory_namespaces",
]

SEMANTIC_MEMORY_FIELDS = [
    "semantic_memory_enabled",
    "semantic_store_kind",
    "semantic_namespaces",
]

MEMORY_PROJECTION_FIELDS = [
    "memory_store_configured",
    "memory_store_kind",
    "memory_namespaces",
    "semantic_memory_enabled",
    "semantic_store_kind",
    "semantic_namespaces",
    "helper_pointer",
]

COMMAND_TRANSITION_KINDS = [
    "update",
    "goto",
    "update_goto",
    "resume",
    "resume_with_payload",
    "parent_handoff",
    "resume_parent_handoff",
]

COMMAND_GRAPH_SCOPES = [
    "current",
    "parent",
]

COMMAND_RESUME_POSTURES = [
    "ordinary",
    "awaiting_command_resume",
    "resumed_without_payload",
    "resumed_with_payload",
]

COMMAND_STATE_FIELDS = [
    "transition_kind",
    "update_keys",
    "goto_target",
    "graph_scope",
    "source_subgraph",
    "target_subgraph",
    "parent_handoff_target",
    "resume_posture",
    "resume_payload_present",
    "resume_payload_keys",
]

COMMAND_PROJECTION_FIELDS = [
    "transition_kind",
    "update_keys",
    "goto_target",
    "graph_scope",
    "source_subgraph",
    "target_subgraph",
    "parent_handoff_target",
    "resume_posture",
    "resume_payload_present",
    "resume_payload_keys",
    "helper_pointer",
]

PHASE_TO_SUBGRAPH = {
    "define-target": "research",
    "read-context": "research",
    "freeze-plan": "planning",
    "execute-parallel": "execution",
    "integrate-converge": "execution",
    "stabilize": "execution",
    "verify-accept": "verification",
}

SUBGRAPHS = {
    "research": {
        "subgraph_id": "research",
        "role_family": "research",
        "roles": ["analyst", "researcher", "architect"],
        "default_phase": "read-context",
        "phase_families": ["define-target", "read-context"],
        "input_artifacts": [],
        "output_artifacts": ["frozen_implementation_brief"],
        "handoff_artifacts": ["frozen_implementation_brief"],
        "fresh_context_boundary": False,
        "durable_worker_default": "",
        "read_only_default": True,
        "persistence_mode_default": "per_thread",
        "checkpointer_mode_default": "separate_subgraph",
        "state_inspection_default": True,
        "state_inspection_scope_default": "thread_accumulated",
        "static_discoverable": True,
        "same_subgraph_parallel_calls_supported": False,
        "allowed_parent_graph_scopes": ["parent"],
    },
    "planning": {
        "subgraph_id": "planning",
        "role_family": "planning",
        "roles": ["planner"],
        "default_phase": "freeze-plan",
        "phase_families": ["freeze-plan"],
        "input_artifacts": ["frozen_implementation_brief"],
        "output_artifacts": ["execution_slice_plan", "ownership_boundaries"],
        "handoff_artifacts": ["execution_slice_plan", "ownership_boundaries"],
        "fresh_context_boundary": True,
        "durable_worker_default": "",
        "read_only_default": True,
        "persistence_mode_default": "per_invocation",
        "checkpointer_mode_default": "inherit_parent",
        "state_inspection_default": True,
        "state_inspection_scope_default": "current_invocation",
        "static_discoverable": True,
        "same_subgraph_parallel_calls_supported": True,
        "allowed_parent_graph_scopes": ["parent"],
    },
    "execution": {
        "subgraph_id": "execution",
        "role_family": "execution",
        "roles": ["executor", "team-executor"],
        "default_phase": "execute-parallel",
        "phase_families": ["execute-parallel", "integrate-converge", "stabilize"],
        "input_artifacts": ["execution_slice_plan", "ownership_boundaries"],
        "output_artifacts": ["implementation_patch_set", "execution_evidence"],
        "handoff_artifacts": ["implementation_patch_set", "execution_evidence"],
        "fresh_context_boundary": True,
        "durable_worker_default": "team-executor",
        "read_only_default": False,
        "persistence_mode_default": "per_invocation",
        "checkpointer_mode_default": "inherit_parent",
        "state_inspection_default": True,
        "state_inspection_scope_default": "current_invocation",
        "static_discoverable": True,
        "same_subgraph_parallel_calls_supported": True,
        "allowed_parent_graph_scopes": ["parent"],
    },
    "verification": {
        "subgraph_id": "verification",
        "role_family": "verification",
        "roles": ["verifier", "test-engineer", "security-reviewer", "writer"],
        "default_phase": "verify-accept",
        "phase_families": ["verify-accept"],
        "input_artifacts": ["implementation_patch_set", "execution_evidence"],
        "output_artifacts": ["verification_report"],
        "handoff_artifacts": ["verification_report"],
        "fresh_context_boundary": True,
        "durable_worker_default": "",
        "read_only_default": True,
        "persistence_mode_default": "stateless",
        "checkpointer_mode_default": "disabled",
        "state_inspection_default": False,
        "state_inspection_scope_default": "unavailable",
        "static_discoverable": True,
        "same_subgraph_parallel_calls_supported": True,
        "allowed_parent_graph_scopes": ["parent"],
    },
    "adversarial-review": {
        "subgraph_id": "adversarial-review",
        "role_family": "adversarial-review",
        "roles": ["bug-finder", "bug-rebutter", "bug-judge"],
        "default_phase": "verify-accept",
        "phase_families": [],
        "input_artifacts": ["implementation_patch_set", "execution_evidence"],
        "output_artifacts": ["judge_approved_survivor_queue"],
        "handoff_artifacts": ["judge_approved_survivor_queue"],
        "fresh_context_boundary": True,
        "durable_worker_default": "",
        "read_only_default": True,
        "persistence_mode_default": "stateless",
        "checkpointer_mode_default": "disabled",
        "state_inspection_default": False,
        "state_inspection_scope_default": "unavailable",
        "static_discoverable": True,
        "same_subgraph_parallel_calls_supported": True,
        "allowed_parent_graph_scopes": ["parent"],
    },
}

IMPLEMENTATION_BRIEF_FIELDS = [
    "brief_id",
    "thread_id",
    "objective",
    "non_goals",
    "accepted_decisions",
    "constraints",
    "interfaces",
    "ownership_boundaries",
    "acceptance_criteria",
    "validation_plan",
    "source_evidence_refs",
    "frozen_at",
]

SURVIVOR_QUEUE_FIELDS = [
    "bug_id",
    "title",
    "severity",
    "evidence",
    "judge_verdict",
    "owner_lane",
    "status",
    "verification_result",
    "updated_at",
]

SURVIVOR_QUEUE_METADATA_FIELDS = [
    "queue_kind",
    "thread_id",
    "item_count",
    "updated_at",
]

INTERRUPT_POINTS = [
    "freeze-plan",
    "stabilize-risk-review",
    "verify-accept-failed",
]

APPROVAL_QUEUE_ITEM_STATUSES = [
    "pending",
    "resolved",
]

APPROVAL_QUEUE_POSTURES = [
    "no_interrupts",
    "pending",
    "partially_resolved",
    "resolved",
]

APPROVAL_QUEUE_ITEM_FIELDS = [
    "interrupt_id",
    "order",
    "interrupt_point",
    "value_summary",
    "reason",
    "status",
    "resume_value_present",
    "resume_value_keys",
]

APPROVAL_QUEUE_PROJECTION_FIELDS = [
    "queue_posture",
    "queue_size",
    "pending_count",
    "resolved_count",
    "pending_interrupt_ids",
    "resolved_interrupt_ids",
    "current_interrupt_id",
    "resume_map_keys",
    "queue_items",
    "helper_pointer",
]

AUTOMATIC_RUNTIME_POLICY_IDENTITY = {
    "policy_kind": "bounded_langgraph_runtime_policy",
    "policy_id": "codex_user_level_langgraph_runtime_policy",
    "manual_first_default": True,
}

AUTOMATIC_RUNTIME_POLICY_IDENTITY_FIELDS = [
    "policy_kind",
    "policy_id",
    "manual_first_default",
]

AUTOMATIC_RUNTIME_POLICY_MIGRATION_POSTURES = [
    "manual_only",
    "auto_continue_safe",
    "auto_continue_with_notice",
    "manual_recovery_required",
]

AUTOMATIC_RUNTIME_POLICY_APPROVAL_POSTURES = [
    "no_queue_work",
    "waiting_for_manual_approval",
    "auto_resume_safe",
    "auto_clear_stale_interrupt",
    "resolved_queue_retained",
]

AUTOMATIC_RUNTIME_POLICY_RECOVERY_POSTURES = [
    "ordinary",
    "auto_continue_safe",
    "manual_recovery_required",
]

AUTOMATIC_RUNTIME_POLICY_ACTIONS = [
    "continue_on_migration_safe",
    "continue_on_degraded_compatible",
    "resume_after_resolved_queue",
    "continue_after_safe_recovery",
    "clear_stale_interrupt",
]

AUTOMATIC_RUNTIME_POLICY_PROJECTION_FIELDS = [
    "policy_identity",
    "migration_policy_posture",
    "approval_policy_posture",
    "recovery_policy_posture",
    "automatic_actions_available",
    "safe_to_auto_apply",
    "last_auto_action",
    "last_auto_reason",
    "helper_pointer",
]

GATE_VERDICTS = [
    "accept",
    "revise",
    "escalate",
    "halt",
    "needs_human",
]

LOOP_CAPABLE_FLOWS = {
    "review": {
        "entry_phase": "execute-parallel",
        "initial_stage": "draft",
        "resume_stage": "review",
        "accept_phase": "integrate-converge",
    },
    "execution": {
        "entry_phase": "execute-parallel",
        "initial_stage": "execute",
        "resume_stage": "execute",
        "accept_phase": "integrate-converge",
    },
    "stabilization": {
        "entry_phase": "stabilize",
        "initial_stage": "stabilize",
        "resume_stage": "stabilize",
        "accept_phase": "verify-accept",
    },
}

LOOP_PROJECTION_FIELDS = [
    "active_loop",
    "loop_stage",
    "iteration_count",
    "iteration_budget",
    "last_gate_verdict",
    "last_gate_reason",
    "stop_reason",
]

HISTORY_COMPATIBILITY_STATES = [
    "tracked_history",
    "synthetic_latest_only",
    "no_history",
]

HISTORY_PROJECTION_FIELDS = [
    "compatibility",
    "history_path",
    "history_record_count",
    "target_count",
    "available_targets",
    "source_records",
]

RECOVERY_POSTURES = [
    "ordinary",
    "recovered_pending_resume",
]

RECOVERABLE_THREAD_FIELDS = [
    "phase",
    "status",
    "parallel_slices",
    "blocking_issues",
    "active_loop",
    "loop_stage",
    "iteration_count",
    "iteration_budget",
    "last_gate_verdict",
    "last_gate_reason",
    "stop_reason",
]

RECOVERABLE_INTERRUPT_FIELDS = [
    "interrupt_point",
    "status",
    "reason",
]

RECOVERY_MUTATION_INTENTS = [
    "explicit-recovery",
]

RECOVERY_PROJECTION_FIELDS = [
    "posture",
    "last_action",
    "target_id",
    "recovered_at",
    "source_records",
    "recoverable_fields_touched",
]

REDUCER_MERGE_CHANNELS = {
    "branch_findings": {
        "reducer_kind": "dedupe_append",
        "identity_field": "finding_id",
    },
    "branch_evidence_refs": {
        "reducer_kind": "dedupe_append",
        "identity_field": "evidence_id",
    },
    "branch_artifact_pointers": {
        "reducer_kind": "dedupe_append",
        "identity_field": "artifact_id",
    },
    "branch_completion_records": {
        "reducer_kind": "replace_by_branch",
        "identity_field": "branch_id",
    },
    "branch_warnings": {
        "reducer_kind": "dedupe_append",
        "identity_field": "warning_id",
    },
    "branch_blockers": {
        "reducer_kind": "dedupe_append",
        "identity_field": "blocker_id",
    },
}

SINGLE_WRITER_FIELDS = [
    "thread_id",
    "repo_root",
    "worktree_id",
    "task",
    "phase",
    "parallel_slices",
    "blocking_issues",
    "backend",
    "langgraph_available",
    "status",
    "updated_at",
]

LEADER_OWNED_SUMMARY_FIELDS = [
    "final_summary",
    "accepted_outcome",
    "leader_summary",
]

REDUCER_COMPATIBILITY_STATES = [
    "reducer_aware",
    "pre_reducer",
]

REDUCER_PROJECTION_FIELDS = [
    "compatibility",
    "reducer_channels_present",
    "fanout_state",
    "invalid_multi_writer_detected",
    "invalid_multi_writer_updates",
    "merge_channels_updated",
    "channel_item_counts",
    "source_records",
]
