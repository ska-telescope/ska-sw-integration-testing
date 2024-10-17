"""Test module to test TMC-CSP Configure functionality."""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_till_delay_values_are_populated,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    wait_added_for_skb372,
)


@pytest.mark.skip
@pytest.mark.tmc_csp
@scenario(
    "../../mid/features/tmc_csp/xtp_29345_configure.feature",
    "Configure a CSP subarray for a scan using TMC",
)
def test_tmc_csp_configure_functionality() -> None:
    """
    Test case to verify TMC-CSP Configure functionality
    """


@given(parsers.parse("TMC subarray {subarray_id} in ObsState IDLE"))
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to IDLE obsstate."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    # Create json for AssignResources commands with requested subarray_id
    assign_input = json.loads(assign_input_json)
    assign_input["subarray_id"] = int(subarray_id)
    pytest.command_result = central_node_mid.perform_action(
        "AssignResources", json.dumps(assign_input)
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=20,
    )
    wait_added_for_skb372()


@when(
    parsers.parse(
        "I issue the Configure command to the TMC subarray {subarray_id}"
    )
)
def invoke_configure_command(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """Invoke Configure command."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    pytest.command_result = subarray_node.execute_transition(
        "Configure", argin=configure_input_json
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@then(
    parsers.parse(
        "the CSP subarray {subarray_id} transitions to ObsState READY"
    )
)
def check_if_csp_subarray_moved_to_ready_obsstate(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
) -> None:
    """Ensure CSP subarray is moved to READY obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState READY"
    )
)
def check_if_tmc_subarray_moved_to_ready_obsstate(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to READY obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )


@then(
    parsers.parse(
        "CSP subarray leaf node {subarray_id} starts generating delay values"
    )
)
def check_if_delay_values_are_generating(
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Check if delay values are generating."""
    wait_till_delay_values_are_populated(subarray_node.csp_subarray_leaf_node)
